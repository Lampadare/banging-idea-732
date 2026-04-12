"""Compute η_max: maximum achievable spatial selectivity per electrode config.

For each config, finds the weight vector + target region (top 6 fascicles)
that maximizes η = mean_recruit(target) − mean_recruit(off_target).

Uses basis field superposition + threshold model. No FEM needed.

Usage:
    python src/compute_eta.py
"""

import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from pathlib import Path

TEMPLATE = "plotly_dark"
N_TARGET = 6  # top 10% of 57
AMPS = np.linspace(100, 1000, 20).astype(int)

CONFIG_COLORS = {
    "bipolar": "#FF5252",
    "4contact": "#4CAF50",
    "8contact": "#2196F3",
    "16contact": "#FFB74D",
}
CONFIG_LABELS = {
    "bipolar": "Bipolar (2 rings)",
    "4contact": "4-contact",
    "8contact": "8-contact",
    "16contact": "16-contact",
}


def load_geometry(path="data/bovine_geometry.json"):
    with open(path) as f:
        return json.load(f)


def load_basis_fields(cfg_dir):
    d = np.load(f"{cfg_dir}/basis_fields.npz", allow_pickle=True)
    n_elec = int(d["n_electrodes"])
    basis = {}
    for e in range(n_elec):
        basis[e] = {}
        for k in d.files:
            if k.startswith(f"e{e}_f") and "_grid" not in k:
                fid = int(k.split("_f")[1])
                basis[e][fid] = d[k]
    return n_elec, basis


def load_thresholds(cal_path="merged/results.json", vol_path="merged/57voltages.npz"):
    with open(cal_path) as f:
        results = json.load(f)
    voltages = {}
    if Path(vol_path).exists():
        d = np.load(vol_path)
        for k in d.files:
            if k.startswith("f"):
                voltages[k] = d[k]

    fi = results["fi"]
    amps_data = results["amps"]
    amp_keys = sorted([int(k) for k in amps_data.keys()])

    vpeaks = []
    for f in fi:
        key = f"f{f['orig_id']}"
        if key in voltages and np.abs(voltages[key]).max() > 0:
            vpeaks.append(np.abs(voltages[key]).max())
        else:
            vpeaks.append(0)

    vm_pts = []
    for amp in amp_keys:
        ad = amps_data[str(amp)]
        for i, f in enumerate(fi):
            if vpeaks[i] == 0:
                continue
            v_eff = vpeaks[i] * amp
            fd = ad["f"][str(i)] if str(i) in ad["f"] else ad["f"][str(f["id"])]
            if fd["vm_t"] > 0:
                vm_pts.append((v_eff, fd["vm_r"] / fd["vm_t"]))

    pts = np.array(vm_pts) if vm_pts else np.array([[0, 0]])
    recruited = pts[pts[:, 1] > 0.5, 0]
    not_rec = pts[pts[:, 1] < 0.1, 0]
    if len(recruited) > 0 and len(not_rec) > 0:
        thresh = (recruited.min() + not_rec.max()) / 2
    elif len(recruited) > 0:
        thresh = recruited.min() * 0.8
    else:
        thresh = float("inf")

    return thresh


def predict_fascicle_recruitment(vpeak, amp, threshold):
    """Predict myelinated recruitment fraction for one fascicle."""
    v_eff = vpeak * amp
    rng = np.random.default_rng(42)
    n_vm = 13  # typical myelinated count per fascicle
    diams = rng.lognormal(1.8, 0.5, n_vm).clip(2, 16)
    recruited = sum(1 for d in diams if v_eff > threshold * (8.0 / max(d, 1)))
    return recruited / n_vm


def generate_rotations(n_contact):
    """All cathode cluster rotations, normalized weights."""
    cluster_sizes = [1, 2, 3] if n_contact >= 4 else [1, 2]
    weight_profiles = {
        1: [[1.0]],
        2: [[0.5, 0.5]],
        3: [[0.25, 0.5, 0.25]],
    }
    rotations = []
    for cs in cluster_sizes:
        if cs > n_contact:
            continue
        for start in range(n_contact):
            for wp in weight_profiles[cs]:
                w = np.zeros(n_contact)
                for j, wv in enumerate(wp):
                    w[(start + j) % n_contact] = -wv
                cathode_idxs = set((start + j) % n_contact for j in range(cs))
                anode_idxs = [i for i in range(n_contact) if i not in cathode_idxs]
                if anode_idxs:
                    for ai in anode_idxs:
                        w[ai] = -w.sum() / len(anode_idxs)
                w_abs = np.sum(np.abs(w))
                if w_abs > 0:
                    w = w / w_abs
                rotations.append(w)
    return rotations


