"""Generate fig-5-5-json-parse-fallback.png.

The four-stage JSON parse hardening chain, as a top-to-bottom
flowchart. On success any stage emits the parsed dict; on failure the
next stage is attempted; the final diagnostic failure preserves the
raw LLM output for post-hoc inspection.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).parent / "fig-5-5-json-parse-fallback.png"

fig, ax = plt.subplots(figsize=(8.4, 6.2))
ax.set_xlim(0, 8.4)
ax.set_ylim(0, 6.2)
ax.axis("off")

ax.text(4.2, 6.0, "Figure 5.5  JSON parse hardening chain",
        ha="center", va="top", fontsize=12, fontweight="bold")


def box(x, y, w, h, text, *, face="white", bold=False, fs=9.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.04",
                                facecolor=face, edgecolor="black",
                                linewidth=1.2))
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal")


def arrow(x1, y1, x2, y2, *, label=None, dashed=False):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->",
                                linestyle="--" if dashed else "-",
                                color="black", lw=1.1))
    if label:
        ax.text((x1 + x2) / 2 + 0.15, (y1 + y2) / 2, label,
                ha="left", va="center", fontsize=8.5, style="italic")


box(2.5, 5.0, 3.4, 0.65, "raw LLM output string", bold=True,
    face="#f0f3f9")

box(2.5, 4.0, 3.4, 0.65, "1. direct json.loads(text.strip())")
arrow(4.2, 5.0, 4.2, 4.65)

box(2.5, 3.0, 3.4, 0.65, "2. strip triple-backtick\njson-fenced block and parse",
    fs=9)
arrow(4.2, 4.0, 4.2, 3.65, label="fail")

box(2.5, 2.0, 3.4, 0.65, "3. extract first brace-balanced\n{...} substring and parse",
    fs=9)
arrow(4.2, 3.0, 4.2, 2.65, label="fail")

box(2.5, 1.0, 3.4, 0.65,
    "4. raise ValueError with\nfirst 500 chars of raw output",
    fs=9, face="#fff0ef")
arrow(4.2, 2.0, 4.2, 1.65, label="fail")

box(6.7, 3.3, 1.5, 0.65, "parsed dict", bold=True, face="#eaf6ec")
arrow(5.9, 4.3, 6.7, 3.62, label="ok", dashed=True)
arrow(5.9, 3.3, 6.7, 3.45, label="ok", dashed=True)
arrow(5.9, 2.3, 6.7, 3.30, label="ok", dashed=True)

ax.text(4.2, 0.5,
        "Stage 4 preserves raw_llm_output.txt for the run so a parse\n"
        "failure is recoverable and post-hoc auditable (NFR8).",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#444")

fig.savefig(OUT, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Wrote {OUT}")
