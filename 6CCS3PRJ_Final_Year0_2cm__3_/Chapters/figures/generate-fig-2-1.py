"""Generate fig-2-1-document-class-spectrum.png.

Three-panel horizontal spectrum showing the three document classes.
Greyscale-friendly; semi-structured panel visually emphasised.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

OUT = Path(__file__).parent / "fig-2-1-document-class-spectrum.png"

fig, ax = plt.subplots(figsize=(10.5, 4.0))

panel_w, panel_h = 2.6, 2.4
gap = 0.6
y_panel = 0.8

panels = [
    ("Unstructured", "news article", "prose",
     [(0.15, 1.6, 2.3, 0.05),
      (0.15, 1.4, 2.0, 0.05),
      (0.15, 1.2, 2.3, 0.05),
      (0.15, 1.0, 1.9, 0.05),
      (0.15, 0.8, 2.2, 0.05),
      (0.15, 0.6, 1.8, 0.05),
      (0.15, 0.4, 2.0, 0.05),
      (0.15, 0.2, 1.6, 0.05)],
     False),
    ("Semi-structured", "utility bill", "stable schema, varying layout",
     [(0.15, 2.0, 1.4, 0.12),
      (1.8, 2.0, 0.65, 0.12),
      (0.15, 1.70, 1.0, 0.07),
      (0.15, 1.30, 2.30, 0.08),
      (0.15, 1.05, 0.9, 0.06),
      (1.3, 1.05, 1.15, 0.06),
      (0.15, 0.80, 2.30, 0.05),
      (0.15, 0.55, 1.8, 0.05),
      (0.15, 0.30, 0.9, 0.10),
      (1.3, 0.30, 1.15, 0.10)],
     True),
    ("Structured", "database row / form", "fixed schema and layout",
     [(0.15, 1.9, 2.3, 0.12),
      (0.15, 1.6, 2.3, 0.12),
      (0.15, 1.3, 2.3, 0.12),
      (0.15, 1.0, 2.3, 0.12),
      (0.15, 0.7, 2.3, 0.12),
      (0.15, 0.4, 2.3, 0.12),
      (0.15, 0.1, 2.3, 0.12)],
     False),
]

x = 0.0
centres = []
for title, subtitle, tag, strokes, emphasise in panels:
    lw = 2.4 if emphasise else 1.2
    ax.add_patch(Rectangle((x, y_panel), panel_w, panel_h,
                           facecolor="white", edgecolor="black", linewidth=lw))
    for sx, sy, sw, sh in strokes:
        ax.add_patch(Rectangle((x + sx, y_panel + sy), sw, sh,
                               facecolor="#555555", edgecolor="none"))
    ax.text(x + panel_w / 2, y_panel + panel_h + 0.25, title,
            ha="center", va="bottom", fontsize=13, fontweight="bold")
    ax.text(x + panel_w / 2, y_panel + panel_h + 0.05,
            f"e.g.\\ {subtitle}", ha="center", va="bottom", fontsize=10,
            style="italic")
    ax.text(x + panel_w / 2, y_panel - 0.25, tag,
            ha="center", va="top", fontsize=9, style="italic")
    centres.append(x + panel_w / 2)
    x += panel_w + gap

total_w = x - gap
arrow = FancyArrowPatch((0.1, 0.25), (total_w - 0.1, 0.25),
                        arrowstyle="-|>", mutation_scale=18,
                        linewidth=1.4, color="black")
ax.add_patch(arrow)
ax.text(total_w / 2, 0.05, "increasing structural regularity",
        ha="center", va="top", fontsize=10, style="italic")

ax.set_xlim(-0.2, total_w + 0.2)
ax.set_ylim(-0.2, y_panel + panel_h + 0.9)
ax.set_aspect("equal")
ax.axis("off")

fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
