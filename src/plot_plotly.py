"""Plotly-based plots for bovine VNS results."""

import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path


def load_results(path):
    with open(path) as f:
        return json.load(f)


def load_geometry(path="data/bovine_geometry.json"):
    with open(path) as f:
        return json.load(f)


def load_grid(path):
    d = np.load(path, allow_pickle=True)
    return d["y"], d["z"], d["v"], float(d["semi_major"]), float(d["semi_minor"])


TEMPLATE = "plotly_dark"
COLORS = {"vm": "#4CAF50", "vu": "#2196F3", "s": "#FF5252", "si": "#FFB74D"}

ACTIVATION_CMAP = [
    [0.0, "rgb(20,10,40)"], [0.15, "rgb(70,10,110)"],
    [0.3, "rgb(130,20,100)"], [0.45, "rgb(190,50,60)"],
    [0.6, "rgb(230,110,20)"], [0.75, "rgb(250,180,20)"],
    [0.9, "rgb(255,230,50)"], [1.0, "rgb(255,255,140)"],
]

FASCICLE_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
    "#F7DC6F", "#BB8FCE", "#85C1E9", "#F1948A", "#82E0AA",
    "#F8C471", "#AED6F1", "#D7BDE2", "#A3E4D7", "#FAD7A0",
    "#D5F5E3", "#FADBD8", "#D6EAF8", "#E8DAEF", "#FCF3CF",
]


def frac_to_color(frac):
    for i in range(len(ACTIVATION_CMAP) - 1):
        lo_val, lo_rgb = ACTIVATION_CMAP[i]
        hi_val, hi_rgb = ACTIVATION_CMAP[i + 1]
        if frac <= hi_val:
            t = (frac - lo_val) / max(hi_val - lo_val, 1e-9)
            lo = [int(x) for x in lo_rgb.split("(")[1].split(")")[0].split(",")]
            hi = [int(x) for x in hi_rgb.split("(")[1].split(")")[0].split(",")]
            return f"rgb({int(lo[0]+t*(hi[0]-lo[0]))},{int(lo[1]+t*(hi[1]-lo[1]))},{int(lo[2]+t*(hi[2]-lo[2]))})"
    return ACTIVATION_CMAP[-1][1]


def ellipse_xy(sa, sb, n=200):
    theta = np.linspace(0, 2 * np.pi, n)
    return sa * np.cos(theta), sb * np.sin(theta)


def circle_xy(cx, cy, r, n=50):
    t = np.linspace(0, 2 * np.pi, n)
    return cx + r * np.cos(t), cy + r * np.sin(t)


