"""Spatial selectivity analysis for electrode configurations.

Computes per-fascicle recruitment range across all cathode rotations,
then summarizes as a spatial selectivity metric.

Spatial selectivity = how much control the electrode gives over
WHICH fascicles are recruited, independent of total recruitment level.
"""

import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from pathlib import Path

TEMPLATE = "plotly_dark"

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
    """Load per-contact basis fields from npz."""
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


def generate_all_rotations(n_contact):
    """Generate all cathode cluster rotations with standard weight profiles."""
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
                # Normalize: sum(|w|) = 1 for fair comparison
                w_abs = np.sum(np.abs(w))
                if w_abs > 0:
                    w = w / w_abs
                rotations.append({"weights": w, "start": start, "size": cs})
    return rotations


def compute_vpeak_per_rotation(basis, fascicle_ids, rotations, n_contact):
    """For each rotation, compute V_peak at each fascicle."""
    # shape: (n_rotations, n_fascicles)
    n_rot = len(rotations)
    n_fasc = len(fascicle_ids)
    vpeak_matrix = np.zeros((n_rot, n_fasc))

    for ri, rot in enumerate(rotations):
        w = rot["weights"]
        for fi, fid in enumerate(fascicle_ids):
            v_combined = np.zeros_like(next(iter(basis[0].values())))
            for e in range(n_contact):
                v_combined += w[e] * basis[e].get(fid, np.zeros_like(v_combined))
            vpeak_matrix[ri, fi] = np.abs(v_combined).max()

    return vpeak_matrix


def compute_spatial_selectivity(vpeak_matrix):
    """Compute per-fascicle and aggregate spatial selectivity.

    Per-fascicle: range of V_peak across rotations (normalized by max).
    A fascicle that can go from 0 to 100% of max voltage has selectivity = 1.
    A fascicle that stays the same regardless of rotation has selectivity = 0.

    Returns per-fascicle selectivity and mean.
    """
    # Normalize each fascicle by its max V_peak across all rotations
    vmax = vpeak_matrix.max(axis=0)
    vmax[vmax == 0] = 1  # avoid div by zero

    # Range: (max - min) / max for each fascicle
    v_range = (vpeak_matrix.max(axis=0) - vpeak_matrix.min(axis=0)) / vmax

    return v_range, float(np.mean(v_range))


