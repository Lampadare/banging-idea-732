"""Bovine vagosympathetic trunk geometry — scaled from pig SPARC Dataset 64.

Source: Pelot et al. 2020, SPARC Dataset 64 (DOI: 10.26275/MAQ2-EII4)
Sample: sub-4_sam-3 (pig cervical vagus, 40 fascicles, 1863um diameter)
Scale: ×2.68 to bovine 5mm diameter (allometric extrapolation)
"""

import json
import numpy as np
from pathlib import Path


SPARC_JSON = Path(__file__).parent.parent / "data" / "sparc" / "sub-4_sam-3_fascicle_morphometry.json"

PIG_NERVE_DIAMETER = 1863.0  # um
BOVINE_NERVE_DIAMETER = 5000.0  # um
SCALE_FACTOR = BOVINE_NERVE_DIAMETER / PIG_NERVE_DIAMETER  # ~2.68
BOVINE_ASPECT_RATIO = 1.4  # elliptical, from design brief


def load_pig_morphometry(json_path=SPARC_JSON):
    with open(json_path) as f:
        data = json.load(f)
    return data


def build_bovine_fascicles(json_path=SPARC_JSON, scale=SCALE_FACTOR,
                           sympathetic_fraction=0.15):
    """Build bovine fascicle list from scaled pig morphometry.

    Returns list of dicts with keys:
        id, y_um, z_um, diameter_um, is_sympathetic
    """
    data = load_pig_morphometry(json_path)
    fascicles = []

    rng = np.random.default_rng(42)
    n_fasc = len(data["fascicles"])
    n_sympathetic = int(n_fasc * sympathetic_fraction)
    sympathetic_ids = set(rng.choice(n_fasc, n_sympathetic, replace=False))

    # Compute pig nerve radius for normalization
    pig_max_r = max(
        np.sqrt(f["centroid_y_rel_um"]**2 + f["centroid_z_rel_um"]**2)
        + f["equiv_diameter_um"] / 2
        for f in data["fascicles"]
    )

    for i, f in enumerate(data["fascicles"]):
        # Normalize positions to unit circle, then map to bovine ellipse
        y_norm = f["centroid_y_rel_um"] / pig_max_r
        z_norm = f["centroid_z_rel_um"] / pig_max_r
        d = f["equiv_diameter_um"] * scale

        # Map to bovine ellipse (semi_major along y, semi_minor along z)
        semi_a = BOVINE_NERVE_DIAMETER / 2
        semi_b = semi_a / BOVINE_ASPECT_RATIO
        # Shrink slightly to keep fascicles + their radius inside boundary
        margin = 0.85
        y = y_norm * semi_a * margin
        z = z_norm * semi_b * margin

        fascicles.append({
            "id": f["fascicle_id"],
            "y_um": round(y, 1),
            "z_um": round(z, 1),
            "diameter_um": round(d, 1),
            "area_um2": round(f["area_um2"] * scale**2, 1),
            "is_sympathetic": i in sympathetic_ids,
            "pig_source": {
                "y_rel": f["centroid_y_rel_um"],
                "z_rel": f["centroid_z_rel_um"],
                "diameter": f["equiv_diameter_um"],
            },
        })

    return fascicles


def get_bovine_nerve_params():
    return {
        "diameter_um": BOVINE_NERVE_DIAMETER,
        "semi_major_um": BOVINE_NERVE_DIAMETER / 2,
        "semi_minor_um": BOVINE_NERVE_DIAMETER / (2 * BOVINE_ASPECT_RATIO),
        "scale_factor": SCALE_FACTOR,
        "aspect_ratio": BOVINE_ASPECT_RATIO,
        "source": "Pelot et al. 2020 SPARC-64, scaled ×{:.2f}".format(SCALE_FACTOR),
    }


if __name__ == "__main__":
    fascicles = build_bovine_fascicles()
    params = get_bovine_nerve_params()

    print(f"Bovine vagosympathetic trunk geometry")
    print(f"  Source: {params['source']}")
    print(f"  Nerve diameter: {params['diameter_um']}um")
    print(f"  Semi-major: {params['semi_major_um']:.0f}um, Semi-minor: {params['semi_minor_um']:.0f}um")
    print(f"  Fascicles: {len(fascicles)}")
    print(f"  Sympathetic fascicles: {sum(1 for f in fascicles if f['is_sympathetic'])}")
    print()

    diameters = [f["diameter_um"] for f in fascicles]
    print(f"  Diameter range: {min(diameters):.0f} - {max(diameters):.0f} um")
    print(f"  Mean diameter: {np.mean(diameters):.0f} um")
    print()

    for f in fascicles[:5]:
        sym = " [SYMP]" if f["is_sympathetic"] else ""
        print(f"  F{f['id']:2d}: d={f['diameter_um']:6.1f}um at ({f['y_um']:+7.1f}, {f['z_um']:+7.1f}){sym}")
    print(f"  ... ({len(fascicles) - 5} more)")
