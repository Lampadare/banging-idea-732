#!/bin/bash
# Local dispatcher: batches 0, 1 — sequential
set -e
cd "$(dirname "$0")/.."
PYTHON=/opt/homebrew/Caskroom/miniforge/base/envs/vns/bin/python

echo "=== LOCAL MEGA RUN: batches 0, 1 ==="

for B in 0 1; do
    mkdir -p batches/batch${B}
    echo "--- Batch $B starting ---"
    $PYTHON -u src/fem_6_mixed.py --batch $B 2>&1 | tee batches/batch${B}/run.log
    echo "--- Batch $B done ---"
done

echo "=== LOCAL DONE ==="
ls batches/batch*/results.json
