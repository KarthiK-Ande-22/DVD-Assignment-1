#!/usr/bin/env python3
"""Block diagram of mult_array (rtl/mult_array.v) as a square grid, black and white.

Columns j = 3..0 run left to right, rows 0..3 top to bottom. Connections (Section 2):
    pp_i[j] = a_reg[j] & b_reg[i]
    r0 = {0, pp0[3], pp0[2], pp0[1]},   r_i = {c_i[4], s_i[3], s_i[2], s_i[1]}
    FA[i,j]: a = pp_i[j], b = r_(i-1)[j], cin = c_i[j] (c_i[0] = 0) -> s_i[j], c_i[j+1]
    p[0] = pp0[0], p[i] = s_i[0], p[7:4] = {c3[4], s3[3], s3[2], s3[1]}

Usage: python3 draw_block_diagram.py   ->  block_diagram.png
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

W = 2.4                                # column pitch
FA_W, FA_H = 1.25, 0.85
AND_W, AND_H = 0.95, 0.5
Y_REG = 4.4                            # input registers
Y_AND0 = 1.7                           # row 0 AND gates
Y_FA = {1: -1.6, 2: -5.0, 3: -8.4}     # full-adder rows
Y_OUT = -11.0                          # output register
LANE = {2: 1.5, 1: 2.4, 0: 3.3}        # right-hand lanes for p[2], p[1], p[0] (offset from column 0)
REG_FILL = "#D9EAD3"      # registers: light green
AND_FILL = "#FFF2CC"      # AND gates: light yellow
FA_FILL = "#DDEBF7"       # full adders: light blue
CARRY = "#C0392B"         # carry wires: red


def X(j):
    """Centre x of column j (j = 4 is the carry column on the left)."""
    return (4 - j) * W


fig, ax = plt.subplots(figsize=(12, 14))
ax.set_aspect("equal")
ax.axis("off")
ax.set_xlim(-2.2, X(0) + 4.4)
ax.set_ylim(Y_OUT - 2.2, Y_REG + 2.0)


def arrow(p0, p1, dashed=False, lw=1.5):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=12, lw=lw, color=CARRY if dashed else "black",
                                 linestyle=(0, (4, 3)) if dashed else "-", shrinkA=0, shrinkB=0, zorder=2))


def path(points, dashed=False):
    for a, b in zip(points[:-2], points[1:-1]):
        ax.plot(*zip(a, b), color=CARRY if dashed else "black", lw=1.5, linestyle=(0, (4, 3)) if dashed else "-", zorder=2)
    arrow(points[-2], points[-1], dashed)


def box(xc, yc, w, h, text, fill="white", lw=1.4, size=11, bold=False):
    ax.add_patch(FancyBboxPatch((xc - w / 2, yc - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fill, ec="black", lw=lw, zorder=3))
    ax.text(xc, yc, text, ha="center", va="center", fontsize=size, zorder=4,
            fontweight="bold" if bold else "normal")


def and_gate(xc, yc, i, j):
    box(xc, yc, AND_W, AND_H, f"pp{i}[{j}]", fill=AND_FILL, size=10)
    return xc, yc - AND_H / 2


# ------------------------------------------------------------- input registers
for label, xc in (("a_reg[3:0]", X(3)), ("b_reg[3:0]", X(1))):
    box(xc, Y_REG, 3.6, 0.9, f"input register  {label}\n(4 D flip-flops)", fill=REG_FILL, size=11)
    arrow((xc, Y_REG + 1.25), (xc, Y_REG + 0.45))
    ax.text(xc + 0.12, Y_REG + 0.95, label.split("_")[0] + "[3:0]", fontsize=11, va="center")
ax.text((X(3) + X(1)) / 2, Y_REG - 1.0,
        "a_reg[j] and b_reg[i] drive AND gate pp$_i$[j]  (16 AND gates)", ha="center", fontsize=11, style="italic")
ax.text(X(0) + 1.5, Y_REG, "clk, rst_n", fontsize=10, va="center")
arrow((X(0) + 1.45, Y_REG), (X(1) + 1.8, Y_REG), lw=1.0)

# ------------------------------------------------------------- column headings and row labels
for j in range(4):
    ax.text(X(j), Y_AND0 + 1.0, f"j = {j}", ha="center", fontsize=10)
ax.text(-2.1, Y_AND0, "Row 0", fontsize=12, fontweight="bold", va="center")
for i in (1, 2, 3):
    ax.text(-2.1, Y_FA[i] + 0.9, f"Row {i}", fontsize=12, fontweight="bold", va="center")

# ------------------------------------------------------------- row 0: AND gates only
src = {}                                   # (row, j) -> bottom point of r_(row-1)[j]
carry_in = set()                           # inputs fed by a carry (drawn dashed)
for j in range(4):
    out = and_gate(X(j) + 0.3, Y_AND0, 0, j)
    if j >= 1:
        src[(1, j - 1)] = out              # r0[j-1] = pp0[j]
    else:
        lane = X(0) + LANE[0]              # p[0] = pp0[0]
        path([out, (out[0], out[1] - 0.4), (lane, out[1] - 0.4), (lane, Y_OUT + 0.45)])
ax.text(X(4) + 0.3, Y_AND0, "0", ha="center", va="center", fontsize=12, fontweight="bold")
src[(1, 3)] = (X(4) + 0.3, Y_AND0 - 0.25)   # r0[3] = 0

# ------------------------------------------------------------- rows 1..3
for i in (1, 2, 3):
    yf = Y_FA[i]
    top, bot = yf + FA_H / 2, yf - FA_H / 2
    prev_bot = src[(i, 0)][1]
    y_and = prev_bot - 0.3 * (prev_bot - top)
    for j in range(4):
        x = X(j)
        g = and_gate(x - 0.3, y_and, i, j)
        arrow(g, (x - 0.3, top))                       # a = pp_i[j]
        arrow(src.pop((i, j)), (x + 0.3, top), dashed=(i, j) in carry_in)   # b = r_(i-1)[j]  (diagonal)
        box(x, yf, FA_W, FA_H, f"FA[{i},{j}]", fill=FA_FILL, lw=1.8, size=11, bold=True)
        if j == 0:                                     # c_i[0] = 0
            arrow((x + FA_W / 2 + 0.45, yf), (x + FA_W / 2, yf), dashed=True)
            ax.text(x + FA_W / 2 + 0.58, yf, "0", va="center", fontsize=11, fontweight="bold", color=CARRY)
        if j < 3:                                      # c_i[j+1] to the left
            arrow((x - FA_W / 2, yf), (X(j + 1) + FA_W / 2, yf), dashed=True)
        s = (x + 0.3, bot)                             # sum s_i[j]
        if i == 3:
            arrow(s, (s[0], Y_OUT + 0.45))             # p[3..6]
        elif j == 0:
            lane = X(0) + LANE[i]                      # p[i] = s_i[0]
            path([s, (lane, bot - 0.9), (lane, Y_OUT + 0.45)])
        else:
            src[(i + 1, j - 1)] = s                    # r_i[j-1] = s_i[j]
    # final carry c_i[4]: left into the carry column, then down
    cx = X(4) + 0.3
    if i < 3:
        for a, b in (((X(3) - FA_W / 2, yf), (cx, yf)), ((cx, yf), (cx, bot))):
            ax.plot(*zip(a, b), color=CARRY, lw=1.5, linestyle=(0, (4, 3)), zorder=2)
        src[(i + 1, 3)] = (cx, bot)                    # r_i[3] = c_i[4]
        carry_in.add((i + 1, 3))
        ax.text(cx - 0.15, yf + 0.15, f"c{i}[4]", ha="right", fontsize=10, color=CARRY)
    else:
        path([(X(3) - FA_W / 2, yf), (cx, yf), (cx, Y_OUT + 0.45)], dashed=True)
        ax.text(cx - 0.15, yf + 0.15, "c3[4]", ha="right", fontsize=10, color=CARRY)
assert not src, f"unconnected: {src}"

# ------------------------------------------------------------- output register
x0, x1 = X(4) - 0.5, X(0) + LANE[0] + 0.5
box((x0 + x1) / 2, Y_OUT, x1 - x0, 0.9, "output register  p[7:0]   (8 D flip-flops)", fill=REG_FILL, size=12)
lanes = {7: X(4) + 0.3, 6: X(3) + 0.3, 5: X(2) + 0.3, 4: X(1) + 0.3, 3: X(0) + 0.3,
         2: X(0) + LANE[2], 1: X(0) + LANE[1], 0: X(0) + LANE[0]}
for k, xl in lanes.items():
    ax.text(xl - 0.08, Y_OUT + 0.75, f"p[{k}]", ha="right", fontsize=10, fontweight="bold")
arrow(((x0 + x1) / 2, Y_OUT - 0.45), ((x0 + x1) / 2, Y_OUT - 1.3), lw=2.2)
ax.text((x0 + x1) / 2 + 0.2, Y_OUT - 1.0, "p[7:0] = a x b  (2 clock cycles after a, b are applied)",
        fontsize=11, va="center")
ax.text(x1 + 0.15, Y_OUT, "clk, rst_n", fontsize=10, va="center")

# ------------------------------------------------------------- legend
lx, ly = X(0) + 1.3, Y_AND0 + 1.25
ax.plot([lx, lx + 0.8], [ly, ly], color="black", lw=1.5)
ax.text(lx + 0.95, ly, "partial product / sum", va="center", fontsize=10)
ax.plot([lx, lx + 0.8], [ly - 0.5, ly - 0.5], color=CARRY, lw=1.5, linestyle=(0, (4, 3)))
ax.text(lx + 0.95, ly - 0.5, "carry", va="center", fontsize=10)

fig.savefig("block_diagram.png", dpi=170, bbox_inches="tight", facecolor="white")
print("wrote block_diagram.png")
