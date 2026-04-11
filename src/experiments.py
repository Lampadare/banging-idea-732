"""Threshold search experiments using NRV framework.

Units (NRV convention):
  - distances: μm
  - current: μA
  - time: ms
  - fiber diameter: μm
"""

import nrv
import numpy as np
import pandas as pd
from src.geometry import Fascicle, Electrode


FIBER_TYPES = {
    "Aalpha": {"diameter": 16.0, "model": "MRG", "cls": nrv.myelinated},
    "B":      {"diameter": 3.0,  "model": "MRG", "cls": nrv.myelinated},
    "C":      {"diameter": 0.8,  "model": "Sundt", "cls": nrv.unmyelinated},
}

FIBER_LENGTH_UM = 10000  # 10mm along z-axis
SIM_T_MS = 3.0
PULSE_START_MS = 0.1


def _find_threshold(
    fascicle: Fascicle,
    fiber_spec: dict,
    electrodes: list[Electrode],
    weights: list[float],
    total_amp_ua: float,
    pulse_duration_ms: float = 0.2,
    amp_lo: float = 1.0,
    amp_hi: float = 5000.0,
    n_iter: int = 12,
) -> float:
    """Binary search for activation threshold (μA total cathodic current).

    Returns threshold in μA, or np.inf if not activated at amp_hi.
    """
    # First check if max amplitude activates
    if not _test_activation(fascicle, fiber_spec, electrodes, weights, amp_hi, pulse_duration_ms):
        return np.inf

    # Check if min amplitude already activates
    if _test_activation(fascicle, fiber_spec, electrodes, weights, amp_lo, pulse_duration_ms):
        return amp_lo

    lo, hi = amp_lo, amp_hi
    for _ in range(n_iter):
        mid = (lo + hi) / 2
        if _test_activation(fascicle, fiber_spec, electrodes, weights, mid, pulse_duration_ms):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _test_activation(
    fascicle: Fascicle,
    fiber_spec: dict,
    electrodes: list[Electrode],
    weights: list[float],
    total_amp_ua: float,
    pulse_duration_ms: float = 0.2,
) -> bool:
    """Test if a fiber in a fascicle fires at given total amplitude."""
    fiber_z_center = FIBER_LENGTH_UM / 2

    axon = fiber_spec["cls"](
        y=fascicle.cx,  # NRV: y,z are transverse, x is along fiber
        z=fascicle.cy,
        d=fiber_spec["diameter"],
        L=FIBER_LENGTH_UM,
        model=fiber_spec["model"],
    )

    extra_stim = nrv.stimulation("endoneurium_ranck")
    for elec, w in zip(electrodes, weights):
        if w == 0:
            continue
        e = nrv.point_source_electrode(x=fiber_z_center, y=elec.x, z=elec.y)
        s = nrv.stimulus()
        s.pulse(start=PULSE_START_MS, value=-total_amp_ua * w, duration=pulse_duration_ms)
        extra_stim.add_electrode(e, s)

    axon.attach_extracellular_stimulation(extra_stim)
    results = axon(t_sim=SIM_T_MS)
    return results.is_recruited()


def run_monopolar_sweep(
    fascicles: list[Fascicle],
    electrodes: list[Electrode],
    fiber_types: dict = None,
    pulse_duration_ms: float = 0.2,
) -> pd.DataFrame:
    """Phase 1: Find threshold for each electrode × fascicle × fiber type."""
    if fiber_types is None:
        fiber_types = FIBER_TYPES

    results = []
    n_total = len(electrodes) * len(fascicles) * len(fiber_types)
    done = 0

    for elec in electrodes:
        weights_mono = [1.0]
        for fasc in fascicles:
            for fname, fspec in fiber_types.items():
                threshold = _find_threshold(
                    fasc, fspec, [elec], weights_mono,
                    total_amp_ua=5000, pulse_duration_ms=pulse_duration_ms,
                )
                results.append({
                    "electrode_id": elec.id,
                    "fascicle_id": fasc.id,
                    "fiber_type": fname,
                    "diameter_um": fspec["diameter"],
                    "threshold_uA": threshold,
                    "threshold_mA": threshold / 1000,
                })
                done += 1
                print(f"  [{done}/{n_total}] E{elec.id} F{fasc.id} {fname}: {threshold:.0f} μA")

    return pd.DataFrame(results)


def run_config_sweep(
    fascicles: list[Fascicle],
    electrodes: list[Electrode],
    configs: dict,
    fiber_types: dict = None,
    pulse_duration_ms: float = 0.2,
) -> pd.DataFrame:
    """Phase 2: Threshold sweep with named electrode configurations.

    configs: dict of {name: {electrode_id: weight, ...}}
    """
    if fiber_types is None:
        fiber_types = FIBER_TYPES

    results = []
    for config_name, elec_weights in configs.items():
        active_elecs = [e for e in electrodes if e.id in elec_weights]
        weights = [elec_weights[e.id] for e in active_elecs]

        for fasc in fascicles:
            for fname, fspec in fiber_types.items():
                threshold = _find_threshold(
                    fasc, fspec, active_elecs, weights,
                    total_amp_ua=5000, pulse_duration_ms=pulse_duration_ms,
                )
                results.append({
                    "config": config_name,
                    "fascicle_id": fasc.id,
                    "fiber_type": fname,
                    "diameter_um": fspec["diameter"],
                    "threshold_uA": threshold,
                    "threshold_mA": threshold / 1000,
                })
                print(f"  {config_name} F{fasc.id} {fname}: {threshold:.0f} μA")

    return pd.DataFrame(results)


def run_recruitment_curve(
    fascicle: Fascicle,
    electrodes: list[Electrode],
    weights: list[float],
    fiber_spec: dict,
    amplitudes_ua: np.ndarray,
    pulse_duration_ms: float = 0.2,
    n_fibers: int = 5,
    seed: int = 42,
) -> np.ndarray:
    """Compute fraction of fibers recruited at each amplitude.

    Scatters n_fibers at random positions within the fascicle.
    Returns array of shape (len(amplitudes),) with fraction recruited.
    """
    rng = np.random.default_rng(seed)
    offsets = []
    for _ in range(n_fibers):
        r = fascicle.radius * np.sqrt(rng.random())
        theta = rng.random() * 2 * np.pi
        offsets.append((r * np.cos(theta), r * np.sin(theta)))

    recruited = np.zeros(len(amplitudes_ua))
    for amp_idx, amp in enumerate(amplitudes_ua):
        count = 0
        for dx, dy in offsets:
            sub_fasc = Fascicle(
                cx=fascicle.cx + dx,
                cy=fascicle.cy + dy,
                radius=0,
                id=fascicle.id,
            )
            if _test_activation(sub_fasc, fiber_spec, electrodes, weights, amp, pulse_duration_ms):
                count += 1
        recruited[amp_idx] = count / n_fibers
    return recruited
