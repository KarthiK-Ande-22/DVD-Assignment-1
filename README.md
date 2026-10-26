# 4-bit Array Multiplier - RTL to GDSII (SKY130)

Digital VLSI Design assignment: a 4 x 4 unsigned array multiplier (`mult_array`) written in Verilog,
verified, synthesized, timed and taken to a GDSII layout with open-source tools on SkyWater SKY130.

## Team

| Name | Roll number |
|------|-------------|
| Ande Karthik | 2023102009 |
| Kalluri Roshan Lal | 2023102010 |

## Summary of results

| Part | Key result | Details |
|---|---|---|
| A - RTL + verification | `PASS: 256 vectors checked, 0 errors`; error test `FAIL: 256 vectors checked, 95 errors` | `results/PartA/` |
| B - Synthesis | 73 cells, 16 flip-flops, 805.77 um^2 (flip-flops 49.69 %); netlist simulation PASS | `results/PartB/` |
| C - STA | WNS 7.404 ns at 10 ns, Tmin 2.596 ns, Fmax 385.21 MHz | `results/PartC/` |
| D - RTL to GDSII | passes at CLOCK_PERIOD 7.0 ns (8 runs), setup slack +0.364 ns, post-route Fmax 150.70 MHz, 0 DRC, 0 LVS | `results/PartD/`, `pnr/` |

## Environment

- Host: Ubuntu 24.04.4 LTS, Docker 29.1.3
- All tools run inside the IIC-OSIC-TOOLS Docker image `hpretl/iic-osic-tools:latest`:
  Icarus Verilog 14.0 (devel), GTKWave 4.0.0-prealpha, Yosys 0.70, OpenSTA 3.1.0, LibreLane 3.1.0.dev3,
  KLayout, Magic, Netgen
- PDK: `sky130A` at `$PDK_ROOT=/foss/pdks`, standard-cell library `sky130_fd_sc_hd`,
  Liberty corner `tt_025C_1v80`
- The container's **default PDK is IHP `ihp-sg13g2`**, so SKY130 is selected explicitly
  (`$PDK_ROOT/sky130A/...` paths in Parts A-C, `PDK=sky130A` in Part D)

### Opening the container

The parent folder of this repository is mounted as `/foss/designs`:

```bash
cd ~/Documents/sem_7/DvD/Ass            # folder that contains mult4_2023102009/
docker run --rm -it --user $(id -u):$(id -g) -v "$PWD":/foss/designs \
  --entrypoint bash hpretl/iic-osic-tools:latest -l
cd /foss/designs/mult4_2023102009       # all commands below run from here unless stated
```

For the GUI tools (GTKWave, KLayout) the X display is passed to the container:

```bash
xhost +local:docker
docker run --rm -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
  --user $(id -u):$(id -g) -v "$PWD":/foss/designs \
  --entrypoint bash hpretl/iic-osic-tools:latest -l
```

## Repository structure

