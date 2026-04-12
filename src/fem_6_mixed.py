#!/usr/bin/env python
"""Mixed vagal/sympathetic population on bovine geometry.

Based on the proven pure config + correctly ordered mixed populations.
  - P2 elements (default)
  - nerve_length=10000
  - Mixed populations: 85% vagal + 15% sympathetic per fascicle
  - fasc.fill(data={"types": t, "diameters": d}) — CORRECT ORDER
  - Single compute_electrodes_footprints() call
  - nmod_ncore=high
  - No CharacteristicLengthMin
  - Delaunay only if HXT crashes (try without first)

Plus: voltage sampling at 57 centroids + grid + incremental NEURON saves.
"""

import nrv
import numpy as np
import time
import json
import os
import sys
import threading
import resource
import types
import gmsh

IS_MAC = sys.platform == "darwin"
N_CPU = os.cpu_count() or 4
NMOD_CORES = min(N_CPU - 2, 28) if N_CPU > 4 else 2
GMSH_CORES = min(N_CPU, 16)

NERVE_LENGTH = 10000
NERVE_DIAM = 5000
N_AX = 50
SYMP_FRAC = 0.15
AMPS = np.linspace(100, 1000, 20).astype(int)
N_XPTS = 200
GRID_RES = 80

# Args: fascicle_count [offset]
N_FASC = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 6
OFFSET = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 0
TAG = f"{N_FASC}" if OFFSET == 0 else f"{N_FASC}_{OFFSET}"
RESULTS_FILE = f"bovine_{TAG}_mixed_results.json"
VOLTAGES_FILE = f"bovine_{TAG}_mixed_57voltages.npz"
GRID_FILE = f"bovine_{TAG}_mixed_grid.npz"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def build_mixed_pop(n, frac, seed=0):
    """Build 85% vagal + 15% sympathetic population."""
    n_s = max(1, int(n * frac))
    n_v = n - n_s
    vd, vt, _, _ = nrv.create_axon_population(
        n_v, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U"
    )
    rng = np.random.default_rng(seed)
    sd = rng.uniform(0.3, 1.2, n_s)  # sympathetic C-fiber diameters
    st = np.zeros(n_s)  # type 0 = unmyelinated
    diams = np.concatenate([vd, sd])
    types = np.concatenate([vt, st])
    labels = ["vagal"] * n_v + ["sympathetic"] * n_s
    return diams, types, labels


def extract(fr, n_ax, labels):
    """Extract recruitment with vagal/sympathetic tracking."""
    vm_r, vm_t, vu_r, vu_t, s_r, s_t = 0, 0, 0, 0, 0, 0
    rd = []
    for j in range(n_ax):
        ax = getattr(fr, f"axon{j}", None)
        if ax is None:
            continue
        m = ax.get("myelinated", False) if hasattr(ax, "get") else False
        r = ax.is_recruited()
        d = float(ax.get("d", 0) if hasattr(ax, "get") else 0)
        lb = labels[j] if j < len(labels) else "vagal"
        if lb == "sympathetic":
            s_t += 1
            if r:
                s_r += 1
                rd.append(d)
        elif m:
            vm_t += 1
            if r:
                vm_r += 1
                rd.append(d)
        else:
            vu_t += 1
            if r:
                vu_r += 1
                rd.append(d)
    return {
        "vm_r": vm_r, "vm_t": vm_t,
        "vu_r": vu_r, "vu_t": vu_t,
        "s_r": s_r, "s_t": s_t,
        "rd": rd,
    }


def save_incremental(res, path):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(res, f, indent=2, default=str)
    os.replace(tmp, path)


def load_partial(path):
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        done = set(int(k) for k in data.get("amps", {}).keys())
        return data, done
    return None, set()


def sample_centroids(model, all_fascs, n_xpts, nerve_length):
    log("Sampling voltage at 57 fascicle centroids...")
    x_pts = np.linspace(0, nerve_length, n_xpts)
    voltages = {}
    for idx, fg in enumerate(all_fascs):
        y_f, z_f = float(fg["y_um"]), float(fg["z_um"])
        try:
            V = model.get_potentials(x_pts.copy(), y_f, z_f)
            V = np.array(V)
            v_arr = V[:, 0] if V.ndim == 2 else V
            voltages[fg["id"]] = v_arr.astype(float)
            if (idx + 1) % 10 == 0 or idx == len(all_fascs) - 1:
                log(f"  {idx+1}/{len(all_fascs)} — F{fg['id']} |V|_max={np.abs(v_arr).max():.6f}")
        except Exception as e:
            log(f"  F{fg['id']} FAILED: {e}")
            voltages[fg["id"]] = np.zeros(n_xpts)
    return x_pts, voltages


