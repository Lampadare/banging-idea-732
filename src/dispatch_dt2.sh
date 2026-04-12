#!/bin/bash
# DT-2 dispatcher: batches 2, 3, 4, 5, 6 — sequential
set -e
cd /home/martin/vns-hack
export LD_LIBRARY_PATH=~/miniforge3/envs/vns/lib
PYTHON=~/miniforge3/envs/vns/bin/python

echo "=== DT-2 MEGA RUN: batches 2, 3, 4, 5, 6 ==="

for B in 2 3 4 5 6; do
    mkdir -p batches/batch${B}
    echo "--- Batch $B starting ---"
    $PYTHON -u src/fem_6_mixed.py --batch $B 2>&1 | tee batches/batch${B}/run.log
    echo "--- Batch $B done ---"
done

echo "=== DT-2 DONE ==="
ls batches/batch*/results.json
