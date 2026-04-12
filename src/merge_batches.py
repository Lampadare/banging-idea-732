"""Merge batch results into unified 57-fascicle dataset.

Reads batches/batch0-9/results.json, combines into one file
compatible with plot_plotly.py.

Usage:
    python src/merge_batches.py                    # auto-discover batches/
    python src/merge_batches.py batches/batch0 batches/batch3  # specific dirs
"""

import json
import numpy as np
import os
import sys
from pathlib import Path


def log(msg):
    print(f"[merge] {msg}", flush=True)


def load_geometry(path="data/bovine_geometry.json"):
    with open(path) as f:
        return json.load(f)


def merge(batch_dirs, geom):
    all_fascs = geom["vagal_fascicles"]
    n_total = len(all_fascs)

    # Load all batch results
    batches = []
    for bd in sorted(batch_dirs):
        rp = Path(bd) / "results.json"
        if not rp.exists():
            log(f"  SKIP {bd} — no results.json")
            continue
        with open(rp) as f:
            data = json.load(f)
        batches.append({"dir": bd, "data": data})
        log(f"  Loaded {bd}: {len(data['fi'])} fascicles, {len(data['amps'])} amplitudes")

    if not batches:
        log("ERROR: no batch results found")
        return None

    # Build orig_id → (batch_idx, local_idx) mapping
    orig_to_source = {}
    for bi, b in enumerate(batches):
        for f in b["data"]["fi"]:
            oid = f["orig_id"]
            if oid not in orig_to_source:
                orig_to_source[oid] = (bi, f["id"])

    log(f"Merged: {len(orig_to_source)} unique fascicles from {len(batches)} batches")

    # Find common amplitudes across all batches
    amp_sets = [set(int(k) for k in b["data"]["amps"].keys()) for b in batches]
    common_amps = sorted(set.intersection(*amp_sets))
    log(f"Common amplitudes: {len(common_amps)} ({common_amps[0]}-{common_amps[-1]} uA)")

    # Build unified fi list — one entry per geometry fascicle, sorted by orig_id
    fi_merged = []
    global_map = {}  # orig_id → global_idx
    for global_idx, fg in enumerate(all_fascs):
        oid = fg["id"]
        if oid in orig_to_source:
            bi, local_idx = orig_to_source[oid]
            src_fi = batches[bi]["data"]["fi"][local_idx]
            fi_merged.append({
                "id": global_idx,
                "orig_id": oid,
                "d": src_fi["d"],
                "y": src_fi["y"],
                "z": src_fi["z"],
                "np": src_fi["np"],
                "nv": src_fi["nv"],
                "ns": src_fi["ns"],
                "source": "fem",
            })
        else:
            fi_merged.append({
                "id": global_idx,
                "orig_id": oid,
                "d": round(fg["diameter_um"]),
                "y": round(fg["y_um"]),
                "z": round(fg["z_um"]),
                "np": 0, "nv": 0, "ns": 0,
                "source": "missing",
            })
        global_map[oid] = global_idx

    n_fem = sum(1 for f in fi_merged if f["source"] == "fem")
    n_missing = sum(1 for f in fi_merged if f["source"] == "missing")
    log(f"Coverage: {n_fem} FEM, {n_missing} missing out of {n_total}")

    # Merge per-amplitude data
    amps_merged = {}
    for amp in common_amps:
        ad = {"st": 0, "f": {}}
        tvm, tvmt, tvu, tvut, ts, tst = 0, 0, 0, 0, 0, 0

        for global_idx, fg in enumerate(all_fascs):
            oid = fg["id"]
            if oid in orig_to_source:
                bi, local_idx = orig_to_source[oid]
                src_amp = batches[bi]["data"]["amps"][str(amp)]
                fd = src_amp["f"][str(local_idx)]
                ad["st"] += src_amp.get("st", 0) / len(orig_to_source)
            else:
                fd = {"vm_r": 0, "vm_t": 0, "vu_r": 0, "vu_t": 0,
                      "s_r": 0, "s_t": 0, "rd": []}

            ad["f"][str(global_idx)] = fd
            tvm += fd["vm_r"]
            tvmt += fd["vm_t"]
            tvu += fd["vu_r"]
            tvut += fd["vu_t"]
            ts += fd["s_r"]
            tst += fd["s_t"]

        ad["sum"] = {
            "vm": f"{tvm}/{tvmt}",
            "vu": f"{tvu}/{tvut}",
            "s": f"{ts}/{tst}",
        }
        amps_merged[amp] = ad

    result = {
        "geometry": {
            "n_f": n_total,
            "n_fem": n_fem,
            "n_missing": n_missing,
            "n_batches": len(batches),
            "config": "merged_57_all_fem_mixed",
            "batch_dirs": [b["dir"] for b in batches],
        },
        "fi": fi_merged,
        "amps": amps_merged,
    }
    return result


