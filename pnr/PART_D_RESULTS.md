# Part D - Physical Design: RTL to GDSII

## Configuration (`pnr/config.json`)

| Key | Value |
|---|---|
| DESIGN_NAME | `"mult_array"` |
| VERILOG_FILES | `["dir::../rtl/full_adder.v", "dir::../rtl/mult_array.v"]` |
| CLOCK_PORT | `"clk"` |
| CLOCK_PERIOD | started at 1.2 x Tmin = 1.2 x 2.596 = 3.115 -> **3.5 ns**; final **7.0 ns** |
| FP_SIZING | `"absolute"` |
| DIE_AREA | `[0, 0, 150, 150]` |

## Commands

Run inside the IIC-OSIC-TOOLS container, from `pnr/` (the SKY130 PDK is selected as in Section 4.2):

```bash
export PDK=sky130A STD_CELL_LIBRARY=sky130_fd_sc_hd
librelane config.json
```

`run_all.sh` repeats this from CLOCK_PERIOD = 3.5 ns, adding 0.5 ns after each failing run
(`run_attempt.sh` does one run). Screenshots: `klayout -zz -r render_layout.py`.

## Attempts (Task 1)

| Run | CLOCK_PERIOD (ns) | setup__ws (ns) | ss-corner slack (ns) | tt-corner slack (ns) | DRC | LVS | Result |
|---|---|---|---|---|---|---|---|
| 1 | 3.5 | -2.154 | -2.108 | +0.587 | 0 | 0 | FAIL |
| 2 | 4.0 | -1.654 | -1.608 | +1.087 | 0 | 0 | FAIL |
| 3 | 4.5 | -1.154 | -1.108 | +1.587 | 0 | 0 | FAIL |
| 4 | 5.0 | -0.654 | -0.608 | +2.087 | 0 | 0 | FAIL |
| 5 | 5.5 | -0.155 | -0.109 | +2.587 | 0 | 0 | FAIL |
| 6 | 6.0 | -0.107 | -0.055 | +2.899 | 0 | 0 | FAIL |
| 7 | 6.5 | -0.136 | -0.094 | +3.199 | 0 | 0 | FAIL |
| 8 | 7.0 | **+0.364** | +0.406 | +3.699 | 0 | 0 | **PASS** |

LibreLane signs off setup timing at 9 PVT corners. `setup__ws` is the worst of them, which is always the
slow corner `ss_100C_1v60` (1.60 V, 100 C). The typical corner used in Part C passed in every run.
Runs 6 and 7 gained almost nothing from the extra 0.5 ns because place-and-route timing repair changed
the critical path (the synthesized netlist was identical in all 8 runs).

## Part D results table (completed)

| Metric | Value |
|---|---|
| CLOCK_PERIOD used (ns) | 7.0 |
| Number of runs needed | 8 |
| Core area (um^2) | 17,759.5 (die area 22,500) |
| Cells after synthesis (from Part B) | 73 |
| Cells after place and route | 1,895 (`instance__count`) |
| Kinds of cells added | buffers (`buf_2` x17, `clkbuf_16` x3, `clkdlybuf4s50_1` x2), tap (`tapvpwrvgnd_1` x245), decap (`decap_3/4/6/8/12` x1314), fill (`fill_1` x215, `fill_2` x32) |
| Wirelength (um) | 2,362 |
| Setup slack (ns) | +0.364 |
| Post-route Fmax (MHz) | 1000 / (7.0 - 0.364) = **150.70** |
| Fmax from Part C (MHz) | 385.21 |
| DRC errors | 0 (Magic 0, KLayout 0, router 0) |
| LVS errors | 0 |

## Fmax comparison (Task 3)

Post-route Fmax = 1000 / (7.0 - 0.364) = 150.70 MHz, against 385.21 MHz from Part C, i.e. 2.6x lower.
Two effects combine:

1. **Corner.** Part C used only the typical corner; `setup__ws` is set by the slow corner. Using the
   typical-corner slack of the same layout gives 1000 / (7.0 - 3.699) = 302.9 MHz.
2. **Physical effects.** Even at the same corner, 302.9 MHz is below 385.21 MHz because the routed design
   adds wire resistance and capacitance (from extraction), clock-tree insertion delay and skew, and
   LibreLane's default clock uncertainty (0.25 ns) and derating (5 %). Part C had ideal wires and an ideal clock.

## Cell comparison (Task 4)

| Group | Count |
|---|---|
| Logic cells (48 multi-input + 3 inverters) | 51 |
| Flip-flops (`dfrtp_1`) | 16 |
| Buffers: timing repair (`buf_2` x17, `clkdlybuf4s50_1` x2) + clock tree (`clkbuf_16` x3) | 22 |
| Tap cells (`tapvpwrvgnd_1`) | 245 |
| Decap cells (`decap_*`) | 1,314 |
| Fill cells (`fill_*`) | 247 |
| **Total** | **1,895** |

LibreLane's own Yosys run produced 67 logic + flip-flop cells (Part B's script produced 73; the scripts
differ). Of the 1,895 cells, 1,828 were added by the physical flow: 22 buffers, plus 1,806 tap/decap/fill
cells that carry no logic.

Source: `runs/<final run>/53-odb-cellfrequencytables/cell.rpt` and `metrics.json`.

## Screenshots (Task 5)

- `layout_whole_die.png` - the whole 150 x 150 um die: I/O pins on the edges, core rows, power grid, logic in the centre.
- `layout_zoom.png` - 30 x 30 um zoom: standard-cell rows, metal-1/metal-2 wires and vias.