# ============================================================
# ACTIVATION MAPS
# ============================================================
def plot_activation_maps(results, geom, save_prefix="outputs/figures/bovine"):
    fi = results["fi"]
    amps = results["amps"]
    amp_keys = sorted([int(k) for k in amps.keys()])
    sa, sb = geom["nerve"]["semi_major_um"], geom["nerve"]["semi_minor_um"]
    all_fascs = geom["vagal_fascicles"]
    n_f, n_a = len(fi), len(amp_keys)

    pick_idx = [min(2, n_a-1), n_a//2, min(n_a-2, n_a-1)]
    pick_amps = [amp_keys[i] for i in pick_idx]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[f"<b>{a} μA (~{a/1000:.1f} mA)</b>" for a in pick_amps],
        horizontal_spacing=0.07,
    )

    modeled_ids = set(f["orig_id"] for f in fi)
    ex, ey = ellipse_xy(sa, sb)

    for col, amp in enumerate(pick_amps, 1):
        ad = amps[str(amp)]
        fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines",
            line=dict(color="rgba(255,255,255,0.5)", width=2),
            showlegend=False, hoverinfo="skip"), row=1, col=col)

        for fg in all_fascs:
            if fg["id"] not in modeled_ids:
                cx, cy = circle_xy(fg["y_um"], fg["z_um"], fg["diameter_um"]/2, 40)
                fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines", fill="toself",
                    fillcolor="rgba(60,60,70,0.4)",
                    line=dict(color="rgba(100,100,110,0.4)", width=0.5),
                    showlegend=False, hoverinfo="skip"), row=1, col=col)

        for i in range(n_f):
            fd = ad["f"][str(i)]
            frac = fd["vm_r"] / max(fd["vm_t"], 1)
            is_extrap = fi[i].get("source") == "extrapolated"
            color = frac_to_color(frac)
            cx, cy = circle_xy(fi[i]["y"], fi[i]["z"], fi[i]["d"]/2, 50)
            fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines", fill="toself",
                fillcolor=color,
                line=dict(color="rgba(255,255,255,0.8)" if not is_extrap else "rgba(255,255,255,0.3)",
                          width=1.5 if not is_extrap else 0.8),
                showlegend=False,
                hovertext=f"F{fi[i]['orig_id']}: {frac*100:.0f}% recruited",
                hoverinfo="text"), row=1, col=col)

        s = ad["sum"]
        fig.add_annotation(text=f"Vm: {s['vm']}  |  Vu: {s['vu']}  |  S: {s['s']}",
            xref=f"x{col}", yref=f"y{col}", x=0, y=-sb*1.3, showarrow=False,
            font=dict(size=10, color="rgba(255,255,255,0.6)"))

    # Colorbar via visible scatter with tiny markers placed off-screen
    cb_vals = np.linspace(0, 1, 50)
    fig.add_trace(go.Scatter(
        x=[sa * 2] * 50, y=np.linspace(-sb, sb, 50),
        mode="markers", marker=dict(size=0.1, color=cb_vals,
            colorscale=ACTIVATION_CMAP, cmin=0, cmax=1, showscale=True,
            colorbar=dict(title=dict(text="Myelinated<br>recruitment", side="right"),
                x=1.02, len=0.7, yanchor="middle", y=0.5, thickness=15,
                tickvals=[0,0.25,0.5,0.75,1], ticktext=["0%","25%","50%","75%","100%"])),
        showlegend=False, hoverinfo="skip",
    ), row=1, col=3)

    for col in range(1, 4):
        fig.update_xaxes(range=[-sa*1.3, sa*1.3], scaleanchor=f"y{col}",
            showgrid=False, zeroline=False, row=1, col=col)
        fig.update_yaxes(range=[-sb*1.5, sb*1.5], showgrid=False, zeroline=False,
            row=1, col=col)

    fig.update_layout(template=TEMPLATE,
        title=dict(text=f"<b>Bovine Vagosympathetic Trunk — Activation Maps</b><br>"
                        f"<sub>{n_f} fascicles, bipolar cuff, 200μs pulse</sub>", x=0.5, y=0.96),
        height=620, width=1500, showlegend=False,
        margin=dict(t=110, b=80, l=60, r=110))
    fig.write_html(f"{save_prefix}_activation_maps.html")
    fig.write_image(f"{save_prefix}_activation_maps.png", scale=3)
    print(f"Saved: {save_prefix}_activation_maps.html + .png")


