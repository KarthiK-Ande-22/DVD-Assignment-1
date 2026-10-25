#!/usr/bin/env bash
# Run the complete Part C OpenSTA flow from the repository root inside IIC-OSIC-TOOLS.
set -euo pipefail

# Run the required 10 ns baseline and save its detailed timing report.
STA_PERIOD=10.00 STA_REPORT=sta/mult_array_timing_10ns.rpt \
  sta sta/sta.tcl | tee sta/sta_run_T10.log

# Confirm the calculated Tmin rounded to two decimal places (2.60 ns).
STA_PERIOD=2.60 STA_REPORT=sta/mult_array_timing.rpt \
  sta sta/sta.tcl | tee sta/sta_run_Tmin.log