```text
mult4_2023102009/
|-- README.md
|-- rtl/      full_adder.v, mult_array.v
|-- tb/       tb_mult.v
|-- synth/    synth.tcl, mult_array_netlist.v, mult_array_stat.rpt  (+ yosys_run.log, gate_level_simulation.txt)
|-- sta/      sta.tcl, mult_array_timing.rpt                        (+ 10 ns report, logs, run_part_c.sh)
|-- pnr/      config.json, metrics.json, mult_array.gds             (+ run scripts, attempts.md, screenshots)
|-- results/  PartA/ PartB/ PartC/ PartD/ - logs, tables, screenshots and write-ups for every task
`-- report/   report.pdf
```

`pnr/runs/` (LibreLane run folders, about 700 MB) is not committed, as required.

---

## Part A - RTL design and verification

### Task 1 - Full adder: `rtl/full_adder.v`
Module `full_adder`, ports `a`, `b`, `cin` -> `sum`, `cout`, written with `assign` statements:
`sum = a ^ b ^ cin`, `cout = (a & b) | (b & cin) | (a & cin)`.

### Task 2 - Array multiplier: `rtl/mult_array.v`
Module `mult_array` with ports `clk`, `rst_n`, `a[3:0]`, `b[3:0]`, `p[7:0]`.
16 AND gates (`pp0`..`pp3`), 12 `full_adder` instances (`fa10`..`fa33`) wired as in Section 2,
input registers `a_reg`, `b_reg` and output register `p` with asynchronous active-low reset
(16 flip-flops, latency 2 cycles). The `*` operator is not used.

### Task 3 - Testbench: `tb/tb_mult.v`
10 ns clock, `rst_n` low for the first 2 cycles, all 256 input pairs, waits the 2-cycle latency,
compares with `a * b`, prints every mismatch and one summary line, writes `mult.vcd`.

### Task 4 - Simulate until PASS
```bash
iverilog -g2012 -o sim tb/tb_mult.v rtl/full_adder.v rtl/mult_array.v
vvp sim
```
Result: `PASS: 256 vectors checked, 0 errors`
-> `results/PartA/pass_line.txt`, full log `results/PartA/1_rtl_sim_pass.log`

### Task 5 - Hand-worked example and waveform
Roll number 2023102009 -> A = 9 + 5 = **14** (`1110`), B = **7** (`0111`), P = **98** (`0110 0010`).

- Hand-worked shift-and-add and the row-by-row array computation: `results/PartA/hand_example.txt`
- Waveform: the testbench applies a = 14, b = 7 at 4650 ns; the input registers capture them at the
  rising edge at 4655 ns and `p` = 98 appears at the next rising edge, 4665 ns (2-cycle latency).
  ```bash
  gtkwave mult.vcd      # signals clk, rst_n, a, b, p; view 4640-4700 ns; screenshot taken
  ```
  Screenshots: `results/PartA/waveform.png`, `results/PartA/latency_marking_raw.png`;
  annotated with the 2-cycle latency: `results/PartA/latency_marking.png`

### Task 6 - Check that the testbench catches errors
```bash
sed -i 's/assign sum  = a ^ b ^ cin;/assign sum  = a ^ b;/' rtl/full_adder.v    # inject the bug
iverilog -g2012 -o sim tb/tb_mult.v rtl/full_adder.v rtl/mult_array.v
vvp sim
git checkout rtl/full_adder.v                                                  # undo
git diff rtl/full_adder.v                                                      # empty = restored
iverilog -g2012 -o sim tb/tb_mult.v rtl/full_adder.v rtl/mult_array.v && vvp sim   # PASS again
```
Result: `FAIL: 256 vectors checked, 95 errors`
-> `results/PartA/fail_line.txt`, full log (diff, all mismatches, revert, PASS) `results/PartA/2_fail_test.log`

### Block diagram
`results/PartA/block_diagram.png` - bit-weight-aligned view: 16 AND gates, 12 full adders in 3
ripple-carry rows, input registers `a_reg`/`b_reg` and output register `p` (drawn with Python matplotlib
from the connections in `rtl/mult_array.v`).

---

## Part B - Logic synthesis with Yosys

### Task 1 - Write and run `synth/synth.tcl`
The script sets `$lib` to `sky130_fd_sc_hd__tt_025C_1v80.lib` and runs the 7 required steps:
`read_verilog`, `synth -top mult_array -flatten`, `dfflibmap -liberty $lib`, `abc -liberty $lib`,
`opt_clean -purge`, `tee -o synth/mult_array_stat.rpt stat -liberty $lib`,
`write_verilog -noattr synth/mult_array_netlist.v`.
```bash
yosys -c synth/synth.tcl
```
Outputs: `synth/mult_array_netlist.v`, `synth/mult_array_stat.rpt`; log `results/PartB/1_yosys_synth.log`

### Task 2 - Results table (from `synth/mult_array_stat.rpt`)

| Metric | Value |
|:---:|:---:|
| Total number of cells | 73 |
| Number of flip-flops | 16 (`dfrtp_1`) |
| Total cell area (um^2) | 805.77 |
| Flip-flop area (um^2) | 16 x 25.024 = 400.38 |
| Flip-flop area (% of total) | 49.69 % |
| 3 most-used cell types | dfrtp_1 x16, nand2_1 x11, a21oi_1 x4 |
| Netlist simulation result | PASS: 256 vectors checked, 0 errors |

-> `results/PartB/results_table.md`, notes in `results/PartB/part_b_results.md`

### Task 3 - Simulate the synthesized netlist
```bash
CELLS=$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/verilog
iverilog -g2012 -DFUNCTIONAL -DUNIT_DELAY=#1 -o gls \
  tb/tb_mult.v $CELLS/primitives.v $CELLS/sky130_fd_sc_hd.v synth/mult_array_netlist.v