# ============================================================
# RECRUITMENT CURVES
# ============================================================
def plot_recruitment(results, geom, save_prefix="outputs/figures/bovine"):
    fi = results["fi"]
    amps = results["amps"]
    amp_keys = sorted([int(k) for k in amps.keys()])
    amps_mA = [a / 1000 for a in amp_keys]
    n_f = len(fi)

    fig = make_subplots(rows=1, cols=3,
        subplot_titles=["<b>Vagal Myelinated (per fascicle)</b>",
                        "<b>Fiber-Type Selectivity</b>",
                        "<b>Selectivity Index</b>"],
        horizontal_spacing=0.08)

    # Panel 1
    diams = [fi[i]["d"] for i in range(n_f) if fi[i].get("source") != "missing"]
    d_min, d_max = min(diams), max(diams)
    for i in range(n_f):
        if fi[i].get("source") == "missing":
            continue
        pcts = [amps[str(a)]["f"][str(i)]["vm_r"] / max(amps[str(a)]["f"][str(i)]["vm_t"], 1) * 100
                for a in amp_keys]
        is_first = (i == 0)
        # Rainbow color based on position in the set
        hue = int(i * 360 / max(n_f, 1))
        fig.add_trace(go.Scatter(x=amps_mA, y=pcts, mode="lines",
            line=dict(color=f"hsl({hue},80%,65%)", width=2),
            name=f"Individual fascicles ({d_min}–{d_max} μm, n={len(diams)})" if is_first else None,
            showlegend=is_first,
            legendgroup="fascicles",
            hovertext=f"F{fi[i]['orig_id']} ({fi[i]['d']}μm)",
            hoverinfo="text+y",
            legend="legend"), row=1, col=1)

    # Panel 2
    vm_pct, vu_pct, s_pct = [], [], []
    for a in amp_keys:
        sd = amps[str(a)]["sum"]
        vm_n, vm_d = map(int, sd["vm"].split("/"))
        vu_n, vu_d = map(int, sd["vu"].split("/"))
        s_n, s_d = map(int, sd["s"].split("/"))
        vm_pct.append(vm_n / max(vm_d, 1) * 100)
        vu_pct.append(vu_n / max(vu_d, 1) * 100)
        s_pct.append(s_n / max(s_d, 1) * 100)

    fig.add_trace(go.Scatter(x=amps_mA, y=vm_pct, mode="lines+markers",
        line=dict(color=COLORS["vm"], width=3.5), marker=dict(size=6),
        name="Vagal myelinated (A/B)", legend="legend2"), row=1, col=2)
    fig.add_trace(go.Scatter(x=amps_mA, y=vu_pct, mode="lines+markers",
        line=dict(color=COLORS["vu"], width=3.5), marker=dict(size=6),
        name="Vagal unmyelinated (C)", legend="legend2"), row=1, col=2)
    fig.add_trace(go.Scatter(x=amps_mA, y=s_pct, mode="lines+markers",
        line=dict(color=COLORS["s"], width=3.5), marker=dict(size=6),
        name="Sympathetic (unmyelinated)", legend="legend2"), row=1, col=2)

    for j in range(len(amp_keys) - 1):
        if vm_pct[j] > 50 and s_pct[j] < 20:
            fig.add_vrect(x0=amps_mA[j], x1=amps_mA[j+1],
                fillcolor=COLORS["vm"], opacity=0.08, line_width=0, row=1, col=2)

    # Annotation: explain flat C-fiber lines
    fig.add_annotation(x=0.95, y=0.35, xref="x2 domain", yref="y2 domain",
        text="Unmyelinated fibers have<br>significantly higher activation<br>thresholds (typically >2 mA)",
        showarrow=False, font=dict(size=9, color="rgba(255,255,255,0.45)"),
        xanchor="right", yanchor="middle")

    # Panel 3
    si = [vm_pct[j]/100 - max(s_pct[j]/100, vu_pct[j]/100) for j in range(len(amp_keys))]
    fig.add_trace(go.Scatter(x=amps_mA, y=si, mode="lines+markers",
        line=dict(color=COLORS["si"], width=3.5), marker=dict(size=6),
        name="SI", showlegend=False), row=1, col=3)
    best = int(np.argmax(si))
    fig.add_annotation(x=0.95, y=0.15,
        xref="x3 domain", yref="y3 domain",
        text=f"<b>Best SI = {si[best]:.2f}</b><br>at {amps_mA[best]:.2f} mA",
        showarrow=False,
        font=dict(color=COLORS["si"], size=12), bgcolor="rgba(0,0,0,0.7)",
        borderpad=6, bordercolor=COLORS["si"], borderwidth=1,
        xanchor="right", yanchor="bottom")
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)", row=1, col=3)

    for col in range(1, 4):
        fig.update_xaxes(title_text="Current (mA)", row=1, col=col)
    fig.update_yaxes(title_text="% Recruited", range=[-5, 105], row=1, col=1)
    fig.update_yaxes(title_text="% Recruited", range=[-5, 105], row=1, col=2)
    fig.update_yaxes(title_text="SI", range=[-0.5, 1.1], row=1, col=3)

    fig.update_layout(template=TEMPLATE,
        title=dict(text=f"<b>Bovine Vagosympathetic Trunk — Recruitment Analysis</b><br>"
                        f"<sub>{n_f} fascicles, bipolar cuff, mixed vagal/sympathetic</sub>",
                   x=0.5, y=0.97),
        height=580, width=1500,
        # Two-column legend under panel 1
        legend=dict(orientation="h", yanchor="top", y=-0.13,
            xanchor="left", x=0.0,
            font=dict(size=10), bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
        legend2=dict(orientation="h", yanchor="top", y=-0.13,
            xanchor="right", x=0.65,
            font=dict(size=10), bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
        margin=dict(t=100, b=130, l=60, r=40))
    fig.write_html(f"{save_prefix}_recruitment.html")
    fig.write_image(f"{save_prefix}_recruitment.png", scale=3)
    print(f"Saved: {save_prefix}_recruitment.html + .png")


# ============================================================
# RECRUITMENT — individual standalone panels
# ============================================================
def plot_recruitment_panels(results, geom, save_prefix="outputs/figures/bovine"):
    fi = results["fi"]
    amps = results["amps"]
    amp_keys = sorted([int(k) for k in amps.keys()])
    amps_mA = [a / 1000 for a in amp_keys]
    n_f = len(fi)

    diams = [fi[i]["d"] for i in range(n_f) if fi[i].get("source") != "missing"]
    d_min, d_max = min(diams), max(diams)

    vm_pct, vu_pct, s_pct = [], [], []
    for a in amp_keys:
        sd = amps[str(a)]["sum"]
        vm_n, vm_d = map(int, sd["vm"].split("/"))
        vu_n, vu_d = map(int, sd["vu"].split("/"))
        s_n, s_d = map(int, sd["s"].split("/"))
        vm_pct.append(vm_n / max(vm_d, 1) * 100)
        vu_pct.append(vu_n / max(vu_d, 1) * 100)
        s_pct.append(s_n / max(s_d, 1) * 100)

    # Panel 1: Per-fascicle myelinated
    fig1 = go.Figure()
    for i in range(n_f):
        if fi[i].get("source") == "missing":
            continue
        pcts = [amps[str(a)]["f"][str(i)]["vm_r"] / max(amps[str(a)]["f"][str(i)]["vm_t"], 1) * 100
                for a in amp_keys]
        hue = int(i * 360 / max(n_f, 1))
        is_first = (i == 0)
        fig1.add_trace(go.Scatter(x=amps_mA, y=pcts, mode="lines",
            line=dict(color=f"hsl({hue},80%,65%)", width=2),
            name=f"Individual fascicles ({d_min}–{d_max} μm, n={len(diams)})" if is_first else None,
            showlegend=is_first, legendgroup="fascicles",
            hovertext=f"F{fi[i]['orig_id']} ({fi[i]['d']}μm)", hoverinfo="text+y"))
    fig1.update_layout(template=TEMPLATE,
        title=dict(text="<b>Vagal Myelinated Recruitment (per fascicle)</b>", x=0.5),
        xaxis=dict(title="Current (mA)"),
        yaxis=dict(title="% Recruited", range=[-5, 105]),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(size=10)),
        height=500, width=650, margin=dict(t=60, b=90, l=60, r=30))
    fig1.write_html(f"{save_prefix}_recruitment_fascicles.html")
    fig1.write_image(f"{save_prefix}_recruitment_fascicles.png", scale=3)
    print(f"Saved: {save_prefix}_recruitment_fascicles.html + .png")

    # Panel 2: Fiber-type selectivity
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=amps_mA, y=vm_pct, mode="lines+markers",
        line=dict(color=COLORS["vm"], width=3.5), marker=dict(size=6),
        name="Vagal myelinated (A/B)"))
    fig2.add_trace(go.Scatter(x=amps_mA, y=vu_pct, mode="lines+markers",
        line=dict(color=COLORS["vu"], width=3.5), marker=dict(size=6),
        name="Vagal unmyelinated (C)"))
    fig2.add_trace(go.Scatter(x=amps_mA, y=s_pct, mode="lines+markers",
        line=dict(color=COLORS["s"], width=3.5), marker=dict(size=6),
        name="Sympathetic (unmyelinated)"))
    for j in range(len(amp_keys) - 1):
        if vm_pct[j] > 50 and s_pct[j] < 20:
            fig2.add_vrect(x0=amps_mA[j], x1=amps_mA[j+1],
                fillcolor=COLORS["vm"], opacity=0.08, line_width=0)
    fig2.add_annotation(x=0.95, y=0.35, xref="paper", yref="paper",
        text="Unmyelinated fibers have<br>significantly higher activation<br>thresholds (typically >2 mA)",
        showarrow=False, font=dict(size=9, color="rgba(255,255,255,0.45)"),
        xanchor="right", yanchor="middle")
    fig2.update_layout(template=TEMPLATE,
        title=dict(text="<b>Fiber-Type Selectivity</b>", x=0.5),
        xaxis=dict(title="Current (mA)"),
        yaxis=dict(title="% Recruited", range=[-5, 105]),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(size=10)),
        height=500, width=650, margin=dict(t=60, b=90, l=60, r=30))
    fig2.write_html(f"{save_prefix}_recruitment_selectivity.html")
    fig2.write_image(f"{save_prefix}_recruitment_selectivity.png", scale=3)
    print(f"Saved: {save_prefix}_recruitment_selectivity.html + .png")

    # Panel 3: Selectivity index
    fig3 = go.Figure()
    si = [vm_pct[j]/100 - max(s_pct[j]/100, vu_pct[j]/100) for j in range(len(amp_keys))]
    fig3.add_trace(go.Scatter(x=amps_mA, y=si, mode="lines+markers",
        line=dict(color=COLORS["si"], width=3.5), marker=dict(size=6),
        name="Selectivity Index"))
    fig3.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    best = int(np.argmax(si))
    fig3.add_annotation(x=0.95, y=0.15, xref="paper", yref="paper",
        text=f"<b>Best SI = {si[best]:.2f}</b><br>at ~{amps_mA[best]:.2f} mA",
        showarrow=False, font=dict(color=COLORS["si"], size=12),
        bgcolor="rgba(0,0,0,0.7)", borderpad=6,
        bordercolor=COLORS["si"], borderwidth=1,
        xanchor="right", yanchor="bottom")
    fig3.update_layout(template=TEMPLATE,
        title=dict(text="<b>Selectivity Index</b>", x=0.5),
        xaxis=dict(title="Current (mA)"),
        yaxis=dict(title="SI = (vagal myel %) − max(unmyel %, symp %)", range=[-0.5, 1.1]),
        height=500, width=650, margin=dict(t=60, b=60, l=60, r=30),
        showlegend=False)
    fig3.write_html(f"{save_prefix}_recruitment_si.html")
    fig3.write_image(f"{save_prefix}_recruitment_si.png", scale=3)
    print(f"Saved: {save_prefix}_recruitment_si.html + .png")