def plot_spatial_selectivity(all_data, geom, save_prefix):
    """Multi-panel spatial selectivity comparison."""
    all_fascs = geom["vagal_fascicles"]
    sa, sb = geom["nerve"]["semi_major_um"], geom["nerve"]["semi_minor_um"]
    fids = [fg["id"] for fg in all_fascs]

    cfg_list = [c for c in ["bipolar", "4contact", "8contact", "16contact"] if c in all_data]

    # === Figure 1: Spatial selectivity map (2×2) ===
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=[f"<b>{CONFIG_LABELS[c]}</b><br><sub>SSI={all_data[c]['mean_ssi']:.2f}</sub>"
                        for c in cfg_list],
        horizontal_spacing=0.06, vertical_spacing=0.12)

    theta = np.linspace(0, 2 * np.pi, 200)

    for idx, cfg in enumerate(cfg_list):
        row = idx // 2 + 1
        col = idx % 2 + 1
        ax_idx = idx + 1
        d = all_data[cfg]

        fig.add_trace(go.Scatter(
            x=sa * np.cos(theta), y=sb * np.sin(theta),
            mode="lines", line=dict(color="rgba(255,255,255,0.4)", width=1.5),
            showlegend=False, hoverinfo="skip"), row=row, col=col)

        for fi, fg in enumerate(all_fascs):
            ssi_val = d["per_fascicle"][fi]
            r = int(80 + 175 * (1 - ssi_val))
            g = int(80 + 175 * ssi_val)
            b = 80
            color = f"rgb({r},{g},{b})"

            t = np.linspace(0, 2 * np.pi, 40)
            rad = fg["diameter_um"] / 2
            fig.add_trace(go.Scatter(
                x=fg["y_um"] + rad * np.cos(t),
                y=fg["z_um"] + rad * np.sin(t),
                mode="lines", fill="toself", fillcolor=color,
                line=dict(color="rgba(255,255,255,0.5)", width=0.8),
                showlegend=False,
                hovertext=f"F{fg['id']}: SSI={ssi_val:.2f}",
                hoverinfo="text"), row=row, col=col)

        scaleanchor = f"y{ax_idx}" if ax_idx > 1 else "y"
        fig.update_xaxes(range=[-sa*1.2, sa*1.2], scaleanchor=scaleanchor,
            showgrid=False, zeroline=False, row=row, col=col)
        fig.update_yaxes(range=[-sb*1.4, sb*1.4], showgrid=False, zeroline=False,
            row=row, col=col)

    # Colorbar
    fig.add_trace(go.Scatter(
        x=[sa * 2] * 50, y=np.linspace(-sb, sb, 50),
        mode="markers", marker=dict(size=0.1, color=np.linspace(0, 1, 50),
            colorscale=[[0, "rgb(255,80,80)"], [0.5, "rgb(180,180,80)"], [1, "rgb(80,255,80)"]],
            cmin=0, cmax=1, showscale=True,
            colorbar=dict(title=dict(text="Spatial<br>selectivity", side="right"),
                x=1.02, len=0.6, thickness=15,
                tickvals=[0, 0.5, 1], ticktext=["0 (fixed)", "0.5", "1 (steerable)"])),
        showlegend=False, hoverinfo="skip"), row=2, col=2)

    fig.update_layout(template=TEMPLATE,
        title=dict(text="<b>Spatial Selectivity — Which Fascicles Can Be Targeted?</b><br>"
                        "<sub>Green = controllable by steering, red = always activated regardless of rotation</sub>",
                   x=0.5, y=0.98),
        height=900, width=900,
        margin=dict(t=120, b=40, l=40, r=100))
    fig.write_html(f"{save_prefix}_spatial_map.html")
    fig.write_image(f"{save_prefix}_spatial_map.png", scale=3)
    print(f"Saved: {save_prefix}_spatial_map.html + .png")

    # === Figure 2: SSI bar chart + recruitment range ===
    fig2 = make_subplots(rows=1, cols=2,
        subplot_titles=["<b>Mean Spatial Selectivity Index</b>",
                        "<b>Recruitment Range per Fascicle</b>"],
        horizontal_spacing=0.1)

    # Bar chart
    fig2.add_trace(go.Bar(
        x=[CONFIG_LABELS[c] for c in cfg_list],
        y=[all_data[c]["mean_ssi"] for c in cfg_list],
        marker_color=[CONFIG_COLORS[c] for c in cfg_list],
        text=[f"{all_data[c]['mean_ssi']:.2f}" for c in cfg_list],
        textposition="outside", textfont=dict(size=14),
        showlegend=False,
    ), row=1, col=1)

    # Box plot of per-fascicle selectivity
    for cfg in cfg_list:
        fig2.add_trace(go.Box(
            y=all_data[cfg]["per_fascicle"],
            name=CONFIG_LABELS[cfg],
            marker_color=CONFIG_COLORS[cfg],
            boxmean=True,
        ), row=1, col=2)

    fig2.update_yaxes(title_text="SSI", range=[0, 1.05], row=1, col=1)
    fig2.update_yaxes(title_text="Per-fascicle selectivity", range=[0, 1.05], row=1, col=2)

    fig2.update_layout(template=TEMPLATE,
        title=dict(text="<b>Spatial Selectivity Comparison</b><br>"
                        "<sub>SSI = mean voltage range across cathode rotations (0=uniform, 1=fully steerable)</sub>",
                   x=0.5, y=0.97),
        height=500, width=1100, showlegend=False,
        margin=dict(t=110, b=60, l=60, r=40))
    fig2.write_html(f"{save_prefix}_ssi_comparison.html")
    fig2.write_image(f"{save_prefix}_ssi_comparison.png", scale=3)
    print(f"Saved: {save_prefix}_ssi_comparison.html + .png")


if __name__ == "__main__":
    geom = load_geometry()
    all_fascs = geom["vagal_fascicles"]
    fids = [fg["id"] for fg in all_fascs]

    all_data = {}

    for cfg in ["bipolar", "4contact", "8contact", "16contact"]:
        cfg_dir = f"electrode_comparison/{cfg}"
        bf_path = f"{cfg_dir}/basis_fields.npz"
        if not Path(bf_path).exists():
            print(f"SKIP {cfg}: no basis_fields.npz")
            continue

        print(f"=== {cfg} ===")
        n_elec, basis = load_basis_fields(cfg_dir)
        print(f"  {n_elec} basis fields loaded")

        rotations = generate_all_rotations(n_elec)
        print(f"  {len(rotations)} rotations generated")

        vpeak_matrix = compute_vpeak_per_rotation(basis, fids, rotations, n_elec)
        per_fascicle, mean_ssi = compute_spatial_selectivity(vpeak_matrix)

        print(f"  Mean SSI = {mean_ssi:.3f}")
        print(f"  Per-fascicle SSI: min={per_fascicle.min():.3f}, "
              f"max={per_fascicle.max():.3f}, std={per_fascicle.std():.3f}")

        all_data[cfg] = {
            "mean_ssi": mean_ssi,
            "per_fascicle": per_fascicle.tolist(),
            "n_rotations": len(rotations),
        }

    # Save SSI data
    out_dir = "outputs/figures/electrode_comparison"
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/spatial_selectivity.json", "w") as f:
        json.dump(all_data, f, indent=2)
    print(f"\nSaved: {out_dir}/spatial_selectivity.json")

    # Plot
    plot_spatial_selectivity(all_data, geom, f"{out_dir}/comparison")
    print("Done!")
