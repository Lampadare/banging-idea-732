# Next Steps Plan

## Status
- [x] Environment setup (Mac + DT-2, NRV 1.3.2, NEURON, dolfinx 0.9.0)
- [x] SPARC pig vagus morphometry downloaded (9 samples, 422 fascicles)
- [x] Pig→bovine geometry transform (P12-1, PCA-aligned, 75μm gaps)
- [x] Mixed vagal/sympathetic population model (85/15%)
- [x] FEM optimizations (footprint caching, JIT -O0, P1 elements)
- [x] 6-fascicle optimized sweep (20 amplitudes, recruitment data)
- [x] 10-fascicle FEM solve on bovine geometry (531s, SUCCESSFUL)
- [ ] 10-fascicle amplitude sweep results + plots
- [ ] Electrode configuration comparison (bipolar vs steered)
- [ ] Extrapolation to 57 fascicles
- [ ] Publication-quality figures
- [ ] Dash dashboard (stretch)

## Immediate (do now)

### 1. Plot 10-fascicle results
- `src/plot_bovine_results.py` is ready
- Generates: activation maps, recruitment curves, selectivity index
- Run as soon as `bovine_10_results.json` drops

### 2. Three-config electrode comparison
Same 10-fascicle geometry, three electrode configs:
- **Monopolar**: single contact active
- **Bipolar**: two ring contacts (current config)
- **Steered**: CUFF_MP_electrode with 8 contacts, weighted current steering
Each needs ONE FEM solve (~9 min) then fast amplitude sweep
- Total: ~30 min for all three configs

### 3. Extrapolate to 57 fascicles
- Use the FEM voltage field from the 10-fascicle model
- Interpolate potentials at the 47 un-modeled fascicle positions
- Run NEURON (analytical, no new FEM solve) on those fibers
- Gives full 57-fascicle activation map from a single FEM solve

## Figures Needed for Pitch

### Hero Figure (slide 2)
Three-panel cross-section: monopolar | bipolar | steered
- All 57 fascicles colored by activation (10 FEM + 47 extrapolated)
- Electrode contacts highlighted
- Annotation: selectivity metrics

### Proof Figure (slide 3)  
Recruitment curves: vagal myelinated vs unmyelinated vs sympathetic
- Therapeutic window shaded
- Selectivity index subplot

### Context Figure (slide 1)
Nerve cross-section anatomy + cuff placement
- Already have: plots 08, 10, 12, 14

## DT-2 Notes
- DT-2 Linux PETSc uses ~5× more RAM than Mac for same ILU solve
- Max feasible on DT-2: ~6 fascicles (proven at 2GB)
- Use DT-2 for NEURON-only sweeps (analytical stimulation, 28 cores)
- Use local Mac for FEM solves (64GB, handles 10 fascicles at 22GB)

## Key Commands

### Activate environment
```bash
# Mac
eval "$(/opt/homebrew/bin/conda shell.zsh hook)" && conda activate vns

# DT-2
export LD_LIBRARY_PATH=~/miniforge3/envs/vns/lib
~/miniforge3/envs/vns/bin/python script.py
```

### Run FEM
```bash
python -u src/fem_bovine_20.py  # uses representative_subset from bovine_geometry.json
```

### Plot results
```bash
python src/plot_bovine_results.py bovine_10_results.json
```

## Architecture Notes (for future sessions)
- NRV mixed-element formulation limits FEM to ~10 fascicles on 64GB
- `inbound=False` fix would enable 57+ fascicles (single function space)
- ASCENT/COMSOL handles 57 fascicles natively (different perineurium model)
- CoreNEURON GPU not viable (extracellular mechanism unsupported)
- Footprint caching is the #1 optimization (1 FEM solve for any amplitude sweep)
