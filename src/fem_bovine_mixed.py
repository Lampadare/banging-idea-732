"""FEM sweep on bovine vagosympathetic trunk — mixed vagal/sympathetic populations.

57 fascicles from P12-1 pig (SPARC-64), scaled to bovine.
Each fascicle: 85% vagal fibers + 15% sympathetic fibers (intermingled).

Optimizations:
  - Footprint caching (1 FEM solve)
  - 28-core NEURON parallelism
  - 16-thread gmsh meshing
  - Coarsened axon mesh resolution (50um)
"""

import nrv
import numpy as np
import time
import json
import pickle

N_AX_PER_FASC = 30
SYMPATHETIC_FRACTION = 0.15
SYMPATHETIC_DIAM_RANGE = (0.3, 1.2)  # um, small unmyelinated C-fibers


def build_mixed_population(n_total, symp_fraction, seed=0):
    """Build a mixed vagal + sympathetic fiber population.

    Returns:
        diams: array of diameters (um)
        types: array of 1.0 (myelinated) or 0.0 (unmyelinated)
        labels: list of 'vagal' or 'sympathetic' per fiber
    """
    n_symp = max(1, int(n_total * symp_fraction))
    n_vagal = n_total - n_symp

    # Vagal fibers: standard distribution (mix of myelinated + unmyelinated)
    vagal_diams, vagal_types, _, _ = nrv.create_axon_population(
        n_vagal, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U"
    )

    # Sympathetic fibers: small unmyelinated C-fibers
    rng = np.random.default_rng(seed)
    symp_diams = rng.uniform(SYMPATHETIC_DIAM_RANGE[0], SYMPATHETIC_DIAM_RANGE[1], n_symp)
    symp_types = np.zeros(n_symp)  # all unmyelinated

    # Combine
    diams = np.concatenate([vagal_diams, symp_diams])
    types = np.concatenate([vagal_types, symp_types])
    labels = ["vagal"] * n_vagal + ["sympathetic"] * n_symp

    return diams, types, labels


def extract_fiber_results(fr, n_ax, fiber_labels):
    """Extract per-fiber recruitment results with vagal/sympathetic breakdown."""
    vagal_myel_r, vagal_myel_t = 0, 0
    vagal_unmyel_r, vagal_unmyel_t = 0, 0
    symp_r, symp_t = 0, 0
    recruited_diams = []

    for j in range(n_ax):
        ax = getattr(fr, f"axon{j}", None)
        if ax is None:
            continue

        is_myel = ax.get("myelinated", False) if hasattr(ax, "get") else False
        is_rec = ax.is_recruited()
        d_ax = float(ax.get("d", 0) if hasattr(ax, "get") else 0)
        label = fiber_labels[j] if j < len(fiber_labels) else "vagal"

        if label == "sympathetic":
            symp_t += 1
            if is_rec:
                symp_r += 1
                recruited_diams.append(d_ax)
        elif is_myel:
            vagal_myel_t += 1
            if is_rec:
                vagal_myel_r += 1
                recruited_diams.append(d_ax)
        else:
            vagal_unmyel_t += 1
            if is_rec:
                vagal_unmyel_r += 1
                recruited_diams.append(d_ax)

    return {
        "vagal_myel_recruited": vagal_myel_r,
        "vagal_myel_total": vagal_myel_t,
        "vagal_unmyel_recruited": vagal_unmyel_r,
        "vagal_unmyel_total": vagal_unmyel_t,
        "symp_recruited": symp_r,
        "symp_total": symp_t,
        "recruited_diameters": recruited_diams,
    }


