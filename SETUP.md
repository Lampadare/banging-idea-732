# Hackathon Environment Setup

## Activate the environment
```bash
eval "$(/opt/homebrew/bin/conda shell.zsh hook)"
conda activate vns
```

## Verify it works
```bash
python -c "import nrv; print(f'NRV {nrv.__version__}')"
```

## Key unit conventions (NRV)
- **Distances**: µm (micrometers)
- **Stimulus current**: µA (microamps) — NOT mA!
- **Time**: ms (milliseconds)
- **Pulse duration**: ms (e.g., 0.2 = 200µs)
- **Fiber diameter**: µm

## Quick reference
```python
import nrv

# Myelinated fiber (MRG model)
axon = nrv.myelinated(y=0, z=0, d=10, L=10000, model='MRG')

# Unmyelinated fiber (Sundt model)  
axon = nrv.unmyelinated(y=0, z=0, d=0.8, L=5000, model='Sundt')

# Point source electrode
elec = nrv.point_source_electrode(x=5000, y=1000, z=0)

# Stimulus: cathodic pulse
stim = nrv.stimulus()
stim.pulse(start=0.1, value=-500, duration=0.2)  # -500uA, 200us

# Attach and simulate
extra_stim = nrv.stimulation('endoneurium_ranck')
extra_stim.add_electrode(elec, stim)
axon.attach_extracellular_stimulation(extra_stim)
results = axon(t_sim=3)
print(results.is_recruited())
```

## Environment details
- conda env: `vns` at `/opt/homebrew/Caskroom/miniforge/base/envs/vns/`
- Python 3.12, NRV 1.3.2, NEURON 9.0.1, dolfinx 0.9.0
- mph is a stub (COMSOL not needed)
- pyeit not installed (EIT not needed)
