#!/usr/bin/env python3
"""Render KLayout screenshots of the final layout: whole die and a zoomed view.

Run inside IIC-OSIC-TOOLS from pnr/:  klayout -zz -r render_layout.py
"""

import os
import pya

# Load the final GDSII layout and show every level of the cell hierarchy.
view = pya.LayoutView()
view.load_layout("mult_array.gds")
view.max_hier()

# Use the SKY130 layer colours shipped with the PDK.
pdk_root = os.environ.get("PDK_ROOT", "/foss/pdks")
view.load_layer_props(f"{pdk_root}/sky130A/libs.tech/klayout/tech/sky130A.lyp")
view.set_config("background-color", "#FFFFFF")
view.set_config("text-visible", "false")

# Screenshot 1: the whole 150 um x 150 um die.
view.zoom_box(pya.DBox(-2.0, -2.0, 152.0, 152.0))
view.save_image_with_options("layout_whole_die.png", 1400, 1400, oversampling=0)

# Screenshot 2: a 30 um x 30 um window showing standard-cell rows and metal wires.
view.zoom_box(pya.DBox(60.0, 60.0, 90.0, 90.0))
view.save_image_with_options("layout_zoom.png", 1400, 1400, oversampling=0)

# Screenshot 3: a 16 um x 10 um window with only the top level drawn in full, so every
# standard cell appears as a box labelled with its name (logic, decap, tap, fill, clkbuf).
view.min_hier_levels = 0
view.max_hier_levels = 1
view.zoom_box(pya.DBox(60.0, 66.0, 76.0, 76.0))
view.save_image_with_options("layout_zoom_cells.png", 1600, 1000, oversampling=0)
