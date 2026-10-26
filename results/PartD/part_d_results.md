# Part D - Physical Design: RTL to GDSII (LibreLane)

LibreLane 3.1.0.dev3 (Classic flow) on SKY130 (`sky130A`, `sky130_fd_sc_hd`), run inside IIC-OSIC-TOOLS.
The container's default PDK is IHP `ihp-sg13g2`, so SKY130 must be selected before every run.
Submission files: `pnr/config.json`, `pnr/metrics.json`, `pnr/mult_array.gds` (copied byte-for-byte
from the final run `runs/RUN_2026-10-25_08-00-39/final/`).

## Configuration (`pnr/config.json`)

| Key | Value |
|---|---|
| DESIGN_NAME | `"mult_array"` |
| VERILOG_FILES | `["dir::../rtl/full_adder.v", "dir::../rtl/mult_array.v"]` |
| CLOCK_PORT | `"clk"` |
| CLOCK_PERIOD | start 1.2 x Tmin = 1.2 x 2.596 = 3.115 -> **3.5 ns**; final **7.0 ns** |
| FP_SIZING | `"absolute"` |
| DIE_AREA | `[0, 0, 150, 150]` |

## Commands (inside IIC-OSIC-TOOLS)

```bash
cd pnr
export PDK=sky130A STD_CELL_LIBRARY=sky130_fd_sc_hd   # select SKY130 (Section 4.2)
librelane config.json
cp runs/<final run>/final/metrics.json metrics.json
cp runs/<final run>/final/gds/mult_array.gds mult_array.gds
klayout mult_array.gds                                  # screenshots
```

## Task 1 - Attempts (CLOCK_PERIOD +0.5 ns after each failing run)

| Run | CLOCK_PERIOD (ns) | setup__ws (ns) | ss-corner slack (ns) | tt-corner slack (ns) | hold__ws (ns) | DRC | LVS | Result |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 3.5 | -2.154 | -2.108 | +0.587 | +0.100 | 0 | 0 | FAIL (setup) |
| 2 | 4.0 | -1.654 | -1.608 | +1.087 | +0.147 | 0 | 0 | FAIL (setup) |
| 3 | 4.5 | -1.154 | -1.108 | +1.587 | +0.147 | 0 | 0 | FAIL (setup) |
| 4 | 5.0 | -0.654 | -0.608 | +2.087 | +0.147 | 0 | 0 | FAIL (setup) |
| 5 | 5.5 | -0.155 | -0.109 | +2.587 | +0.147 | 0 | 0 | FAIL (setup) |
| 6 | 6.0 | -0.107 | -0.055 | +2.899 | +0.148 | 0 | 0 | FAIL (setup) |
| 7 | 6.5 | -0.136 | -0.094 | +3.199 | +0.141 | 0 | 0 | FAIL (setup) |
| 8 | 7.0 | **+0.364** | +0.406 | +3.699 | +0.141 | 0 | 0 | **PASS** |

- LibreLane signs off setup timing at 9 PVT corners; `setup__ws` is the worst of them, always the slow
  corner `ss_100C_1v60` (1.60 V, 100 C). The typical corner used in Part C passed in every run.
- Why the slack changes unevenly: during placement the flow checks timing with estimated wire delays, and the
  timing-repair step acts only if that estimate violates. From 3.5 to 6.0 ns the slow-corner estimate is negative,
  so repair adds the same 4 cells every run (3 `buf_4` re-buffers + 1 `dlygate4sd3_1` hold cell). At 6.5 ns the
  estimate is +0.435 ns, so repair adds nothing, but the real routed wires are about 0.57 ns slower, giving
  -0.136 ns. At 7.0 ns the estimate (+0.935 ns) leaves enough room and the run passes (+0.364 ns).
  The synthesised logic (67 cells) is identical in all 8 runs.
- DRC, LVS and hold were clean in every run; only setup timing failed.
- Per-attempt files are in `attempts/`: `config_<period>.json` (the 6 config keys used for that run, taken
  from the run's `resolved.json`) and `metrics_<period>.json` (that run's `final/metrics.json`), e.g.
  `config_3p5ns.json` / `metrics_3p5ns.json` for run 1 and `config_7ns.json` / `metrics_7ns.json` for run 8.

## Part D results table

| Metric | Value |
|:---:|:---:|
| CLOCK_PERIOD used (ns) | 7.0 |
| Number of runs needed | 8 |
| Core area (um^2) | 17759.5 (die area 22500) |
| Cells after synthesis (from Part B) | 73 |
| Cells after place and route | 1895 (334 excluding decap/fill) |
| Kinds of cells added | buffers (22), tap (245), decap (1314), fill (247) |
| Wirelength (um) | 2362 |
| Setup slack (ns) | +0.364 |
| Post-route Fmax (MHz) | 150.70 |
| Fmax from Part C (MHz) | 385.21 |
| DRC errors | 0 |
| LVS errors | 0 |

Sources: `pnr/metrics.json` (`design__instance__count`, `design__core__area`, `route__wirelength`,
`timing__setup__ws`, `magic__drc_error__count`, `klayout__drc_error__count`, `route__drc_errors`,
`design__lvs_error__count`).

## Task 3 - Post-route Fmax vs Part C

```text
Post-route Fmax = 1000 / (CLOCK_PERIOD - setup slack) = 1000 / (7.0 - 0.364) = 1000 / 6.636 = 150.70 MHz
Part C Fmax     = 385.21 MHz   ->  post-route is about 2.6x lower
```

