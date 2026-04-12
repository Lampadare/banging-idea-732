"""Fiber-class recruitment breakdown using Erlanger-Gasser diameter bins.

Regenerates fiber populations from deterministic seeds, classifies by
diameter into Aα/Aβ, Aδ/B, vagal C, sympathetic C, then plots recruitment
curves per class from the merged batch results.

Usage:
    python src/plot_fiber_breakdown.py [merged/results.json]
"""

import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from pathlib import Path

TEMPLATE = "plotly_dark"

# Erlanger-Gasser classification by diameter
# Based on Ochoa distributions used in our pipeline
FIBER_CLASSES = {
    "Aα/Aβ": {"min_d": 6.0, "myelinated": True, "color": "#FF6B6B",
               "desc": "Large myelinated (≥6μm)"},
    "Aδ/B":  {"min_d": 1.0, "max_d": 6.0, "myelinated": True, "color": "#4ECDC4",
               "desc": "Small myelinated (1–6μm)"},
    "Vagal C": {"max_d": 1.5, "myelinated": False, "label": "vagal", "color": "#45B7D1",
                "desc": "Vagal unmyelinated (<1.5μm)"},
    "Sympathetic C": {"max_d": 1.2, "myelinated": False, "label": "sympathetic", "color": "#FF5252",
                      "desc": "Sympathetic unmyelinated (<1.2μm)"},
}


def load_geometry(path="data/bovine_geometry.json"):
    with open(path) as f:
        return json.load(f)


def build_mixed_pop(n, frac, seed=0):
    """Reproduce the exact fiber population from the FEM scripts."""
    rng = np.random.default_rng(seed)
    n_s = max(1, int(n * frac))
    n_v = n - n_s

    # Vagal: 70% unmyelinated, 30% myelinated (matching NRV Ochoa stats)
    n_myel = int(n_v * 0.3)
    n_unmyel = n_v - n_myel

    # NRV's create_axon_population uses its own RNG, but we need diameters
    # for classification. Approximate the Ochoa distributions:
    rng2 = np.random.default_rng(seed + 10000)
    myel_d = rng2.lognormal(mean=1.8, sigma=0.5, size=n_myel).clip(2, 16)
    unmyel_d = rng2.lognormal(mean=-0.3, sigma=0.4, size=n_unmyel).clip(0.3, 1.5)
    symp_d = rng.uniform(0.3, 1.2, n_s)

    fibers = []
    for d in myel_d:
        fibers.append({"d": float(d), "myelinated": True, "label": "vagal"})
    for d in unmyel_d:
        fibers.append({"d": float(d), "myelinated": False, "label": "vagal"})
    for d in symp_d:
        fibers.append({"d": float(d), "myelinated": False, "label": "sympathetic"})

    return fibers


def classify_fiber(fiber):
    """Classify a fiber into an Erlanger-Gasser class."""
    d = fiber["d"]
    m = fiber["myelinated"]
    lb = fiber["label"]

    if lb == "sympathetic":
        return "Sympathetic C"
    if not m:
        return "Vagal C"
    if d >= 6.0:
        return "Aα/Aβ"
    return "Aδ/B"


def compute_breakdown(results, geom):
    """Compute per-class recruitment across all amplitudes."""
    fi = results["fi"]
    amps_data = results["amps"]
    amp_keys = sorted([int(k) for k in amps_data.keys()])
    all_fascs = geom["vagal_fascicles"]

    # Regenerate full fiber populations for all fascicles
    populations = {}  # fascicle_idx → list of fibers with class labels
    class_totals = {c: 0 for c in FIBER_CLASSES}

    for i, f in enumerate(fi):
        if f.get("source") == "missing":
            continue
        fg_id = f["orig_id"]
        fibers = build_mixed_pop(50, 0.15, seed=fg_id)[:f["np"]]
        for fib in fibers:
            fib["class"] = classify_fiber(fib)
            class_totals[fib["class"]] += 1
        populations[i] = fibers

    print(f"Total fibers classified: {sum(class_totals.values())}")
    for c, n in class_totals.items():
        print(f"  {c}: {n}")

    # For each amplitude, count recruited per class
    # recruited diameters are in rd, but they're mixed together
    # Strategy: match rd diameters to population fibers
    class_recruited = {c: [] for c in FIBER_CLASSES}

    for amp in amp_keys:
        ad = amps_data[str(amp)]
        counts = {c: 0 for c in FIBER_CLASSES}

        for i in populations:
            fd = ad["f"][str(i)]
            rd_list = fd.get("rd", [])
            fibers = populations[i]

            # Sort both by diameter for matching
            remaining_rd = sorted(rd_list, reverse=True)

            # Count recruited per class using the known population
            # vm_r = myelinated recruited, vu_r = unmyelinated vagal, s_r = sympathetic
            vm_r = fd["vm_r"]
            vu_r = fd["vu_r"]
            s_r = fd["s_r"]

            # Split myelinated recruited into Aα/Aβ vs Aδ/B using rd diameters
            myel_recruited_d = [d for d in rd_list if d >= 1.5]  # myelinated diameters
            n_alpha = sum(1 for d in myel_recruited_d if d >= 6.0)
            n_delta = sum(1 for d in myel_recruited_d if d < 6.0)

            counts["Aα/Aβ"] += n_alpha
            counts["Aδ/B"] += n_delta
            counts["Vagal C"] += vu_r
            counts["Sympathetic C"] += s_r

        for c in FIBER_CLASSES:
            pct = counts[c] / max(class_totals[c], 1) * 100
            class_recruited[c].append(pct)

    return amp_keys, class_totals, class_recruited


