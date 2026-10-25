#!/usr/bin/env python3
"""Print the Part D metrics from a LibreLane metrics.json file."""

import json
import sys

m = json.load(open(sys.argv[1]))

# Keys named in the assignment's "Where to find the numbers" table.
keys = [
    "design__instance__count",
    "design__instance__count__stdcell",
    "design__die__area",
    "design__core__area",
    "route__wirelength",
    "timing__setup__ws",
    "timing__setup__ws__corner:nom_tt_025C_1v80",
    "timing__setup__ws__corner:nom_ss_100C_1v60",
    "timing__setup__ws__corner:nom_ff_n40C_1v95",
    "timing__hold__ws",
    "route__drc_errors",
    "magic__drc_error__count",
    "klayout__drc_error__count",
    "design__lvs_error__count",
]
for k in keys:
    print(f"{k:45s} {m.get(k)}")
