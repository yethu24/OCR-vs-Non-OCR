"""Generate fig-5-1-architecture.png.

End-to-end block architecture showing shared preprocessing, the two
modality branches, and shared post-processing. The branch boundary is
the modality-isolation control (ER1): inside the branch the input
modality varies; outside the branch every component is held constant.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

OUT = Path(__file__).parent / "fig-5-1-architecture.png"

fig, ax = plt.subplots(figsize=(10.5, 6.4))
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 6.4)
ax.axis("off")


def box(x, y, w, h, text, *, fs=9, bold=False, face="white", edge="black",
        lw=1.2, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02",
                                facecolor=face, edgecolor=edge,
                                linewidth=lw, linestyle=ls))
    weight = "bold" if bold else "normal"
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight=weight)


def arrow(x1, y1, x2, y2, *, ls="-", color="black", lw=1.2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", linestyle=ls,
                                color=color, lw=lw))


ax.text(5.25, 6.15, "Figure 5.1  End-to-end architecture",
        ha="center", va="top", fontsize=12, fontweight="bold")

SHARED_IN = "#eef3fb"
BRANCH = "#fdf1dc"
SHARED_OUT = "#eaf6ec"

ax.add_patch(Rectangle((0.3, 0.5), 1.95, 5.1, facecolor=SHARED_IN,
                       edgecolor="none", alpha=0.6))
ax.text(1.275, 5.5, "Shared input", ha="center", va="center",
        fontsize=9, fontweight="bold", color="#1f3a5f")

box(0.5, 4.55, 1.55, 0.65, "Dataset\nmanifest (CSV)", fs=9, bold=True)
box(0.5, 3.55, 1.55, 0.65, "DatasetLoader\nvalidate + filter", fs=9)
box(0.5, 2.55, 1.55, 0.65, "PDF files", fs=9)
box(0.5, 1.55, 1.55, 0.65, "Rasterise\n(PDF to image)", fs=9)
arrow(1.275, 4.55, 1.275, 4.22)
arrow(1.275, 3.55, 1.275, 3.22)
arrow(1.275, 2.55, 1.275, 2.22)

ax.add_patch(Rectangle((2.6, 1.1), 4.7, 3.55, facecolor=BRANCH,
                       edgecolor="#b0761d", linewidth=1.4, linestyle="--"))
ax.text(4.95, 4.45, "Modality branch  (ER1: input-only variable)",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color="#6a4a16")

box(2.85, 3.35, 2.0, 0.75, "Tesseract OCR\nlanguage from manifest",
    fs=9, face="white")
box(2.85, 2.35, 2.0, 0.75, "LLM text mode\n(provider, prompt,\ntemperature fixed)",
    fs=9, face="white")
arrow(3.85, 3.35, 3.85, 3.10)

box(5.1, 2.85, 2.0, 0.75, "LLM vision mode\n(same provider, prompt,\ntemperature)",
    fs=9, face="white")

arrow(2.05, 1.87, 2.85, 3.72, color="#555")
arrow(2.05, 1.87, 5.1, 3.22, color="#555")

ax.text(2.85, 4.12, "OCR path", ha="left", va="bottom", fontsize=8,
        style="italic", color="#6a4a16")
ax.text(5.1, 3.62, "Vision path", ha="left", va="bottom", fontsize=8,
        style="italic", color="#6a4a16")

ax.add_patch(Rectangle((7.65, 0.5), 2.6, 5.1, facecolor=SHARED_OUT,
                       edgecolor="none", alpha=0.7))
ax.text(8.95, 5.5, "Shared output", ha="center", va="center",
        fontsize=9, fontweight="bold", color="#1f4a26")

box(7.85, 4.55, 2.2, 0.65, "JSON parse\n(fallback chain)", fs=9)
box(7.85, 3.55, 2.2, 0.65, "Normalise\n(dispatch table)", fs=9)
box(7.85, 2.55, 2.2, 0.65, "Pydantic validate", fs=9)
box(7.85, 1.55, 2.2, 0.65, "Persist run artefacts", fs=9)
box(7.85, 0.55, 2.2, 0.65, "Evaluate +\ncompare +\nreport", fs=9, bold=True)

arrow(4.85, 2.72, 7.85, 4.70, color="#333")
arrow(7.1, 3.22, 7.85, 4.70, color="#333")

arrow(8.95, 4.55, 8.95, 4.22)
arrow(8.95, 3.55, 8.95, 3.22)
arrow(8.95, 2.55, 8.95, 2.22)
arrow(8.95, 1.55, 8.95, 1.22)

legend_elems = [
    Line2D([0], [0], marker='s', color='w',
           markerfacecolor=SHARED_IN, markersize=11,
           label="Shared input  (held constant)"),
    Line2D([0], [0], marker='s', color='w',
           markerfacecolor=BRANCH, markersize=11,
           label="Modality branch  (varies per condition)"),
    Line2D([0], [0], marker='s', color='w',
           markerfacecolor=SHARED_OUT, markersize=11,
           label="Shared output  (held constant)"),
]
ax.legend(handles=legend_elems, loc="lower center", ncol=3,
          frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.02))

fig.savefig(OUT, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Wrote {OUT}")
