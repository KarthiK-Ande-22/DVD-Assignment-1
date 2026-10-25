#!/usr/bin/env bash
# Usage (on host, from pnr/): ./run_attempt.sh <run_number> <clock_period_ns>
# Sets CLOCK_PERIOD in config.json, runs LibreLane on SKY130 in the IIC-OSIC-TOOLS container, prints metrics.
set -uo pipefail
n=$1; period=$2
sed -i "s/\"CLOCK_PERIOD\": [0-9.]*/\"CLOCK_PERIOD\": $period/" config.json
ass_dir=$(cd ../.. && pwd)
docker run --rm --user "$(id -u):$(id -g)" -v "$ass_dir":/foss/designs --entrypoint bash \
    hpretl/iic-osic-tools:latest -lc \
    'cd /foss/designs/mult4_2023102009/pnr && export PDK=sky130A STD_CELL_LIBRARY=sky130_fd_sc_hd && librelane config.json' \
    > "logs/run${n}_${period}ns.log" 2>&1
echo "librelane exit code: $?"
grep -E "Flow complete|Setup violations|\* (nom|min|max)_" "logs/run${n}_${period}ns.log"
R=$(ls -d runs/* | tail -1)
echo "Run folder: $R"
python3 show_metrics.py "$R/final/metrics.json"
