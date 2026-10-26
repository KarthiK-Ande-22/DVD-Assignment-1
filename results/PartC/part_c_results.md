# Part C - Static Timing Analysis with OpenSTA

OpenSTA 3.1.0, SKY130 `sky130_fd_sc_hd`, typical corner `tt_025C_1v80`, netlist `synth/mult_array_netlist.v`.

## Commands (inside IIC-OSIC-TOOLS, from the repository root)

```bash
sta sta/sta.tcl                     # T = 10.00 ns (default in sta.tcl)
STA_PERIOD=2.60 sta sta/sta.tcl     # T = Tmin rounded to 0.01 ns
```

`sta/sta.tcl` runs the 7 required steps: `read_liberty $lib`, `read_verilog` + `link_design mult_array`,
`create_clock -name clk -period T [get_ports clk]`, `set_input_delay 1.0`, `set_output_delay 1.0`,
`report_worst_slack -max`, `report_checks -path_delay max -digits 3 > sta/mult_array_timing.rpt`.

## Part C results table

| Metric | Value |
|:---:|:---:|
| Worst slack at T = 10 ns (ns) | 7.404 |
| Tmin (ns) | 2.596 |
| Fmax (MHz) | 385.21 |
| Slack at T = Tmin (ns) | +0.004 (at 2.60 ns) |
| Critical path start point | b_reg[0] (flip-flop _118_) |
| Critical path end point | p[6] (flip-flop _112_) |
| Number of cells on the critical path | 10 (2 flip-flops + 8 logic cells) |
| Latency (ns) = 2 x Tmin | 5.192 |
| Throughput (million results per second) | 385.21 |

## Task 1 - Tmin and Fmax

Run 1, T = 10.00 ns: worst setup slack WNS = **7.404 ns** (data arrival 2.460 ns, required 9.865 ns).

```text
Tmin = T - WNS   = 10.000 - 7.404 = 2.596 ns
Fmax = 1000/Tmin = 1000 / 2.596   = 385.21 MHz
```

Run 2, T = Tmin rounded to 0.01 ns = **2.60 ns**: slack = 2.465 - 2.460 = **+0.004 ns** (MET, close to 0),
which confirms Tmin.

```text
Latency    = 2 x Tmin = 2 x 2.596 = 5.192 ns   (input register -> output register, 2 clock cycles)
Throughput = Fmax     = 385.21 million results per second (one result per clock cycle)
```

## Task 2 - Critical path

- **Start point:** `_118_` = input-register flip-flop `b_reg[0]` (D = `b[0]`)
- **End point:** `_112_` = output-register flip-flop `p[6]` (D = `fa33.sum` = s3[3], the sum of FA[3,3])

Cells in order (from `sta/mult_array_timing.rpt`; roles traced in `synth/mult_array_netlist.v`):

| # | Instance | Cell | Delay (ns) | Arrival (ns) | Role in the RTL |
|---|---|---|---|---|---|
| 1 | `_118_` | `dfrtp_1` | 0.395 | 0.395 | launch flip-flop, Q = b_reg[0] |
| 2 | `_083_` | `and2_0` | 0.212 | 0.607 | AND gate pp0[0] = a_reg[0] & b_reg[0] |
| 3 | `_055_` | `or3_1` | 0.361 | 0.968 | row-1 carry logic (merged) |
| 4 | `_059_` | `and4_1` | 0.215 | 1.183 | row-1 carry logic merged with an a_reg[1] AND |
| 5 | `_070_` | `o2111a_1` | 0.234 | 1.417 | carry logic merged with pp2[2] = a_reg[2] & b_reg[2] |
| 6 | `_076_` | `o21ai_0` | 0.216 | 1.634 | carry-chain logic |
| 7 | `_090_` | `xnor3_1` | 0.274 | 1.907 | full-adder sum function |
| 8 | `_091_` | `maj3_1` | 0.375 | 2.282 | full-adder carry function |
| 9 | `_092_` | `xor3_1` | 0.178 | 2.460 | full-adder sum of FA[3,3] (s3[3]) |
| 10 | `_112_` | `dfrtp_1` | setup 0.135 | - | capture flip-flop, Q = p[6] |

## Task 3 - Full-adder cells vs the 2N = 8 estimate

- 8 logic cells are on the path; **7 of them come from full-adder logic**:
  3 pure full-adder functions (`xnor3` sum, `maj3` carry, `xor3` sum of FA[3,3]) and
  4 compound gates (`or3`, `and4`, `o2111a`, `o21ai`) that implement the ripple-carry logic
  merged with partial-product AND gates. Only `_083_` is a plain AND gate.
- This is close to the estimate of about **2N = 8 full-adder delays**. The match is approximate because
  `synth -flatten` removes the `full_adder` boundaries and ABC folds AND gates and parts of several
  full adders into single compound cells, while a 3-input `xor3`/`maj3` replaces the two-level
  XOR / AND-OR of a textbook full adder.
- Logic delay = 2.460 - 0.395 = 2.065 ns over 8 cells, about 0.26 ns per cell.

## Other observations

- **Asynchronous reset recovery check:** `rst_n` to the flip-flop `RESET_B` pins has slack +9.228 ns at
  T = 10 ns and +1.828 ns at T = 2.60 ns. It is not the limiting path.
- **Pre-layout numbers:** this analysis uses an ideal clock (no clock-tree delay or skew) and no wire
  delay. After place and route (Part D), wire RC and the clock tree add delay, so the post-route Fmax is lower.
