#!/usr/bin/env python
"""Electrode comparison: per-contact basis fields + linear combination search.

For each contact count (bipolar, 4, 8, 16):
  1. Build nerve with 6 fascicles (proven config)
  2. Create CUFF_MP_electrode with N contacts
  3. FEM solve → N basis fields (NRV loops per-contact automatically)
  4. Sample each basis field at 57 centroids + cross-section grid
  5. Save basis fields
  6. Search: linearly combine basis fields with candidate weight vectors
     Score by selectivity (vagal myelinated vs sympathetic recruitment)
  7. Output: best configs + heatmaps

Uses threshold model calibrated from batch run results — no NEURON needed.

Usage:
    python src/electrode_comparison.py [--calibration merged/results.json]
    python src/electrode_comparison.py --contacts 4   # single config
"""

import nrv
import numpy as np
import time
import json
import os
import sys
import types
import gmsh
import threading
import resource
from pathlib import Path
from itertools import product

IS_MAC = sys.platform == "darwin"
N_CPU = os.cpu_count() or 4
GMSH_CORES = min(N_CPU, 16)

NERVE_LENGTH = 10000
NERVE_DIAM = 5000
N_AX = 50
SYMP_FRAC = 0.15
N_XPTS = 200
GRID_RES = 80
AMPS = np.linspace(100, 1000, 20).astype(int)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def build_mixed_pop(n, frac, seed=0):
    n_s = max(1, int(n * frac))
    n_v = n - n_s
    vd, vt, _, _ = nrv.create_axon_population(
        n_v, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U"
    )
    rng = np.random.default_rng(seed)
    sd = rng.uniform(0.3, 1.2, n_s)
    st = np.zeros(n_s)
    return (
        np.concatenate([vd, sd]),
        np.concatenate([vt, st]),
        ["vagal"] * n_v + ["sympathetic"] * n_s,
    )


# ============================================================
# Threshold model (from extrapolate_57.py)
# ============================================================
def calibrate_thresholds(results, voltages):
    """Calibrate V_eff → recruitment thresholds from FEM results + voltage data."""
    fi = results["fi"]
    amps_data = results["amps"]
    amp_keys = sorted([int(k) for k in amps_data.keys()])

    # V_peak per modeled fascicle
    vpeaks = []
    for f in fi:
        oid = f["orig_id"]
        key = f"f{oid}"
        if key in voltages and np.abs(voltages[key]).max() > 0:
            vpeaks.append(np.abs(voltages[key]).max())
        else:
            vpeaks.append(0)

    # Collect (V_eff, recruitment_fraction) per fiber type
    vm_pts, vu_pts, s_pts = [], [], []
    for amp in amp_keys:
        ad = amps_data[str(amp)]
        for i, f in enumerate(fi):
            if vpeaks[i] == 0:
                continue
            v_eff = vpeaks[i] * amp
            fd = ad["f"][str(i)] if str(i) in ad["f"] else ad["f"][str(f["id"])]
            if fd["vm_t"] > 0:
                vm_pts.append((v_eff, fd["vm_r"] / fd["vm_t"]))
            if fd["vu_t"] > 0:
                vu_pts.append((v_eff, fd["vu_r"] / fd["vu_t"]))
            if fd["s_t"] > 0:
                s_pts.append((v_eff, fd["s_r"] / fd["s_t"]))

    def fit_threshold(pts):
        if not pts:
            return float("inf")
        pts = np.array(pts)
        recruited = pts[pts[:, 1] > 0.5, 0]
        not_rec = pts[pts[:, 1] < 0.1, 0]
        if len(recruited) > 0 and len(not_rec) > 0:
            return (recruited.min() + not_rec.max()) / 2
        elif len(recruited) > 0:
            return recruited.min() * 0.8
        return float("inf")

    thresholds = {
        "vagal_myel": fit_threshold(vm_pts),
        "vagal_unmyel": fit_threshold(vu_pts),
        "sympathetic": fit_threshold(s_pts),
    }
    log(f"Thresholds: vm={thresholds['vagal_myel']:.0f}, "
        f"vu={thresholds['vagal_unmyel']:.0f}, s={thresholds['sympathetic']:.0f}")
    return thresholds


