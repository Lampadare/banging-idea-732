"""Plot bovine FEM results — activation maps, recruitment curves, voltage heatmap."""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import os
import sys

plt.style.use("dark_background")


def load_results(path):
    with open(path) as f:
        return json.load(f)


def load_geometry(path="data/bovine_geometry.json"):
    with open(path) as f:
        return json.load(f)


def load_grid(path):
    d = np.load(path)
    return d["y"], d["z"], d["v"], float(d["semi_major"]), float(d["semi_minor"])


def plot_all(results, geom, save_prefix="outputs/figures/bovine"):
    fi = results["fi"]
    amps = results["amps"]
    amp_keys = sorted([int(k) for k in amps.keys()])

    sa = geom["nerve"]["semi_major_um"]
    sb = geom["nerve"]["semi_minor_um"]
    all_fascs = geom["vagal_fascicles"]
    theta = np.linspace(0, 2 * np.pi, 200)

    n_f = len(fi)

    # === Figure 1: Cross-section activation maps at 3 amplitudes ===
    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    n_amps = len(amp_keys)
    pick_idx = [min(2, n_amps-1), min(9, n_amps-1), min(17, n_amps-1)]
    pick_amps = [amp_keys[i] for i in pick_idx]

    for ax_idx, amp in enumerate(pick_amps):
        ax = axes[ax_idx]
        ax.plot(sa * np.cos(theta), sb * np.sin(theta), "w-", linewidth=2)

        ad = amps[str(amp)]

        # Draw ALL fascicles colored by recruitment
        modeled_ids = set(f["orig_id"] for f in fi)
        for fg in all_fascs:
            if fg["id"] not in modeled_ids:
                c = plt.Circle((fg["y_um"], fg["z_um"]), fg["diameter_um"] / 2,
                               fill=True, color="#333333", alpha=0.3)
                ax.add_patch(c)

        for i in range(n_f):
            fd = ad["f"][str(i)]
            total_myel = fd["vm_t"]
            rec_myel = fd["vm_r"]
            frac = rec_myel / max(total_myel, 1)

            is_extrap = fi[i].get("source") == "extrapolated"
            color = plt.cm.inferno(frac)
            alpha = 0.6 if is_extrap else 0.8
            c = plt.Circle((fi[i]["y"], fi[i]["z"]), fi[i]["d"] / 2,
                           fill=True, color=color, alpha=alpha)
            ax.add_patch(c)
            edge_style = {"linestyle": "--", "linewidth": 0.5} if is_extrap else {"linewidth": 0.8}
            ce = plt.Circle((fi[i]["y"], fi[i]["z"]), fi[i]["d"] / 2,
                            fill=False, edgecolor="white", **edge_style)
            ax.add_patch(ce)

        ax.set_xlim(-3000, 3000)
        ax.set_ylim(-2200, 2200)
        ax.set_aspect("equal")
        s = ad["sum"]
        ax.set_title(f"{amp} μA ({amp/1000:.1f} mA)\n"
                     f"Vm: {s['vm']} | Vu: {s['vu']} | S: {s['s']}",
                     fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.1)

    sm = plt.cm.ScalarMappable(cmap=plt.cm.inferno, norm=plt.Normalize(0, 1))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=axes, shrink=0.7, pad=0.02)
    cbar.set_label("Vagal myelinated recruitment fraction", fontsize=11)

    fig.suptitle("Bovine Vagosympathetic Trunk — FEM Activation Maps\n"
                 f"{n_f} representative fascicles, bipolar cuff, 200μs pulse",
                 fontsize=14, fontweight="bold", y=1.04)
    plt.tight_layout()
    plt.savefig(f"{save_prefix}_activation_maps.png", dpi=200, bbox_inches="tight")
    print(f"Saved: {save_prefix}_activation_maps.png")

    # === Figure 2: Recruitment curves ===
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    amps_mA = [a / 1000 for a in amp_keys]

    # Panel 1: Vagal myelinated per fascicle
    ax = axes[0]
    colors = plt.cm.tab10(np.linspace(0, 1, n_f))
    for i in range(n_f):
        pcts = []
        for a in amp_keys:
            fd = amps[str(a)]["f"][str(i)]
            pcts.append(fd["vm_r"] / max(fd["vm_t"], 1) * 100)
        ax.plot(amps_mA, pcts, "-o", color=colors[i], linewidth=2, markersize=3,
                label=f"F{fi[i]['orig_id']} ({fi[i]['d']}μm)")
    ax.set_xlabel("Current (mA)", fontsize=12)
    ax.set_ylabel("% Recruited", fontsize=12)
    ax.set_title("Vagal Myelinated (per fascicle)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=7, ncol=2, loc="lower right")
    ax.set_ylim(-5, 105)
    ax.grid(True, alpha=0.2)

    # Panel 2: Aggregate — vagal myel vs vagal unmyel vs sympathetic
    ax = axes[1]
    vm_pct, vu_pct, s_pct = [], [], []
    for a in amp_keys:
        s_data = amps[str(a)]["sum"]
        vm_n, vm_d = map(int, s_data["vm"].split("/"))
        vu_n, vu_d = map(int, s_data["vu"].split("/"))
        s_n, s_d = map(int, s_data["s"].split("/"))
        vm_pct.append(vm_n / max(vm_d, 1) * 100)
        vu_pct.append(vu_n / max(vu_d, 1) * 100)
        s_pct.append(s_n / max(s_d, 1) * 100)

    ax.plot(amps_mA, vm_pct, "-o", color="#66BB6A", linewidth=2.5, markersize=4,
            label="Vagal myelinated (Aα/Aδ/B)")
    ax.plot(amps_mA, vu_pct, "-o", color="#42A5F5", linewidth=2.5, markersize=4,
            label="Vagal unmyelinated (C)")
    ax.plot(amps_mA, s_pct, "-o", color="#EF5350", linewidth=2.5, markersize=4,
            label="Sympathetic (C)")

    # Shade therapeutic window
    for j in range(len(amp_keys) - 1):
        if vm_pct[j] > 50 and s_pct[j] < 20:
            ax.axvspan(amps_mA[j], amps_mA[j + 1], color="#66BB6A", alpha=0.1)

    ax.set_xlabel("Current (mA)", fontsize=12)
    ax.set_ylabel("% Recruited", fontsize=12)
    ax.set_title("Fiber-Type Selectivity", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    ax.set_ylim(-5, 105)
    ax.grid(True, alpha=0.2)

    # Panel 3: Selectivity index
    ax = axes[2]
    si = []
    for j in range(len(amp_keys)):
        target = vm_pct[j] / 100
        offtarget = max(s_pct[j] / 100, vu_pct[j] / 100)
        si.append(target - offtarget)
    ax.plot(amps_mA, si, "-o", color="#FFB74D", linewidth=2.5, markersize=4)
    ax.axhline(0, color="white", linestyle="--", alpha=0.3)
    best_idx = np.argmax(si)
    ax.axvline(amps_mA[best_idx], color="#FFB74D", linestyle="--", alpha=0.5)
    ax.annotate(f"Best SI = {si[best_idx]:.2f}\nat {amps_mA[best_idx]:.2f} mA",
                xy=(amps_mA[best_idx], si[best_idx]),
                xytext=(amps_mA[best_idx] + 0.1, si[best_idx] - 0.15),
                fontsize=10, color="#FFB74D",
                arrowprops=dict(arrowstyle="->", color="#FFB74D"))
    ax.set_xlabel("Current (mA)", fontsize=12)
    ax.set_ylabel("Selectivity Index", fontsize=12)
    ax.set_title("SI = (vagal myel %) − max(unmyel %, symp %)", fontsize=11, fontweight="bold")
    ax.set_ylim(-0.5, 1.1)
    ax.grid(True, alpha=0.2)

    fig.suptitle("Bovine Vagosympathetic Trunk — Recruitment Analysis\n"
                 f"FEM, {n_f} fascicles, bipolar cuff, mixed vagal/sympathetic populations",
                 fontsize=14, fontweight="bold", y=1.04)
    plt.tight_layout()
    plt.savefig(f"{save_prefix}_recruitment.png", dpi=200, bbox_inches="tight")
    print(f"Saved: {save_prefix}_recruitment.png")


def plot_heatmap(grid_path, geom, results=None, save_prefix="outputs/figures/bovine"):
    """Cross-section voltage heatmap with fascicle overlay."""
    y, z, v, sa, sb = load_grid(grid_path)
    all_fascs = geom["vagal_fascicles"]
    theta = np.linspace(0, 2 * np.pi, 200)

    fig, ax = plt.subplots(1, 1, figsize=(10, 7))

    # Voltage heatmap
    extent = [y.min(), y.max(), z.min(), z.max()]
    im = ax.imshow(v, extent=extent, origin="lower", cmap="magma",
                   aspect="equal", interpolation="bilinear")
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("Extracellular voltage at 1 mA (V)", fontsize=11)

    # Nerve boundary
    ax.plot(sa * np.cos(theta), sb * np.sin(theta), "w-", linewidth=2)

    # Fascicle boundaries
    for fg in all_fascs:
        c = plt.Circle((fg["y_um"], fg["z_um"]), fg["diameter_um"] / 2,
                       fill=False, edgecolor="white", linewidth=0.6, linestyle="--", alpha=0.5)
        ax.add_patch(c)

    # Highlight modeled fascicles if results provided
    if results:
        for f in results["fi"]:
            is_fem = f.get("source", "fem") == "fem"
            if is_fem:
                c = plt.Circle((f["y"], f["z"]), f["d"] / 2,
                               fill=False, edgecolor="#66BB6A", linewidth=1.5)
                ax.add_patch(c)

    ax.set_xlim(-sa * 1.15, sa * 1.15)
    ax.set_ylim(-sb * 1.15, sb * 1.15)
    ax.set_xlabel("y (μm)", fontsize=12)
    ax.set_ylabel("z (μm)", fontsize=12)
    ax.set_title("Bovine Vagosympathetic Trunk — FEM Voltage Field\n"
                 "Cross-section at cuff center, bipolar electrode, 1 mA",
                 fontsize=13, fontweight="bold")

    plt.tight_layout()
    plt.savefig(f"{save_prefix}_heatmap.png", dpi=200, bbox_inches="tight")
    print(f"Saved: {save_prefix}_heatmap.png")


if __name__ == "__main__":
    results_path = sys.argv[1] if len(sys.argv) > 1 else "bovine_6_results.json"
    results = load_results(results_path)
    geom = load_geometry()

    os.makedirs("outputs/figures", exist_ok=True)
    plot_all(results, geom)

    # Try to plot heatmap if grid data exists
    grid_candidates = [
        results_path.replace("_results.json", "_crosssection_grid.npz"),
        "bovine_6_crosssection_grid.npz",
        "bovine_10_crosssection_grid.npz",
    ]
    for gp in grid_candidates:
        if Path(gp).exists():
            plot_heatmap(gp, geom, results)
            break

    print("All plots generated!")
