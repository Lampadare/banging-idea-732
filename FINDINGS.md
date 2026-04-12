# Bovine VNS Simulation — Technical Findings

## Environment Setup

### Local Mac (M2 Max)
- 64GB RAM, 12 cores
- conda env `vns`: Python 3.12, NRV 1.3.2, NEURON 9.0.1, dolfinx 0.9.0
- All 49 NEURON .mod files compiled (arm64)
- mph stubbed (COMSOL not needed)

### DT-2 (London server)
- 60GB RAM, 32 cores, RTX 5090 (unused — NEURON is CPU-only)
- conda env `vns`: same stack as local
- ENT_DOM_offset patched: Electrode 100→200 (allows 95 fascicles)
- Axon mesh resolution patched: 10→50μm

## Geometry Pipeline

### Source Data
- SPARC Dataset 64 (Pelot et al. 2020, DOI: 10.26275/MAQ2-EII4)
- 9 pig cervical vagus cross-sections, 422 fascicles total
- Selected sample: P12-1 (57 fascicles, nerve d=2207μm)

### Pig → Bovine Transform
1. PCA alignment of fascicle positions (principal axis → horizontal)
2. Uniform scale ×1.26 (based on fascicle extent, not equiv diameter)
3. Elliptical boundary wrapping (5000×3571μm, 1.4:1 ratio)
4. Collision resolution: iterative push-apart, **75μm minimum gap** (critical for gmsh)
5. Mixed vagosympathetic populations: 85% vagal + 15% sympathetic per fascicle
6. Sympathetic fibers: small unmyelinated C-fibers (0.3-1.2μm diameter)

### Representative Subset (for FEM)
- 20 fascicles selected from 57: 10 largest by area + 10 spatially distributed
- Selection preserves angular coverage (8 sectors × 2 radial bands)
- Scientifically defensible: VaStim (Nature Comms 2024) used 9 fascicles

## FEM Pipeline — What Works

### Proven Configuration
- **6 fascicles**: 234K elements, 7 subspaces, 170s solve, ~2GB RAM ✅
- **5 fascicles (bovine geometry)**: 252K elements, 6 subspaces, 98s solve, ~2GB RAM ✅
- Default solver: CG + ILU preconditioner
- P2 elements (default) or P1 (4× fewer DOFs)

### Optimizations Applied
1. **Footprint caching**: FEM solves at 1mA, stores V/mA. Amplitude sweep = scalar multiply. Eliminates redundant FEM solves.
2. **CPU parallelism**: `set_nmod_ncore(28)` for NEURON fiber sims (was 3 by default)
3. **gmsh parallelism**: `set_gmsh_ncore(16)` for mesh generation
4. **JIT options**: `{"timeout": 600, "cffi_extra_compile_args": ["-O0", "-g0"]}` — prevents FFCx timeout and cuts compile time 5-10×

### Optimized 6-Fascicle Sweep
- 20-point amplitude sweep (100-1000μA): **912s total** (15 min)
- FEM: 166s (one-time) + NEURON: 746s (37s per amplitude, 28 cores)
- Previously would have taken ~22 hours without optimizations

## FEM Pipeline — Scaling Limits

### The Mixed-Element Formulation Problem
NRV models perineurium as an interface jump condition using a **mixed finite element space**.
Each fascicle adds one copy of the function space: `Nspace = n_fascicles + 1`.

This causes three compounding issues:
1. **DOF explosion**: DOFs = Nspace × mesh_nodes (not just mesh_nodes)
2. **JIT compilation**: FFCx generates C code for each (subspace × domain) combination. At 57 fascicles: ~50-100K lines of C, takes 10-15 min to compile (2-3 min with -O0)
3. **ILU fill-in**: The ILU preconditioner's memory scales super-linearly with DOFs on high-contrast problems (endoneurium 0.571 S/m vs perineurium 0.0009 S/m)

### Observed Memory Scaling (ILU, P1 elements)

| Fascicles | Subspaces | Mesh elements | DOFs | Peak RAM | Result |
|-----------|-----------|---------------|------|----------|--------|
| 5 | 6 | 252K | ~228K | ~2GB | ✅ |
| 6 | 7 | 234K | ~245K | ~2GB | ✅ |
| 20 | 21 | 417K | ~1.3M | 11GB (local), 59GB (DT-2) | OOM on both |
| 57 | 58 | 1.14M | ~9.5M | >64GB | OOM everywhere |

### Key Finding: Platform-Dependent Memory
Same 20-fascicle problem used 11GB on Mac but 59GB on DT-2 Linux. ILU fill-in is not deterministic across platforms — depends on PETSc build, matrix ordering, and MPI configuration.

### BoomerAMG Did Not Help
Switching from ILU to hypre BoomerAMG made memory **worse** — AMG builds a multigrid hierarchy for each of the 21 block components. Peak memory exceeded 18GB on local and 59GB on DT-2 for 10 fascicles.

### What Was NOT the Problem
- Mesh generation: gmsh handles 57 fascicles fine (with 75μm gaps and Delaunay)
- JIT compilation: solved with -O0 and timeout=600
- NEURON simulations: fast and scalable (footprint caching + 28 cores)
- GPU: CoreNEURON doesn't support `extracellular` mechanism — RTX 5090 is unusable

## Geometry Issues Encountered