# ============================================================
# HEATMAP — mask outside nerve boundary
# ============================================================
def plot_heatmap(grid_path, geom, results=None, save_prefix="outputs/figures/bovine"):
    y, z, v, sa, sb = load_grid(grid_path)
    all_fascs = geom["vagal_fascicles"]

    # Mask voltage outside nerve boundary
    yy, zz = np.meshgrid(y, z)
    inside = (yy / sa) ** 2 + (zz / sb) ** 2 <= 1.0
    v_masked = np.where(inside, v, np.nan)

    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=v_masked, x=y, y=z,
        colorscale="Inferno", zsmooth="best",
        colorbar=dict(title=dict(text="V at 1 mA", side="right"), x=1.02, thickness=15),
        hovertemplate="y: %{x:.0f} μm<br>z: %{y:.0f} μm<br>V: %{z:.4f}<extra></extra>"))

    ex, ey = ellipse_xy(sa, sb)
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines",
        line=dict(color="rgba(255,255,255,0.7)", width=2.5),
        showlegend=False, hoverinfo="skip"))

    modeled_ids = set()
    if results:
        modeled_ids = set(f["orig_id"] for f in results["fi"] if f.get("source", "fem") == "fem")

    shown_legend = {"fem": False, "other": False}
    for fg in all_fascs:
        cx, cy = circle_xy(fg["y_um"], fg["z_um"], fg["diameter_um"]/2, 80)
        is_fem = fg["id"] in modeled_ids
        show = False
        if is_fem and not shown_legend["fem"]:
            show = True
            shown_legend["fem"] = True
        elif not is_fem and not shown_legend["other"]:
            show = True
            shown_legend["other"] = True
        fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines",
            line=dict(
                color="rgba(100,255,100,1)" if is_fem else "rgba(220,220,230,1)",
                width=2.5 if is_fem else 1.2,
            ),
            name="FEM-modeled" if is_fem else "Not modeled",
            showlegend=show,
            legendgroup="fem" if is_fem else "other",
            hovertext=f"F{fg['id']} ({fg['diameter_um']:.0f}μm)" + (" [FEM]" if is_fem else ""),
            hoverinfo="text"))

    fig.update_layout(template=TEMPLATE,
        title=dict(text="<b>Bovine Vagosympathetic Trunk — FEM Voltage Field</b><br>"
                        "<sub>Cross-section at cuff center, bipolar electrode, 1 mA</sub>",
                   x=0.5, y=0.97),
        xaxis=dict(title="y (μm)", scaleanchor="y", showgrid=False,
                   range=[-sa*1.15, sa*1.15]),
        yaxis=dict(title="z (μm)", showgrid=False, range=[-sb*1.15, sb*1.15]),
        height=700, width=850, margin=dict(t=100, b=60, l=60, r=100),
        legend=dict(x=0.01, y=0.01, yanchor="bottom", xanchor="left",
            font=dict(size=10), bgcolor="rgba(0,0,0,0.5)",
            bordercolor="rgba(255,255,255,0.2)", borderwidth=1))
    fig.write_html(f"{save_prefix}_heatmap.html")
    fig.write_image(f"{save_prefix}_heatmap.png", scale=3)
    print(f"Saved: {save_prefix}_heatmap.html + .png")