def predict_recruitment_from_vpeak(vpeak, amp, thresholds, n_fibers=50, symp_frac=0.15):
    """Predict recruitment at a fascicle given V_peak and amplitude."""
    v_eff = vpeak * amp
    n_s = max(1, int(n_fibers * symp_frac))
    n_v = n_fibers - n_s
    n_vm = int(n_v * 0.3)
    n_vu = n_v - n_vm

    # Diameter-dependent threshold for myelinated
    rng = np.random.default_rng(42)
    myel_diams = rng.lognormal(1.8, 0.5, n_vm).clip(2, 16)
    vm_r = sum(1 for d in myel_diams if v_eff > thresholds["vagal_myel"] * (8.0 / max(d, 1)))
    vu_r = n_vu if v_eff > thresholds["vagal_unmyel"] else 0
    s_r = n_s if v_eff > thresholds["sympathetic"] else 0

    return {
        "vm_r": vm_r, "vm_t": n_vm,
        "vu_r": vu_r, "vu_t": n_vu,
        "s_r": s_r, "s_t": n_s,
        "rd": [],
    }


# ============================================================
# Nerve building (reused from fem_6_mixed.py)
# ============================================================
def build_nerve_and_fascicles(geom):
    """Build nerve with 6 representative fascicles. Returns nerve, fi, all_labels."""
    all_fascs = geom["vagal_fascicles"]
    indices = geom["representative_subset_15"]["indices"][:6]
    fascs_geo = [all_fascs[i] for i in indices]

    nerve = nrv.nerve(length=NERVE_LENGTH, diameter=NERVE_DIAM, Outer_D=10)
    fi = []
    all_labels = {}
    for i, fg in enumerate(fascs_geo):
        fasc = nrv.fascicle(diameter=fg["diameter_um"], ID=i)
        diams, ftypes, labels = build_mixed_pop(N_AX, SYMP_FRAC, seed=fg["id"])
        fasc.fill(data={"types": ftypes, "diameters": diams}, delta=5)
        n_placed = fasc.n_ax
        all_labels[i] = labels[:n_placed]
        nerve.add_fascicle(fasc, y=fg["y_um"], z=fg["z_um"])
        fi.append({
            "id": i, "orig_id": fg["id"], "d": round(fg["diameter_um"]),
            "y": round(fg["y_um"]), "z": round(fg["z_um"]),
            "np": n_placed,
            "nv": sum(1 for l in labels[:n_placed] if l == "vagal"),
            "ns": sum(1 for l in labels[:n_placed] if l == "sympathetic"),
            "source": "fem",
        })
    return nerve, fi, all_labels


# ============================================================
# Electrode configs
# ============================================================
def setup_bipolar(nerve):
    """True bipolar: two full-ring CUFF_electrodes at different x positions."""
    fem_stim = nrv.FEM_stimulation(
        endo_mat="endoneurium_ranck", peri_mat="perineurium",
        epi_mat="epineurium", ext_mat="saline",
    )

    # Cathode
    cathode = nrv.CUFF_electrode(
        label="cathode", contact_length=500, contact_thickness=200,
        insulator_length=1000, insulator_thickness=800,
        x_center=NERVE_LENGTH / 2 - 500,
    )
    stim_c = nrv.stimulus()
    stim_c.pulse(start=0.5, value=-1, duration=0.2)

    # Anode
    anode = nrv.CUFF_electrode(
        label="anode", contact_length=500, contact_thickness=200,
        insulator_length=1000, insulator_thickness=800,
        x_center=NERVE_LENGTH / 2 + 500,
    )
    stim_a = nrv.stimulus()
    stim_a.pulse(start=0.5, value=1, duration=0.2)

    fem_stim.add_electrode(cathode, stim_c)
    fem_stim.add_electrode(anode, stim_a)
    return fem_stim, 2


