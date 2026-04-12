#!/usr/bin/env python
"""Extrapolate 10-fascicle FEM results to all 57 fascicles.

Uses voltage field data (from AWS) + recruitment results (from local)
to predict recruitment at un-modeled fascicle positions via a
threshold model calibrated on the 10 FEM-modeled fascicles.

No NRV dependency — pure numpy/scipy.

Usage:
    python src/extrapolate_57.py bovine_10_results.json bovine_57_voltages.npz
    python src/extrapolate_57.py bovine_10_results.json  # distance-based fallback
"""

import json
import sys
import numpy as np
from pathlib import Path


def log(msg):
    print(f"[extrapolate] {msg}", flush=True)


def load_geometry(path="data/bovine_geometry.json"):
    with open(path) as f:
        return json.load(f)


def load_results(path):
    with open(path) as f:
        return json.load(f)


def load_voltages(path):
    data = np.load(path)
    x_pts = data["x_pts"]
    voltages = {}
    for key in data.files:
        if key.startswith("f"):
            fid = int(key[1:])
            voltages[fid] = data[key]
    return x_pts, voltages


def build_mixed_pop(n, frac, seed=0):
    """Generate fiber population matching FEM scripts exactly."""
    rng = np.random.default_rng(seed)
    n_s = max(1, int(n * frac))
    n_v = n - n_s

    # Vagal: 70% unmyelinated, 30% myelinated (Ochoa stats)
    n_myel = int(n_v * 0.3)
    n_unmyel = n_v - n_myel
    # Myelinated diameters: ~2-16um (Ochoa_M distribution approximation)
    myel_d = rng.lognormal(mean=1.8, sigma=0.5, size=n_myel).clip(2, 16)
    # Unmyelinated diameters: ~0.3-1.5um (Ochoa_U distribution approximation)
    unmyel_d = rng.lognormal(mean=-0.3, sigma=0.4, size=n_unmyel).clip(0.3, 1.5)
    # Sympathetic: small unmyelinated C-fibers
    symp_d = rng.uniform(0.3, 1.2, n_s)

    diameters = np.concatenate([myel_d, unmyel_d, symp_d])
    types = (["vagal_myel"] * n_myel +
             ["vagal_unmyel"] * n_unmyel +
             ["sympathetic"] * n_s)
    return diameters, types


def compute_vpeak(voltages, fascicle_id):
    """Get peak absolute voltage at a fascicle centroid (at 1mA)."""
    if fascicle_id in voltages:
        v = voltages[fascicle_id]
        return np.max(np.abs(v))
    return 0.0


def calibrate_thresholds(results, voltages, geom):
    """From 10 modeled fascicles, learn voltage threshold per fiber type.

    For each amplitude, we know V_peak * amplitude at each fascicle
    and whether fibers recruited. We find the effective voltage threshold
    that best separates recruited from non-recruited fascicles.
    """
    fi = results["fi"]
    amps = results["amps"]
    amp_keys = sorted([int(k) for k in amps.keys()])

    # Get modeled fascicle orig_ids
    modeled_orig_ids = [f["orig_id"] for f in fi]

    # Compute V_peak for each modeled fascicle
    vpeaks = []
    for f in fi:
        vpeaks.append(compute_vpeak(voltages, f["orig_id"]))
    vpeaks = np.array(vpeaks)

    if vpeaks.max() == 0:
        log("WARNING: No voltage data for modeled fascicles, using distance fallback")
        return None

    # For each fiber type, collect (V_effective, recruitment_fraction) pairs
    # V_effective = V_peak * amplitude
    vm_points = []  # (V_eff, fraction_recruited)
    vu_points = []
    s_points = []

    for amp in amp_keys:
        ad = amps[str(amp)]
        for i, f in enumerate(fi):
            fd = ad["f"][str(i)]
            v_eff = vpeaks[i] * amp

            vm_t = fd["vm_t"]
            vm_r = fd["vm_r"]
            if vm_t > 0:
                vm_points.append((v_eff, vm_r / vm_t))

            vu_t = fd["vu_t"]
            vu_r = fd["vu_r"]
            if vu_t > 0:
                vu_points.append((v_eff, vu_r / vu_t))

            s_t = fd["s_t"]
            s_r = fd["s_r"]
            if s_t > 0:
                s_points.append((v_eff, s_r / s_t))

    def fit_threshold(points):
        """Find V_eff where recruitment transitions from 0 to >0."""
        if not points:
            return float("inf")
        pts = np.array(points)
        v_effs = pts[:, 0]
        fracs = pts[:, 1]
        # Find the lowest V_eff with >50% recruitment
        recruited = v_effs[fracs > 0.5]
        not_recruited = v_effs[fracs < 0.1]
        if len(recruited) > 0 and len(not_recruited) > 0:
            return (recruited.min() + not_recruited.max()) / 2
        elif len(recruited) > 0:
            return recruited.min() * 0.8
        return float("inf")

    thresholds = {
        "vagal_myel": fit_threshold(vm_points),
        "vagal_unmyel": fit_threshold(vu_points),
        "sympathetic": fit_threshold(s_points),
    }
    log(f"Calibrated thresholds: vm={thresholds['vagal_myel']:.1f}, "
        f"vu={thresholds['vagal_unmyel']:.1f}, s={thresholds['sympathetic']:.1f}")

    # Also fit per-diameter sigmoid for myelinated (larger fibers recruit first)
    # Collect (diameter, V_eff, recruited) triples from recruited_diameters
    vm_diameter_points = []
    for amp in amp_keys:
        ad = amps[str(amp)]
        for i, f in enumerate(fi):
            v_eff = vpeaks[i] * amp
            fd = ad["f"][str(i)]
            for rd in fd.get("rd", []):
                vm_diameter_points.append((rd, v_eff, 1))

    return thresholds, vm_diameter_points


