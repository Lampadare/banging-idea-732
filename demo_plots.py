"""Night-before demo: generate plots to verify everything works.

Runs a reduced experiment (6 fascicles, 8 electrodes, 3 fiber types)
and produces 3 plots:
  1. Nerve cross-section with fascicles and electrodes
  2. Monopolar threshold heatmap (closest electrode per fascicle)
  3. Recruitment curves for target fascicle
"""

import sys
sys.path.insert(0, ".")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from src.geometry import pack_fascicles, build_electrode_ring, build_nerve_boundary, Fascicle
from src.experiments import FIBER_TYPES, _find_threshold, _test_activation

plt.style.use("dark_background")

# --- Build geometry ---
semi_a, semi_b = build_nerve_boundary()
fascicles = pack_fascicles(n_fascicles=12, seed=42)
electrodes = build_electrode_ring(n_electrodes=8)

print(f"Placed {len(fascicles)} fascicles, {len(electrodes)} electrodes")

# ============================================================
# PLOT 1: Nerve cross-section with geometry
# ============================================================
print("\n--- Plot 1: Nerve cross-section ---")
fig, ax = plt.subplots(1, 1, figsize=(8, 7))

# Nerve boundary
theta = np.linspace(0, 2 * np.pi, 200)
ax.plot(semi_a * np.cos(theta), semi_b * np.sin(theta), "w-", linewidth=2, label="Nerve boundary")

# Fascicles
for f in fascicles:
    circle = plt.Circle((f.cx, f.cy), f.radius, fill=True, color="#2196F3", alpha=0.5, linewidth=1.5)
    ax.add_patch(circle)
    circle_edge = plt.Circle((f.cx, f.cy), f.radius, fill=False, edgecolor="#64B5F6", linewidth=1.5)
    ax.add_patch(circle_edge)
    ax.text(f.cx, f.cy, str(f.id), ha="center", va="center", fontsize=9, color="white", fontweight="bold")

# Electrodes
for e in electrodes:
    ax.plot(e.x, e.y, "o", color="#FF5722", markersize=12, markeredgecolor="white", markeredgewidth=1.5)
    ax.text(e.x * 1.15, e.y * 1.15, f"E{e.id}", ha="center", va="center", fontsize=9, color="#FF8A65")

ax.set_xlim(-3500, 3500)
ax.set_ylim(-3000, 3000)
ax.set_aspect("equal")
ax.set_xlabel("x (μm)", fontsize=13)
ax.set_ylabel("y (μm)", fontsize=13)
ax.set_title("Bovine Vagus Nerve — Synthetic Cross-Section", fontsize=15, fontweight="bold")

