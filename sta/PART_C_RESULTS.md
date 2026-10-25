# Part C - Static Timing Analysis with OpenSTA

## Commands run

Run all commands from the repository root inside the IIC-OSIC-TOOLS container:

```bash
./sta/run_part_c.sh
```

The script first runs the required 10 ns baseline, then runs the Tmin confirmation at 2.60 ns. It uses `sta/sta.tcl`, the SKY130 `tt_025C_1v80` Liberty file, and the synthesized gate-level netlist.

## Calculation

The baseline synchronous setup path has a worst slack of 7.404 ns at a 10.000 ns clock period.

```text
Tmin = T - WNS = 10.000 - 7.404 = 2.596 ns
Fmax = 1000 / Tmin = 1000 / 2.596 = 385.21 MHz
```

The assignment requests a Tmin confirmation rounded to 0.01 ns, therefore the second run uses 2.60 ns. Its slack is +0.004 ns, which confirms setup timing passes.

## Part C results table (completed)

| Metric | Value |
|---|---:|
| Worst slack at T = 10 ns | 7.404 ns |
| Tmin | 2.596 ns |
| Fmax | 385.21 MHz |
| Slack at T = Tmin | +0.004 ns at 2.60 ns (Tmin rounded to 0.01 ns) |
| Critical path start point | `_118_` / `b_reg[0]` launch flip-flop |
| Critical path end point | `_112_` / `p[6]` capture flip-flop |
| Cells on path | 10 total: 2 flip-flops + 8 combinational cells |
| Latency = 2 x Tmin | 5.192 ns (about 5.19 ns) |
| Throughput | 385.21 million results/s |

## Critical-path cells in order

1. `_118_` - `sky130_fd_sc_hd__dfrtp_1` (launch flip-flop)
2. `_083_` - `sky130_fd_sc_hd__and2_0`
3. `_055_` - `sky130_fd_sc_hd__or3_1`
4. `_059_` - `sky130_fd_sc_hd__and4_1`
5. `_070_` - `sky130_fd_sc_hd__o2111a_1`
6. `_076_` - `sky130_fd_sc_hd__o21ai_0`
7. `_090_` - `sky130_fd_sc_hd__xnor3_1`
8. `_091_` - `sky130_fd_sc_hd__maj3_1`
9. `_092_` - `sky130_fd_sc_hd__xor3_1`
10. `_112_` - `sky130_fd_sc_hd__dfrtp_1` (capture flip-flop)

The `synth -flatten` command removed individual `full_adder` instance boundaries. Therefore OpenSTA reports the eight mapped standard cells above, not the original full-adder instance names. This is expected. The final logic cell `_092_` drives `fa33.sum`; the eight mapped cell stages must not be interpreted as eight separate full adders.

## Part C deliverables checklist

- [x] `sta.tcl`: commented OpenSTA script containing all seven required STA steps.
- [x] `mult_array_timing.rpt`: detailed final critical-path report at the 2.60 ns rounded Tmin confirmation.
- [x] Completed Part C results table: included above.
- [x] Critical-path cell list in order: included above.
- [x] `mult_array_timing_10ns.rpt`: detailed 10 ns baseline report used to calculate WNS, Tmin, and Fmax.
- [x] `sta_run_T10.log` and `sta_run_Tmin.log`: terminal logs proving both OpenSTA runs completed.
- [x] `run_part_c.sh`: optional one-command rerun script for both required analyses.

**Submission files required by the assignment:** `sta/sta.tcl` and `sta/mult_array_timing.rpt`. The completed table and critical-path list in this document should be copied into the final report.
