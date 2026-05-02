"""Generate fig-4-1-factorial-matrix.png.

2x2 factorial matrix for Ch4 Section 4.6. Rows: LLM provider.
Columns: input modality. Cells: condition labels C1-C4 with a short
descriptor. Image is rendered greyscale-friendly (no colour-only
information) and sized for single-column placement in a KCL
informatics-report class document.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = Path(__file__).parent / "fig-4-1-factorial-matrix.png"

fig, ax = plt.subplots(figsize=(7.5, 4.6))

cell_w, cell_h = 1.3, 1.0
x_origin, y_origin = 0.0, 0.0

# Cell positions (col, row): columns = modality, rows = provider
cells = {
    (0, 1): ("C1", "OpenAI GPT-4o", "OCR-mediated"),
    (1, 1): ("C2", "OpenAI GPT-4o", "vision-mediated"),
    (0, 0): ("C3", "Anthropic Claude", "OCR-mediated"),
    (1, 0): ("C4", "Anthropic Claude", "vision-mediated"),
}

for (col, row), (tag, model, mode) in cells.items():
    x = x_origin + col * cell_w
    y = y_origin + row * cell_h
    rect = Rectangle((x, y), cell_w, cell_h,
                     facecolor="white", edgecolor="black", linewidth=1.4)
    ax.add_patch(rect)
    ax.text(x + cell_w / 2, y + cell_h * 0.72, tag,
            ha="center", va="center", fontsize=22, fontweight="bold")
    ax.text(x + cell_w / 2, y + cell_h * 0.42, model,
            ha="center", va="center", fontsize=9)
    ax.text(x + cell_w / 2, y + cell_h * 0.26, "+",
            ha="center", va="center", fontsize=9)
    ax.text(x + cell_w / 2, y + cell_h * 0.13, mode,
            ha="center", va="center", fontsize=9, style="italic")

# Column headers
for col, label in enumerate(["Text mode", "Vision mode"]):
    ax.text(x_origin + col * cell_w + cell_w / 2,
            y_origin + 2 * cell_h + 0.12,
            label, ha="center", va="bottom",
            fontsize=11, fontweight="bold")
ax.text(x_origin + cell_w, y_origin + 2 * cell_h + 0.40,
        "Input modality", ha="center", va="bottom",
        fontsize=11, fontstyle="italic")

# Row labels
for row, label in enumerate(["Model B", "Model A"]):
    ax.text(x_origin - 0.10, y_origin + row * cell_h + cell_h / 2,
            label, ha="right", va="center",
            fontsize=11, fontweight="bold")
ax.text(x_origin - 0.55, y_origin + cell_h,
        "LLM provider", ha="center", va="center",
        fontsize=11, fontstyle="italic", rotation=90)

ax.set_xlim(x_origin - 0.85, x_origin + 2 * cell_w + 0.15)
ax.set_ylim(y_origin - 0.15, y_origin + 2 * cell_h + 0.60)
ax.set_aspect("equal")
ax.axis("off")

fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
