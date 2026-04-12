"""FEM sweep on real bovine vagosympathetic trunk geometry (103 fascicles).

Source: P12-1 pig cervical vagus (SPARC-64), PCA-aligned, scaled to bovine,
collision-resolved, 46 sympathetic fascicles added (15% area).
"""

import nrv
import numpy as np
import time
import json
import pickle

if __name__ == "__main__":
    # --- Optimization ---
    nrv.backend.parameters.set_nmod_ncore(28)
    nrv.backend.parameters.set_gmsh_ncore(16)
    print(f"NMOD cores: {nrv.backend.parameters.get_nmod_ncore()}")
    print(f"GMSH cores: {nrv.backend.parameters.get_gmsh_ncore()}")

    # --- Load bovine geometry ---
    with open("bovine_geometry.json") as f:
        geom = json.load(f)

    all_fascicles = geom["vagal_fascicles"] + geom["sympathetic_fascicles"]
    n_fascicles = len(all_fascicles)
    print(f"\nGeometry: {len(geom['vagal_fascicles'])} vagal + "
          f"{len(geom['sympathetic_fascicles'])} sympathetic = {n_fascicles} fascicles")
    print(f"Nerve: {geom['nerve']['diameter_um']}um, "
          f"aspect ratio {geom['nerve']['aspect_ratio']}")

    # --- Build nerve ---
    nerve_d = geom["nerve"]["diameter_um"]
    nerve_l = 10000  # 10mm
    outer_d = 12  # mm, needs to be larger for bigger nerve

    nerve = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)

    n_ax_per_fasc = 30
    fasc_info = []

    print(f"\nBuilding {n_fascicles} fascicles with {n_ax_per_fasc} axons each...")
    for i, f in enumerate(all_fascicles):
        d = f["diameter_um"]
        fasc = nrv.fascicle(diameter=d, ID=i)
        fasc.fill(n_ax=n_ax_per_fasc, percent_unmyel=0.7,
                  M_stat="Ochoa_M", U_stat="Ochoa_U", delta=5)

        nerve.add_fascicle(fasc, y=f["y_um"], z=f["z_um"])
        fasc_info.append({
            "id": i,
            "orig_id": f["id"],
            "type": f["type"],
            "d": round(d),
            "y": round(f["y_um"]),
            "z": round(f["z_um"]),
        })
        if (i + 1) % 20 == 0 or i == n_fascicles - 1:
            print(f"  {i + 1}/{n_fascicles} fascicles placed")

    # --- Electrode ---
    cuff = nrv.CUFF_electrode(
        label="bipolar_cuff",
        contact_length=500,
        contact_thickness=200,
        insulator_length=2000,
        insulator_thickness=800,
        x_center=nerve_l / 2,
    )
    stim = nrv.stimulus()
    stim.pulse(start=0.5, value=-100, duration=0.2)

    fem_stim = nrv.FEM_stimulation(
        endo_mat="endoneurium_ranck",
        peri_mat="perineurium",
        epi_mat="epineurium",
        ext_mat="saline",
    )
    fem_stim.add_electrode(cuff, stim)
    nerve.attach_extracellular_stimulation(fem_stim)

    # --- Phase 1: FEM solve (one-time) ---
    print(f"\n{'='*60}")
    print("Phase 1: FEM solve (one-time)")
    print(f"{'='*60}")
    t0_fem = time.time()
    nerve.compute_electrodes_footprints()
    fem_time = time.time() - t0_fem
    print(f"FEM solved in {fem_time:.1f}s ({fem_time/60:.1f} min)")

    # --- Phase 2: Amplitude sweep ---
    amplitudes = np.linspace(100, 1000, 20).astype(int)
    print(f"\n{'='*60}")
    print(f"Phase 2: Amplitude sweep ({len(amplitudes)} points, NEURON only)")
    print(f"Amplitudes: {amplitudes.tolist()}")
    print(f"{'='*60}")

    all_results = {
        "geometry": {
            "source": geom["source"],
            "nerve_diameter_um": nerve_d,
            "n_vagal": len(geom["vagal_fascicles"]),
            "n_sympathetic": len(geom["sympathetic_fascicles"]),
            "n_total": n_fascicles,
            "n_axons_per_fascicle": n_ax_per_fasc,
            "fem_solve_time_s": round(fem_time, 1),
        },
        "amplitudes": {},
    }

    for amp_idx, amp in enumerate(amplitudes):
        print(f"\n[{amp_idx + 1}/{len(amplitudes)}] {amp} uA ({amp/1000:.2f} mA)")

        new_stim = nrv.stimulus()
        new_stim.pulse(start=0.5, value=-float(amp), duration=0.2)
        nerve.change_stimulus_from_electrode(0, new_stim)

        t0 = time.time()
        results = nerve(t_sim=3)
        sim_time = time.time() - t0
        print(f"  NEURON sim: {sim_time:.1f}s")

        amp_data = {"sim_time_s": round(sim_time, 1), "fascicles": {}}

        # Aggregate stats
        vagal_myel_recruited = 0
        vagal_myel_total = 0
        vagal_unmyel_recruited = 0
        vagal_unmyel_total = 0
        symp_myel_recruited = 0
        symp_myel_total = 0
        symp_unmyel_recruited = 0
        symp_unmyel_total = 0

        for i in range(n_fascicles):
            fr = results.get_fascicle_results(i)
            n_recruited = fr.get_recruited_axons()

            n_mr, n_mt, n_ur, n_ut = 0, 0, 0, 0
            rec_diams = []
            for j in range(n_ax_per_fasc):
                ax = getattr(fr, f"axon{j}", None)
                if ax is not None:
                    is_myel = ax.get("myelinated", False) if hasattr(ax, "get") else False
                    is_rec = ax.is_recruited()
                    d_ax = ax.get("d", 0) if hasattr(ax, "get") else 0
                    if is_myel:
                        n_mt += 1
                        if is_rec:
                            n_mr += 1
                            rec_diams.append(float(d_ax))
                    else:
                        n_ut += 1
                        if is_rec:
                            n_ur += 1

            ftype = fasc_info[i]["type"]
            if ftype == "vagal":
                vagal_myel_recruited += n_mr
                vagal_myel_total += n_mt
                vagal_unmyel_recruited += n_ur
                vagal_unmyel_total += n_ut
            else:
                symp_myel_recruited += n_mr
                symp_myel_total += n_mt
                symp_unmyel_recruited += n_ur
                symp_unmyel_total += n_ut

            amp_data["fascicles"][i] = {
                "info": fasc_info[i],
                "total_recruited": n_recruited,
                "myel_recruited": n_mr,
                "myel_total": n_mt,
                "unmyel_recruited": n_ur,
                "unmyel_total": n_ut,
                "recruited_diameters": rec_diams,
            }

        amp_data["summary"] = {
            "vagal_myel": f"{vagal_myel_recruited}/{vagal_myel_total}",
            "vagal_unmyel": f"{vagal_unmyel_recruited}/{vagal_unmyel_total}",
            "symp_myel": f"{symp_myel_recruited}/{symp_myel_total}",
            "symp_unmyel": f"{symp_unmyel_recruited}/{symp_unmyel_total}",
        }

        print(f"  Vagal:  myel {vagal_myel_recruited}/{vagal_myel_total} | "
              f"unmyel {vagal_unmyel_recruited}/{vagal_unmyel_total}")
        print(f"  Symp:   myel {symp_myel_recruited}/{symp_myel_total} | "
              f"unmyel {symp_unmyel_recruited}/{symp_unmyel_total}")

        all_results["amplitudes"][int(amp)] = amp_data

    # --- Save ---
    with open("bovine_sweep_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    with open("bovine_sweep_results.pkl", "wb") as f:
        pickle.dump(all_results, f)

    total_neuron = sum(
        all_results["amplitudes"][a]["sim_time_s"]
        for a in all_results["amplitudes"]
    )
    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"FEM solve: {fem_time:.1f}s ({fem_time/60:.1f} min)")
    print(f"NEURON sims: {total_neuron:.1f}s ({total_neuron/60:.1f} min)")
    print(f"Total: {fem_time + total_neuron:.1f}s ({(fem_time + total_neuron)/60:.1f} min)")
    print(f"Saved: bovine_sweep_results.json + .pkl")