def setup_mp(nerve, n_contact):
    """Multipolar cuff with N contacts."""
    fem_stim = nrv.FEM_stimulation(
        endo_mat="endoneurium_ranck", peri_mat="perineurium",
        epi_mat="epineurium", ext_mat="saline",
    )

    contact_width = 0.5 * np.pi * NERVE_DIAM / n_contact

    elec = nrv.CUFF_MP_electrode(
        label=f"mp{n_contact}",
        N_contact=n_contact,
        contact_length=500,
        contact_thickness=200,
        contact_width=contact_width,
        insulator_length=2000,
        insulator_thickness=800,
        x_center=NERVE_LENGTH / 2,
    )

    # Per-contact stimuli at 1mA (NRV will solve one at a time)
    stimuli = []
    for c in range(n_contact):
        s = nrv.stimulus()
        s.pulse(start=0.5, value=-1, duration=0.2)
        stimuli.append(s)

    fem_stim.add_electrode(elec, stimuli)
    return fem_stim, n_contact


# ============================================================
# Voltage sampling
# ============================================================
def sample_basis_centroids(model, all_fascs, n_xpts, nerve_length, n_electrodes):
    """Sample each electrode's basis field at all 57 centroids."""
    x_pts = np.linspace(0, nerve_length, n_xpts)
    basis = {}  # {electrode_idx: {fascicle_id: V_array}}

    for e in range(n_electrodes):
        basis[e] = {}
        for fg in all_fascs:
            y_f, z_f = float(fg["y_um"]), float(fg["z_um"])
            try:
                V = model.sim_res[e].eval(
                    [[x, y_f, z_f] for x in x_pts],
                    model.is_multi_proc,
                )
                v_arr = np.array(V, dtype=float).ravel()[:n_xpts]
                basis[e][fg["id"]] = v_arr
            except Exception as ex:
                basis[e][fg["id"]] = np.zeros(n_xpts)
        log(f"  Electrode {e}: sampled {len(all_fascs)} centroids")
    return x_pts, basis


def sample_basis_grid(model, sa, sb, grid_res, x_center, n_electrodes):
    """Sample each electrode's basis field on cross-section grid."""
    y_range = np.linspace(-sa * 1.1, sa * 1.1, grid_res)
    z_range = np.linspace(-sb * 1.1, sb * 1.1, grid_res)
    yy, zz = np.meshgrid(y_range, z_range)
    inside = (yy / sa) ** 2 + (zz / sb) ** 2 <= 1.0

    grids = {}
    pts_inside = np.column_stack([
        np.full(inside.sum(), x_center),
        yy[inside], zz[inside],
    ])

    for e in range(n_electrodes):
        v = np.full((grid_res, grid_res), np.nan)
        try:
            vals = model.sim_res[e].eval(pts_inside.tolist(), model.is_multi_proc)
            v[inside] = np.array(vals, dtype=float).ravel()
        except Exception as ex:
            log(f"  Grid electrode {e} FAILED: {ex}")
        grids[e] = v
        log(f"  Electrode {e}: grid V range [{np.nanmin(v):.4f}, {np.nanmax(v):.4f}]")

    return y_range, z_range, grids


