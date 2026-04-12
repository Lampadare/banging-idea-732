"""Side-by-side electrode comparison plots."""

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
    "4contact": "4-contact steered",
    "8contact": "8-contact steered",
    "16contact": "16-contact steered",
}


def load_all_configs(base_dir="electrode_comparison"):
    configs = {}
    for cfg in ["bipolar", "4contact", "8contact", "16contact"]:
        rp = Path(base_dir) / cfg / "results.json"
        if rp.exists():
            with open(rp) as f:
                configs[cfg] = json.load(f)
    return configs


def plot_recruitment_comparison(configs, save_prefix="outputs/figures/electrode_comparison"):
    """Overlay recruitment curves for all configs."""
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=["<b>Mean Myelinated Recruitment</b>",
                        "<b>Current Efficiency</b>"],
        horizontal_spacing=0.1)

    threshold_data = {}

    for cfg, data in configs.items():
        amps = sorted(data["amps"].keys(), key=int)
        amps_mA = [int(a) / 1000 for a in amps]
        mean_pcts = []
        for a in amps:
            fracs = [data["amps"][a]["f"][str(i)]["vm_r"] / max(data["amps"][a]["f"][str(i)]["vm_t"], 1)
                     for i in range(len(data["fi"]))]
            mean_pcts.append(np.mean(fracs) * 100)

        fig.add_trace(go.Scatter(
            x=amps_mA, y=mean_pcts, mode="lines+markers",
            line=dict(color=CONFIG_COLORS[cfg], width=3),
            marker=dict(size=5),
            name=CONFIG_LABELS[cfg],
        ), row=1, col=1)

        # Find 50% threshold
        for i, p in enumerate(mean_pcts):
            if p >= 50:
                threshold_data[cfg] = amps_mA[i]
                break

    # Panel 2: Bar chart of current needed for 50% recruitment
    cfgs_with_thresh = [c for c in ["bipolar", "4contact", "8contact", "16contact"] if c in threshold_data]
    fig.add_trace(go.Bar(
        x=[CONFIG_LABELS[c] for c in cfgs_with_thresh],
        y=[threshold_data[c] for c in cfgs_with_thresh],
        marker_color=[CONFIG_COLORS[c] for c in cfgs_with_thresh],
        text=[f"~{threshold_data[c]:.2f} mA" for c in cfgs_with_thresh],
        textposition="outside",
        textfont=dict(size=12),
        showlegend=False,
    ), row=1, col=2)

    # Add 5x annotation
    if "bipolar" in threshold_data and "4contact" in threshold_data:
        ratio = threshold_data["bipolar"] / threshold_data["4contact"]
        fig.add_annotation(
            x=0.5, y=0.5, xref="x2 domain", yref="y2 domain",
            text=f"<b>{ratio:.0f}× less current<br>with steering</b>",
            showarrow=False, font=dict(size=16, color="#4CAF50"),
            bgcolor="rgba(0,0,0,0.6)", borderpad=8,
        )

    fig.update_xaxes(title_text="Current (mA)", row=1, col=1)
    fig.update_yaxes(title_text="Mean % myelinated recruited", range=[-5, 105], row=1, col=1)
    fig.update_yaxes(title_text="Current for 50% recruitment (mA)", row=1, col=2)

    fig.update_layout(template=TEMPLATE,
        title=dict(text="<b>Electrode Configuration Comparison</b><br>"
                        "<sub>Bovine vagosympathetic trunk, 57 fascicles, mixed populations</sub>",
                   x=0.5, y=0.97),
        height=500, width=1200,
        legend=dict(orientation="h", y=-0.15, x=0.25, xanchor="center", font=dict(size=11)),
        margin=dict(t=100, b=100, l=60, r=40))
    os.makedirs(os.path.dirname(save_prefix), exist_ok=True)
    fig.write_html(f"{save_prefix}_recruitment.html")
    fig.write_image(f"{save_prefix}_recruitment.png", scale=3)
    print(f"Saved: {save_prefix}_recruitment.html + .png")


