"""Generate fig-5-6-run-directory.png.

Per-run directory tree, visualising the disk-mediated decoupling
between the pipeline and the evaluator (ER4 reproducibility +
auditability).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "fig-5-6-run-directory.png"

fig, ax = plt.subplots(figsize=(8.6, 5.2))
ax.set_xlim(0, 8.6)
ax.set_ylim(0, 5.2)
ax.axis("off")

ax.text(4.3, 5.0, "Figure 5.6  Per-run directory layout",
        ha="center", va="top", fontsize=12, fontweight="bold")

tree = [
    ("results/runs/{run_id}/",               0, "run root"),
    ("config.yaml",                          1, "effective config snapshot"),
    ("manifest_snapshot.csv",                1, "dataset manifest at run time"),
    ("prompt.txt",                           1, "exact prompt template used"),
    ("summary.json",                         1, "processed, skipped, failed counts"),
    ("evaluation.json",                      1, "written by evaluate command"),
    ("documents/",                           1, ""),
    ("  {document_id}/",                     2, "one dir per document"),
    ("    extraction.json",                  3, "12-field BillExtraction"),
    ("    raw_llm_output.txt",               3, "verbatim LLM response (NFR8)"),
    ("    ocr_text.txt",                     3, "Tesseract output (OCR mode only)"),
    ("    timings.json",                     3, "per-stage timing"),
    ("    metadata.json",                    3, "tokens, cost estimate, model id"),
    ("    error.json (optional)",            3, "written on failure (NFR3)"),
    ("    diagnosis.json (optional)",        3, "failure attribution"),
]

y = 4.45
for label, depth, note in tree:
    indent = 0.4 + depth * 0.7
    prefix = ""
    if depth > 0:
        prefix = "|- "
    ax.text(indent, y, prefix + label, ha="left", va="top",
            fontsize=9, fontfamily="monospace")
    if note:
        ax.text(5.9, y, note, ha="left", va="top",
                fontsize=8.5, style="italic", color="#555")
    y -= 0.27

ax.text(0.4, 0.35,
        "The evaluator reads only from this directory. The pipeline and the\n"
        "evaluator never share memory, so each can be run, replayed, and\n"
        "inspected independently.",
        ha="left", va="top", fontsize=8.5, style="italic", color="#444")

fig.savefig(OUT, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Wrote {OUT}")