# ============================================================
# Current steering search
# ============================================================
def search_steering(basis_centroids, all_fascs, thresholds, n_contact, amps):
    """Search over cathode cluster positions and weights."""
    log(f"Searching {n_contact}-contact steering configs...")

    # Generate candidate weight vectors
    candidates = []
    cluster_sizes = [1, 2, 3] if n_contact >= 4 else [1, 2]
    weight_profiles = {
        1: [[1.0]],
        2: [[0.5, 0.5]],
        3: [[0.25, 0.5, 0.25], [0.33, 0.34, 0.33]],
    }

    for cs in cluster_sizes:
        if cs > n_contact:
            continue
        for start in range(n_contact):
            for wp in weight_profiles[cs]:
                w = np.zeros(n_contact)
                for j, wv in enumerate(wp):
                    idx = (start + j) % n_contact
                    w[idx] = -wv  # cathode (negative)
                # Return current spread across non-cathode contacts
                cathode_idxs = set((start + j) % n_contact for j in range(cs))
                anode_idxs = [i for i in range(n_contact) if i not in cathode_idxs]
                if anode_idxs:
                    return_per = -w.sum() / len(anode_idxs)
                    for ai in anode_idxs:
                        w[ai] = return_per
                candidates.append({
                    "weights": w.tolist(),
                    "cluster_start": start,
                    "cluster_size": cs,
                })

    log(f"  {len(candidates)} candidate configs")

    # Score each candidate
    best_score = -999
    best_config = None
    all_scores = []

    for ci, cand in enumerate(candidates):
        w = np.array(cand["weights"])

        # Combine basis fields: V_combined(fascicle) = sum(w_i * V_i(fascicle))
        vpeaks = {}
        for fg in all_fascs:
            fid = fg["id"]
            v_combined = np.zeros(len(next(iter(basis_centroids[0].values()))))
            for e in range(n_contact):
                v_combined += w[e] * basis_centroids[e].get(fid, np.zeros_like(v_combined))
            vpeaks[fid] = np.abs(v_combined).max()

        # Score at mid-amplitude
        mid_amp = amps[len(amps) // 2]
        total_vm_r, total_vm_t = 0, 0
        total_s_r, total_s_t = 0, 0
        for fg in all_fascs:
            r = predict_recruitment_from_vpeak(vpeaks[fg["id"]], mid_amp, thresholds)
            total_vm_r += r["vm_r"]
            total_vm_t += r["vm_t"]
            total_s_r += r["s_r"]
            total_s_t += r["s_t"]

        vm_frac = total_vm_r / max(total_vm_t, 1)
        s_frac = total_s_r / max(total_s_t, 1)
        si = vm_frac - s_frac

        cand["si"] = round(si, 4)
        cand["vm_pct"] = round(vm_frac * 100, 1)
        cand["s_pct"] = round(s_frac * 100, 1)
        cand["vpeaks"] = {str(k): round(v, 6) for k, v in vpeaks.items()}
        all_scores.append(cand)

        if si > best_score:
            best_score = si
            best_config = cand

    all_scores.sort(key=lambda x: -x["si"])
    log(f"  Best SI={best_score:.3f} (vm={best_config['vm_pct']}%, s={best_config['s_pct']}%)")
    log(f"  Best weights: {best_config['weights']}")
    return best_config, all_scores[:20]  # top 20


def generate_results(best_config, basis_centroids, all_fascs, thresholds, n_contact, fi):
    """Generate full recruitment results for the best steering config."""
    w = np.array(best_config["weights"])

    # Combined voltage at each fascicle centroid
    vpeaks_all = {}
    for fg in all_fascs:
        fid = fg["id"]
        v_combined = np.zeros(len(next(iter(basis_centroids[0].values()))))
        for e in range(n_contact):
            v_combined += w[e] * basis_centroids[e].get(fid, np.zeros_like(v_combined))
        vpeaks_all[fid] = np.abs(v_combined).max()

    # Build results for all 57 fascicles at each amplitude
    fi_57 = []
    for idx, fg in enumerate(all_fascs):
        fi_57.append({
            "id": idx, "orig_id": fg["id"],
            "d": round(fg["diameter_um"]),
            "y": round(fg["y_um"]), "z": round(fg["z_um"]),
            "np": 50, "nv": 43, "ns": 7,
            "source": "threshold_model",
        })

    amps_out = {}
    for amp in AMPS:
        ad = {"st": 0, "f": {}}
        tvm, tvmt, tvu, tvut, ts, tst = 0, 0, 0, 0, 0, 0
        for idx, fg in enumerate(all_fascs):
            r = predict_recruitment_from_vpeak(vpeaks_all[fg["id"]], amp, thresholds)
            ad["f"][str(idx)] = r
            tvm += r["vm_r"]
            tvmt += r["vm_t"]
            tvu += r["vu_r"]
            tvut += r["vu_t"]
            ts += r["s_r"]
            tst += r["s_t"]
        ad["sum"] = {"vm": f"{tvm}/{tvmt}", "vu": f"{tvu}/{tvut}", "s": f"{ts}/{tst}"}
        amps_out[int(amp)] = ad

    return {
        "geometry": {
            "n_f": len(all_fascs),
            "n_contacts": n_contact,
            "weights": best_config["weights"],
            "si": best_config["si"],
            "config": f"{n_contact}contact_steered",
        },
        "fi": fi_57,
        "amps": amps_out,
    }


def combine_grid(basis_grids, weights, sa, sb):
    """Linearly combine basis field grids."""
    n = len(weights)
    combined = np.zeros_like(basis_grids[0])
    for e in range(n):
        combined += weights[e] * np.nan_to_num(basis_grids[e])
    # Re-mask outside nerve
    y = np.linspace(-sa * 1.1, sa * 1.1, combined.shape[1])
    z = np.linspace(-sb * 1.1, sb * 1.1, combined.shape[0])
    yy, zz = np.meshgrid(y, z)
    outside = (yy / sa) ** 2 + (zz / sb) ** 2 > 1.0
    combined[outside] = np.nan
    return combined


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
    log(f"Working dir: {os.getcwd()}")

    # Parse args
    contact_counts = [4, 8, 16]
    calibration_path = None
    include_bipolar = True

    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--contacts":
            contact_counts = [int(args[i + 1])]
        elif a == "--calibration":
            calibration_path = args[i + 1]
        elif a == "--no-bipolar":
            include_bipolar = False

    # Load geometry
    with open("data/bovine_geometry.json") as f:
        geom = json.load(f)
    all_fascs = geom["vagal_fascicles"]
    sa = geom["nerve"]["semi_major_um"]
    sb = geom["nerve"]["semi_minor_um"]

    # Load calibration data
    if calibration_path is None:
        for cp in ["merged/results.json", "batches/batch0/results.json",
                    "archive/local/pre_mega/bovine_6_mixed_results.json"]:
            if Path(cp).exists():
                calibration_path = cp
                break
    if calibration_path is None:
        log("ERROR: no calibration data found")
        sys.exit(1)

    log(f"Calibration: {calibration_path}")
    with open(calibration_path) as f:
        cal_results = json.load(f)

    # Load voltage data for calibration
    vol_candidates = [
        calibration_path.replace("results.json", "57voltages.npz"),
        "merged/57voltages.npz",
        "batches/batch0/57voltages.npz",
    ]
    cal_voltages = {}
    for vp in vol_candidates:
        if Path(vp).exists():
            d = np.load(vp)
            for k in d.files:
                if k.startswith("f"):
                    cal_voltages[k] = d[k]
            log(f"Voltage data: {vp} ({len(cal_voltages)} profiles)")
            break

    thresholds = calibrate_thresholds(cal_results, cal_voltages)

    nrv.backend.parameters.set_gmsh_ncore(GMSH_CORES)
    # nmod not needed — no NEURON sims
    nrv.backend.parameters.set_nmod_ncore(2)

    # Configs to run
    configs = []
    if include_bipolar:
        configs.append(("bipolar", 2))
    for nc in contact_counts:
        configs.append((f"{nc}contact", nc))

    for config_name, n_contact in configs:
        log("=" * 60)
        log(f"CONFIG: {config_name} ({n_contact} contacts)")

        out_dir = f"electrode_comparison/{config_name}"
        os.makedirs(out_dir, exist_ok=True)

        # Build fresh nerve for each config
        nerve, fi, all_labels = build_nerve_and_fascicles(geom)

        # Setup electrode
        if config_name == "bipolar":
            fem_stim, n_elec = setup_bipolar(nerve)
        else:
            fem_stim, n_elec = setup_mp(nerve, n_contact)

        nerve.attach_extracellular_stimulation(fem_stim)

        # Delaunay patch (safety)
        def pcm(self_m):
            self_m.compute_geo()
            self_m.compute_domains()
            self_m.compute_res()
            gmsh.option.setNumber("Mesh.Algorithm3D", 1)
            self_m.generate()
        nerve.extra_stim.model.mesh.compute_mesh = types.MethodType(
            pcm, nerve.extra_stim.model.mesh
        )

        # FEM solve — NRV automatically does one solve per electrode
        log(f"FEM solving ({n_elec} basis fields)...")
        t0 = time.time()
        nerve.extra_stim.run_model()
        t_fem = time.time() - t0
        log(f"FEM done: {t_fem:.1f}s ({t_fem/60:.1f} min), {len(nerve.extra_stim.model.sim_res)} fields")

        # Sample basis fields
        log("Sampling basis fields...")
        x_pts, basis_centroids = sample_basis_centroids(
            nerve.extra_stim.model, all_fascs, N_XPTS, NERVE_LENGTH, n_elec
        )
        y_grid, z_grid, basis_grids = sample_basis_grid(
            nerve.extra_stim.model, sa, sb, GRID_RES, NERVE_LENGTH / 2, n_elec
        )

        # Save basis fields
        save_dict = {"x_pts": x_pts, "n_electrodes": n_elec}
        for e in range(n_elec):
            for fid, varr in basis_centroids[e].items():
                save_dict[f"e{e}_f{fid}"] = varr
            save_dict[f"e{e}_grid"] = basis_grids[e]
        np.savez_compressed(f"{out_dir}/basis_fields.npz", **save_dict)
        log(f"Saved: {out_dir}/basis_fields.npz")

        # Search for best steering (skip for bipolar — just combine cathode+anode)
        if config_name == "bipolar":
            best = {
                "weights": [-1, 1],
                "cluster_start": 0, "cluster_size": 1,
                "si": 0, "vm_pct": 0, "s_pct": 0,
            }
            top_configs = [best]
            # Compute SI for bipolar
            vpeaks = {}
            for fg in all_fascs:
                fid = fg["id"]
                v = np.zeros(N_XPTS)
                for e in range(n_elec):
                    v += best["weights"][e] * basis_centroids[e].get(fid, np.zeros(N_XPTS))
                vpeaks[fid] = np.abs(v).max()
            mid_amp = AMPS[len(AMPS) // 2]
            tvm_r, tvm_t, ts_r, ts_t = 0, 0, 0, 0
            for fg in all_fascs:
                r = predict_recruitment_from_vpeak(vpeaks[fg["id"]], mid_amp, thresholds)
                tvm_r += r["vm_r"]
                tvm_t += r["vm_t"]
                ts_r += r["s_r"]
                ts_t += r["s_t"]
            best["si"] = round(tvm_r / max(tvm_t, 1) - ts_r / max(ts_t, 1), 4)
            best["vm_pct"] = round(tvm_r / max(tvm_t, 1) * 100, 1)
            best["s_pct"] = round(ts_r / max(ts_t, 1) * 100, 1)
            log(f"Bipolar SI={best['si']:.3f}")
        else:
            best, top_configs = search_steering(
                basis_centroids, all_fascs, thresholds, n_contact, AMPS
            )

        # Generate full results for best config
        results = generate_results(best, basis_centroids, all_fascs, thresholds, n_contact, fi)
        with open(f"{out_dir}/results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save search results
        with open(f"{out_dir}/search_results.json", "w") as f:
            json.dump({"best": best, "top_20": top_configs}, f, indent=2, default=str)

        # Save combined grid for best config
        combined_grid = combine_grid(basis_grids, best["weights"], sa, sb)
        np.savez_compressed(f"{out_dir}/grid.npz",
            y=y_grid, z=z_grid, v=combined_grid, semi_major=sa, semi_minor=sb)

        log(f"Saved: {out_dir}/results.json, search_results.json, grid.npz")
        log(f"Best: SI={best['si']:.3f}, vm={best['vm_pct']}%, s={best['s_pct']}%")

    log("=" * 60)
    log("ALL CONFIGS DONE")
    log("Plot with: python src/plot_plotly.py electrode_comparison/CONFIG/results.json")
