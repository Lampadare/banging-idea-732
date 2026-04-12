"""FEM bovine vagosympathetic trunk — 20 representative fascicles.

Selection: 10 largest by area + 10 spatially distributed (angular + radial).
All fixes: P1 elements, BoomerAMG, -O0 JIT, 75um geometry gaps.
"""

import nrv
import numpy as np
import time
import json
import pickle
import gmsh
import os
import types

N_AX_PER_FASC = 30
SYMPATHETIC_FRACTION = 0.15
SYMPATHETIC_DIAM_RANGE = (0.3, 1.2)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def build_mixed_population(n_total, symp_fraction, seed=0):
    n_symp = max(1, int(n_total * symp_fraction))
    n_vagal = n_total - n_symp
    vagal_d, vagal_t, _, _ = nrv.create_axon_population(
        n_vagal, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U"
    )
    rng = np.random.default_rng(seed)
    symp_d = rng.uniform(SYMPATHETIC_DIAM_RANGE[0], SYMPATHETIC_DIAM_RANGE[1], n_symp)
    symp_t = np.zeros(n_symp)
    diams = np.concatenate([vagal_d, symp_d])
    types = np.concatenate([vagal_t, symp_t])
    labels = ["vagal"] * n_vagal + ["sympathetic"] * n_symp
    return diams, types, labels


def extract_fiber_results(fr, n_ax, fiber_labels):
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
        "vagal_myel_recruited": vagal_myel_r, "vagal_myel_total": vagal_myel_t,
        "vagal_unmyel_recruited": vagal_unmyel_r, "vagal_unmyel_total": vagal_unmyel_t,
        "symp_recruited": symp_r, "symp_total": symp_t,
        "recruited_diameters": recruited_diams,
    }


