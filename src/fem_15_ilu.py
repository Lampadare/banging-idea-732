import nrv
import numpy as np
import time
import json
import pickle
import gmsh
import os
import types

N_AX = 30
SYMP_FRAC = 0.15

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def build_mixed_pop(n, frac, seed=0):
    n_s = max(1, int(n * frac))
    n_v = n - n_s
    vd, vt, _, _ = nrv.create_axon_population(n_v, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U")
    rng = np.random.default_rng(seed)
    sd = rng.uniform(0.3, 1.2, n_s)
    st = np.zeros(n_s)
    return np.concatenate([vd, sd]), np.concatenate([vt, st]), ["vagal"]*n_v + ["sympathetic"]*n_s

def extract(fr, n_ax, labels):
    vm_r, vm_t, vu_r, vu_t, s_r, s_t = 0, 0, 0, 0, 0, 0
    rd = []
    for j in range(n_ax):
        ax = getattr(fr, f"axon{j}", None)
        if ax is None: continue
        m = ax.get("myelinated", False) if hasattr(ax, "get") else False
        r = ax.is_recruited()
        d = float(ax.get("d", 0) if hasattr(ax, "get") else 0)
        lb = labels[j] if j < len(labels) else "vagal"
        if lb == "sympathetic":
            s_t += 1
            if r: s_r += 1; rd.append(d)
        elif m:
            vm_t += 1
            if r: vm_r += 1; rd.append(d)
        else:
            vu_t += 1
            if r: vu_r += 1; rd.append(d)
    return {"vm_r": vm_r, "vm_t": vm_t, "vu_r": vu_r, "vu_t": vu_t, "s_r": s_r, "s_t": s_t, "rd": rd}

if __name__ == "__main__":
    nc = min(28, os.cpu_count() - 2)
    nrv.backend.parameters.set_nmod_ncore(nc)
    nrv.backend.parameters.set_gmsh_ncore(min(16, os.cpu_count()))
    log(f"NMOD={nc}, GMSH={min(16, os.cpu_count())}, cores={os.cpu_count()}")

    geom_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "bovine_geometry.json")
    if not os.path.exists(geom_path):
        geom_path = "bovine_geometry.json"
    if not os.path.exists(geom_path):
        geom_path = "data/bovine_geometry.json"
    with open(geom_path) as f:
        geom = json.load(f)

    indices = geom["representative_subset_15"]["indices"]
    fascs_geo = [geom["vagal_fascicles"][i] for i in indices]
    n_f = len(fascs_geo)
    log(f"{n_f} fascicles (P1 + ILU, no BoomerAMG)")
    log(f"Diameters: {[round(f['diameter_um']) for f in fascs_geo]}")

    nerve = nrv.nerve(length=5000, diameter=5000, Outer_D=10)
    fi = []
    fl = {}
    for i, fg in enumerate(fascs_geo):
        fasc = nrv.fascicle(diameter=fg["diameter_um"], ID=i)
        d, t, lb = build_mixed_pop(N_AX, SYMP_FRAC, seed=i)
        fasc.fill(data=(d, t), delta=5)
        np_ = fasc.n_ax
        fl[i] = lb[:np_]
        nerve.add_fascicle(fasc, y=fg["y_um"], z=fg["z_um"])
        fi.append({"id": i, "orig_id": fg["id"], "d": round(fg["diameter_um"]),
                   "y": round(fg["y_um"]), "z": round(fg["z_um"]), "np": np_,
                   "nv": sum(1 for l in lb[:np_] if l == "vagal"),
                   "ns": sum(1 for l in lb[:np_] if l == "sympathetic")})
        if (i+1) % 5 == 0 or i == n_f-1:
            log(f"  {i+1}/{n_f} | F{fg['id']} d={fg['diameter_um']:.0f}um at ({fg['y_um']:.0f},{fg['z_um']:.0f})")
    log(f"Total: {sum(x['np'] for x in fi)} fibers ({sum(x['nv'] for x in fi)}V + {sum(x['ns'] for x in fi)}S)")

    cuff = nrv.CUFF_electrode(label="bp", contact_length=500, contact_thickness=200,
        insulator_length=2000, insulator_thickness=800, x_center=2500)
    stim = nrv.stimulus()
    stim.pulse(start=0.5, value=-100, duration=0.2)
    fem = nrv.FEM_stimulation(endo_mat="endoneurium_ranck", peri_mat="perineurium",
        epi_mat="epineurium", ext_mat="saline")
    fem.model.elem = ("Lagrange", 1)
    fem.add_electrode(cuff, stim)
    nerve.attach_extracellular_stimulation(fem)

    # Gmsh coarsening only
    orig_cm = nerve.extra_stim.model.mesh.compute_mesh.__func__
    def pcm(self_m):
        self_m.compute_geo()
        self_m.compute_domains()
        self_m.compute_res()
        log("  gmsh: Min=30, Delaunay")
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 30)
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        self_m.generate()
    nerve.extra_stim.model.mesh.compute_mesh = types.MethodType(pcm, nerve.extra_stim.model.mesh)

    log("=" * 50)
    log("Phase 1: FEM (P1 + ILU)")
    t0 = time.time()
    nerve.compute_electrodes_footprints()
    ft = time.time() - t0
    log(f"FEM solved: {ft:.1f}s ({ft/60:.1f} min)")

    nerve.save("bovine_15_ilu.json", extracel_context=True)
    log("Saved footprints")

    amps = np.linspace(50, 1000, 20).astype(int)
    log("=" * 50)
    log(f"Phase 2: Sweep ({len(amps)} amps)")
    res = {"geometry": {"n_f": n_f, "n_f_total": len(geom["vagal_fascicles"]),
           "selection": geom["representative_subset_15"]["selection_method"],
           "fem_s": round(ft, 1)}, "fi": fi, "amps": {}}

    for ai, amp in enumerate(amps):
        log(f"[{ai+1}/{len(amps)}] {amp}uA ({amp/1000:.2f}mA)")
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
            e = extract(fr, fi[i]["np"], fl.get(i, []))
            tvm += e["vm_r"]; tvmt += e["vm_t"]
            tvu += e["vu_r"]; tvut += e["vu_t"]
            ts += e["s_r"]; tst += e["s_t"]
            ad["f"][i] = e
        ad["sum"] = {"vm": f"{tvm}/{tvmt}", "vu": f"{tvu}/{tvut}", "s": f"{ts}/{tst}"}
        log(f"  Vm:{tvm}/{tvmt} Vu:{tvu}/{tvut} S:{ts}/{tst}")
        res["amps"][int(amp)] = ad

    with open("bovine_15_ilu_results.json", "w") as f:
        json.dump(res, f, indent=2, default=str)
    with open("bovine_15_ilu_results.pkl", "wb") as f:
        pickle.dump(res, f)

    tn = sum(res["amps"][a]["st"] for a in res["amps"])
    log("=" * 50)
    log("COMPLETE")
    log(f"FEM: {ft:.1f}s | NEURON: {tn:.1f}s | Total: {ft+tn:.1f}s")
