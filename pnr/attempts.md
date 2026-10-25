# Part D - LibreLane attempts

Every run: inside IIC-OSIC-TOOLS, from `pnr/`: `export PDK=sky130A STD_CELL_LIBRARY=sky130_fd_sc_hd; librelane config.json`

| Run | CLOCK_PERIOD (ns) | Run folder | setup__ws (ns) | ss-corner slack (ns) | tt-corner slack (ns) | DRC (magic/klayout/route) | LVS | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | 3.5 | RUN_2026-10-25_07-47-34 | -2.154 | -2.108 | +0.587 | 0/0/0 | 0 | FAIL |
| 2 | 4.0 | RUN_2026-10-25_07-49-33 | -1.654 | -1.608 | +1.087 | 0/0/0 | 0 | FAIL |
| 3 | 4.5 | RUN_2026-10-25_07-51-18 | -1.154 | -1.108 | +1.587 | 0/0/0 | 0 | FAIL |
| 4 | 5.0 | RUN_2026-10-25_07-53-23 | -0.654 | -0.608 | +2.087 | 0/0/0 | 0 | FAIL |
| 5 | 5.5 | RUN_2026-10-25_07-55-08 | -0.155 | -0.109 | +2.587 | 0/0/0 | 0 | FAIL |
| 6 | 6.0 | RUN_2026-10-25_07-57-15 | -0.107 | -0.055 | +2.899 | 0/0/0 | 0 | FAIL |
| 7 | 6.5 | RUN_2026-10-25_07-58-58 | -0.136 | -0.094 | +3.199 | 0/0/0 | 0 | FAIL |
| 8 | 7.0 | RUN_2026-10-25_08-00-39 | +0.364 | +0.406 | +3.699 | 0/0/0 | 0 | PASS |