# ============================================================
# 3D NERVE with colorbar + cuff electrodes + tight framing
# ============================================================
def plot_3d_nerve(results, geom, amp_idx=None, save_prefix="outputs/figures/bovine"):
    fi = results["fi"]
    amps = results["amps"]
    amp_keys = sorted([int(k) for k in amps.keys()])
    if amp_idx is None:
        amp_idx = len(amp_keys) // 3  # lower amplitude shows gradient better
    amp = amp_keys[amp_idx]
    ad = amps[str(amp)]

    sa, sb = geom["nerve"]["semi_major_um"], geom["nerve"]["semi_minor_um"]
    all_fascs = geom["vagal_fascicles"]
    modeled_ids = set(f["orig_id"] for f in fi)
    n_f = len(fi)
    nerve_len = 3000

    fig = go.Figure()

    # Nerve boundary rings
    theta = np.linspace(0, 2 * np.pi, 100)
    for zoff in [0, nerve_len]:
        fig.add_trace(go.Scatter3d(
            x=sa*np.cos(theta), y=sb*np.sin(theta), z=np.full(100, zoff),
            mode="lines", line=dict(color="rgba(255,255,255,0.2)", width=2),
            showlegend=False, hoverinfo="skip"))

    # Cuff electrode ring (single contact, distant ground model)
    cuff_z = nerve_len / 2
    cuff_r = max(sa, sb) * 1.15
    fig.add_trace(go.Scatter3d(
        x=cuff_r*np.cos(theta), y=cuff_r*np.sin(theta)*sb/sa,
        z=np.full(100, cuff_z),
        mode="lines", line=dict(color="#FF5252", width=5),
        name="Cathode (distant ground)", showlegend=True,
        hovertext="Cathode ring", hoverinfo="text"))
    fig.add_trace(go.Scatter3d(
        x=cuff_r*1.02*np.cos(theta), y=cuff_r*1.02*np.sin(theta)*sb/sa,
        z=np.full(100, cuff_z),
        mode="lines", line=dict(color="#FF5252", width=2, dash="dot"),
        showlegend=False, hoverinfo="skip"))

    # Un-modeled fascicles
    for fg in all_fascs:
        if fg["id"] not in modeled_ids:
            t = np.linspace(0, 2*np.pi, 20)
            r = fg["diameter_um"] / 2
            for zoff in [0, nerve_len]:
                fig.add_trace(go.Scatter3d(
                    x=fg["y_um"]+r*np.cos(t), y=fg["z_um"]+r*np.sin(t),
                    z=np.full(20, zoff), mode="lines",
                    line=dict(color="rgba(80,80,90,0.3)", width=1),
                    showlegend=False, hoverinfo="skip"))

    # Modeled fascicle cylinders with activation color
    fracs = []
    for i in range(n_f):
        fd = ad["f"][str(i)]
        frac = fd["vm_r"] / max(fd["vm_t"], 1)
        fracs.append(frac)
        color = frac_to_color(frac)

        r = fi[i]["d"] / 2
        cx, cy = fi[i]["y"], fi[i]["z"]

        # Cylinder surface
        t_mesh = np.linspace(0, 2*np.pi, 25)
        z_mesh = np.array([0, nerve_len])
        T, Z = np.meshgrid(t_mesh, z_mesh)
        fig.add_trace(go.Surface(
            x=cx+r*np.cos(T), y=cy+r*np.sin(T), z=Z,
            colorscale=[[0, color], [1, color]],
            surfacecolor=np.ones_like(Z), showscale=False, opacity=0.9,
            hoverinfo="text",
            text=f"F{fi[i]['orig_id']}: {frac*100:.0f}%"))

        # End caps
        for zoff in [0, nerve_len]:
            fig.add_trace(go.Scatter3d(
                x=cx+r*np.cos(np.linspace(0,2*np.pi,30)),
                y=cy+r*np.sin(np.linspace(0,2*np.pi,30)),
                z=np.full(30, zoff), mode="lines",
                line=dict(color="white", width=1.5),
                showlegend=False, hoverinfo="skip"))

    # Colorbar via dummy scatter with marker color
    fig.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None], mode="markers",
        marker=dict(size=0.1, color=[0], colorscale=ACTIVATION_CMAP,
            cmin=0, cmax=1, showscale=True,
            colorbar=dict(title=dict(text="Myelinated<br>recruitment", side="right"),
                x=1.0, len=0.6, thickness=15,
                tickvals=[0,0.25,0.5,0.75,1],
                ticktext=["0%","25%","50%","75%","100%"])),
        showlegend=False, hoverinfo="skip"))

    fig.update_layout(template=TEMPLATE,
        title=dict(text=f"<b>Bovine Vagosympathetic Trunk — 3D View</b><br>"
                        f"<sub>{n_f} fascicles, {amp} μA (~{amp/1000:.1f} mA), cuff electrode, distant ground</sub>",
                   x=0.5, y=0.95),
        scene=dict(
            xaxis=dict(title="y (μm)", showgrid=False, showbackground=False,
                       range=[-sa*1.3, sa*1.3]),
            yaxis=dict(title="z (μm)", showgrid=False, showbackground=False,
                       range=[-sb*1.3, sb*1.3]),
            zaxis=dict(title="x (μm)", showgrid=False, showbackground=False,
                       range=[-200, nerve_len+200]),
            aspectmode="manual",
            aspectratio=dict(x=1.4, y=1, z=1),
            camera=dict(projection=dict(type="orthographic"),
                        eye=dict(x=1.8, y=1.2, z=0.6))),
        height=750, width=950,
        legend=dict(x=0.02, y=0.98, font=dict(size=11),
                    bgcolor="rgba(0,0,0,0.4)"),
        margin=dict(t=80, b=10, l=10, r=10))
    fig.write_html(f"{save_prefix}_3d.html")
    fig.write_image(f"{save_prefix}_3d.png", scale=3)
    print(f"Saved: {save_prefix}_3d.html + .png")


if __name__ == "__main__":
    results_path = sys.argv[1] if len(sys.argv) > 1 else "bovine_6_pure_results.json"
    results = load_results(results_path)
    geom = load_geometry()

    # Create per-run subdir based on results filename
    run_name = Path(results_path).stem.replace("_results", "")
    out_dir = f"outputs/figures/{run_name}"
    os.makedirs(out_dir, exist_ok=True)
    prefix = f"{out_dir}/bovine"

    plot_activation_maps(results, geom, save_prefix=prefix)
    plot_recruitment(results, geom, save_prefix=prefix)
    plot_recruitment_panels(results, geom, save_prefix=prefix)
    plot_3d_nerve(results, geom, save_prefix=prefix)

    results_dir = str(Path(results_path).parent)
    grid_candidates = [
        results_path.replace("results.json", "grid.npz"),
        f"{results_dir}/grid.npz",
        "bovine_6_pure_grid.npz",
        "bovine_6_mixed_grid.npz",
    ]
    for gp in grid_candidates:
        if Path(gp).exists():
            plot_heatmap(gp, geom, results, save_prefix=prefix)
            break

    print(f"All plots saved to {out_dir}/")