def compute_eta_for_config(basis, fids, n_contact, threshold, amps):
    """Compute η_max for one electrode config."""
    rotations = generate_rotations(n_contact)

    best_eta = -999
    best_result = None

    for wi, w in enumerate(rotations):
        # V_peak per fascicle for this weight vector
        vpeaks = np.zeros(len(fids))
        for fi, fid in enumerate(fids):
            v_combined = np.zeros_like(next(iter(basis[0].values())))
            for e in range(n_contact):
                v_combined += w[e] * basis[e].get(fid, np.zeros_like(v_combined))
            vpeaks[fi] = np.abs(v_combined).max()

        # Target = top N_TARGET fascicles by V_peak
        target_idx = np.argsort(vpeaks)[-N_TARGET:]
        off_target_idx = np.array([i for i in range(len(fids)) if i not in target_idx])

        # η at each amplitude
        eta_curve = []
        for amp in amps:
            recruit = np.array([predict_fascicle_recruitment(vpeaks[fi], amp, threshold)
                                for fi in range(len(fids))])
            mu_target = recruit[target_idx].mean()
            mu_off = recruit[off_target_idx].mean() if len(off_target_idx) > 0 else 0
            eta_curve.append(mu_target - mu_off)

        eta_max_this = max(eta_curve)
        best_amp_idx = np.argmax(eta_curve)

        if eta_max_this > best_eta:
            best_eta = eta_max_this
            recruit_at_best = np.array([predict_fascicle_recruitment(vpeaks[fi], amps[best_amp_idx], threshold)
                                        for fi in range(len(fids))])
            best_result = {
                "eta_max": round(float(eta_max_this), 4),
                "best_amp_uA": int(amps[best_amp_idx]),
                "weights": w.tolist(),
                "target_fascicle_ids": [fids[i] for i in target_idx],
                "target_mean_recruit": round(float(recruit_at_best[target_idx].mean()), 4),
                "off_target_mean_recruit": round(float(recruit_at_best[off_target_idx].mean()), 4),
                "eta_curve": [round(float(e), 4) for e in eta_curve],
                "per_fascicle_recruit": {str(fids[i]): round(float(recruit_at_best[i]), 4)
                                         for i in range(len(fids))},
            }

    return best_result


