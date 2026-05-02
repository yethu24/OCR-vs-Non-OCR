"""Generate fig-3-3-extraction-paradigm-tree.png.

Taxonomy tree organising extraction approaches surveyed in Chapter 3
by their answer to the template-free criterion.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).parent / "fig-3-3-extraction-paradigm-tree.png"

fig, ax = plt.subplots(figsize=(14.0, 7.5))


def box(ax, x, y, w, h, text, *, facecolor="white",
        edgecolor="black", fontsize=10, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.03,rounding_size=0.08",
                                facecolor=facecolor, edgecolor=edgecolor,
                                linewidth=1.2))
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, fontweight="bold" if bold else "normal")


def edge(ax, x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                 arrowstyle="-", mutation_scale=10,
                                 linewidth=1.0, color="#555555"))


root_x, root_y = 7.0, 7.2
box(ax, root_x, root_y, 7.0, 0.8,
    "Structured extraction from semi-structured documents",
    facecolor="#ececec", bold=True, fontsize=11)

template_x = 3.0
learned_x = 11.0
branch_y = 5.8
box(ax, template_x, branch_y, 4.0, 0.8,
    "Template-based\n(fails template-free criterion)",
    facecolor="#fce5cd", edgecolor="#9e1b32", fontsize=10, bold=True)
box(ax, learned_x, branch_y, 4.0, 0.8,
    "Learned-generalist\n(satisfies template-free criterion)",
    facecolor="#e2f0d9", edgecolor="#2e7d32", fontsize=10, bold=True)

edge(ax, root_x, root_y - 0.4, template_x, branch_y + 0.4)
edge(ax, root_x, root_y - 0.4, learned_x, branch_y + 0.4)

sub1_x = 1.5
sub2_x = 4.5
sub_y = 4.2
box(ax, sub1_x, sub_y, 2.4, 0.65, "rule-based",
    facecolor="#fff3e6", fontsize=9)
box(ax, sub2_x, sub_y, 2.4, 0.65, "2D-grid",
    facecolor="#fff3e6", fontsize=9)
edge(ax, template_x, branch_y - 0.4, sub1_x, sub_y + 0.35)
edge(ax, template_x, branch_y - 0.4, sub2_x, sub_y + 0.35)

leaf_fs = 8
leaf_h = 0.45
leaf_w = 2.4
leaves_rule = ["Klink & Kieninger", "Intellix"]
for i, leaf in enumerate(leaves_rule):
    ly = sub_y - 0.95 - i * 0.55
    box(ax, sub1_x, ly, leaf_w, leaf_h, leaf, fontsize=leaf_fs)
    edge(ax, sub1_x, sub_y - 0.35, sub1_x, ly + leaf_h / 2)

leaves_grid = ["Chargrid", "BERTgrid", "CloudScan"]
for i, leaf in enumerate(leaves_grid):
    ly = sub_y - 0.95 - i * 0.55
    box(ax, sub2_x, ly, leaf_w, leaf_h, leaf, fontsize=leaf_fs)
    edge(ax, sub2_x, sub_y - 0.35, sub2_x, ly + leaf_h / 2)

sub3_x = 9.2
sub4_x = 12.6
box(ax, sub3_x, sub_y, 2.8, 0.65, "OCR + LLM cascade",
    facecolor="#e6f4ea", fontsize=9)
box(ax, sub4_x, sub_y, 2.8, 0.65, "end-to-end VLM",
    facecolor="#e6f4ea", fontsize=9)
edge(ax, learned_x, branch_y - 0.4, sub3_x, sub_y + 0.35)
edge(ax, learned_x, branch_y - 0.4, sub4_x, sub_y + 0.35)

leaves_cascade = ["Shen et al. 2026", "Wei (ChatIE)", "Thomas et al.",
                  "Borchmann GPT-4", "Bourne (CLOCR-C)"]
for i, leaf in enumerate(leaves_cascade):
    ly = sub_y - 0.95 - i * 0.55
    box(ax, sub3_x, ly, 2.8, leaf_h, leaf, fontsize=leaf_fs)
    edge(ax, sub3_x, sub_y - 0.35, sub3_x, ly + leaf_h / 2)

leaves_vlm = ["Donut", "LayoutLMv3", "Pix2Struct",
              "InternVL 1.5", "Florence-2"]
for i, leaf in enumerate(leaves_vlm):
    ly = sub_y - 0.95 - i * 0.55
    box(ax, sub4_x, ly, 2.8, leaf_h, leaf, fontsize=leaf_fs)
    edge(ax, sub4_x, sub_y - 0.35, sub4_x, ly + leaf_h / 2)

ax.set_xlim(-0.2, 14.2)
ax.set_ylim(0.4, 8.0)
ax.set_aspect("equal")
ax.axis("off")

fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
