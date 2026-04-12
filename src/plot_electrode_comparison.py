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

    # Load η results
    eta_data = {}
    eta_path = Path("outputs/figures/electrode_comparison/eta_results.json")
    if eta_path.exists():
        with open(eta_path) as f:
            eta_data = json.load(f)

    threshold_data = {}

    for cfg, data in configs.items():
        amps = sorted(data["amps"].keys(), key=int)
        amps_mA = [int(a) / 1000 for a in amps]
        mean_pcts = []
        for a in amps:
            fracs = [data["amps"][a]["f"][str(i)]["vm_r"] / max(data["amps"][a]["f"][str(i)]["vm_t"], 1)
                     for i in range(len(data["fi"]))]
            mean_pcts.append(np.mean(fracs) * 100)

        eta_val = eta_data.get(cfg, {}).get("eta_max", 0)
        fig.add_trace(go.Scatter(
            x=amps_mA, y=mean_pcts, mode="lines+markers",
            line=dict(color=CONFIG_COLORS[cfg], width=3),
            marker=dict(size=5),
            name=f"{CONFIG_LABELS[cfg]} (η={eta_val:.2f})",
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

    fig = make_subplots(rows=2, cols=2,
        subplot_titles=[f"<b>{CONFIG_LABELS[c]}</b>" for c in cfg_list],
        horizontal_spacing=0.06, vertical_spacing=0.1)

    for idx, cfg in enumerate(cfg_list):
        row = idx // 2 + 1
        col = idx % 2 + 1
        ax_idx = idx + 1
        gp = f"electrode_comparison/{cfg}/grid.npz"
        if not Path(gp).exists():
            continue
        y, z, v, _, _ = load_grid(gp)

        yy, zz = np.meshgrid(y, z)
        inside = (yy / sa) ** 2 + (zz / sb) ** 2 <= 1.0
        v_masked = np.where(inside, v, np.nan)

        v_abs_max = np.nanmax(np.abs(v_masked))
        if v_abs_max > 0:
            v_norm = v_masked / v_abs_max
        else:
            v_norm = v_masked

        fig.add_trace(go.Heatmap(
            z=v_norm, x=y, y=z,
            colorscale="Inferno", zsmooth="best",
            zmin=-1, zmax=1,
            showscale=(idx == n_cfg - 1),
            colorbar=dict(title=dict(text="Normalized<br>field", side="right"),
                          x=1.02, thickness=12) if idx == n_cfg - 1 else None,
        ), row=row, col=col)

        ex, ey = ellipse_xy(sa, sb)
        fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines",
            line=dict(color="rgba(255,255,255,0.5)", width=1.5),
            showlegend=False, hoverinfo="skip"), row=row, col=col)

        for fg in all_fascs:
            cx, cy = circle_xy(fg["y_um"], fg["z_um"], fg["diameter_um"] / 2, 40)
            fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines",
                line=dict(color="rgba(255,255,255,0.4)", width=0.6),
                showlegend=False, hoverinfo="skip"), row=row, col=col)

        scaleanchor = f"y{ax_idx}" if ax_idx > 1 else "y"
        fig.update_xaxes(range=[-sa*1.15, sa*1.15], scaleanchor=scaleanchor,
            showgrid=False, row=row, col=col)
        fig.update_yaxes(range=[-sb*1.15, sb*1.15], showgrid=False, row=row, col=col)

    fig.update_layout(template=TEMPLATE,
        title=dict(text="<b>Voltage Field Comparison — Current Steering</b><br>"
                        "<sub>Cross-section at cuff center, optimized contact weights, normalized</sub>",
                   x=0.5, y=0.98),
        height=900, width=900,
        margin=dict(t=100, b=40, l=40, r=80))
    fig.write_html(f"{save_prefix}_heatmaps.html")
    fig.write_image(f"{save_prefix}_heatmaps.png", scale=3)
    print(f"Saved: {save_prefix}_heatmaps.html + .png")