1. **Corner (main cause, about 2x).** Part C used only the typical corner; `setup__ws` is set by the slow
   corner `ss_100C_1v60` (1.60 V, 100 C), where cells are about 2x slower. Using the typical-corner slack of
   the same layout: 1000 / (7.0 - 3.699) = **302.9 MHz**.
2. **Physical effects (about 27 % at the same corner).** Even at the typical corner the minimum period grows
   from 2.596 ns (Part C, ideal wires and clock) to 3.301 ns. From the post-route typical-corner timing report
   (register-to-register path `a_reg[0]` -> `p[6]`):

| Component | Part C (ns) | Post-route, tt (ns) | Added (ns) |
|---|:---:|:---:|:---:|
| Launch flip-flop clk -> Q | 0.395 | 0.472 | +0.077 (real wire load) |
| Logic cells + wires | 2.065 (8 cells) | 2.439 (9 cells) | +0.374 (wire RC; LibreLane's own netlist) |
| Clock uncertainty | 0 | 0.250 | +0.250 (LibreLane default) |
| Clock skew (launch 0.336 - capture 0.302 - CRPR 0.018) | 0 (ideal clock) | 0.016 | +0.016 |
| Library setup time | 0.135 | 0.124 | -0.011 |
| **Minimum period** | **2.596** | **3.301** | **+0.705** |

   Real clock-tree latency (about 0.3 ns) mostly cancels between launch and capture flip-flops; what remains
   is the skew. LibreLane also applies a 5 % timing derate to cell delays.

Post-route critical path (LibreLane step `55-openroad-stapostpnr`, corner `max_ss_100C_1v60`): `_102_` (`a_reg[0]`) -> `_100_`
(D = `fa33.sum`, output `p[6]`), arrival 6.656 ns, slack +0.364 ns. It ends at the same output bit `p[6]`
(sum of FA[3,3]) as the Part C path.

## Task 4 - Cells after place and route vs synthesis

**Comparison:** Part B synthesis = **73 cells** -> after place and route = **1895 cells**
(`design__instance__count`), about 26x more. Almost all of the extra cells carry no logic.

Cells added, found by name in the cell report (LibreLane step `53-odb-cellfrequencytables`, `cell.rpt`):

| Name contains | Cells in the report | Count | Added by |
|---|---|---:|---|
| `buf` | `buf_2` x17, `clkdlybuf4s50_1` x2, `clkbuf_16` x3 | 22 | I/O port buffers (17) + reset-fanout buffers (2) + clock-tree synthesis (3) |
| `tap` | `tapvpwrvgnd_1` x245 | 245 | tap insertion (floorplan) |
| `decap` | `decap_3` x130, `decap_4` x49, `decap_6` x175, `decap_8` x55, `decap_12` x905 | 1314 | fill insertion |
| `fill` | `fill_1` x215, `fill_2` x32 | 247 | fill insertion |
| **Added in total** | | **1828** | |
| (logic + flip-flops) | 51 logic gates + 16 `dfrtp_1` | 67 | synthesis |
| **Total after place and route** | | **1895** | |

Why each kind is needed:

- **`buf`** - `buf_2` x17 (`input1`-`input9`, `output10`-`output17`): one buffer on each of the 9 input pins
  (`rst_n`, `a`, `b`) and 8 output pins (`p`), isolating the core from external drivers and loads.
  `clkdlybuf4s50_1` x2 (`fanout18`, `fanout19`): split the reset net, which drives all 16 flip-flops,
  into two branches (10 + 6) to meet slew and load limits. `clkbuf_16` x3: clock-tree synthesis, so the
  clock reaches all 16 flip-flops at nearly the same time (low skew).
- **`tap`** (`tapvpwrvgnd`) - tie the n-well to VPWR and the substrate to VGND at regular spacing to prevent
  latch-up.
- **`decap`** - decoupling capacitors between VPWR and VGND that reduce supply noise / IR drop.
- **`fill`** - fill the remaining gaps so every row is continuous (wells, implants and power rails stay
  connected) and density rules are met.

Notes:

- The logic part is 67 cells, not Part B's 73, because LibreLane runs its own Yosys synthesis with a
  different script. So 73 + 1828 is not 1895; 67 + 1828 = 1895.
- Without decap/fill there are 334 standard-cell instances (67 + 22 buffers + 245 taps,
  `design__instance__count__stdcell`), with area 1224.92 um^2 = **6.9 %** of the 17759.5 um^2 core
  (`design__instance__utilization`). The fixed 150 x 150 um die is much larger than this design needs,
  which is why most of each row is decap/fill.

## Signoff checks (final run)

| Check | Result | Source (`pnr/metrics.json` key or LibreLane step) |
|---|---|---|
| DRC (Magic) | 0 errors | `magic__drc_error__count` |
| DRC (KLayout) | 0 violations | `klayout__drc_error__count` |
| Detailed-router DRC | 0 (intermediate router iterations 28 -> 3 -> 3 -> 0) | `pnr/metrics.json` |
| LVS (Netgen) | "Circuits match uniquely", 0 errors | `design__lvs_error__count` |
| Antenna / LVS / DRC summary | all Passed | LibreLane step `76-misc-reportmanufacturability` |
| Hold | worst hold slack +0.141 ns | `timing__hold__ws` |