def calibrate_from_distance(results, geom):
    """Fallback: estimate recruitment based on distance from electrode center."""
    fi = results["fi"]
    amps = results["amps"]
    amp_keys = sorted([int(k) for k in amps.keys()])

    # Electrode at cuff center — approximate as origin for bipolar cuff
    # (cuff wraps around nerve, so distance from nerve center matters)
    distances = []
    for f in fi:
        d = np.sqrt(f["y"] ** 2 + f["z"] ** 2)
        distances.append(d)
    distances = np.array(distances)

    # Build recruitment vs distance model per amplitude
    models = {}
    for amp in amp_keys:
        ad = amps[str(amp)]
        vm_fracs = []
        vu_fracs = []
        s_fracs = []
        for i in range(len(fi)):
            fd = ad["f"][str(i)]
            vm_fracs.append(fd["vm_r"] / max(fd["vm_t"], 1))
            vu_fracs.append(fd["vu_r"] / max(fd["vu_t"], 1))
            s_fracs.append(fd["s_r"] / max(fd["s_t"], 1))
        models[amp] = {
            "distances": distances,
            "vm": np.array(vm_fracs),
            "vu": np.array(vu_fracs),
            "s": np.array(s_fracs),
        }
    return models


def predict_recruitment(v_eff, thresholds, fiber_diameters, fiber_types):
    """Predict which fibers recruit given effective voltage."""
    vm_r, vm_t, vu_r, vu_t, s_r, s_t = 0, 0, 0, 0, 0, 0
    rd = []

    for d, ft in zip(fiber_diameters, fiber_types):
        thresh = thresholds[ft]
        # Diameter scaling: larger myelinated fibers have lower thresholds
        if ft == "vagal_myel":
            # Scale threshold inversely with diameter (larger = easier to recruit)
            diameter_factor = 8.0 / max(d, 1.0)  # normalize around 8um
            adj_thresh = thresh * diameter_factor
        else:
            adj_thresh = thresh

        recruited = v_eff > adj_thresh

        if ft == "vagal_myel":
            vm_t += 1
            if recruited:
                vm_r += 1
                rd.append(d)
        elif ft == "vagal_unmyel":
            vu_t += 1
            if recruited:
                vu_r += 1
                rd.append(d)
        else:
            s_t += 1
            if recruited:
                s_r += 1
                rd.append(d)

    return {
        "vm_r": vm_r, "vm_t": vm_t,
        "vu_r": vu_r, "vu_t": vu_t,
        "s_r": s_r, "s_t": s_t,
        "rd": rd,
    }


