"""Generate fig-3-2-gap-to-requirements-map.png.

Two-column diagram: four gap boxes (literature review subsections) on the
left, seven ER boxes (ER1-ER7) on the right. Arrows connect gaps to the
ERs they motivate.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).parent / "fig-3-2-gap-to-requirements-map.png"

GAPS = [
    ("§3.2 OCR cascade",
     "OCR error cascade on\nmultilingual noisy input"),
    ("§3.3 Text-mode LLM",
     "Output-mechanism\nasymmetry across providers"),
    ("§3.5 Controlled comparisons",
     "No study meets all four\nrubric controls at once"),
    ("§3.6 Evaluation methodology",
     "Null handling and failure\nattribution gaps"),
]

ERS = [
    ("ER1", "Modality-Isolation"),
    ("ER2", "Multilingual-Coverage"),
    ("ER3", "Operational-Instrumentation"),
    ("ER4", "Reproducibility"),
    ("ER5", "Failure-Attribution"),
    ("ER6", "Null-Aware Evaluation"),
    ("ER7", "Cross-Provider Generality"),
]

EDGES = [
    (0, 0), (0, 1), (0, 4),
    (1, 3), (1, 6), (1, 4),
    (2, 0), (2, 1), (2, 2), (2, 6),
    (3, 3), (3, 4), (3, 5),
]

fig, ax = plt.subplots(figsize=(13.0, 8.5))

left_x = 0.2
left_w = 4.0
right_x = 8.0
right_w = 4.2

gap_top = 7.8
gap_spacing = 1.9
gap_h = 1.2

er_top = 8.0
er_spacing = 1.05
er_h = 0.75

gap_centres = []
for i, (section, label) in enumerate(GAPS):
    y = gap_top - i * gap_spacing
    box = FancyBboxPatch((left_x, y - gap_h / 2), left_w, gap_h,
                         boxstyle="round,pad=0.04,rounding_size=0.12",
                         facecolor="#fce5cd", edgecolor="#9e1b32",
                         linewidth=1.3)
    ax.add_patch(box)
    ax.text(left_x + left_w / 2, y + 0.25, label,
            ha="center", va="center", fontsize=10)
    ax.text(left_x + left_w / 2, y - 0.40, section,
            ha="center", va="center", fontsize=9,
            style="italic", color="#444444")
    gap_centres.append((left_x + left_w, y))

er_centres = []
for i, (rid, label) in enumerate(ERS):
    y = er_top - i * er_spacing
    box = FancyBboxPatch((right_x, y - er_h / 2), right_w, er_h,
                         boxstyle="round,pad=0.03,rounding_size=0.08",
                         facecolor="#e2f0d9", edgecolor="#2e7d32",
                         linewidth=1.3)
    ax.add_patch(box)
    ax.text(right_x + 0.2, y, rid,
            ha="left", va="center", fontsize=11, fontweight="bold",
            color="#2e7d32")
    ax.text(right_x + 1.1, y, label,
            ha="left", va="center", fontsize=10)
    er_centres.append((right_x, y))

for gi, ei in EDGES:
    x0, y0 = gap_centres[gi]
    x1, y1 = er_centres[ei]
    arrow = FancyArrowPatch((x0, y0), (x1, y1),
                            arrowstyle="-|>", mutation_scale=10,
                            linewidth=0.9, color="#555555",
                            connectionstyle="arc3,rad=0.0",
                            alpha=0.75)
    ax.add_patch(arrow)

ax.text(left_x + left_w / 2, gap_top + 1.1,
        "Literature-review gaps",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color="#9e1b32")
ax.text(right_x + right_w / 2, er_top + 1.1,
        "Experimental requirement classes",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color="#2e7d32")

ax.set_xlim(-0.2, right_x + right_w + 0.5)
ax.set_ylim(er_top - er_spacing * (len(ERS) - 1) - 1.0, gap_top + 1.8)
ax.set_aspect("equal")
ax.axis("off")

fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