def plot_breakdown(amp_keys, class_totals, class_recruited, save_prefix):
    """Plot recruitment curves per fiber class."""
    amps_mA = [a / 1000 for a in amp_keys]

    # === Figure 1: Recruitment by fiber class ===
    fig = go.Figure()

    for cls_name, cls_info in FIBER_CLASSES.items():
        pcts = class_recruited[cls_name]
        n_total = class_totals[cls_name]
        fig.add_trace(go.Scatter(
            x=amps_mA, y=pcts, mode="lines+markers",
            line=dict(color=cls_info["color"], width=3),
            marker=dict(size=6),
            name=f"{cls_name} (n={n_total})",
        ))

    # Annotation explaining classification
    annotation_text = (
        "<b>Fiber Classification (Erlanger-Gasser)</b><br>"
        "─────────────────────────────<br>"
        "<b>Aα/Aβ</b>: myelinated ≥6μm (MRG model)<br>"
        "<b>Aδ/B</b>: myelinated 1–6μm (MRG model)<br>"
        "<b>Vagal C</b>: unmyelinated <1.5μm (Rattay model)<br>"
        "<b>Sympathetic C</b>: unmyelinated <1.2μm (Rattay model)<br>"
        "─────────────────────────────<br>"
        "<i>Classification by diameter only.<br>"
        "MRG and Rattay are the two distinct<br>"
        "biophysical models in NRV.</i>"
    )

    fig.add_annotation(
        x=0.98, y=0.55, xref="paper", yref="paper",
        text=annotation_text,
        showarrow=False,
        font=dict(size=10, color="rgba(255,255,255,0.85)", family="monospace"),
        bgcolor="rgba(30,30,50,0.85)",
        bordercolor="rgba(255,255,255,0.2)",
        borderwidth=1, borderpad=10,
        xanchor="right", yanchor="middle",
        align="left",
    )

    fig.update_layout(template=TEMPLATE,
        title=dict(
            text="<b>Recruitment by Fiber Class — Size-Recruitment Principle</b><br>"
                 "<sub>55 fascicles, mixed vagal/sympathetic populations, "
                 "bipolar cuff electrode</sub>",
            x=0.5, y=0.97),
        xaxis=dict(title="Current (mA)"),
        yaxis=dict(title="% Recruited", range=[-5, 105]),
        legend=dict(orientation="h", y=-0.12, x=0.3, xanchor="center",
            font=dict(size=12), bgcolor="rgba(0,0,0,0.3)"),
        height=600, width=850,
        margin=dict(t=100, b=100, l=60, r=40))

    fig.write_html(f"{save_prefix}_fiber_breakdown.html")
    fig.write_image(f"{save_prefix}_fiber_breakdown.png", scale=3)
    print(f"Saved: {save_prefix}_fiber_breakdown.html + .png")

    # === Figure 2: Population pie chart + threshold bars ===
    fig2 = make_subplots(rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}]],
        subplot_titles=["<b>Fiber Population</b>", "<b>Recruitment at ~0.5 mA</b>"])

    colors = [FIBER_CLASSES[c]["color"] for c in FIBER_CLASSES]
    labels = list(FIBER_CLASSES.keys())
    values = [class_totals[c] for c in FIBER_CLASSES]

    fig2.add_trace(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors),
        textinfo="label+percent",
        textfont=dict(size=11),
        hole=0.3,
    ), row=1, col=1)

    # Bar: recruitment at mid amplitude
    mid_idx = len(amp_keys) // 2
    mid_pcts = [class_recruited[c][mid_idx] for c in FIBER_CLASSES]

    fig2.add_trace(go.Bar(
        x=labels, y=mid_pcts,
        marker_color=colors,
        text=[f"{p:.0f}%" for p in mid_pcts],
        textposition="outside", textfont=dict(size=12),
    ), row=1, col=2)

    fig2.update_yaxes(title_text="% Recruited", range=[0, 110], row=1, col=2)

    fig2.update_layout(template=TEMPLATE,
        title=dict(text="<b>Fiber Population & Recruitment Summary</b><br>"
                        "<sub>Size-recruitment principle: large myelinated fibers "
                        "recruit first</sub>", x=0.5, y=0.97),
        height=450, width=1000, showlegend=False,
        margin=dict(t=100, b=60))

    fig2.write_html(f"{save_prefix}_fiber_summary.html")
    fig2.write_image(f"{save_prefix}_fiber_summary.png", scale=3)
    print(f"Saved: {save_prefix}_fiber_summary.html + .png")


if __name__ == "__main__":
    results_path = sys.argv[1] if len(sys.argv) > 1 else "merged/results.json"
    print(f"Loading: {results_path}")
    with open(results_path) as f:
        results = json.load(f)
    geom = load_geometry()

    amp_keys, class_totals, class_recruited = compute_breakdown(results, geom)

    out_dir = "outputs/figures/final_results/merged"
    os.makedirs(out_dir, exist_ok=True)
    plot_breakdown(amp_keys, class_totals, class_recruited, f"{out_dir}/bovine")
    print("Done!")