def plot_heatmap_comparison(configs, save_prefix="outputs/figures/electrode_comparison"):
    """4-panel heatmap comparison."""
    from plot_plotly import load_geometry, load_grid, ellipse_xy, circle_xy

    geom = load_geometry()
    sa, sb = geom["nerve"]["semi_major_um"], geom["nerve"]["semi_minor_um"]
    all_fascs = geom["vagal_fascicles"]

    cfg_list = [c for c in ["bipolar", "4contact", "8contact", "16contact"] if c in configs]
    n_cfg = len(cfg_list)

    fig = make_subplots(rows=1, cols=n_cfg,
        subplot_titles=[f"<b>{CONFIG_LABELS[c]}</b>" for c in cfg_list],
        horizontal_spacing=0.04)

    for col, cfg in enumerate(cfg_list, 1):
        gp = f"electrode_comparison/{cfg}/grid.npz"
        if not Path(gp).exists():
            continue
        y, z, v, _, _ = load_grid(gp)

        # Mask outside nerve
        yy, zz = np.meshgrid(y, z)
        inside = (yy / sa) ** 2 + (zz / sb) ** 2 <= 1.0
        v_masked = np.where(inside, v, np.nan)

        # Normalize to own max absolute value → shows field shape, not magnitude
        v_abs_max = np.nanmax(np.abs(v_masked))
        if v_abs_max > 0:
            v_norm = v_masked / v_abs_max
        else:
            v_norm = v_masked

        fig.add_trace(go.Heatmap(
            z=v_norm, x=y, y=z,
            colorscale="Inferno", zsmooth="best",
            zmin=-1, zmax=1,
            showscale=(col == n_cfg),
            colorbar=dict(title=dict(text="Normalized<br>field", side="right"),
                          x=1.02, thickness=12) if col == n_cfg else None,
        ), row=1, col=col)

        # Nerve boundary
        ex, ey = ellipse_xy(sa, sb)
        fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines",
            line=dict(color="rgba(255,255,255,0.5)", width=1.5),
            showlegend=False, hoverinfo="skip"), row=1, col=col)

        # Fascicle outlines
        for fg in all_fascs:
            cx, cy = circle_xy(fg["y_um"], fg["z_um"], fg["diameter_um"] / 2, 40)
            fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines",
                line=dict(color="rgba(255,255,255,0.4)", width=0.6),
                showlegend=False, hoverinfo="skip"), row=1, col=col)

    for col in range(1, n_cfg + 1):
        fig.update_xaxes(range=[-sa*1.15, sa*1.15], scaleanchor=f"y{col}",
            showgrid=False, row=1, col=col)
        fig.update_yaxes(range=[-sb*1.15, sb*1.15], showgrid=False, row=1, col=col)

    fig.update_layout(template=TEMPLATE,
        title=dict(text="<b>Voltage Field Comparison — Current Steering</b><br>"
                        "<sub>Cross-section at cuff center, optimized contact weights, 1 mA total</sub>",
                   x=0.5, y=0.97),
        height=500, width=1600,
        margin=dict(t=100, b=40, l=40, r=80))
    fig.write_html(f"{save_prefix}_heatmaps.html")
    fig.write_image(f"{save_prefix}_heatmaps.png", scale=3)
    print(f"Saved: {save_prefix}_heatmaps.html + .png")


def plot_summary_table(configs, save_prefix="outputs/figures/electrode_comparison"):
    """Summary metrics as a clean table figure."""
    rows = []
    for cfg in ["bipolar", "4contact", "8contact", "16contact"]:
        if cfg not in configs:
            continue
        data = configs[cfg]
        amps = sorted(data["amps"].keys(), key=int)

        # Find 50% threshold
        thresh_mA = ">1.0"
        for a in amps:
            fracs = [data["amps"][a]["f"][str(i)]["vm_r"] / max(data["amps"][a]["f"][str(i)]["vm_t"], 1)
                     for i in range(len(data["fi"]))]
            if np.mean(fracs) >= 0.5:
                thresh_mA = f"~{int(a)/1000:.2f}"
                break

        # Recruitment at mid amplitude
        mid = amps[len(amps)//2]
        mid_fracs = [data["amps"][mid]["f"][str(i)]["vm_r"] / max(data["amps"][mid]["f"][str(i)]["vm_t"], 1)
                     for i in range(len(data["fi"]))]

        # Gini at mid amplitude
        v = np.sort(np.array(mid_fracs))
        n = len(v)
        gini = (2 * np.sum(np.arange(1, n+1) * v) - (n+1) * v.sum()) / (n * v.sum()) if v.sum() > 0 else 0

        n_contacts = data["geometry"]["n_contacts"]
        weights = data["geometry"].get("weights", [])
        si = data["geometry"].get("si", 0)

        rows.append({
            "config": CONFIG_LABELS[cfg],
            "contacts": n_contacts,
            "thresh": thresh_mA,
            "mean_recruit": f"{np.mean(mid_fracs)*100:.1f}%",
            "gini": f"{gini:.3f}",
        })

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Configuration", "Contacts", "50% threshold", "Mean recruit @0.5mA", "Gini @0.5mA"],
            fill_color="#2a2a3e", font=dict(color="white", size=13),
            align="center",
        ),
        cells=dict(
            values=[[r["config"] for r in rows],
                    [r["contacts"] for r in rows],
                    [r["thresh"] for r in rows],
                    [r["mean_recruit"] for r in rows],
                    [r["gini"] for r in rows]],
            fill_color="#1a1a2e", font=dict(color="white", size=12),
            align="center",
        ),
    )])
    fig.update_layout(template=TEMPLATE,
        title=dict(text="<b>Electrode Configuration Summary</b>", x=0.5),
        height=300, width=900, margin=dict(t=60, b=20))
    fig.write_html(f"{save_prefix}_table.html")
    fig.write_image(f"{save_prefix}_table.png", scale=3)
    print(f"Saved: {save_prefix}_table.html + .png")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")

    configs = load_all_configs()
    print(f"Loaded {len(configs)} configs: {list(configs.keys())}")

    prefix = "outputs/figures/electrode_comparison/comparison"
    os.makedirs("outputs/figures/electrode_comparison", exist_ok=True)

    plot_recruitment_comparison(configs, save_prefix=prefix)
    plot_heatmap_comparison(configs, save_prefix=prefix)
    plot_summary_table(configs, save_prefix=prefix)
    print("All comparison plots done!")