### Overlapping Facets (gmsh)
- **Cause**: 10μm collision gap too small — perineurium thickness (0.03 × fascicle_diameter ≈ 10-20μm) makes boundaries overlap
- **Fix**: 75μm minimum gap in collision resolution
- **Symptom**: `Invalid boundary mesh (overlapping facets) on surface 173`

### Fascicle Limit (NRV)
- **Cause**: `ENT_DOM_offset["Electrode"] = 100` limits fascicles to (100-10)/2 = 45
- **Fix**: Patch to `"Electrode": 200` (allows 95 fascicles)

### HXT Mesh Algorithm
- NRV auto-selects HXT (Algorithm3D=10) when gmsh threads > 1
- HXT fails on complex multi-fascicle geometries
- **Fix**: Force Delaunay (Algorithm3D=1) after NRV's gmsh config

## What Actually Works (Final Proven Config)

### 10-fascicle FEM — SUCCESSFUL
- **10 fascicles**, P1 elements, ILU solver, Delaunay mesh, CharacteristicLengthMin=30
- Mesh: 204K elements, 30K nodes, 11 subspaces
- FEM solve: **531s** (8.9 min), peak ~22GB RAM (Mac M2 Max 64GB)
- Memory drops to ~7GB after solve during footprint interpolation
- Amplitude sweep: 20 points with footprint caching, ~30s each
- **This is the production configuration**

### Why 15+ Fascicles Fail
- 15 fascicles: PETSc `MatXIJSetPreallocation` error on Mac (block matrix too large)
- 15 fascicles: OOM at 59GB on DT-2 Linux
- 20 fascicles: OOM on both machines (11GB Mac, 59GB DT-2)
- 57 fascicles: OOM everywhere even with BoomerAMG
- Root cause: NRV mixed-element formulation (Nspace = n_fasc + 1)
- DT-2 Linux PETSc uses ~5× more RAM than Mac for same problem

### Critical Settings
```json
// dolfinx_jit_options.json (in working directory)
{"timeout": 600, "cffi_extra_compile_args": ["-O0", "-g0"]}
```

### NRV Patches Required (on both machines)
```
# In _NerveMshCreator.py:
ENT_DOM_offset["Electrode"] = 200  # was 100, allows 95 fascicles
default_res["Axon"] = 50           # was 10, reduces mesh 5x
```

### Geometry Requirements
- Minimum 75μm gap between fascicles (for perineurium + gmsh stability)
- Force Delaunay mesher (Algorithm3D=1), NOT HXT (Algorithm3D=10)
- HXT fails on complex multi-fascicle geometries

## Recommendations for Next Steps

### Immediate
1. Plot 10-fascicle FEM results (activation maps + recruitment curves)
2. Extrapolate to 57 fascicles using voltage field interpolation
3. Run 2-3 electrode configurations (monopolar, bipolar, steered)

### For the Pitch
- 10 representative fascicles is scientifically defensible (VaStim used 9)
- Frame as: "representative-subset FEM model with extrapolation to full cross-section"
- The selectivity story holds at N≥10 fascicles (confirmed by literature review)

### Architectural Fix (if continuing the project)
- Model perineurium as volumetric low-conductivity domain (`inbound=False`) instead of interface jump
- This reduces Nspace from N+1 to 1 regardless of fascicle count
- Used by ASCENT/COMSOL pipeline — scientifically equivalent
- Would enable 57+ fascicles trivially
- Or: rent 256GB VPS (~$1/hr on Hetzner) and brute-force 57 fascicles

## Files

### Scripts
- `src/fem_optimized_sweep.py` — 6-fascicle optimized sweep (footprint caching + 28 cores)
- `src/fem_bovine_20.py` — 20-fascicle representative subset with all fixes
- `src/fem_bovine_optimized.py` — 57-fascicle attempt with P1 + BoomerAMG + mesh coarsening
- `src/fem_bovine_mixed.py` — mixed vagal/sympathetic population builder
- `src/bovine_geometry.py` — pig→bovine geometry transform

### Data
- `data/bovine_geometry.json` — 57 vagal fascicles + 20-fascicle representative subset indices
- `data/sparc/` — SPARC Dataset 64 raw morphometry (9 pig samples, 422 fascicles)
- `outputs/data/optimized_sweep_results.json` — 6-fascicle fine sweep results (20 amplitudes)

### Key Figures
- `outputs/figures/07_all_pig_samples.png` — all 9 pig vagus cross-sections
- `outputs/figures/08_p12_bovine_transform.png` — PCA-aligned pig→bovine transform
- `outputs/figures/10_bovine_final_v2.png` — final bovine geometry with interleaved sympathetic
- `outputs/figures/11_optimized_sweep_results.png` — recruitment curves from optimized sweep
- `outputs/figures/14_representative_20.png` — 20 representative fascicles selection

## References
- Pelot et al. 2020, Front. Neurosci. — pig vagus morphometry (SPARC Dataset 64)
- Ciotti et al. 2024, Nature Comms (VaStim) — 9-fascicle selective VNS model
- Zanos et al. 2025, Nature Comms — 1 fiber/fascicle centroid approach
- Couppey/Kolbl et al. 2024, PLOS Comp Biol — NRV framework (validated with 1-2 fascicles)
- Blanz et al. 2023, J Neural Eng — pig ASCENT models with 33-63 fascicles (COMSOL)
