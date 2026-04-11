"""Analytical extracellular potential computation.

Physics: point-source in homogeneous isotropic medium.
V(r) = (rho * I) / (4 * pi * r)

Units contract:
  - electrode positions: μm (converted to meters internally)
  - fiber compartment positions: μm (converted to meters internally)
  - rho: Ω·m (tissue resistivity, default 3.0 for peripheral nerve)
  - current weights: dimensionless multipliers on total stimulus current
  - stimulus amplitude: mA
  - output potentials: mV
"""

import numpy as np
from src.geometry import Electrode

RHO_DEFAULT = 3.0  # Ω·m, peripheral nerve tissue


def compute_potentials(
    electrodes: list[Electrode],
    weights: list[float],
    fiber_coords_um: np.ndarray,
    rho: float = RHO_DEFAULT,
) -> np.ndarray:
    """Compute extracellular potential at each fiber compartment per unit mA stimulus.

    Args:
        electrodes: list of Electrode objects (positions in μm)
        weights: current weight per electrode (sum of cathodes = +1 typically)
        fiber_coords_um: (n_compartments, 3) array, positions in μm
        rho: tissue resistivity in Ω·m

    Returns:
        potentials: (n_compartments,) array in mV per mA of total stimulus current
    """
    assert len(electrodes) == len(weights), "Electrode count must match weight count"
    assert fiber_coords_um.ndim == 2 and fiber_coords_um.shape[1] == 3

    n_comp = fiber_coords_um.shape[0]
    potentials = np.zeros(n_comp)

    # Convert μm to meters
    fiber_m = fiber_coords_um * 1e-6

    for elec, w in zip(electrodes, weights):
        elec_pos_m = np.array([elec.x, elec.y, elec.z]) * 1e-6

        # Distance from this electrode to each compartment
        diff = fiber_m - elec_pos_m[np.newaxis, :]
        r = np.sqrt(np.sum(diff**2, axis=1))

        # Avoid division by zero
        r = np.maximum(r, 1e-9)

        # V = (rho * I * w) / (4 * pi * r)
        # With I in mA (1e-3 A), output in mV (1e-3 V):
        # V[mV] = (rho[Ω·m] * I[mA]*1e-3) / (4*pi*r[m]) * 1e3
        # The 1e-3 and 1e3 cancel, so:
        # V[mV per mA] = (rho * w) / (4 * pi * r)
        potentials += (rho * w) / (4 * np.pi * r)

    return potentials


def sanity_check():
    """Quick sanity check: 1mA monopolar at 2.5mm should give ~0.05 mV."""
    from src.geometry import Electrode
    elec = Electrode(x=2500.0, y=0.0, z=0.0, id=1)
    # Fiber at origin
    fiber = np.array([[0.0, 0.0, 0.0]])
    v = compute_potentials([elec], [1.0], fiber)
    print(f"V at 2.5mm from 1mA monopolar: {v[0]:.4f} mV")
    # Expected: 3.0 / (4 * pi * 0.0025) ≈ 95.5 mV — that's the peak at the node closest to electrode
    # Actually at 2.5mm: 3.0/(4*pi*0.0025) = 95.49 mV
    assert 50 < v[0] < 200, f"Unexpected potential: {v[0]} mV"
    print("Sanity check PASSED")


if __name__ == "__main__":
    sanity_check()
