"""Generate fig-5-3-strategy-pattern.png.

Class diagram of the provider and OCR strategy hierarchies with the
registry as the indirection point. A greyed-out panel shows the
rejected alternative (hard-coded dispatch) for explicit D-2 evidence.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).parent / "fig-5-3-strategy-pattern.png"

fig, ax = plt.subplots(figsize=(11.0, 7.4))
ax.set_xlim(0, 11.0)
ax.set_ylim(0, 7.4)
ax.axis("off")

ax.text(5.5, 7.20, "Figure 5.3  Strategy pattern for LLM providers and OCR engines",
        ha="center", va="top", fontsize=12, fontweight="bold")


def umlbox(x, y, w, h, title, body, *, face="white", edge="black",
           title_bold=True, body_mono=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02",
                                facecolor=face, edgecolor=edge,
                                linewidth=1.2))
    ax.plot([x + 0.05, x + w - 0.05], [y + h - 0.35, y + h - 0.35],
            color=edge, linewidth=0.8)
    ax.text(x + w / 2, y + h - 0.2, title,
            ha="center", va="center",
            fontsize=9.5, fontweight="bold" if title_bold else "normal")
    ax.text(x + 0.15, y + h - 0.5, body,
            ha="left", va="top",
            fontsize=8.5,
            fontfamily="monospace" if body_mono else "sans-serif")


def arrow(x1, y1, x2, y2, *, ls="-", lw=1.0, color="black"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", linestyle=ls,
                                color=color, lw=lw))


umlbox(4.2, 5.8, 2.6, 0.95,
       "registry.get_provider(config)",
       "lazy import + instantiate\nby provider name",
       face="#fdf1dc")

umlbox(1.3, 4.0, 2.7, 1.55,
       "<<ABC>> LLMProvider",
       "+ extract_from_text(text, prompt)\n"
       "+ extract_from_image(imgs, prompt)\n"
       "+ get_model_id()\n"
       "+ encode_image_base64()",
       face="#eef3fb")

umlbox(7.0, 4.0, 2.7, 1.55,
       "<<ABC>> OCREngine",
       "+ extract_text(image, lang)",
       face="#eef3fb")

arrow(4.2, 5.90, 2.95, 5.55, color="#7a5418")
arrow(6.8, 5.90, 8.05, 5.55, color="#7a5418")

umlbox(0.15, 2.0, 2.6, 1.5,
       "OpenAIProvider",
       "Responses API\n"
       "Structured Outputs\n"
       "text_format=BillExtraction")

umlbox(2.85, 2.0, 2.6, 1.5,
       "AnthropicProvider",
       "Messages API\n"
       "prompt-instructed JSON\n"
       "+ _strip_json_fencing()")

arrow(1.45, 3.50, 2.20, 4.00)
arrow(4.15, 3.50, 3.10, 4.00)

umlbox(7.0, 2.0, 2.6, 1.5,
       "TesseractOCR",
       "pytesseract binding\n"
       "LANGUAGE_MAP:\n"
       "en, de, fr, it")

arrow(8.30, 3.50, 8.30, 4.00)

umlbox(1.3, 0.15, 5.0, 1.35,
       "Rejected: hard-coded dispatch in pipeline",
       "if cfg.provider == \"openai\":\n"
       "    use OpenAIProvider\n"
       "elif cfg.provider == \"anthropic\":\n"
       "    use AnthropicProvider",
       face="#efefef")

ax.text(6.6, 0.82,
        "rejected because adding a\n"
        "provider would require editing\n"
        "pipeline.py, breaking NFR4 and\n"
        "coupling tests to provider choice.",
        ha="left", va="center", fontsize=9, style="italic",
        color="#8a1111")

fig.savefig(OUT, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Wrote {OUT}")
