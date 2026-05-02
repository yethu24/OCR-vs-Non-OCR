"""Generate fig-3-1-studies-vs-controls-matrix.png.

Matrix of controlled-comparison studies against four rubric controls:
(i) same reasoning engine, (ii) identical prompt, (iii) multilingual
coverage, (iv) per-stage cost/latency. Full circle = met, half = partial,
empty = not met. Final highlighted row is the target for this dissertation.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Wedge

OUT = Path(__file__).parent / "fig-3-1-studies-vs-controls-matrix.png"

STUDIES = [
    ("Shen et al. 2026",       ["full", "none", "none", "partial"]),
    ("Benkirane et al. 2026",  ["none", "none", "full", "none"]),
    ("Borchmann 2024",         ["full", "none", "none", "none"]),
    ("Wang & Shen 2025",       ["none", "none", "none", "partial"]),
    ("Nunes et al. 2025",      ["none", "none", "none", "none"]),
    ("Berghaus et al. 2025",   ["full", "partial", "none", "none"]),
]

CONTROLS = [
    "(i) same\nreasoning engine",
    "(ii) identical\nprompt",
    "(iii) multilingual\ncoverage",
    "(iv) cost & latency\nmeasured",
]

TARGET = ("This dissertation", ["full", "full", "full", "full"])

fig, ax = plt.subplots(figsize=(12.0, 6.0))

row_h = 0.7
col_w = 2.1
label_col_w = 3.2
x0 = label_col_w
n_rows = len(STUDIES) + 1
total_w = x0 + col_w * len(CONTROLS)
total_h = row_h * (n_rows + 1)

for j, control in enumerate(CONTROLS):
    cx = x0 + col_w * (j + 0.5)
    cy = total_h - row_h * 0.5
    ax.text(cx, cy, control,
            ha="center", va="center", fontsize=10, fontweight="bold")

def draw_mark(ax, cx, cy, state):
    r = 0.18
    if state == "full":
        ax.add_patch(Circle((cx, cy), r, facecolor="#2e7d32",
                            edgecolor="black", linewidth=0.8))
    elif state == "partial":
        ax.add_patch(Circle((cx, cy), r, facecolor="white",
                            edgecolor="black", linewidth=0.8))
        ax.add_patch(Wedge((cx, cy), r, 90, 270,
                           facecolor="#2e7d32", edgecolor="black",
                           linewidth=0.8))
    else:
        ax.add_patch(Circle((cx, cy), r, facecolor="white",
                            edgecolor="black", linewidth=0.8))

for i, (label, states) in enumerate(STUDIES):
    row_y = total_h - row_h * (i + 1.5)
    if i % 2 == 0:
        ax.add_patch(Rectangle((0, row_y - row_h / 2), total_w, row_h,
                               facecolor="#f5f5f5", edgecolor="none"))
    ax.text(label_col_w - 0.15, row_y, label,
            ha="right", va="center", fontsize=10)
    for j, state in enumerate(states):
        cx = x0 + col_w * (j + 0.5)
        draw_mark(ax, cx, row_y, state)

target_y = total_h - row_h * (len(STUDIES) + 1.5) - 0.15
ax.add_patch(Rectangle((0, target_y - row_h / 2),
                       total_w, row_h,
                       facecolor="#fff4cf", edgecolor="#b58900",
                       linewidth=1.6))
ax.text(label_col_w - 0.15, target_y, TARGET[0],
        ha="right", va="center", fontsize=11, fontweight="bold")
for j, state in enumerate(TARGET[1]):
    cx = x0 + col_w * (j + 0.5)
    draw_mark(ax, cx, target_y, state)

legend_y = target_y - row_h - 0.15
legend_items = [("full", "met"),
                ("partial", "partial"),
                ("none", "not met")]
lx = 0.2
for state, label in legend_items:
    draw_mark(ax, lx + 0.20, legend_y, state)
    ax.text(lx + 0.45, legend_y, label,
            ha="left", va="center", fontsize=10)
    lx += 1.7

ax.set_xlim(0, total_w)
ax.set_ylim(legend_y - 0.5, total_h + 0.3)
ax.set_aspect("equal")
ax.axis("off")

fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
