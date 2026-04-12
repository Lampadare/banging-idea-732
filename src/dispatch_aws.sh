#!/bin/bash
# AWS dispatcher: batches 7, 8, 9 — all 3 parallel
set -e
cd /home/martin/vns-hack
PYTHON=/home/ubuntu/envs/vns-explicit/bin/python

echo "=== AWS MEGA RUN: batches 7, 8, 9 ==="

mkdir -p batches/batch7 batches/batch8 batches/batch9

$PYTHON -u src/fem_6_mixed.py --batch 7 2>&1 | tee batches/batch7/run.log &
PID7=$!
$PYTHON -u src/fem_6_mixed.py --batch 8 2>&1 | tee batches/batch8/run.log &
PID8=$!
$PYTHON -u src/fem_6_mixed.py --batch 9 2>&1 | tee batches/batch9/run.log &
PID9=$!

echo "PIDs: $PID7 $PID8 $PID9"
wait $PID7 $PID8 $PID9
echo "=== AWS DONE ==="
ls batches/batch*/results.json