def plot_summary_table(configs, save_prefix="outputs/figures/electrode_comparison"):
    """Summary metrics as a clean table figure."""
    # Load η results
    eta_data = {}
    eta_path = Path("outputs/figures/electrode_comparison/eta_results.json")
    if eta_path.exists():
        with open(eta_path) as f:
            eta_data = json.load(f)

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

        n_contacts = data["geometry"]["n_contacts"]
        eta = eta_data.get(cfg, {}).get("eta_max", 0)
        eta_amp = eta_data.get(cfg, {}).get("best_amp_uA", 0)
        efficiency = ""
        if cfg != "bipolar":
            try:
                bp_val = 0.95
                cfg_val = float(thresh_mA.replace("~", "").replace(">", "").replace(" mA", ""))
                if cfg_val > 0:
                    ratio = bp_val / cfg_val
                    efficiency = f"{ratio:.0f}×" if ratio > 1 else "—"
            except:
                efficiency = "—"

        rows.append({
            "config": CONFIG_LABELS[cfg],
            "contacts": n_contacts,
            "thresh": thresh_mA + " mA",
            "eta": f"{eta:.2f}",
            "eta_amp": f"~{eta_amp/1000:.2f} mA" if eta_amp else "—",
            "efficiency": efficiency if efficiency else "baseline",
        })

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Configuration", "Contacts", "50% threshold",
                    "η_max", "η best amplitude", "Current efficiency"],
            fill_color="#2a2a3e", font=dict(color="white", size=13),
            align="center",
        ),
        cells=dict(
            values=[[r["config"] for r in rows],
                    [r["contacts"] for r in rows],
                    [r["thresh"] for r in rows],
                    [r["eta"] for r in rows],
                    [r["eta_amp"] for r in rows],
                    [r["efficiency"] for r in rows]],
            fill_color="#1a1a2e", font=dict(color="white", size=12),
            align="center",
        ),
    )])
    fig.update_layout(template=TEMPLATE,
        title=dict(text="<b>Electrode Configuration Summary</b><br>"
                        "<sub>η = spatial selectivity (target 6 fascicles vs remaining 51)</sub>", x=0.5),
        height=300, width=1100, margin=dict(t=80, b=20))
    fig.write_html(f"{save_prefix}_table.html")
    fig.write_image(f"{save_prefix}_table.png", scale=3)
    print(f"Saved: {save_prefix}_table.html + .png")