def merge_voltages(batch_dirs, out_path):
    """Merge centroid voltage profiles from all batches."""
    merged = {}
    x_pts = None
    for bd in sorted(batch_dirs):
        vp = Path(bd) / "57voltages.npz"
        if not vp.exists():
            continue
        d = np.load(vp)
        if x_pts is None:
            x_pts = d["x_pts"]
        for k in d.files:
            if k.startswith("f") and k not in merged:
                v = d[k]
                if np.abs(v).max() > 0:
                    merged[k] = v

    if x_pts is not None and merged:
        save_dict = {"x_pts": x_pts, **merged}
        np.savez_compressed(out_path, **save_dict)
        log(f"Voltages merged: {len(merged)} nonzero profiles -> {out_path}")
    else:
        log("No voltage data to merge")


def merge_grids(batch_dirs, out_path):
    """Average cross-section grids from all batches."""
    grids = []
    y, z, sa, sb = None, None, None, None
    for bd in sorted(batch_dirs):
        gp = Path(bd) / "grid.npz"
        if not gp.exists():
            continue
        d = np.load(gp)
        v = d["v"]
        if np.abs(v).max() > 0:
            grids.append(v)
            if y is None:
                y, z = d["y"], d["z"]
                sa, sb = float(d["semi_major"]), float(d["semi_minor"])

    if grids:
        avg = np.nanmean(grids, axis=0)
        np.savez_compressed(out_path, y=y, z=z, v=avg, semi_major=sa, semi_minor=sb)
        log(f"Grid merged: {len(grids)} grids averaged -> {out_path}")
    else:
        log("No grid data to merge")


if __name__ == "__main__":
    # Auto-discover or use specified dirs
    if len(sys.argv) > 1:
        batch_dirs = sys.argv[1:]
    else:
        batch_dirs = sorted([
            str(p) for p in Path("batches").iterdir()
            if p.is_dir() and (p / "results.json").exists()
        ])

    if not batch_dirs:
        log("No batch directories found. Run the batch dispatcher first.")
        sys.exit(1)

    log(f"Found {len(batch_dirs)} batch directories")
    geom = load_geometry()

    # Merge results
    result = merge(batch_dirs, geom)
    if result is None:
        sys.exit(1)

    # Save merged results
    out_dir = "merged"
    os.makedirs(out_dir, exist_ok=True)

    results_path = f"{out_dir}/results.json"
    with open(results_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    log(f"Saved: {results_path}")

    # Merge voltages
    merge_voltages(batch_dirs, f"{out_dir}/57voltages.npz")

    # Merge grids
    merge_grids(batch_dirs, f"{out_dir}/grid.npz")

    # Summary
    n_f = result["geometry"]["n_fem"]
    n_m = result["geometry"]["n_missing"]
    n_a = len(result["amps"])
    log(f"DONE: {n_f} FEM fascicles, {n_m} missing, {n_a} amplitudes")
    log(f"Plot with: python src/plot_plotly.py {results_path}")
