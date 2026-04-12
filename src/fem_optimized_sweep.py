"""Optimized FEM amplitude sweep — solves FEM once, reuses footprints.

Optimizations applied:
  1. Footprint caching: FEM solves at 1mA, stores V/mA. Amplitude = scalar multiply.
  2. NMOD_CPU = 28: NEURON fiber sims parallelized across 28 cores.
  3. GMSH_CPU = 16: mesh generation uses 16 threads.
"""

import nrv
import numpy as np
import time
import json
import pickle
import sys

if __name__ == "__main__":
    # --- Optimization: max CPU usage ---
    nrv.backend.parameters.set_nmod_ncore(28)
    nrv.backend.parameters.set_gmsh_ncore(16)
    print(f"NMOD cores: {nrv.backend.parameters.get_nmod_ncore()}")
    print(f"GMSH cores: {nrv.backend.parameters.get_gmsh_ncore()}")

    # --- Geometry ---
    nerve_d = 5000
    nerve_l = 10000
    outer_d = 10

    rng_master = np.random.default_rng(42)
    n_fascicles = 6
    semi_a = nerve_d / 2 * 0.75
    semi_b = semi_a / 1.4

    amplitudes = np.linspace(100, 1000, 20).astype(int)
    print(f"Amplitudes: {amplitudes.tolist()}")

    # --- Build nerve ONCE ---
    print("\n=== Building nerve geometry ===")
    nerve = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)
    fasc_info = []

    for i in range(n_fascicles):
        rng_f = np.random.default_rng(42 + i)
        d = np.clip(rng_f.normal(350, 80), 150, 550)
        fasc = nrv.fascicle(diameter=d, ID=i)
        fasc.fill(n_ax=50, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U", delta=5)

        rng_pos = np.random.default_rng(42)
        for j in range(i + 1):
            for _ in range(200):
                y = rng_pos.uniform(-semi_a, semi_a)
                z = rng_pos.uniform(-semi_b, semi_b)
                if (y / semi_a) ** 2 + (z / semi_b) ** 2 < 0.85:
                    break

        nerve.add_fascicle(fasc, y=y, z=z)
        fasc_info.append({"id": i, "d": round(d), "y": round(y), "z": round(z)})
        print(f"  F{i}: d={d:.0f}um at ({y:.0f}, {z:.0f})")

    # --- Electrode + initial stimulus ---
    cuff = nrv.CUFF_electrode(
        label="bipolar_cuff",
        contact_length=500,
        contact_thickness=200,
        insulator_length=2000,
        insulator_thickness=800,
        x_center=nerve_l / 2,
    )
    stim = nrv.stimulus()
    stim.pulse(start=0.5, value=-100, duration=0.2)  # initial amplitude doesn't matter

    fem_stim = nrv.FEM_stimulation(
        endo_mat="endoneurium_ranck",
        peri_mat="perineurium",
        epi_mat="epineurium",
        ext_mat="saline",
    )
    fem_stim.add_electrode(cuff, stim)
    nerve.attach_extracellular_stimulation(fem_stim)

    # --- PHASE 1: Solve FEM ONCE ---
    print("\n=== Phase 1: FEM solve (one-time) ===")
    t0 = time.time()
    nerve.compute_electrodes_footprints()
    fem_time = time.time() - t0
    print(f"FEM solved in {fem_time:.1f}s")
    print(f"Footprints cached: nerve.is_footprinted = True")

    # --- PHASE 2: Amplitude sweep (NEURON only, no FEM re-solve) ---
    print(f"\n=== Phase 2: Amplitude sweep ({len(amplitudes)} points, NEURON only) ===")
    all_results = {}

    for amp_idx, amp in enumerate(amplitudes):
        print(f"\n[{amp_idx + 1}/{len(amplitudes)}] {amp} uA ({amp / 1000:.2f} mA)")

        # Update stimulus amplitude — footprint stays cached
        new_stim = nrv.stimulus()
        new_stim.pulse(start=0.5, value=-float(amp), duration=0.2)
        nerve.change_stimulus_from_electrode(0, new_stim)

        t0 = time.time()
        results = nerve(t_sim=3)
        sim_time = time.time() - t0
        print(f"  NEURON sim: {sim_time:.1f}s")

        amp_data = {
            "amplitude_uA": int(amp),
            "sim_time_s": round(sim_time, 1),
            "fascicles": {},
        }

        for i in range(n_fascicles):
            fr = results.get_fascicle_results(i)
            n_total = 50
            n_recruited = fr.get_recruited_axons()

            n_myel_recruited = 0
            n_myel_total = 0
            n_unmyel_recruited = 0
            n_unmyel_total = 0
            recruited_diameters = []
            not_recruited_diameters = []

            for j in range(n_total):
                ax = getattr(fr, f"axon{j}", None)
                if ax is not None:
                    is_myel = ax.get("myelinated", False) if hasattr(ax, "get") else False
                    is_rec = ax.is_recruited()
                    d_ax = ax.get("d", 0) if hasattr(ax, "get") else 0
                    if is_myel:
                        n_myel_total += 1
                        if is_rec:
                            n_myel_recruited += 1
                            recruited_diameters.append(float(d_ax))
                        else:
                            not_recruited_diameters.append(float(d_ax))
                    else:
                        n_unmyel_total += 1
                        if is_rec:
                            n_unmyel_recruited += 1

            print(
                f"  F{i}: {n_recruited}/{n_total} | "
                f"myel {n_myel_recruited}/{n_myel_total} | "
                f"unmyel {n_unmyel_recruited}/{n_unmyel_total}"
            )

            amp_data["fascicles"][i] = {
                "position": fasc_info[i],
                "total_recruited": n_recruited,
                "myel_recruited": n_myel_recruited,
                "myel_total": n_myel_total,
                "unmyel_recruited": n_unmyel_recruited,
                "unmyel_total": n_unmyel_total,
                "recruited_diameters": recruited_diameters,
                "not_recruited_diameters": not_recruited_diameters,
            }

        all_results[int(amp)] = amp_data

    # --- Save ---
    with open("optimized_sweep_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    with open("optimized_sweep_results.pkl", "wb") as f:
        pickle.dump(all_results, f)

    total_time = fem_time + sum(
        all_results[a]["sim_time_s"] for a in all_results
    )
    print(f"\n=== COMPLETE ===")
    print(f"FEM solve: {fem_time:.1f}s (one-time)")
    print(f"NEURON sims: {total_time - fem_time:.1f}s ({len(amplitudes)} amplitudes)")
    print(f"Total: {total_time:.1f}s")
    print(f"Saved: optimized_sweep_results.json + .pkl")
