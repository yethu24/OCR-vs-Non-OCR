"""Generate fig-2-4-vlm-architecture.png.

Block diagram of the dominant VLM pattern: vision encoder, projection,
LLM decoder, with a text prompt joining the decoder.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).parent / "fig-2-4-vlm-architecture.png"

fig, ax = plt.subplots(figsize=(12.5, 4.2))


def box(ax, x, y, w, h, text, *, facecolor="white", fontsize=11, bold=False):
    patch = FancyBboxPatch((x, y), w, h,
                           boxstyle="round,pad=0.02,rounding_size=0.08",
                           facecolor=facecolor, edgecolor="black",
                           linewidth=1.2)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center", fontsize=fontsize,
            fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                 arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.1, color="black"))


y_mid = 1.4
box(ax, 0.0, y_mid, 1.7, 0.9, "page image", facecolor="#f3f3f3")

vlm_x, vlm_y, vlm_w, vlm_h = 2.1, 0.9, 6.4, 1.9
dashed = Rectangle((vlm_x, vlm_y), vlm_w, vlm_h,
                   facecolor="none", edgecolor="black", linewidth=1.2,
                   linestyle=(0, (4, 3)))
ax.add_patch(dashed)
ax.text(vlm_x + vlm_w / 2, vlm_y + vlm_h + 0.12,
        "vision-language model",
        ha="center", va="bottom", fontsize=11, style="italic")

inner_y = vlm_y + 0.55
inner_h = 0.9
box(ax, vlm_x + 0.15, inner_y, 1.8, inner_h, "vision\nencoder")
box(ax, vlm_x + 2.20, inner_y, 1.6, inner_h, "projection")
box(ax, vlm_x + 4.05, inner_y, 2.2, inner_h, "LLM\ndecoder", bold=True)

arrow(ax, 1.7, y_mid + 0.45, vlm_x + 0.15, inner_y + inner_h / 2)
arrow(ax, vlm_x + 1.95, inner_y + inner_h / 2, vlm_x + 2.20, inner_y + inner_h / 2)
arrow(ax, vlm_x + 3.80, inner_y + inner_h / 2, vlm_x + 4.05, inner_y + inner_h / 2)

out_x = vlm_x + vlm_w + 0.4
box(ax, out_x, y_mid, 2.2, 0.9, "structured\nrecord", facecolor="#f3f3f3")
arrow(ax, vlm_x + 6.25, inner_y + inner_h / 2, out_x, y_mid + 0.45)

prompt_x, prompt_y = vlm_x + 4.4, 0.05
box(ax, prompt_x, prompt_y, 1.6, 0.55, "text prompt", facecolor="#f3f3f3",
    fontsize=10)
arrow(ax, prompt_x + 0.8, prompt_y + 0.55, vlm_x + 5.15, inner_y)

ax.set_xlim(-0.3, out_x + 2.6)
ax.set_ylim(-0.2, vlm_y + vlm_h + 0.7)
ax.set_aspect("equal")
ax.axis("off")

fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
