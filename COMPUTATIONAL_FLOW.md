# Bovine VNS — Computational Flow

## Overview

Full-nerve FEM simulation of selective vagus nerve stimulation on bovine vagosympathetic trunk geometry. 57 fascicles from porcine morphometry (SPARC Dataset 64, sample P12-1) scaled to bovine dimensions, with mixed vagal/sympathetic fiber populations.

## Pipeline

```
SPARC pig morphometry (P12-1, 57 fascicles)
    │
    ▼  src/bovine_geometry.py
PCA-aligned, scaled ×1.26, collision-resolved (75μm gaps)
    │
    ▼  data/bovine_geometry.json
57 fascicles in 5000×3571μm elliptical boundary
    │
    ▼  src/fem_6_mixed.py --batch N
    │
    ├── Phase 1: FEM solve (dolfinx/PETSc)
    │     Laplace equation for extracellular voltage
    │     Mixed-element formulation: N_subspaces = N_fascicles + 1
    │     P2 Lagrange elements, Delaunay mesh
    │     Bipolar cuff electrode at nerve center
    │     Output: voltage field V(x,y,z) at 1 mA
    │
    ├── Phase 1b: Voltage field sampling
    │     57 centroid profiles V(x) at each fascicle position
    │     80×80 cross-section grid at cuff center
    │     64×96×96 3D volume grid
    │
    ├── Phase 1c: Mesh export
    │     VTX (.bp/) for ParaView
    │     XDMF mesh
    │     Gmsh .msh with physical groups
    │
    ├── Phase 2: NEURON amplitude sweep
    │     20 amplitudes (100-1000 μA)
    │     Footprint caching: V(x) × amplitude = extracellular potential
    │     Each fiber: solve cable equation, check recruitment
    │     Incremental JSON saves after each amplitude
    │
    ▼  batches/batchN/results.json + voltages + grid + mesh
```

## Batching Strategy

57 fascicles ÷ 6 per batch = 10 batches. 6-fascicle batches are the proven sweet spot:
- 7 mixed-element subspaces (manageable for PETSc)
- ~15-20 min per batch end-to-end
- ~2-5 GB RAM on Mac, ~20-30 GB on Linux

```
Batch 0: fascicles  0- 5    LOCAL
Batch 1: fascicles  6-11    LOCAL
Batch 2: fascicles 12-17    DT-2
Batch 3: fascicles 18-23    DT-2
Batch 4: fascicles 24-29    DT-2
Batch 5: fascicles 30-35    DT-2
Batch 6: fascicles 36-41    DT-2
Batch 7: fascicles 42-47    AWS (parallel)
Batch 8: fascicles 48-53    AWS (parallel)
Batch 9: fascicles 54-56    AWS (parallel)
```

## Compute Nodes

| Node | RAM | CPUs | Role | Per-batch time |
|------|-----|------|------|----------------|
| Mac M2 Max | 64 GB | 12 | Local, 2 batches seq | ~22 min |
| DT-2 London | 60 GB | 32 | 5 batches seq | ~12 min |
| AWS r5.8xlarge | 247 GB | 32 | 3 batches parallel | ~20 min |

## Fiber Populations

Each fascicle: 50 fibers, 85% vagal + 15% sympathetic.

- **Vagal myelinated** (A/B fibers): 30% of vagal, 2-16 μm diameter. Ochoa_M stats. Target for therapeutic VNS.
- **Vagal unmyelinated** (C fibers): 70% of vagal, 0.3-1.5 μm. Ochoa_U stats. High threshold.
- **Sympathetic proxy** (C fibers): 15% total, 0.3-1.2 μm. Off-target group; co-activation is treated as side-effect risk.

Population seeds use global fascicle ID (`seed=fg["id"]`) for reproducibility across batches.

### NEURON Axon Models

The mixed-population labels are analysis labels, not separate NEURON electrophysiology models. NRV receives only each axon's numeric `type` and `diameter`:

- `type == 0`: unmyelinated axon, NRV default `Rattay_Aberham` model.
- `type == 1`: myelinated axon, NRV default `MRG` model.

So the current pipeline has two axon model classes, not one generic cable model, but it does **not** have separate vagal-specific and sympathetic-specific membrane models.

Current population semantics:

- Vagal fibers are sampled with `nrv.create_axon_population(..., percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U")`.
- Sympathetic fibers are modeled as small unmyelinated C-fiber-like axons: diameters are sampled uniformly from 0.3-1.2 μm and their type is forced to `0`.
- Therefore vagal unmyelinated and sympathetic-proxy fibers both use the same unmyelinated `Rattay_Aberham` model. They differ by label, diameter distribution, and fascicle geometry, not by a separate sympathetic ion-channel model.
- Vagal myelinated fibers use the `MRG` model and Ochoa_M diameters.