legend_elements = [
    mpatches.Patch(color="#2196F3", alpha=0.5, label=f"Fascicles (n={len(fascicles)})"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#FF5722", markersize=10, label=f"Cuff electrodes (n={len(electrodes)})"),
]
ax.legend(handles=legend_elements, loc="upper right", fontsize=11)
ax.grid(True, alpha=0.15)

plt.tight_layout()
plt.savefig("outputs/figures/01_nerve_cross_section.png", dpi=200)
print("Saved: outputs/figures/01_nerve_cross_section.png")

# ============================================================
# PLOT 2: Monopolar thresholds — E1 activation map
# ============================================================
print("\n--- Plot 2: Monopolar activation map (E1) ---")

# Find thresholds from electrode 1 for all fascicles, all fiber types
e1 = electrodes[0]
thresholds = {}
for f in fascicles:
    thresholds[f.id] = {}
    for fname, fspec in FIBER_TYPES.items():
        t = _find_threshold(f, fspec, [e1], [1.0], total_amp_ua=5000, n_iter=10)
        thresholds[f.id][fname] = t
        print(f"  F{f.id} {fname:6s}: {t:.0f} μA ({t/1000:.2f} mA)")

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax_idx, fname in enumerate(["Aalpha", "B", "C"]):
    ax = axes[ax_idx]

    # Nerve boundary
    ax.plot(semi_a * np.cos(theta), semi_b * np.sin(theta), "w-", linewidth=1.5)

    # Color fascicles by threshold
    thresh_vals = [thresholds[f.id][fname] for f in fascicles]
    finite_vals = [v for v in thresh_vals if np.isfinite(v)]
    if finite_vals:
        vmin, vmax = min(finite_vals), max(finite_vals)
    else:
        vmin, vmax = 0, 1

    cmap = plt.cm.viridis_r
    for f in fascicles:
        t = thresholds[f.id][fname]
        if np.isfinite(t):
            color = cmap((t - vmin) / (vmax - vmin + 1e-9))
        else:
            color = (0.3, 0.3, 0.3, 0.5)
        circle = plt.Circle((f.cx, f.cy), f.radius, fill=True, color=color, linewidth=1)
        ax.add_patch(circle)
        circle_edge = plt.Circle((f.cx, f.cy), f.radius, fill=False, edgecolor="white", linewidth=0.8)
        ax.add_patch(circle_edge)
        label = f"{t:.0f}" if np.isfinite(t) else "∞"
        ax.text(f.cx, f.cy, label, ha="center", va="center", fontsize=7, color="white")

    # Electrodes
    for e in electrodes:
        color = "#FF5722" if e.id == 1 else "#666666"
        size = 14 if e.id == 1 else 8
        ax.plot(e.x, e.y, "o", color=color, markersize=size, markeredgecolor="white", markeredgewidth=1)

    ax.set_xlim(-3500, 3500)
    ax.set_ylim(-3000, 3000)
    ax.set_aspect("equal")
    ax.set_title(f"{fname} fibers ({FIBER_TYPES[fname]['diameter']}μm)", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.1)

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label("Threshold (μA)", fontsize=10)

fig.suptitle("Monopolar Stimulation Thresholds — Electrode 1 Active", fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("outputs/figures/02_monopolar_thresholds.png", dpi=200, bbox_inches="tight")
print("Saved: outputs/figures/02_monopolar_thresholds.png")

# ============================================================
# PLOT 3: Recruitment curves — target fascicle via E1
# ============================================================
print("\n--- Plot 3: Recruitment curves ---")

# Pick the fascicle closest to E1 as target
dists = [np.sqrt((f.cx - e1.x)**2 + (f.cy - e1.y)**2) for f in fascicles]
target_idx = np.argmin(dists)
target = fascicles[target_idx]
print(f"Target fascicle: F{target.id} (closest to E1, dist={dists[target_idx]:.0f}μm)")

amplitudes = np.linspace(10, 2000, 25)

fig, ax = plt.subplots(1, 1, figsize=(10, 6))

colors = {"Aalpha": "#EF5350", "B": "#66BB6A", "C": "#42A5F5"}
labels = {"Aalpha": "Aα motor (16μm)", "B": "B autonomic (3μm)", "C": "C unmyelinated (0.8μm)"}

for fname, fspec in FIBER_TYPES.items():
    print(f"  Sweeping {fname}...")
    recruited = np.zeros(len(amplitudes))
    for i, amp in enumerate(amplitudes):
        # Test 3 positions within fascicle (center + 2 offsets)
        positions = [
            (target.cx, target.cy),
            (target.cx + target.radius * 0.5, target.cy),
            (target.cx, target.cy + target.radius * 0.5),
        ]
        count = 0
        for px, py in positions:
            sub = Fascicle(cx=px, cy=py, radius=0, id=target.id)
            if _test_activation(sub, fspec, [e1], [1.0], amp):
                count += 1
        recruited[i] = count / len(positions)
        if i % 5 == 0:
            print(f"    {amp:.0f} μA: {recruited[i]*100:.0f}%")

    ax.plot(amplitudes / 1000, recruited * 100, "-o", color=colors[fname],
            linewidth=2.5, markersize=4, label=labels[fname])

# Shade therapeutic window (where B > 50% and Aalpha < 50%)
ax.axhline(50, color="white", linestyle="--", alpha=0.3, linewidth=1)
ax.set_xlabel("Stimulus Current (mA)", fontsize=13)
ax.set_ylabel("% Fibers Recruited", fontsize=13)
ax.set_title(f"Recruitment Curves — Fascicle {target.id} via Electrode 1 (Monopolar)", fontsize=14, fontweight="bold")
ax.legend(fontsize=12, loc="lower right")
ax.set_ylim(-5, 105)
ax.set_xlim(0, amplitudes[-1] / 1000)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig("outputs/figures/03_recruitment_curves.png", dpi=200)
print("Saved: outputs/figures/03_recruitment_curves.png")

print("\n=== ALL PLOTS GENERATED ===")
print("Check outputs/figures/ for:")
print("  01_nerve_cross_section.png")
print("  02_monopolar_thresholds.png")
print("  03_recruitment_curves.png")