vvp gls
```
Result: `PASS: 256 vectors checked, 0 errors`
-> `results/PartB/gls_pass_line.txt`, log `results/PartB/2_gate_level_sim.log`

---

## Part C - Static timing analysis with OpenSTA

`sta/sta.tcl` runs the 7 required steps: `read_liberty $lib`, `read_verilog` + `link_design mult_array`,
`create_clock -name clk -period T [get_ports clk]`, `set_input_delay 1.0`, `set_output_delay 1.0`,
`report_worst_slack -max`, `report_checks -path_delay max -digits 3 > sta/mult_array_timing.rpt`.
The period defaults to 10 ns and is overridden with `STA_PERIOD`.

### Task 1 - Tmin and Fmax
```bash
sta -exit sta/sta.tcl                       # T = 10.00 ns
STA_PERIOD=2.60 sta -exit sta/sta.tcl       # T = Tmin rounded to 0.01 ns; writes sta/mult_array_timing.rpt
```
- T = 10 ns: worst slack WNS = **7.404 ns**
- Tmin = 10 - 7.404 = **2.596 ns**, Fmax = 1000 / 2.596 = **385.21 MHz**
- T = 2.60 ns: slack = **+0.004 ns** (close to 0)

Logs and reports: `results/PartC/1_sta_T10ns.log`, `results/PartC/2_sta_Tmin_2.60ns.log`,
`results/PartC/mult_array_timing_T10ns.rpt`, `results/PartC/mult_array_timing_Tmin_2.60ns.rpt`

### Task 2 - Critical path (from `sta/mult_array_timing.rpt`)
- Start point: `_118_` = input register `b_reg[0]`; end point: `_112_` = output register `p[6]`
  (D = `fa33.sum`)
- Cells in order: `dfrtp_1` -> `and2_0` -> `or3_1` -> `and4_1` -> `o2111a_1` -> `o21ai_0` -> `xnor3_1`
  -> `maj3_1` -> `xor3_1` -> `dfrtp_1` (10 cells: 2 flip-flops + 8 logic cells)

### Task 3 - Full-adder cells vs 2N = 8
7 of the 8 logic cells come from full-adder logic (`xnor3`, `maj3`, `xor3` plus 4 merged carry gates),
close to the 2N = 8 estimate. Flattening and ABC merge AND gates and parts of several full adders into
compound cells, so the match is approximate.

### Results table

| Metric | Value |
|:---:|:---:|
| Worst slack at T = 10 ns (ns) | 7.404 |
| Tmin (ns) | 2.596 |
| Fmax (MHz) | 385.21 |
| Slack at T = Tmin (ns) | +0.004 (at 2.60 ns) |
| Critical path start point | b_reg[0] (_118_) |
| Critical path end point | p[6] (_112_) |
| Number of cells on the critical path | 10 |
| Latency (ns) = 2 x Tmin | 5.192 |
| Throughput (million results per second) | 385.21 |

-> full write-up `results/PartC/part_c_results.md`

---

## Part D - Physical design: RTL to GDSII with LibreLane

`pnr/config.json` contains exactly the 6 required keys: `DESIGN_NAME`, `VERILOG_FILES`, `CLOCK_PORT`,
`CLOCK_PERIOD`, `FP_SIZING` = `"absolute"`, `DIE_AREA` = `[0, 0, 150, 150]`.

### Task 1 - Run the flow until 0 DRC, 0 LVS and setup slack >= 0
Start period = 1.2 x Tmin = 1.2 x 2.596 = 3.115 ns, rounded up to the next 0.5 ns = **3.5 ns**;
after every failing run CLOCK_PERIOD is increased by 0.5 ns.

Command for each run (inside the container, from `pnr/`):
```bash
cd pnr
export PDK=sky130A STD_CELL_LIBRARY=sky130_fd_sc_hd     # select SKY130
librelane config.json
```
All attempts were run from the host with one script, which sets `CLOCK_PERIOD`, runs the command
above in the container through `pnr/run_attempt.sh`, and stops at the first passing run:
```bash
cd pnr
./run_all.sh          # 3.5, 4.0, ... ns; writes pnr/attempts.md
```

Every attempt (`setup__ws` = worst over all 9 signoff corners; the limiting corner is always
`ss_100C_1v60`, 1.60 V, 100 C):

| Run | CLOCK_PERIOD (ns) | Setup slack (ns) | Hold slack (ns) | DRC | LVS | Result |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 3.5 | -2.154 | +0.100 | 0 | 0 | FAIL (setup) |
| 2 | 4.0 | -1.654 | +0.147 | 0 | 0 | FAIL (setup) |
| 3 | 4.5 | -1.154 | +0.147 | 0 | 0 | FAIL (setup) |
| 4 | 5.0 | -0.654 | +0.147 | 0 | 0 | FAIL (setup) |
| 5 | 5.5 | -0.155 | +0.147 | 0 | 0 | FAIL (setup) |
| 6 | 6.0 | -0.107 | +0.148 | 0 | 0 | FAIL (setup) |
| 7 | 6.5 | -0.136 | +0.141 | 0 | 0 | FAIL (setup) |
| 8 | **7.0** | **+0.364** | +0.141 | 0 | 0 | **PASS** |

Per-attempt configs and metrics: `results/PartD/attempts/` (`config_3p5ns.json` ... `metrics_7ns.json`);
summary `pnr/attempts.md`.

Copy the final results (run 8):
```bash
cp runs/RUN_2026-10-25_08-00-39/final/metrics.json metrics.json
cp runs/RUN_2026-10-25_08-00-39/final/gds/mult_array.gds mult_array.gds
```

### Task 2 - Results table (from `pnr/metrics.json`)
```bash
python3 show_metrics.py metrics.json      # instance__count, core__area, wirelength, setup__ws, drc, lvs
```

| Metric | Value |
|:---:|:---:|
| CLOCK_PERIOD used (ns) | 7.0 |
| Number of runs needed | 8 |
| Core area (um^2) | 17759.5 (die 22500) |
| Cells after synthesis (from Part B) | 73 |
| Cells after place and route | 1895 |
| Kinds of cells added | buffers (22), tap (245), decap (1314), fill (247) |
| Wirelength (um) | 2362 |
| Setup slack (ns) | +0.364 |
| Post-route Fmax (MHz) | 150.70 |
| Fmax from Part C (MHz) | 385.21 |
| DRC errors | 0 |
| LVS errors | 0 |

### Task 3 - Post-route Fmax vs Part C
Post-route Fmax = 1000 / (7.0 - 0.364) = **150.70 MHz**, about 2.6x below Part C (385.21 MHz):
the slow signoff corner costs about 2x (the same layout gives 302.9 MHz at the typical corner), and
wire RC, clock uncertainty (0.25 ns), clock skew and slower clk -> Q add 0.705 ns even at the same corner.

### Task 4 - Cells added by place and route
73 cells after synthesis -> 1895 after place and route. Added: `buf` 22 (17 I/O port buffers,
2 reset-fanout buffers, 3 clock-tree buffers),
`tap` 245, `decap` 1314, `fill` 247 (from the LibreLane cell-frequency report).

### Task 5 - Layout screenshots
```bash
cd pnr
klayout -zz -r render_layout.py                                                # renders the screenshots
klayout -l $PDK_ROOT/sky130A/libs.tech/klayout/tech/sky130A.lyp mult_array.gds  # interactive view
```
- `results/PartD/layout_whole_die.png` - whole 150 x 150 um die
- `results/PartD/layout_zoom.png` - standard-cell rows and metal wires
- `results/PartD/layout_zoom_cells.png` - deeper zoom with every cell labelled by name

-> full write-up (Fmax breakdown, cell breakdown, signoff checks) `results/PartD/part_d_results.md`

---

## Report

`report/report.pdf`: results tables for Parts A-D, screenshots, block diagram, hand-worked example and
answers to the six questions in Section 10.