if __name__ == "__main__":
    n_cores = min(28, os.cpu_count() - 2)
    nrv.backend.parameters.set_nmod_ncore(n_cores)
    nrv.backend.parameters.set_gmsh_ncore(min(16, os.cpu_count()))
    log(f"NMOD={nrv.backend.parameters.get_nmod_ncore()}, "
        f"GMSH={nrv.backend.parameters.get_gmsh_ncore()}, cores={os.cpu_count()}")

    # Load geometry
    script_dir = os.path.dirname(os.path.abspath(__file__))
    geom_path = os.path.join(script_dir, "..", "data", "bovine_geometry.json")
    if not os.path.exists(geom_path):
        geom_path = "bovine_geometry.json"
    with open(geom_path) as f:
        geom = json.load(f)

    # Use only the 20 representative fascicles
    all_fascs = geom["vagal_fascicles"]
    subset_indices = geom["representative_subset"]["indices"]
    fascicles_geo = [all_fascs[i] for i in subset_indices]
    n_fascicles = len(fascicles_geo)
    log(f"Using {n_fascicles} representative fascicles (of {len(all_fascs)} total)")
    log(f"Selection: {geom['representative_subset']['selection_method']}")

    # Build nerve
    nerve_d = geom["nerve"]["diameter_um"]
    nerve_l = 5000
    outer_d = 10
    nerve = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)

    fasc_info = []
    all_fiber_labels = {}

    log(f"Building {n_fascicles} fascicles with {N_AX_PER_FASC} axons each...")
    t0 = time.time()
    for i, fg in enumerate(fascicles_geo):
        d = fg["diameter_um"]
        fasc = nrv.fascicle(diameter=d, ID=i)
        diams, ftypes, labels = build_mixed_population(N_AX_PER_FASC, SYMPATHETIC_FRACTION, seed=i)
        fasc.fill(data=(diams, ftypes), delta=5)
        n_placed = fasc.n_ax
        all_fiber_labels[i] = labels[:n_placed]
        nerve.add_fascicle(fasc, y=fg["y_um"], z=fg["z_um"])
        fasc_info.append({
            "id": i, "orig_id": fg["id"], "d": round(d),
            "y": round(fg["y_um"]), "z": round(fg["z_um"]),
            "n_placed": n_placed,
            "n_vagal": sum(1 for l in labels[:n_placed] if l == "vagal"),
            "n_symp": sum(1 for l in labels[:n_placed] if l == "sympathetic"),
        })
        if (i + 1) % 5 == 0 or i == n_fascicles - 1:
            log(f"  {i+1}/{n_fascicles} | d={d:.0f}um, {n_placed} axons")
    log(f"Placement done: {time.time()-t0:.1f}s")

    total_fibers = sum(fi["n_placed"] for fi in fasc_info)
    total_vagal = sum(fi["n_vagal"] for fi in fasc_info)
    total_symp = sum(fi["n_symp"] for fi in fasc_info)
    log(f"Total: {total_fibers} fibers ({total_vagal} vagal, {total_symp} sympathetic)")

    # Electrode
    cuff = nrv.CUFF_electrode(
        label="bipolar_cuff", contact_length=500, contact_thickness=200,
        insulator_length=2000, insulator_thickness=800, x_center=nerve_l / 2,
    )
    stim = nrv.stimulus()
    stim.pulse(start=0.5, value=-100, duration=0.2)

    fem_stim = nrv.FEM_stimulation(
        endo_mat="endoneurium_ranck", peri_mat="perineurium",
        epi_mat="epineurium", ext_mat="saline",
    )
    fem_stim.model.elem = ("Lagrange", 1)
    log("P1 elements set")

    fem_stim.add_electrode(cuff, stim)
    nerve.attach_extracellular_stimulation(fem_stim)

    # Monkey-patch: gmsh coarsening
    original_compute_mesh = nerve.extra_stim.model.mesh.compute_mesh.__func__
    def patched_compute_mesh(self_mesh):
        self_mesh.compute_geo()
        self_mesh.compute_domains()
        self_mesh.compute_res()
        log("  gmsh: CharacteristicLengthMin=30, Delaunay")
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 30)
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        self_mesh.generate()
    nerve.extra_stim.model.mesh.compute_mesh = types.MethodType(
        patched_compute_mesh, nerve.extra_stim.model.mesh
    )

    # Monkey-patch: BoomerAMG after setup_simulations
    original_setup_sims = nerve.extra_stim.model.setup_simulations.__func__
    def patched_setup_simulations(self_model):
        original_setup_sims(self_model)
        log("  BoomerAMG: configuring after setup_simulations")
        self_model.sim.petsc_opt = {
            "ksp_type": "cg",
            "pc_type": "hypre",
            "pc_hypre_type": "boomeramg",
            "pc_hypre_boomeramg_strong_threshold": "0.5",
            "ksp_rtol": "1e-4",
            "ksp_atol": "1e-7",
            "ksp_max_it": "2000",
        }
        log("  BoomerAMG: configured")
    nerve.extra_stim.model.setup_simulations = types.MethodType(
        patched_setup_simulations, nerve.extra_stim.model
    )

    # Phase 1: FEM
    log("=" * 60)
    log("Phase 1: FEM solve (one-time)")
    t0_fem = time.time()
    nerve.compute_electrodes_footprints()
    fem_time = time.time() - t0_fem
    log(f"FEM solved: {fem_time:.1f}s ({fem_time/60:.1f} min)")

    # Save
    log("Saving nerve + footprints...")
    nerve.save("bovine_nerve_20fasc.json", extracel_context=True)
    log("Saved: bovine_nerve_20fasc.json")

    # Phase 2: Amplitude sweep
    amplitudes = np.linspace(50, 1000, 20).astype(int)
    log("=" * 60)
    log(f"Phase 2: Amplitude sweep ({len(amplitudes)} points)")

    all_results = {
        "geometry": {
            "source": geom["source"],
            "nerve_diameter_um": nerve_d,
            "n_fascicles_total": len(all_fascs),
            "n_fascicles_modeled": n_fascicles,
            "selection_method": geom["representative_subset"]["selection_method"],
            "n_axons_per_fascicle": N_AX_PER_FASC,
            "sympathetic_fraction": SYMPATHETIC_FRACTION,
            "total_fibers": total_fibers,
            "fem_solve_time_s": round(fem_time, 1),
            "optimizations": "P1+BoomerAMG+gmshCoarsen+footprintCache",
        },
        "fascicle_info": fasc_info,
        "amplitudes": {},
    }

    for amp_idx, amp in enumerate(amplitudes):
        log(f"[{amp_idx+1}/{len(amplitudes)}] {amp} uA ({amp/1000:.2f} mA)")
        new_stim = nrv.stimulus()
        new_stim.pulse(start=0.5, value=-float(amp), duration=0.2)
        nerve.change_stimulus_from_electrode(0, new_stim)

        t0 = time.time()
        results = nerve(t_sim=3)
        sim_time = time.time() - t0
        log(f"  NEURON: {sim_time:.1f}s")

        amp_data = {"sim_time_s": round(sim_time, 1), "fascicles": {}}
        tot_vm_r, tot_vm_t, tot_vu_r, tot_vu_t, tot_s_r, tot_s_t = 0, 0, 0, 0, 0, 0

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
            amp_data["fascicles"][i] = {"info": fasc_info[i], **fiber_res}

        amp_data["summary"] = {
            "vagal_myel": f"{tot_vm_r}/{tot_vm_t}",
            "vagal_unmyel": f"{tot_vu_r}/{tot_vu_t}",
            "sympathetic": f"{tot_s_r}/{tot_s_t}",
        }
        log(f"  V-myel: {tot_vm_r}/{tot_vm_t} | V-unmyel: {tot_vu_r}/{tot_vu_t} | Symp: {tot_s_r}/{tot_s_t}")
        all_results["amplitudes"][int(amp)] = amp_data

    with open("bovine_20fasc_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    with open("bovine_20fasc_results.pkl", "wb") as f:
        pickle.dump(all_results, f)

    total_neuron = sum(all_results["amplitudes"][a]["sim_time_s"] for a in all_results["amplitudes"])
    log("=" * 60)
    log("COMPLETE")
    log(f"FEM: {fem_time:.1f}s ({fem_time/60:.1f} min)")
    log(f"NEURON: {total_neuron:.1f}s ({total_neuron/60:.1f} min)")
    log(f"Total: {fem_time+total_neuron:.1f}s ({(fem_time+total_neuron)/60:.1f} min)")
    log("Saved: bovine_20fasc_results.json + .pkl")
