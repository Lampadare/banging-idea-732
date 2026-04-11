"""Synthetic bovine vagus nerve geometry.

All spatial units: micrometers (μm).
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class Fascicle:
    cx: float  # center x, μm
    cy: float  # center y, μm
    radius: float  # μm
    id: int


@dataclass
class Electrode:
    x: float  # μm
    y: float  # μm
    z: float  # μm
    id: int


def build_nerve_boundary(semi_major_um=2000.0, semi_minor_um=1500.0):
    """Elliptical nerve boundary (cattle vagus ~4x3 mm)."""
    return semi_major_um, semi_minor_um


def pack_fascicles(
    n_fascicles: int = 12,
    semi_major: float = 2000.0,
    semi_minor: float = 1500.0,
    mean_radius: float = 150.0,
    std_radius: float = 50.0,
    min_radius: float = 50.0,
    max_radius: float = 300.0,
    min_gap: float = 50.0,
    seed: int = 42,
) -> list[Fascicle]:
    """Pack fascicles inside elliptical nerve boundary via rejection sampling."""
    rng = np.random.default_rng(seed)
    fascicles = []
    max_attempts = 10000
    attempts = 0

    while len(fascicles) < n_fascicles and attempts < max_attempts:
        attempts += 1
        r = np.clip(rng.normal(mean_radius, std_radius), min_radius, max_radius)
        cx = rng.uniform(-(semi_major - r), semi_major - r)
        cy = rng.uniform(-(semi_minor - r), semi_minor - r)

        if (cx / (semi_major - r)) ** 2 + (cy / (semi_minor - r)) ** 2 > 1.0:
            continue

        overlap = False
        for f in fascicles:
            dist = np.sqrt((cx - f.cx) ** 2 + (cy - f.cy) ** 2)
            if dist < r + f.radius + min_gap:
                overlap = True
                break

        if not overlap:
            fascicles.append(Fascicle(cx=cx, cy=cy, radius=r, id=len(fascicles)))

    if len(fascicles) < n_fascicles:
        print(f"Warning: only placed {len(fascicles)}/{n_fascicles} fascicles")
    return fascicles


def build_electrode_ring(
    n_electrodes: int = 8,
    ring_radius_um: float = 2500.0,
) -> list[Electrode]:
    """Place point-source electrodes in a ring around the nerve (cuff geometry)."""
    electrodes = []
    for i in range(n_electrodes):
        angle = 2 * np.pi * i / n_electrodes
        x = ring_radius_um * np.cos(angle)
        y = ring_radius_um * np.sin(angle)
        electrodes.append(Electrode(x=x, y=y, z=0.0, id=i + 1))
    return electrodes
