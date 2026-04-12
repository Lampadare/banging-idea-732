# AWS Compute Node — Handoff Notes

## Instance Details
- **Public IPv4**: 75.101.200.107
- **SSH user**: ubuntu
- **PEM**: /Users/Martin/Downloads/martin-key-1.pem
- **SSH**: `ssh -i /Users/Martin/Downloads/martin-key-1.pem ubuntu@75.101.200.107`
- **Hardware**: 32 vCPU, 247 GiB RAM, ~193 GB root disk

## Setup Status (by Codex)
- Ubuntu packages installed: build-essential, git, rsync, tmux, etc.
- Repo/scripts copied from DT-2 to `/home/martin/vns-hack`
- Contains: fem_20_ilu.py, fem_15_ilu.py, bovine_geometry.json, etc.
- Miniforge installed at `/home/ubuntu/miniforge3`

### Conda env: `/home/ubuntu/envs/vns-explicit`
- Built from DT-2's explicit spec
- Has: gmsh, petsc4py, mpi4py
- **Missing**: numpy, nrv, neuron (Codex was fixing this)
- dolfinx import fails until numpy installed

### Tar mirror env: `/home/martin/miniforge3/envs/vns`
- Full copy of DT-2's conda env streaming via local relay
- Last seen: ~778M of ~3.2G extracted (may be complete now)

## Why AWS
- 247GB RAM vs 64GB local vs 60GB DT-2
- Should handle 20 fascicles (~59GB ILU peak on Linux)
- Possibly even 30+ fascicles

## Run Commands (once env works)
```bash
# Launch 20-fascicle FEM
cd /home/martin/vns-hack
tmux new-session -d -s vns20 'cd /home/martin/vns-hack && export XDG_CACHE_HOME=/home/martin/vns-hack/fem_cache_cloud && /usr/bin/time -v /home/ubuntu/envs/vns-explicit/bin/python -u fem_20_ilu.py 2>&1 | tee cloud_20_ilu_$(date -u +%Y%m%d_%H%M%S).log'

# Monitor
tmux ls
tail -80 /home/martin/vns-hack/cloud_20_ilu_*.log
```

## Watch Memory
```bash
ssh -i /Users/Martin/Downloads/martin-key-1.pem ubuntu@75.101.200.107 'free -h; ps auxww | grep -E "python|gmsh|cc1|dolfin|ffcx" | grep -v grep'
```

## Key Technical Notes
- AWS Linux PETSc will likely use similar memory to DT-2 (~59GB for 20 fascicles)
- With 247GB headroom, this should complete easily
- JIT options file needed: `{"timeout": 600, "cffi_extra_compile_args": ["-O0", "-g0"]}`
- NRV patches needed: ENT_DOM_offset Electrode=200, Axon res=50
- mph stub needed (same as DT-2 setup)
- dolfinx_jit_options.json must be in working directory

## Scaling Estimates (Linux PETSc)
| Fascicles | Estimated RAM | Fits in 247GB? |
|-----------|--------------|----------------|
| 10 | ~20-30GB | Yes |
| 15 | ~50-60GB | Yes |
| 20 | ~80-100GB | Yes |
| 30 | ~150-180GB | Probably |
| 57 | ~400GB+ | No |
