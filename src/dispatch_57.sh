#!/bin/bash
# Dispatch all 57 fascicles across 3 machines in batches of 6.
#
# Batch 0: fascs 0-5    │ Batch 5: fascs 30-35
# Batch 1: fascs 6-11   │ Batch 6: fascs 36-41
# Batch 2: fascs 12-17  │ Batch 7: fascs 42-47
# Batch 3: fascs 18-23  │ Batch 8: fascs 48-53
# Batch 4: fascs 24-29  │ Batch 9: fascs 54-56 (3 only)
#
# Assignment:
#   LOCAL:  batches 0, 1           (sequential)
#   DT-2:   batches 2, 3, 4        (sequential)
#   AWS:    batches 5,6,7 then 8,9 (2-3 parallel)
#
# Usage: bash src/dispatch_57.sh

set -e

PEM="$HOME/Downloads/martin-key-1.pem"
AWS_HOST="ubuntu@75.101.200.107"
SCRIPT="src/fem_6_mixed.py"

echo "=== DISPATCH 57-FASCICLE COVERAGE ==="
echo "10 batches of 6 across LOCAL + DT-2 + AWS"
echo ""

# --- LOCAL: batches 0, 1 ---
echo "=== LOCAL: batches 0, 1 (sequential) ==="
for B in 0 1; do
    echo "Starting batch $B locally..."
    rm -rf ~/.cache/fenics/ 2>/dev/null
    /opt/homebrew/Caskroom/miniforge/base/envs/vns/bin/python -u $SCRIPT --batch $B 2>&1 | tee "batch${B}_$(date +%Y%m%d_%H%M%S).log"
    echo "Batch $B complete."
done
echo "LOCAL DONE"

# --- DT-2: batches 2, 3, 4 ---
# (launched separately via dispatch_dt2.sh)

# --- AWS: batches 5-9 ---
# (launched separately via dispatch_aws.sh)