def predict_from_distance(dist, amp, models):
    """Fallback prediction using distance-based interpolation."""
    model = models.get(amp)
    if model is None:
        return {"vm_r": 0, "vm_t": 8, "vu_r": 0, "vu_t": 18, "s_r": 0, "s_t": 4, "rd": []}

    dists = model["distances"]
    # IDW interpolation
    weights = 1.0 / (np.abs(dists - dist) + 1e-6)
    weights /= weights.sum()

    vm_frac = float(np.dot(weights, model["vm"]))
    vu_frac = float(np.dot(weights, model["vu"]))
    s_frac = float(np.dot(weights, model["s"]))

    # Apply to standard population counts
    vm_t, vu_t, s_t = 8, 18, 4
    return {
        "vm_r": int(round(vm_frac * vm_t)),
        "vm_t": vm_t,
        "vu_r": int(round(vu_frac * vu_t)),
        "vu_t": vu_t,
        "s_r": int(round(s_frac * s_t)),
        "s_t": s_t,
        "rd": [],
    }


def merge_results(results_list):
    """Merge multiple FEM result sets into one, keyed by orig_id.

    If the same fascicle appears in multiple sets, the first one wins.
    Returns merged (fi, amps, orig_to_source) where orig_to_source maps
    orig_id → (results_index, local_fascicle_index).
    """
    merged_fi = {}  # orig_id → fi entry
    merged_source = {}  # orig_id → (results_idx, local_idx)

    for ri, results in enumerate(results_list):
        for f in results["fi"]:
            oid = f["orig_id"]
            if oid not in merged_fi:
                merged_fi[oid] = f
                local_idx = f["id"]
                merged_source[oid] = (ri, local_idx)

    log(f"Merged: {len(merged_fi)} unique FEM fascicles from {len(results_list)} result set(s)")
    return merged_fi, merged_source


