# AWS Compute Node - Claude Handoff

Last updated by Codex: 2026-04-12 03:07 UTC / 2026-04-11 20:07 PDT.

## Instance

- Public IPv4: `75.101.200.107`
- Instance id: `i-0b74f2e10aab4d547`
- Region/AZ: `us-east-1` / `us-east-1c`
- SSH user: `ubuntu`
- PEM on Martin's Mac: `/Users/Martin/Downloads/martin-key-1.pem`
- SSH command:

```bash
ssh -i /Users/Martin/Downloads/martin-key-1.pem ubuntu@75.101.200.107
```

- Observed hardware: 32 vCPU, 247 GiB RAM, about 193 GB root disk.
- AWS Console:
  `https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#Instances:`

## Current AWS Run

A 20-fascicle ILU run is already launched and should be left alone unless it fails.

- tmux session: `vns20`
- Working directory: `/home/martin/vns-hack`
- Log: `/home/martin/vns-hack/cloud_20_ilu_20260412_025936.log`
- Script: `/home/martin/vns-hack/fem_20_ilu.py`
- Environment: `/home/ubuntu/envs/vns-explicit`
- Configuration from log:
  - `20 fascicles (ILU solver, NO BoomerAMG)`
  - `Total: 600 fibers`
  - `gmsh: Min=30, Delaunay`
  - Mesh: `61,957 nodes`, `418,479 elements`
  - NRV reports `Number of processes : 16`
- Last observed state:
  - `NRV INFO: FEN4NRV: solving electrical potential`
  - No `Error`, `Killed`, or `Traceback`
  - RSS about `134.7 GB`
  - About `116 GB` still available

Check back about 10-15 minutes after the last status, then every 10-15 minutes while it remains in the FEM solve. The key success line is:

```text
NRV INFO: FEN4NRV: solved in ...
```

## Monitoring Commands

From Martin's Mac:

```bash
ssh -i /Users/Martin/Downloads/martin-key-1.pem ubuntu@75.101.200.107 \
  'cd /home/martin/vns-hack && tail -80 cloud_20_ilu_20260412_025936.log'
```

Look for completion or failures:

```bash
ssh -i /Users/Martin/Downloads/martin-key-1.pem ubuntu@75.101.200.107 \
  'cd /home/martin/vns-hack && grep -E "solved|COMPLETE|Error|Killed|Traceback|Maximum resident" cloud_20_ilu_20260412_025936.log || true'
```

Memory/process check:

```bash
ssh -i /Users/Martin/Downloads/martin-key-1.pem ubuntu@75.101.200.107 \
  'free -h; ps auxww | grep -E "fem_20_ilu|python|gmsh|cc1|dolfin|ffcx" | grep -v grep'
```

Attach to the run:

```bash
ssh -i /Users/Martin/Downloads/martin-key-1.pem ubuntu@75.101.200.107
tmux attach -t vns20
```

Detach without killing it: press `Ctrl-b`, then `d`.

## Setup Already Completed

- Ubuntu packages installed: `build-essential`, `git`, `rsync`, `tmux`, `bzip2`, `ca-certificates`, `libgl1`, `libxrender1`, `libxext6`, `libgomp1`, `time`, `htop`.
- Repo/scripts copied from DeepThought-2 to `/home/martin/vns-hack`.
- Miniforge installed at `/home/ubuntu/miniforge3`.
- DT-2 conda explicit spec copied to `/home/martin/vns-hack/vns-explicit.txt`.
- DT-2 pip freeze copied to `/home/martin/vns-hack/vns-pip-freeze.txt`.
- Working fallback env created at `/home/ubuntu/envs/vns-explicit`.
- Pip packages installed into fallback env, including:
  - `nrv-py==1.3.2`
  - `neuron==9.0.1`
  - `numpy==2.3.5`
  - `scipy==1.17.1`
  - `matplotlib==3.10.8`
  - `pandas==3.0.2`
  - `shapely==2.1.2`
- Imports validated: `numpy`, `scipy`, `dolfinx`, `gmsh`, `petsc4py`, `mpi4py`, `nrv`, `neuron`.
- NRV NEURON `.mod` mechanisms compiled successfully after putting `/home/ubuntu/envs/vns-explicit/bin` on `PATH`.

The earlier slow tar mirror of DT-2's whole conda env into `/home/martin/miniforge3/envs/vns` was stopped after the fallback env became usable. Do not depend on `/home/martin/miniforge3/envs/vns`.

## Why This Run Is Reasonable

- The full 57-fascicle NRV mixed FEM is not viable right now because NRV creates `Nspace = n_internal_boundaries + 1`.
- 57 fascicles means 58 mixed subspaces; that creates a huge PETSc system and OOMs.
- `inbound=False` is not a safe drop-in fix unless volumetric perineurium shells are explicitly meshed and tagged. Otherwise it removes the internal-boundary perineurium model.
- BoomerAMG likely increases peak memory on this problem. The current practical route is P1 elements plus NRV's ILU/default solver path.
- Local 10-fascicle ILU solved FEM in about 531 seconds with about 27 GB RSS after solve.
- DT-2 15-fascicle ILU OOMed around 59 GB.
- AWS has 247 GiB RAM; at last check the 20-fascicle solve was high but still safe at about 135 GB RSS.

## If The Run Finishes

After `FEN4NRV: solved in ...`, expect footprint interpolation and then the NEURON phase. Continue tailing the same log. Check for output files in `/home/martin/vns-hack`:

```bash
ssh -i /Users/Martin/Downloads/martin-key-1.pem ubuntu@75.101.200.107 \
  'cd /home/martin/vns-hack && ls -lhtr | tail -40'
```

If the run produces result files, copy them back to the Mac with `scp` or `rsync` before terminating the instance.

## If The Run Fails

- If it is OOM/killed during FEM solve, 20 fascicles is too large for this exact mesh/solver on the 247 GiB node. Fall back to 10 or 15 fascicles on AWS.
- If it fails on missing NEURON mechanisms, rerun with:

```bash
export PATH=/home/ubuntu/envs/vns-explicit/bin:$PATH
export LD_LIBRARY_PATH=/home/ubuntu/envs/vns-explicit/lib:${LD_LIBRARY_PATH:-}
python -c "import nrv, neuron; print(nrv.__version__, neuron.__version__)"
```

- If it fails on JIT/cache permissions, set:

```bash
export XDG_CACHE_HOME=/home/martin/vns-hack/fem_cache_cloud
export MPLCONFIGDIR=/tmp/mpl-ubuntu
```

## Cost Safety

Terminate the instance from EC2 when the results are copied off. Stopping may still keep EBS storage charges; terminating removes the instance and normally deletes the root EBS volume if it was launched with the default delete-on-termination setting.
