"""Night-before smoke test. Run this to verify the simulation stack works."""

import sys
print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")

# Test 1: Core dependencies
import numpy as np
import scipy
import matplotlib
import pandas as pd
print(f"numpy={np.__version__}, scipy={scipy.__version__}, pandas={pd.__version__}")

# Test 2: Our geometry module
sys.path.insert(0, ".")
from src.geometry import pack_fascicles, build_electrode_ring, build_nerve_boundary, get_fiber_coords
fascicles = pack_fascicles(n_fascicles=12, seed=42)
electrodes = build_electrode_ring(n_electrodes=8)
print(f"Fascicles placed: {len(fascicles)}")
print(f"Electrodes placed: {len(electrodes)}")

# Test 3: Potentials
from src.potentials import compute_potentials
coords = get_fiber_coords(fascicles[0])
v = compute_potentials([electrodes[0]], [1.0], coords)
print(f"Peak potential on fiber 0 from electrode 1: {np.max(v):.2f} mV/mA")
print(f"Min potential: {np.min(v):.2f} mV/mA")

# Test 4: PyFibers (the critical one)
try:
    from pyfibers import build_fiber, FiberModel, ScaledStim
    fiber = build_fiber(diameter=10.0, fiber_model=FiberModel.MRG_INTERPOLATION, length=10000)
    print(f"PyFibers OK: fiber has {len(fiber.sections)} sections")
    PYFIBERS_OK = True
except ImportError as e:
    print(f"PyFibers NOT available: {e}")
    PYFIBERS_OK = False
except Exception as e:
    print(f"PyFibers ERROR: {e}")
    PYFIBERS_OK = False

# Summary
print("\n" + "="*50)
print("SMOKE TEST SUMMARY")
print("="*50)
print(f"  Geometry:   OK")
print(f"  Potentials: OK")
print(f"  PyFibers:   {'OK' if PYFIBERS_OK else 'FAILED — need fallback'}")

if not PYFIBERS_OK:
    print("\n  Fallback options:")
    print("    1. Try: pip install pyfibers && pyfibers_compile")
    print("    2. Use NRV framework (pip install nrv-py)")
    print("    3. Use analytical activation function (no cable equation)")