def extrapolate(results_list, geom, voltages=None):
    """Main extrapolation: FEM fascicles → 57 total.

    results_list: list of result dicts (one per run). Can be a single item.
    """
    if not isinstance(results_list, list):
        results_list = [results_list]

    # Merge all FEM result sets
    merged_fi, merged_source = merge_results(results_list)
    modeled_orig_ids = set(merged_fi.keys())

    # Use amplitude keys from first result set (all should have same amplitudes)
    amps_ref = results_list[0]["amps"]
    amp_keys = sorted([int(k) for k in amps_ref.keys()])
    all_fascs = geom["vagal_fascicles"]

    # Calibrate threshold model (uses first result set for calibration)
    use_voltage = voltages is not None and len(voltages) > 0
    if use_voltage:
        cal = calibrate_thresholds(results_list[0], voltages, geom)
        if cal is None:
            use_voltage = False
        else:
            thresholds, _ = cal

    if not use_voltage:
        log("Using distance-based fallback")
        dist_models = calibrate_from_distance(results_list[0], geom)

    # Build fi for all 57 fascicles
    fi_57 = []
    populations = {}
    for idx, fg in enumerate(all_fascs):
        fid = fg["id"]
        diams, ftypes = build_mixed_pop(30, 0.15, seed=fid)
        n_placed = len(diams)
        source = "fem" if fid in modeled_orig_ids else "extrapolated"
        fi_57.append({
            "id": idx, "orig_id": fid,
            "d": round(fg["diameter_um"]),
            "y": round(fg["y_um"]), "z": round(fg["z_um"]),
            "np": n_placed,
            "nv": sum(1 for t in ftypes if t.startswith("vagal")),
            "ns": sum(1 for t in ftypes if t == "sympathetic"),
            "source": source,
        })
        populations[idx] = (diams, ftypes)

    # Compute V_peak for all 57 fascicles
    if use_voltage:
        all_vpeaks = {}
        for fg in all_fascs:
            all_vpeaks[fg["id"]] = compute_vpeak(voltages, fg["id"])

    # Perineurium correction: compare modeled fascicles' recruitment
    # with what pure voltage would predict, derive attenuation factor
    if use_voltage:
        corrections = []
        for oid, (ri, local_idx) in merged_source.items():
            vpk = all_vpeaks.get(oid, 0)
            if vpk > 0:
                mid_amp = amp_keys[len(amp_keys) // 2]
                src_amps = results_list[ri]["amps"]
                fd = src_amps[str(mid_amp)]["f"][str(local_idx)]
                actual_frac = fd["vm_r"] / max(fd["vm_t"], 1)
                v_eff = vpk * mid_amp
                # Use fascicle 0's population as reference
                ref_idx = list(populations.keys())[0]
                diams, ftypes = populations[ref_idx]
                pred = predict_recruitment(v_eff, thresholds, diams, ftypes)
                pred_frac = pred["vm_r"] / max(pred["vm_t"], 1)
                if pred_frac > 0:
                    corrections.append(actual_frac / pred_frac)
        if corrections:
            peri_factor = float(np.median(corrections))
            peri_factor = np.clip(peri_factor, 0.3, 1.0)
            log(f"Perineurium correction factor: {peri_factor:.2f}")
        else:
            peri_factor = 0.7
            log(f"Using default perineurium correction: {peri_factor:.2f}")
    else:
        peri_factor = 1.0

    # Generate results for all 57 fascicles at each amplitude
    amps_57 = {}
    for amp in amp_keys:
        ad = {"st": 0, "f": {}}
        tvm, tvmt, tvu, tvut, ts, tst = 0, 0, 0, 0, 0, 0

        for idx, fg in enumerate(all_fascs):
            fid = fg["id"]
            diams, ftypes = populations[idx]

            if fid in modeled_orig_ids:
                # Use real FEM results from the source run
                ri, local_idx = merged_source[fid]
                fd = results_list[ri]["amps"][str(amp)]["f"][str(local_idx)]
                result = dict(fd)
            elif use_voltage:
                # Voltage-based extrapolation
                vpk = all_vpeaks.get(fid, 0)
                v_eff = vpk * amp * peri_factor
                result = predict_recruitment(v_eff, thresholds, diams, ftypes)
            else:
                # Distance-based fallback
                dist = np.sqrt(fg["y_um"] ** 2 + fg["z_um"] ** 2)
                result = predict_from_distance(dist, amp, dist_models)

            ad["f"][idx] = result
            tvm += result["vm_r"]
            tvmt += result["vm_t"]
            tvu += result["vu_r"]
            tvut += result["vu_t"]
            ts += result["s_r"]
            tst += result["s_t"]

        ad["sum"] = {
            "vm": f"{tvm}/{tvmt}",
            "vu": f"{tvu}/{tvut}",
            "s": f"{ts}/{tst}",
        }
        amps_57[amp] = ad
        log(f"  {amp}uA: Vm={tvm}/{tvmt} Vu={tvu}/{tvut} S={ts}/{tst}")

    n_fem = len(modeled_orig_ids)
    out = {
        "geometry": {
            "n_f": 57,
            "n_fem": n_fem,
            "n_extrapolated": 57 - n_fem,
            "n_result_sets": len(results_list),
            "fem_orig_ids": sorted(modeled_orig_ids),
            "method": "voltage_threshold" if use_voltage else "distance_idw",
            "perineurium_correction": round(peri_factor, 3),
        },
        "fi": fi_57,
        "amps": amps_57,
    }
    return out


if __name__ == "__main__":
    # Usage:
    #   python extrapolate_57.py results1.json [results2.json ...] [--voltage file.npz]
    #   python extrapolate_57.py bovine_6_results.json bovine_6b_results.json --voltage bovine_6_57voltages.npz
    args = sys.argv[1:]
    result_paths = []
    voltage_path = None

    i = 0
    while i < len(args):
        if args[i] == "--voltage" and i + 1 < len(args):
            voltage_path = args[i + 1]
            i += 2
        elif args[i].endswith(".json"):
            result_paths.append(args[i])
            i += 1
        elif args[i].endswith(".npz"):
            voltage_path = args[i]
            i += 1
        else:
            i += 1

    if not result_paths:
        result_paths = ["bovine_6_results.json"]

    results_list = []
    for p in result_paths:
        log(f"Loading results: {p}")
        results_list.append(load_results(p))
    log(f"Loaded {len(results_list)} result set(s)")

    geom = load_geometry()

    voltages = None
    if voltage_path and Path(voltage_path).exists():
        log(f"Loading voltage data: {voltage_path}")
        _, voltages = load_voltages(voltage_path)
        log(f"  {len(voltages)} fascicle voltage profiles loaded")
    elif voltage_path:
        log(f"WARNING: {voltage_path} not found, using distance fallback")

    out = extrapolate(results_list, geom, voltages)

    out_path = "bovine_57_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    log(f"Saved: {out_path}")
    log(f"  {out['geometry']['n_fem']} FEM + {out['geometry']['n_extrapolated']} extrapolated = {out['geometry']['n_f']} total")
    log(f"  Method: {out['geometry']['method']}")