def sample_grid(model, sa, sb, grid_res, x_center):
    log(f"Sampling cross-section grid ({grid_res}x{grid_res})...")
    y_range = np.linspace(-sa * 1.1, sa * 1.1, grid_res)
    z_range = np.linspace(-sb * 1.1, sb * 1.1, grid_res)
    try:
        yy, zz = np.meshgrid(y_range, z_range)
        points = np.column_stack([
            np.full(grid_res * grid_res, x_center),
            yy.ravel(), zz.ravel(),
        ])
        values = model.sim_res[0].eval(points.tolist(), model.is_multi_proc)
        v_grid = np.array(values, dtype=float).reshape(grid_res, grid_res)
        log(f"  Grid: V range [{v_grid.min():.6f}, {v_grid.max():.6f}]")
    except Exception as e:
        log(f"  Grid batch failed ({e}), per-row fallback...")
        v_grid = np.zeros((grid_res, grid_res))
        for j, zv in enumerate(z_range):
            try:
                pts = [[x_center, float(yv), float(zv)] for yv in y_range]
                rv = model.sim_res[0].eval(pts, model.is_multi_proc)
                v_grid[j, :] = np.array(rv, dtype=float).ravel()[:grid_res]
            except:
                pass
        log(f"  Grid (per-row): V range [{v_grid.min():.6f}, {v_grid.max():.6f}]")
    return y_range, z_range, v_grid


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
    log(f"Working dir: {os.getcwd()}")
    log(f"Platform: {'Mac' if IS_MAC else 'Linux'}, {N_CPU} CPUs")
    log(f"NMOD={NMOD_CORES}, GMSH={GMSH_CORES}")
    # --batch N mode: index directly into all 57 fascicles
    # Batch 0=[0-5], 1=[6-11], ..., 9=[54-56]
    BATCH = None
    for a in sys.argv:
        if a.startswith("--batch"):
            BATCH = int(a.split("=")[1] if "=" in a else sys.argv[sys.argv.index(a) + 1])

    nrv.backend.parameters.set_nmod_ncore(NMOD_CORES)
    nrv.backend.parameters.set_gmsh_ncore(GMSH_CORES)

    with open("data/bovine_geometry.json") as f:
        geom = json.load(f)

    all_fascs = geom["vagal_fascicles"]

    if BATCH is not None:
        indices = list(range(BATCH * 6, min((BATCH + 1) * 6, len(all_fascs))))
        TAG = f"batch{BATCH}"
        N_FASC = len(indices)
    else:
        indices = geom["representative_subset_15"]["indices"][OFFSET:OFFSET + N_FASC]
        TAG = f"{N_FASC}" if OFFSET == 0 else f"{N_FASC}_{OFFSET}"

    # Per-batch output directory
    BATCH_DIR = f"batches/{TAG}"
    os.makedirs(BATCH_DIR, exist_ok=True)
    RESULTS_FILE = f"{BATCH_DIR}/results.json"
    VOLTAGES_FILE = f"{BATCH_DIR}/57voltages.npz"
    GRID_FILE = f"{BATCH_DIR}/grid.npz"

    log(f"MIXED POP: P2, nerve=10mm, n_ax={N_AX}, {SYMP_FRAC*100:.0f}% sympathetic")
    log(f"TAG={TAG}, indices={indices}")

    partial, done_amps = load_partial(RESULTS_FILE)
    fascs_geo = [all_fascs[i] for i in indices if i < len(all_fascs)]
    n_f = len(fascs_geo)
    nerve = nrv.nerve(length=NERVE_LENGTH, diameter=NERVE_DIAM, Outer_D=10)
    fi = []
    all_labels = {}
    for i, fg in enumerate(fascs_geo):
        fasc = nrv.fascicle(diameter=fg["diameter_um"], ID=i)
        diams, types, labels = build_mixed_pop(N_AX, SYMP_FRAC, seed=fg["id"])
        # CORRECT ORDER: types first, diameters second
        fasc.fill(data={"types": types, "diameters": diams}, delta=5)
        n_placed = fasc.n_ax
        all_labels[i] = labels[:n_placed]
        nerve.add_fascicle(fasc, y=fg["y_um"], z=fg["z_um"])
        fi.append({
            "id": i, "orig_id": fg["id"], "d": round(fg["diameter_um"]),
            "y": round(fg["y_um"]), "z": round(fg["z_um"]),
            "np": n_placed,
            "nv": sum(1 for l in labels[:n_placed] if l == "vagal"),
            "ns": sum(1 for l in labels[:n_placed] if l == "sympathetic"),
        })
        # Sanity check
        ftypes = fasc.axons["types"] if hasattr(fasc.axons, "__getitem__") else []
        fdiams = fasc.axons["diameters"] if hasattr(fasc.axons, "__getitem__") else []
        log(f"  F{fg['id']} d={fg['diameter_um']:.0f}um — {n_placed} axons "
            f"(types={sorted(set(ftypes)) if len(ftypes) else '?'}, "
            f"diam=[{min(fdiams):.1f}-{max(fdiams):.1f}])")

    log(f"Total: {sum(x['np'] for x in fi)} fibers "
        f"({sum(x['nv'] for x in fi)} vagal, {sum(x['ns'] for x in fi)} sympathetic)")

    # Electrode — SAME as successful run
    cuff = nrv.CUFF_electrode(
        label="bipolar_cuff", contact_length=500, contact_thickness=200,
        insulator_length=2000, insulator_thickness=800, x_center=NERVE_LENGTH / 2,
    )
    stim = nrv.stimulus()
    stim.pulse(start=0.5, value=-100, duration=0.2)
    fem_stim = nrv.FEM_stimulation(
        endo_mat="endoneurium_ranck", peri_mat="perineurium",
        epi_mat="epineurium", ext_mat="saline",
    )
    # NO elem override — P2 default
    fem_stim.add_electrode(cuff, stim)
    nerve.attach_extracellular_stimulation(fem_stim)

    # Try WITHOUT Delaunay patch first. If gmsh crashes, rerun with it.
    use_delaunay = "--delaunay" in sys.argv
    if use_delaunay:
        def pcm(self_m):
            self_m.compute_geo()
            self_m.compute_domains()
            self_m.compute_res()
            gmsh.option.setNumber("Mesh.Algorithm3D", 1)
            log("  gmsh: forced Delaunay")
            self_m.generate()
        nerve.extra_stim.model.mesh.compute_mesh = types.MethodType(
            pcm, nerve.extra_stim.model.mesh
        )
        log("Delaunay forced (--delaunay flag)")
    else:
        log("Using default gmsh algorithm (no patches)")

    # PHASE 1: Single compute_electrodes_footprints — SAME as successful run
    log("=" * 60)
    log("PHASE 1: FEM + footprints (single call)")

    # Heartbeat
    _t0_all = time.time()
    _hb_stop = threading.Event()
    def _hb():
        while not _hb_stop.wait(60):
            el = time.time() - _t0_all
            try:
                rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                rss_gb = rss / (1024**3) if IS_MAC else rss / (1024**2)
            except:
                rss_gb = 0
            log(f"  HEARTBEAT: {el:.0f}s elapsed, peak_rss={rss_gb:.1f}GB")
    threading.Thread(target=_hb, daemon=True).start()

    t0 = time.time()
    nerve.compute_electrodes_footprints()
    t_fem_fp = time.time() - t0
    _hb_stop.set()
    log(f"FEM + footprints: {t_fem_fp:.1f}s ({t_fem_fp/60:.1f} min)")

    # PHASE 1b: Voltage sampling (dolfinx still in memory)
    log("=" * 60)
    log("PHASE 1b: Voltage sampling")
    t0_vs = time.time()
    x_pts, voltages = sample_centroids(nerve.extra_stim.model, all_fascs, N_XPTS, NERVE_LENGTH)
    sa = geom["nerve"]["semi_major_um"]
    sb = geom["nerve"]["semi_minor_um"]
    y_grid, z_grid, v_grid = sample_grid(nerve.extra_stim.model, sa, sb, GRID_RES, NERVE_LENGTH / 2)
    t_vs = time.time() - t0_vs
    log(f"Voltage sampling: {t_vs:.1f}s")

    try:
        sd = {"x_pts": x_pts}
        for fid, varr in voltages.items():
            sd[f"f{fid}"] = varr
        np.savez_compressed(VOLTAGES_FILE, **sd)
        np.savez_compressed(GRID_FILE, y=y_grid, z=z_grid, v=v_grid, semi_major=sa, semi_minor=sb)
        log(f"CHECKPOINT: {VOLTAGES_FILE} + {GRID_FILE}")
    except Exception as e:
        log(f"Voltage save FAILED: {e}")

    # PHASE 1c: 3D volume field + mesh exports
    log("=" * 60)
    log("PHASE 1c: Volume field + mesh export")

    # 3D volume grid for Plotly isosurfaces
    try:
        log("  Sampling 3D volume (64x96x96)...")
        t0_vol = time.time()
        nx, ny, nz = 64, 96, 96
        xs = np.linspace(0, NERVE_LENGTH, nx)
        ys = np.linspace(-sa * 1.05, sa * 1.05, ny)
        zs = np.linspace(-sb * 1.05, sb * 1.05, nz)
        xx, yy, zz = np.meshgrid(xs, ys, zs, indexing="ij")
        inside = (yy / sa) ** 2 + (zz / sb) ** 2 <= 1.0
        pts_inside = np.column_stack([xx[inside], yy[inside], zz[inside]])
        vals = np.empty(len(pts_inside), dtype=float)
        fem_res = nerve.extra_stim.model.sim_res[0]
        chunk = 20000
        for ci in range(0, len(pts_inside), chunk):
            vals[ci:ci+chunk] = np.asarray(
                fem_res.eval(pts_inside[ci:ci+chunk].tolist(), nerve.extra_stim.model.is_multi_proc),
                dtype=float).ravel()
        vol = np.full(xx.shape, np.nan, dtype=float)
        vol[inside] = vals
        vol_file = f"{BATCH_DIR}/volume_field.npz"
        np.savez_compressed(vol_file, x=xs, y=ys, z=zs, v=vol, semi_major=sa, semi_minor=sb)
        log(f"  Volume field: {vol_file} ({time.time()-t0_vol:.1f}s, {len(pts_inside)} points)")
    except Exception as e:
        log(f"  Volume field FAILED: {e}")

    # VTX field export for ParaView
    try:
        fem_res = nerve.extra_stim.model.sim_res[0]
        vtx_path = f"{BATCH_DIR}/fem_field"
        fem_res.save(vtx_path, ftype="vtx")
        log(f"  VTX field: {vtx_path}.bp/")
    except Exception as e:
        log(f"  VTX field FAILED: {e}")

    # XDMF mesh export
    try:
        from dolfinx.io import XDMFFile
        from mpi4py import MPI
        fem_res = nerve.extra_stim.model.sim_res[0]
        mesh_path = f"{BATCH_DIR}/mesh.xdmf"
        with XDMFFile(MPI.COMM_WORLD, mesh_path, "w") as xf:
            xf.write_mesh(fem_res.domain)
        log(f"  XDMF mesh: {mesh_path}")
    except Exception as e:
        log(f"  XDMF mesh FAILED: {e}")

    # Gmsh mesh with physical groups
    try:
        gmsh_path = f"{BATCH_DIR}/gmsh.msh"
        nerve.extra_stim.model.mesh.save(gmsh_path)
        log(f"  Gmsh mesh: {gmsh_path}")
    except Exception as e:
        log(f"  Gmsh mesh FAILED: {e}")

    # PHASE 2: NEURON sweep with incremental saves
    if partial and done_amps:
        res = partial
    else:
        res = {
            "geometry": {
                "n_f": n_f,
                "fem_fp_s": round(t_fem_fp, 1),
                "vs_s": round(t_vs, 1),
                "config": f"mixed_P2_10mm_{TAG}_indices{indices}",
            },
            "fi": fi,
            "amps": {},
        }

    remaining = [a for a in AMPS if int(a) not in done_amps]
    log("=" * 60)
    log(f"PHASE 2: NEURON sweep — {len(remaining)} of {len(AMPS)}")

    for ai, amp in enumerate(remaining):
        amp = int(amp)
        log(f"[{len(done_amps)+ai+1}/{len(AMPS)}] {amp}uA")
        ns = nrv.stimulus()
        ns.pulse(start=0.5, value=-float(amp), duration=0.2)
        nerve.change_stimulus_from_electrode(0, ns)

        t0 = time.time()
        r = nerve(t_sim=3)
        st = time.time() - t0
        log(f"  NEURON: {st:.1f}s")

        ad = {"st": round(st, 1), "f": {}}
        tvm, tvmt, tvu, tvut, ts, tst = 0, 0, 0, 0, 0, 0
        for i in range(n_f):
            fr = r.get_fascicle_results(i)
            e = extract(fr, fi[i]["np"], all_labels.get(i, []))
            tvm += e["vm_r"]
            tvmt += e["vm_t"]
            tvu += e["vu_r"]
            tvut += e["vu_t"]
            ts += e["s_r"]
            tst += e["s_t"]
            ad["f"][i] = e

        ad["sum"] = {
            "vm": f"{tvm}/{tvmt}",
            "vu": f"{tvu}/{tvut}",
            "s": f"{ts}/{tst}",
        }
        log(f"  Vm:{tvm}/{tvmt} Vu:{tvu}/{tvut} S:{ts}/{tst}")
        res["amps"][amp] = ad
        save_incremental(res, RESULTS_FILE)
        log(f"  CHECKPOINT ({len(res['amps'])}/{len(AMPS)})")

    tn = sum(res["amps"][a]["st"] for a in res["amps"])
    log("=" * 60)
    log("COMPLETE")
    log(f"FEM+FP:    {t_fem_fp:.0f}s ({t_fem_fp/60:.1f} min)")
    log(f"Voltages:  {t_vs:.0f}s")
    log(f"NEURON:    {tn:.0f}s ({tn/60:.1f} min)")
    log(f"Total:     {t_fem_fp+t_vs+tn:.0f}s ({(t_fem_fp+t_vs+tn)/60:.1f} min)")