if __name__ == "__main__":
    # --- Optimization ---
    nrv.backend.parameters.set_nmod_ncore(28)
    nrv.backend.parameters.set_gmsh_ncore(16)
    print(f"NMOD cores: {nrv.backend.parameters.get_nmod_ncore()}")
    print(f"GMSH cores: {nrv.backend.parameters.get_gmsh_ncore()}")

    # --- Load geometry ---
    with open("bovine_geometry.json") as f:
        geom = json.load(f)

    fascicles_geo = geom["vagal_fascicles"]
    n_fascicles = len(fascicles_geo)
    print(f"\nGeometry: {n_fascicles} fascicles (mixed vagal+sympathetic populations)")
    print(f"Nerve: {geom['nerve']['diameter_um']}um, ratio {geom['nerve']['aspect_ratio']}")
    print(f"Per fascicle: {N_AX_PER_FASC} axons "
          f"({100-SYMPATHETIC_FRACTION*100:.0f}% vagal, {SYMPATHETIC_FRACTION*100:.0f}% sympathetic)")

    # --- Build nerve ---
    nerve_d = geom["nerve"]["diameter_um"]
    nerve_l = 10000
    outer_d = 12  # mm

    nerve = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)

    fasc_info = []
    all_fiber_labels = {}  # fascicle_id -> list of labels per axon

    print(f"\nBuilding {n_fascicles} fascicles...")
    for i, fg in enumerate(fascicles_geo):
        d = fg["diameter_um"]
        fasc = nrv.fascicle(diameter=d, ID=i)

        # Build mixed population
        diams, types, labels = build_mixed_population(
            N_AX_PER_FASC, SYMPATHETIC_FRACTION, seed=i
        )
        fasc.fill(data=(diams, types), delta=5)

        # Track how many were actually placed (small fascicles may not fit all)
        n_placed = fasc.n_ax
        all_fiber_labels[i] = labels[:n_placed]

        nerve.add_fascicle(fasc, y=fg["y_um"], z=fg["z_um"])
        fasc_info.append({
            "id": i,
            "orig_id": fg["id"],
            "d": round(d),
            "y": round(fg["y_um"]),
            "z": round(fg["z_um"]),
            "n_placed": n_placed,
            "n_vagal": sum(1 for l in labels[:n_placed] if l == "vagal"),
            "n_symp": sum(1 for l in labels[:n_placed] if l == "sympathetic"),
        })

        if (i + 1) % 10 == 0 or i == n_fascicles - 1:
            print(f"  {i+1}/{n_fascicles} | F{i}: d={d:.0f}um, "
                  f"{fasc_info[-1]['n_vagal']}V+{fasc_info[-1]['n_symp']}S={n_placed} placed")

    total_fibers = sum(fi["n_placed"] for fi in fasc_info)
    total_vagal = sum(fi["n_vagal"] for fi in fasc_info)
    total_symp = sum(fi["n_symp"] for fi in fasc_info)
    print(f"\nTotal: {total_fibers} fibers ({total_vagal} vagal, {total_symp} sympathetic)")

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

    # --- Phase 1: FEM solve ---
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
    print(f"Phase 2: Amplitude sweep ({len(amplitudes)} points)")
    print(f"Amplitudes: {amplitudes.tolist()}")
    print(f"{'='*60}")

    all_results = {
        "geometry": {
            "source": geom["source"],
            "nerve_diameter_um": nerve_d,
            "n_fascicles": n_fascicles,
            "n_axons_per_fascicle": N_AX_PER_FASC,
            "sympathetic_fraction": SYMPATHETIC_FRACTION,
            "total_fibers": total_fibers,
            "total_vagal": total_vagal,
            "total_sympathetic": total_symp,
            "fem_solve_time_s": round(fem_time, 1),
        },
        "fascicle_info": fasc_info,
        "amplitudes": {},
    }

    for amp_idx, amp in enumerate(amplitudes):
        print(f"\n[{amp_idx+1}/{len(amplitudes)}] {amp} uA ({amp/1000:.2f} mA)")

        new_stim = nrv.stimulus()
        new_stim.pulse(start=0.5, value=-float(amp), duration=0.2)
        nerve.change_stimulus_from_electrode(0, new_stim)

        t0 = time.time()
        results = nerve(t_sim=3)
        sim_time = time.time() - t0
        print(f"  NEURON: {sim_time:.1f}s")

        amp_data = {"sim_time_s": round(sim_time, 1), "fascicles": {}}

        # Aggregate
        tot_vm_r, tot_vm_t = 0, 0  # vagal myelinated
        tot_vu_r, tot_vu_t = 0, 0  # vagal unmyelinated
        tot_s_r, tot_s_t = 0, 0    # sympathetic

        for i in range(n_fascicles):
            fr = results.get_fascicle_results(i)
            labels = all_fiber_labels.get(i, [])
            fiber_res = extract_fiber_results(fr, fasc_info[i]["n_placed"], labels)

            tot_vm_r += fiber_res["vagal_myel_recruited"]
            tot_vm_t += fiber_res["vagal_myel_total"]
            tot_vu_r += fiber_res["vagal_unmyel_recruited"]
            tot_vu_t += fiber_res["vagal_unmyel_total"]
            tot_s_r += fiber_res["symp_recruited"]
            tot_s_t += fiber_res["symp_total"]

            amp_data["fascicles"][i] = {
                "info": fasc_info[i],
                **fiber_res,
            }

        amp_data["summary"] = {
            "vagal_myel": f"{tot_vm_r}/{tot_vm_t}",
            "vagal_unmyel": f"{tot_vu_r}/{tot_vu_t}",
            "sympathetic": f"{tot_s_r}/{tot_s_t}",
        }

        print(f"  Vagal myel:   {tot_vm_r}/{tot_vm_t}")
        print(f"  Vagal unmyel: {tot_vu_r}/{tot_vu_t}")
        print(f"  Sympathetic:  {tot_s_r}/{tot_s_t}")

        all_results["amplitudes"][int(amp)] = amp_data

    # --- Save ---
    with open("bovine_mixed_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    with open("bovine_mixed_results.pkl", "wb") as f:
        pickle.dump(all_results, f)

    total_neuron = sum(
        all_results["amplitudes"][a]["sim_time_s"]
        for a in all_results["amplitudes"]
    )
    print(f"\n{'='*60}")
    print("COMPLETE")
    print(f"{'='*60}")
    print(f"FEM solve: {fem_time:.1f}s ({fem_time/60:.1f} min)")
    print(f"NEURON sims: {total_neuron:.1f}s ({total_neuron/60:.1f} min)")
    print(f"Total: {fem_time + total_neuron:.1f}s ({(fem_time + total_neuron)/60:.1f} min)")
    print(f"Saved: bovine_mixed_results.json + .pkl")
