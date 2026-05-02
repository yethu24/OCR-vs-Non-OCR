"""Generate fig-5-2-sequence-diagram.png.

Side-by-side sequence for one document through the OCR-mediated path
and the vision-mediated path. The bracketed timing keys match the
Timer labels in src/performance.py.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).parent / "fig-5-2-sequence-diagram.png"

fig, ax = plt.subplots(figsize=(11, 6.8))
ax.set_xlim(0, 11)
ax.set_ylim(0, 6.8)
ax.axis("off")

ax.text(5.5, 6.55, "Figure 5.2  Per-document sequence: OCR-mediated (left) vs vision-mediated (right)",
        ha="center", va="top", fontsize=11, fontweight="bold")

LANES = [
    (0.4, "Pipeline"),
    (2.6, "Rasteriser"),
    (4.8, "Tesseract OCR"),
    (7.0, "LLM provider"),
    (9.2, "Normaliser\n+ persister"),
]
for x, label in LANES:
    ax.add_patch(FancyBboxPatch((x, 5.75), 1.6, 0.5,
                                boxstyle="round,pad=0.02",
                                facecolor="#f0f3f9",
                                edgecolor="black", linewidth=1.0))
    ax.text(x + 0.8, 6.0, label, ha="center", va="center",
            fontsize=9, fontweight="bold")
    ax.plot([x + 0.8, x + 0.8], [5.75, 0.4],
            color="#888", linestyle=":", linewidth=0.9)


def arrow(x1, y, x2, *, label, dashed=False, right=True):
    style = "->" if right else "<-"
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle=style,
                                linestyle="--" if dashed else "-",
                                color="black", lw=1.1))
    mid = (x1 + x2) / 2
    ax.text(mid, y + 0.08, label, ha="center", va="bottom",
            fontsize=8)


ax.text(0.4, 5.55, "OCR-mediated path",
        ha="left", va="top", fontsize=9.5, fontweight="bold",
        color="#6a4a16")
arrow(1.2, 5.05, 3.4, label="rasterise(pdf)  [pdf_to_images_ms]")
arrow(3.4, 4.80, 5.6, label="extract_text(img, lang)  [ocr_ms]")
arrow(5.6, 4.45, 7.8, label="extract_from_text(ocr_text, prompt)  [llm_call_ms]")
arrow(7.8, 4.10, 10.0, label="raw_output, tokens, latency  [parse_normalise_ms]",
      right=False)

ax.axhline(3.85, color="#b0b0b0", linewidth=0.7, linestyle="--")

ax.text(0.4, 3.75, "Vision-mediated path",
        ha="left", va="top", fontsize=9.5, fontweight="bold",
        color="#6a4a16")
arrow(1.2, 3.25, 3.4, label="rasterise(pdf)  [pdf_to_images_ms]")
arrow(3.4, 3.00, 7.8,
      label="(skipped)                                     extract_from_image(pages, prompt)  [llm_call_ms]",
      dashed=True)
arrow(7.8, 2.65, 10.0, label="raw_output, tokens, latency  [parse_normalise_ms]",
      right=False)

ax.text(0.4, 2.20, "Shared finalisation (both paths)",
        ha="left", va="top", fontsize=9.5, fontweight="bold",
        color="#1f4a26")
arrow(10.0, 1.85, 1.2, label="persist extraction.json, raw_llm_output.txt, timings.json, metadata.json",
      right=False)
arrow(1.2, 1.50, 10.0,
      label="next document...", dashed=True)

note = (
    "Same pipeline, same LLM provider, same prompt, same normaliser and same "
    "persister on both paths. The only component that varies between paths is "
    "whether Tesseract sits between the rasteriser and the LLM (ER1 modality "
    "isolation)."
)
ax.text(5.5, 0.85, note, ha="center", va="top", fontsize=8.5,
        wrap=True, style="italic", color="#444")

fig.savefig(OUT, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Wrote {OUT}")
