"""Generate fig-2-3-ocr-error-cascade.png.

Left-to-right four-panel chain illustrating how a single OCR error
propagates through tokenisation and extraction.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

OUT = Path(__file__).parent / "fig-2-3-ocr-error-cascade.png"

fig, ax = plt.subplots(figsize=(13.5, 4.2))

panel_w, panel_h = 2.9, 2.4
gap = 0.7
y = 0.5

panels = [
    ("1. Page image", [
        ("Total due:", 0.20, 1.60, 10, False),
        ("EUR 142,50", 0.20, 1.10, 14, True),
    ]),
    ("2. OCR output", [
        ("Total due:", 0.20, 1.60, 10, False),
        ("£142.5O", 0.20, 1.10, 14, True),
        ("(0 -> O)", 0.20, 0.55, 9, False),
    ]),
    ("3. Tokeniser", [
        ("tokens:", 0.20, 1.70, 10, False),
        ("[\"£\",", 0.20, 1.30, 11, False),
        ("\"142.5\",", 0.20, 0.95, 11, False),
        ("\"O\"]", 0.20, 0.60, 11, False),
    ]),
    ("4. Extractor", [
        ("total_amount_due:", 0.20, 1.60, 9, False),
        ("null", 0.20, 1.10, 14, True),
        ("(unparseable)", 0.20, 0.55, 9, False),
    ]),
]

xs = []
x = 0.0
for title, lines in panels:
    ax.add_patch(Rectangle((x, y), panel_w, panel_h,
                           facecolor="white", edgecolor="black", linewidth=1.3))
    ax.text(x + panel_w / 2, y + panel_h + 0.15, title,
            ha="center", va="bottom", fontsize=11, fontweight="bold")
    for text, tx, ty, fs, bold in lines:
        ax.text(x + tx, y + ty, text, fontsize=fs,
                fontfamily="monospace",
                fontweight="bold" if bold else "normal",
                va="center")
    xs.append((x, x + panel_w))
    x += panel_w + gap

for (_, x_end), (x_start, _) in zip(xs[:-1], xs[1:]):
    arrow = FancyArrowPatch((x_end + 0.05, y + panel_h / 2),
                            (x_start - 0.05, y + panel_h / 2),
                            arrowstyle="-|>", mutation_scale=16,
                            color="black", linewidth=1.2)
    ax.add_patch(arrow)

error_y = y + panel_h + 0.65
ax.annotate("", xy=(xs[-1][0] + 0.8, error_y),
            xytext=(xs[0][1] - 0.5, error_y),
            arrowprops=dict(arrowstyle="->",
                            linestyle=(0, (2, 2)),
                            color="#9e1b32", linewidth=1.5))
ax.text((xs[0][1] + xs[-1][0]) / 2, error_y + 0.18,
        "single recognition error disables every downstream stage",
        ha="center", va="bottom", fontsize=10, style="italic",
        color="#9e1b32")

total_w = x - gap
ax.set_xlim(-0.3, total_w + 0.3)
ax.set_ylim(0, y + panel_h + 1.2)
ax.set_aspect("equal")
ax.axis("off")

fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
