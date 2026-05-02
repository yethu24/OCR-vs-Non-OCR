"""Generate fig-2-5-two-path-pipeline.png.

Consolidating schematic of the two extraction pipelines compared in this
dissertation: OCR-mediated and vision-mediated, sharing the rasteriser,
LLM, and output schema.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).parent / "fig-2-5-two-path-pipeline.png"

fig, ax = plt.subplots(figsize=(13.5, 5.8))


def box(ax, x, y, w, h, text, *, facecolor="white", fontsize=11, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=facecolor, edgecolor="black",
                                linewidth=1.2))
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center", fontsize=fontsize,
            fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1, *, label=None, label_offset=(0.0, 0.15)):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                 arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.1, color="black"))
    if label:
        ax.text((x0 + x1) / 2 + label_offset[0],
                (y0 + y1) / 2 + label_offset[1], label,
                ha="center", va="bottom", fontsize=9, style="italic")


y_upper = 3.7
y_lower = 1.1
y_shared = 2.4

box(ax, 0.0, y_shared, 1.8, 0.9, "bill PDF", facecolor="#f3f3f3")
box(ax, 2.2, y_shared, 1.8, 0.9, "rasterise")

arrow(ax, 1.8, y_shared + 0.45, 2.2, y_shared + 0.45)

box(ax, 5.0, y_upper, 2.0, 0.9, "Tesseract OCR")
box(ax, 7.6, y_upper, 2.0, 0.9, "OCR text")

box(ax, 5.0, y_lower, 2.2, 0.9, "document image")

arrow(ax, 4.0, y_shared + 0.6, 5.0, y_upper + 0.45,
      label="OCR-mediated", label_offset=(0.2, 0.15))
arrow(ax, 4.0, y_shared + 0.3, 5.0, y_lower + 0.45,
      label="vision-mediated", label_offset=(0.2, -0.35))

arrow(ax, 7.0, y_upper + 0.45, 7.6, y_upper + 0.45)

box(ax, 10.2, y_shared, 2.0, 0.9, "LLM", facecolor="#ececec", bold=True)

arrow(ax, 9.6, y_upper + 0.45, 10.2, y_shared + 0.6)
arrow(ax, 7.2, y_lower + 0.45, 10.2, y_shared + 0.3)

box(ax, 12.6, y_shared, 2.4, 0.9, "BillExtraction", facecolor="#f3f3f3")
arrow(ax, 12.2, y_shared + 0.45, 12.6, y_shared + 0.45)

ax.text(7.7, y_upper + 1.1, "OCR-mediated path",
        ha="center", fontsize=11, style="italic")
ax.text(7.7, y_lower - 0.25, "vision-mediated path",
        ha="center", fontsize=11, style="italic")

ax.set_xlim(-0.3, 15.3)
ax.set_ylim(0.3, 5.4)
ax.set_aspect("equal")
ax.axis("off")

fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