def plot_3d_electrode(cfg_name, config_data, geom, save_prefix):
    """3D nerve view with multi-contact electrode layout."""
    from plot_plotly import load_geometry

    fi = config_data["fi"]
    amps = config_data["amps"]
    amp_keys = sorted([int(k) for k in amps.keys()])
    amp_idx = len(amp_keys) // 3
    amp = amp_keys[amp_idx]
    ad = amps[str(amp)]

    sa, sb = geom["nerve"]["semi_major_um"], geom["nerve"]["semi_minor_um"]
    all_fascs = geom["vagal_fascicles"]
    n_f = len(fi)
    nerve_len = 3000

    # Load weights
    weights = config_data["geometry"].get("weights", [])
    n_contacts = config_data["geometry"].get("n_contacts", len(weights))

    # Activation colorscale
    ACMAP = [
        [0.0, "rgb(20,10,40)"], [0.3, "rgb(130,20,100)"],
        [0.6, "rgb(230,110,20)"], [1.0, "rgb(255,255,140)"],
    ]

    def frac_color(f):
        for i in range(len(ACMAP) - 1):
            lo_v, lo_c = ACMAP[i]
            hi_v, hi_c = ACMAP[i + 1]
            if f <= hi_v:
                t = (f - lo_v) / max(hi_v - lo_v, 1e-9)
                lo = [int(x) for x in lo_c.split("(")[1].split(")")[0].split(",")]
                hi = [int(x) for x in hi_c.split("(")[1].split(")")[0].split(",")]
                return f"rgb({int(lo[0]+t*(hi[0]-lo[0]))},{int(lo[1]+t*(hi[1]-lo[1]))},{int(lo[2]+t*(hi[2]-lo[2]))})"
        return ACMAP[-1][1]

    fig = go.Figure()
    theta = np.linspace(0, 2 * np.pi, 100)

    # Nerve boundary rings
    for zoff in [0, nerve_len]:
        fig.add_trace(go.Scatter3d(
            x=sa*np.cos(theta), y=sb*np.sin(theta), z=np.full(100, zoff),
            mode="lines", line=dict(color="rgba(255,255,255,0.15)", width=2),
            showlegend=False, hoverinfo="skip"))

    # Contact patches as colored arcs on the cuff
    cuff_z = nerve_len / 2
    cuff_r = max(sa, sb) * 1.15
    if n_contacts > 0 and weights:
        arc_size = 2 * np.pi / n_contacts * 0.5  # 50% of pitch
        w_abs_max = max(abs(w) for w in weights) if weights else 1

        for ci in range(n_contacts):
            angle_center = 2 * np.pi * ci / n_contacts
            arc_theta = np.linspace(angle_center - arc_size/2, angle_center + arc_size/2, 30)

            w = weights[ci] if ci < len(weights) else 0
            # Color: green for cathode (negative), red for anode (positive), gray for ~zero
            if abs(w) < 0.01:
                color = "rgba(100,100,100,0.4)"
                width = 2
                label = f"C{ci}: inactive"
            elif w < 0:
                intensity = min(abs(w) / w_abs_max, 1)
                color = f"rgba(0,{int(150+105*intensity)},{int(100+55*intensity)},0.9)"
                width = 4 + 4 * intensity
                label = f"C{ci}: cathode ({w:.2f})"
            else:
                intensity = min(abs(w) / w_abs_max, 1)
                color = f"rgba({int(200+55*intensity)},{int(50+50*intensity)},50,0.9)"
                width = 4 + 4 * intensity
                label = f"C{ci}: anode ({w:.2f})"

            fig.add_trace(go.Scatter3d(
                x=cuff_r * np.cos(arc_theta),
                y=cuff_r * np.sin(arc_theta) * sb/sa,
                z=np.full(30, cuff_z),
                mode="lines", line=dict(color=color, width=width),
                name=label, showlegend=(ci < 8),  # limit legend entries
                hovertext=label, hoverinfo="text"))

    # Un-modeled fascicle outlines
    for fg in all_fascs:
        t = np.linspace(0, 2*np.pi, 20)
        r = fg["diameter_um"] / 2
        for zoff in [0, nerve_len]:
            fig.add_trace(go.Scatter3d(
                x=fg["y_um"]+r*np.cos(t), y=fg["z_um"]+r*np.sin(t),
                z=np.full(20, zoff), mode="lines",
                line=dict(color="rgba(80,80,90,0.25)", width=1),
                showlegend=False, hoverinfo="skip"))

    # Modeled fascicle cylinders with recruitment color
    for i in range(n_f):
        fd = ad["f"][str(i)]
        frac = fd["vm_r"] / max(fd["vm_t"], 1)
        color = frac_color(frac)
        r = fi[i]["d"] / 2
        cx, cy = fi[i]["y"], fi[i]["z"]

        t_mesh = np.linspace(0, 2*np.pi, 25)
        z_mesh = np.array([0, nerve_len])
        T, Z = np.meshgrid(t_mesh, z_mesh)
        fig.add_trace(go.Surface(
            x=cx+r*np.cos(T), y=cy+r*np.sin(T), z=Z,
            colorscale=[[0, color], [1, color]],
            surfacecolor=np.ones_like(Z), showscale=False, opacity=0.85,
            hoverinfo="text", text=f"F{fi[i]['orig_id']}: {frac*100:.0f}%"))

    # Colorbar
    fig.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None], mode="markers",
        marker=dict(size=0.1, color=[0], colorscale=ACMAP, cmin=0, cmax=1,
            showscale=True, colorbar=dict(
                title=dict(text="Myelinated<br>recruitment", side="right"),
                x=1.0, len=0.5, thickness=15,
                tickvals=[0,0.25,0.5,0.75,1], ticktext=["0%","25%","50%","75%","100%"])),
        showlegend=False, hoverinfo="skip"))

    fig.update_layout(template=TEMPLATE,
        title=dict(text=f"<b>{CONFIG_LABELS.get(cfg_name, cfg_name)} — 3D View</b><br>"
                        f"<sub>{n_contacts} contacts, {amp} μA (~{amp/1000:.1f} mA), "
                        f"optimal steering weights</sub>",
                   x=0.5, y=0.95),
        scene=dict(
            xaxis=dict(title="y (μm)", showgrid=False, showbackground=False,
                       range=[-sa*1.3, sa*1.3]),
            yaxis=dict(title="z (μm)", showgrid=False, showbackground=False,
                       range=[-sb*1.3, sb*1.3]),
            zaxis=dict(title="x (μm)", showgrid=False, showbackground=False,
                       range=[-200, nerve_len+200]),
            aspectmode="manual", aspectratio=dict(x=1.4, y=1, z=1),
            camera=dict(projection=dict(type="orthographic"),
                        eye=dict(x=1.8, y=1.2, z=0.6))),
        height=750, width=900,
        legend=dict(x=0.02, y=0.98, font=dict(size=10), bgcolor="rgba(0,0,0,0.4)"),
        margin=dict(t=80, b=10, l=10, r=10))

    out_dir = f"outputs/figures/electrode_{cfg_name}"
    os.makedirs(out_dir, exist_ok=True)
    fig.write_html(f"{out_dir}/bovine_3d.html")
    fig.write_image(f"{out_dir}/bovine_3d.png", scale=3)
    print(f"Saved: {out_dir}/bovine_3d.html + .png")


def load_geometry(path="data/bovine_geometry.json"):
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")

    configs = load_all_configs()
    print(f"Loaded {len(configs)} configs: {list(configs.keys())}")

    geom = load_geometry()
    prefix = "outputs/figures/electrode_comparison/comparison"
    os.makedirs("outputs/figures/electrode_comparison", exist_ok=True)

    plot_recruitment_comparison(configs, save_prefix=prefix)
    plot_heatmap_comparison(configs, save_prefix=prefix)
    plot_summary_table(configs, save_prefix=prefix)

    # 3D per config
    for cfg_name, cfg_data in configs.items():
        plot_3d_electrode(cfg_name, cfg_data, geom, prefix)

    print("All comparison plots done!")
