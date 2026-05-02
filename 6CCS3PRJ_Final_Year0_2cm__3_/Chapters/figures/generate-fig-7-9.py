"""Generate fig-7-9-hallucination-omission-pareto.png.

2D scatter of (hallucination count, omission count) for the four
conditions, annotated with condition labels and provider/modality
glyphs. Reads counts directly from comparison.json so the figure
is reproducible from a single run-comparison artefact.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "fig-7-9-hallucination-omission-pareto.png"
COMPARISON = Path(
    "C:/Users/winye/OCR vs Non-OCR/results/reports/four_way_20260429/comparison.json"
)


def _label_for(run_id: str) -> tuple[str, str, str]:
    """Map a run_id to (provider, modality, marker).

    The run_id encodes the provider (anthropic_claudesonnet*/openai_gpt4o)
    and the modality suffix (_ocr_text or _vision). Reading the suffix
    keeps the figure reproducible across re-runs that change the run
    timestamp prefix.
    """
    if "anthropic" in run_id:
        provider = "Sonnet 4.5"
    elif "openai" in run_id:
        provider = "GPT-4o"
    else:
        raise ValueError(f"unknown provider in run_id {run_id}")
    if run_id.endswith("_ocr_text"):
        return provider, "OCR", "o"
    if run_id.endswith("_vision"):
        return provider, "Vision", "s"
    raise ValueError(f"unknown modality in run_id {run_id}")


def main() -> None:
    data = json.loads(COMPARISON.read_text(encoding="utf-8"))
    null_analysis = data["null_analysis"]

    points = []
    for run_id, counts in null_analysis.items():
        provider, modality, marker = _label_for(run_id)
        points.append((counts["hallucinations"], counts["omissions"],
                       provider, modality, marker))

    fig, ax = plt.subplots(figsize=(7.5, 6.0))

    for h, o, provider, modality, marker in points:
        face = "white" if provider == "GPT-4o" else "#444444"
        edge = "black"
        ax.scatter(h, o, marker=marker, s=210, facecolor=face, edgecolor=edge,
                   linewidth=1.6, zorder=3)
        ax.annotate(f"{provider} / {modality}",
                    xy=(h, o), xytext=(h + 0.35, o + 0.35),
                    fontsize=10)

    ax.set_xlabel("hallucinations  (count, all 12 fields x 40 docs)")
    ax.set_ylabel("omissions  (count, all 12 fields x 40 docs)")
    ax.set_xlim(0, max(p[0] for p in points) + 4)
    ax.set_ylim(0, max(p[1] for p in points) + 4)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.7)
    ax.spines[["top", "right"]].set_visible(False)

    ax.text(0.98, 0.02,
            "filled = Sonnet 4.5    hollow = GPT-4o\n"
            "circle = OCR    square = Vision",
            transform=ax.transAxes, fontsize=9, ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor="#999999"))

    ax.set_title("Hallucination vs. omission, four conditions",
                 fontsize=12, fontweight="bold")

    fig.tight_layout()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