The most precise scientific wording is: **sympathetic fibers are represented as small unmyelinated C-fiber-like axons, tagged as sympathetic for recruitment/selectivity analysis**. Selectivity in these runs comes from field geometry, fascicle location, fiber diameter, and myelinated vs unmyelinated status.

### Recruitment Accounting

NEURON activation is not computed from a simple voltage threshold in the main batch runs. For each amplitude, NRV applies the cached extracellular footprint to every axon, solves the cable equation, and `axon.is_recruited()` reports whether that axon fired.

The result extraction then counts recruited axons into three reporting groups:

- `sympathetic`: any axon with our external sympathetic label.
- `vagal_myelinated`: non-sympathetic axons whose NRV result reports `myelinated == True`.
- `vagal_unmyelinated`: non-sympathetic axons whose NRV result is not myelinated.

This means sympathetic recruitment is a label-based reporting category over small unmyelinated axons. It is not a distinct sympathetic NEURON model.

## Output Files (per batch)

```
batches/batchN/
    results.json          Recruitment per fascicle per amplitude
    57voltages.npz        V(x) at all 57 centroids from this batch's FEM
    grid.npz              2D voltage cross-section (80×80)
    volume_field.npz      3D voltage grid (64×96×96)
    fem_field.bp/         VTX field for ParaView
    mesh.xdmf + .h5       Tetrahedral mesh
    gmsh.msh              Gmsh mesh with physical groups
    run.log               Full console output
```

## Merge & Plot

```bash
python src/merge_batches.py              # combines batches/batch0-9/
python src/plot_plotly.py merged/results.json   # generates all figures
```

Merge handles partial results — if only 7/10 batches completed, the other 3 fascicle sets show as `source: "missing"` with zero recruitment. Voltage profiles and grids are also merged (averaged for grids, union for centroids).

## Key Findings That Shaped This Pipeline

### The Mixed-Element Scaling Wall
NRV's perineurium formulation creates N+1 function subspaces. This limits per-batch fascicle count:
- 6 fascicles (7 subspaces): ~2 GB Mac, ~20 GB Linux. Fast.
- 10 fascicles (11 subspaces): ~22 GB Mac, ~100+ GB Linux. Slow footprints.
- 15+ fascicles: PETSc `MatXIJSetPreallocation` error.

Solution: batch in groups of 6.

### The `fill(data=...)` Argument Order Bug
NRV expects `data=(types, diameters)` or `data={"types": t, "diameters": d}`. We had `(diameters, types)` backwards for weeks. This caused:
- `L must be > 0` crashes (myelinated axons with diameter 0 or 1)
- Footprint OOM (nonsense axon morphologies consuming 100+ GB)
- Hours of debugging attributed to geometry, element type, mesh resolution

Fix: `fasc.fill(data={"types": types, "diameters": diams})`.

### P2 vs P1 Elements
P1 (linear) was our "optimization" — fewer DOFs, should be faster. In practice, P2 (quadratic, default) produces faster footprint interpolation because the smoother solution enables more efficient point evaluation. The only successful end-to-end run used P2. All P1 runs hung or crashed in footprints.

### Platform Memory Divergence
Same problem, same solver: Linux PETSc uses 3-5× more RAM than Mac for ILU preconditioning. Cause unknown — likely different matrix ordering or MPI configuration.

### Voltage Field Sampling API
`model.get_potentials(x_array, y_scalar, z_scalar)` — y and z must be **scalars**, not arrays. Returns `(len(x), N_electrodes)` 2D array. Passing arrays creates ragged structures that silently zero out.

## Software Stack

- NRV 1.3.2 (nerve simulation framework)
- NEURON 9.0.1 (cable equation solver)
- dolfinx 0.9.0 / FEniCS (FEM)
- PETSc (linear algebra, CG+ILU)
- gmsh (mesh generation)
- Python 3.12, conda

## References

- Pelot et al. 2020, Front. Neurosci. — pig vagus morphometry (SPARC Dataset 64)
- Ciotti et al. 2024, Nature Comms (VaStim) — 9-fascicle selective VNS model
- Zanos et al. 2025, Nature Comms — 1 fiber/fascicle centroid approach
- Couppey/Kolbl et al. 2024, PLOS Comp Biol — NRV framework
- Blanz et al. 2023, J Neural Eng — pig ASCENT models with 33-63 fascicles