def plot_eta_results(all_results, geom, save_prefix):
    """Generate all η comparison plots."""
    all_fascs = geom["vagal_fascicles"]
    sa, sb = geom["nerve"]["semi_major_um"], geom["nerve"]["semi_minor_um"]
    cfg_list = [c for c in ["bipolar", "4contact", "8contact", "16contact"] if c in all_results]

    # === Figure 1: η vs amplitude curves ===
    fig1 = go.Figure()
    for cfg in cfg_list:
        d = all_results[cfg]
        amps_mA = [a / 1000 for a in AMPS]
        fig1.add_trace(go.Scatter(
            x=amps_mA, y=d["eta_curve"], mode="lines+markers",
            line=dict(color=CONFIG_COLORS[cfg], width=3), marker=dict(size=5),
            name=f"{CONFIG_LABELS[cfg]} (η_max={d['eta_max']:.2f})",
        ))
        # Mark the peak
        best_idx = np.argmax(d["eta_curve"])
        fig1.add_trace(go.Scatter(
            x=[amps_mA[best_idx]], y=[d["eta_curve"][best_idx]],
            mode="markers", marker=dict(size=12, symbol="star", color=CONFIG_COLORS[cfg]),
            showlegend=False,
        ))

    fig1.update_layout(template=TEMPLATE,
        title=dict(text="<b>Spatial Selectivity η vs Stimulus Amplitude</b><br>"
                        f"<sub>η = mean recruit (top {N_TARGET} fascicles) − mean recruit (remaining), "
                        f"best weight vector per config</sub>", x=0.5, y=0.95),
        xaxis=dict(title="Current (mA)"),
        yaxis=dict(title="η (spatial selectivity)", range=[-0.1, 1.05]),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(size=11)),
        height=500, width=800, margin=dict(t=110, b=100))
    fig1.write_html(f"{save_prefix}_eta_curves.html")
    fig1.write_image(f"{save_prefix}_eta_curves.png", scale=3)
    print(f"Saved: {save_prefix}_eta_curves.html + .png")

    # === Figure 2: η_max bar chart ===
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=[CONFIG_LABELS[c] for c in cfg_list],
        y=[all_results[c]["eta_max"] for c in cfg_list],
        marker_color=[CONFIG_COLORS[c] for c in cfg_list],
        text=[f"η={all_results[c]['eta_max']:.2f}<br>@~{all_results[c]['best_amp_uA']/1000:.2f}mA"
              for c in cfg_list],
        textposition="outside", textfont=dict(size=12),
    ))
    fig2.update_layout(template=TEMPLATE,
        title=dict(text="<b>Maximum Achievable Spatial Selectivity</b><br>"
                        f"<sub>Best η over all weight vectors and amplitudes, "
                        f"target = {N_TARGET} fascicles</sub>", x=0.5),
        yaxis=dict(title="η_max", range=[0, 1.1]),
        height=450, width=700, showlegend=False,
        margin=dict(t=100, b=60))
    fig2.write_html(f"{save_prefix}_eta_bar.html")
    fig2.write_image(f"{save_prefix}_eta_bar.png", scale=3)
    print(f"Saved: {save_prefix}_eta_bar.html + .png")

    # === Figure 3: Target region maps ===
    fig3 = make_subplots(rows=1, cols=len(cfg_list),
        subplot_titles=[f"<b>{CONFIG_LABELS[c]}</b><br><sub>η={all_results[c]['eta_max']:.2f}</sub>"
                        for c in cfg_list],
        horizontal_spacing=0.05)

    theta = np.linspace(0, 2 * np.pi, 200)

    for col, cfg in enumerate(cfg_list, 1):
        d = all_results[cfg]
        target_ids = set(d["target_fascicle_ids"])
        recruits = d["per_fascicle_recruit"]

        fig3.add_trace(go.Scatter(
            x=sa * np.cos(theta), y=sb * np.sin(theta),
            mode="lines", line=dict(color="rgba(255,255,255,0.4)", width=1.5),
            showlegend=False, hoverinfo="skip"), row=1, col=col)

        for fg in all_fascs:
            fid = fg["id"]
            is_target = fid in target_ids
            r_val = recruits.get(str(fid), 0)

            if is_target:
                color = f"rgba(76,175,80,{0.3 + 0.7 * r_val})"
                border = dict(color="#4CAF50", width=2)
            else:
                gray = int(60 + 120 * r_val)
                color = f"rgba({gray},{gray},{gray},0.6)"
                border = dict(color="rgba(255,255,255,0.3)", width=0.5)

            t = np.linspace(0, 2 * np.pi, 40)
            rad = fg["diameter_um"] / 2
            fig3.add_trace(go.Scatter(
                x=fg["y_um"] + rad * np.cos(t),
                y=fg["z_um"] + rad * np.sin(t),
                mode="lines", fill="toself", fillcolor=color, line=border,
                showlegend=False,
                hovertext=f"F{fid}: {r_val*100:.0f}% {'[TARGET]' if is_target else ''}",
                hoverinfo="text"), row=1, col=col)

        fig3.update_xaxes(range=[-sa*1.2, sa*1.2], scaleanchor=f"y{col}",
            showgrid=False, zeroline=False, row=1, col=col)
        fig3.update_yaxes(range=[-sb*1.4, sb*1.4], showgrid=False, zeroline=False,
            row=1, col=col)

    fig3.update_layout(template=TEMPLATE,
        title=dict(text=f"<b>Target Regions — Top {N_TARGET} Fascicles per Config</b><br>"
                        "<sub>Green = target fascicles (highest voltage), gray = off-target, "
                        "brightness = recruitment level</sub>",
                   x=0.5, y=0.96),
        height=550, width=400 * len(cfg_list),
        margin=dict(t=120, b=40, l=40, r=40))
    fig3.write_html(f"{save_prefix}_eta_targets.html")
    fig3.write_image(f"{save_prefix}_eta_targets.png", scale=3)
    print(f"Saved: {save_prefix}_eta_targets.html + .png")


if __name__ == "__main__":
    print("Loading data...")
    geom = load_geometry()
    fids = [fg["id"] for fg in geom["vagal_fascicles"]]
    threshold = load_thresholds()
    print(f"Threshold: {threshold:.0f}")

    all_results = {}
    for cfg in ["bipolar", "4contact", "8contact", "16contact"]:
        bf_path = f"electrode_comparison/{cfg}/basis_fields.npz"
        if not Path(bf_path).exists():
            print(f"SKIP {cfg}: no basis_fields.npz")
            continue

        print(f"\n=== {cfg} ===")
        n_elec, basis = load_basis_fields(f"electrode_comparison/{cfg}")
        result = compute_eta_for_config(basis, fids, n_elec, threshold, AMPS)
        all_results[cfg] = result
        print(f"  η_max = {result['eta_max']:.3f} at ~{result['best_amp_uA']/1000:.2f} mA")
        print(f"  Target: {result['target_mean_recruit']*100:.1f}% | "
              f"Off-target: {result['off_target_mean_recruit']*100:.1f}%")
        print(f"  Target fascicles: {result['target_fascicle_ids']}")

    # Save results
    out_dir = "outputs/figures/electrode_comparison"
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/eta_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    # Plot
    plot_eta_results(all_results, geom, f"{out_dir}/comparison")
    print("\nDone!")
