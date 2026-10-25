#!/usr/bin/env bash
# Part D: run LibreLane from CLOCK_PERIOD = 3.5 ns, adding 0.5 ns per run until the flow passes.
# Every run uses the identical command; each attempt is appended to attempts.md.
set -uo pipefail
period=3.5
n=1
echo "# Part D - LibreLane attempts" > attempts.md
echo "" >> attempts.md
echo 'Every run: inside IIC-OSIC-TOOLS, from `pnr/`: `export PDK=sky130A STD_CELL_LIBRARY=sky130_fd_sc_hd; librelane config.json`' >> attempts.md
echo "" >> attempts.md
echo "| Run | CLOCK_PERIOD (ns) | Run folder | setup__ws (ns) | ss-corner slack (ns) | tt-corner slack (ns) | DRC (magic/klayout/route) | LVS | Result |" >> attempts.md
echo "|---|---|---|---|---|---|---|---|---|" >> attempts.md
while [ "$n" -le 12 ]; do
    ./run_attempt.sh "$n" "$period" > "logs/summary_run${n}.txt"
    R=$(ls -d runs/* | tail -1)
    if grep -q "Flow complete" "logs/run${n}_${period}ns.log"; then result="PASS"; else result="FAIL"; fi
    python3 - "$R/final/metrics.json" "$n" "$period" "$(basename "$R")" "$result" >> attempts.md <<'PY'
import json, sys
m = json.load(open(sys.argv[1])); n, p, r, res = sys.argv[2:]
f = lambda k: f"{m[k]:+.3f}" if m.get(k) is not None else "-"
print(f"| {n} | {p} | {r} | {f('timing__setup__ws')} | {f('timing__setup__ws__corner:nom_ss_100C_1v60')} | "
      f"{f('timing__setup__ws__corner:nom_tt_025C_1v80')} | {m.get('magic__drc_error__count')}/"
      f"{m.get('klayout__drc_error__count')}/{m.get('route__drc_errors')} | {m.get('design__lvs_error__count')} | {res} |")
PY
    tail -1 attempts.md
    [ "$result" = "PASS" ] && break
    period=$(python3 -c "print($period + 0.5)")
    n=$((n + 1))
done
