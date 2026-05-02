"""Generate fig-7-10-failure-attribution.png.

Side-by-side stacked bars comparing the strict two-bucket
failure-diagnosis heuristic (OCR / LLM) against a four-bucket
re-classification (Pure OCR / Pure LLM-extraction / LLM-inference /
GT-ambiguity) for the two OCR-mode runs of the four_way_20260429
experiment.

Both sets of counts are derived from
results/reports/four_way_20260429/derived/diagnosis_audit.csv. The
two-bucket counts are read directly from the strict_attribution
column. The four-bucket counts apply two reclassification rules on
top of the strict heuristic:
  - GT-ambiguity: known multiple-defensible-answer cases identified
    during the chapter's error analysis (PSCo legal name vs Xcel
    wordmark; IREN vs IREN MERCATO; ENGIE vs ENGIE Italia S.p.A.;
    Affinity Water current charges vs outstanding balance; Peoples
    Gas account-number whitespace).
  - LLM-inference: currency and utility_type fields where the GT
    string is not in the OCR text but the issuer-locale or
    issuer-logo signal is available to the model.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "fig-7-10-failure-attribution.png"

# Two-bucket strict heuristic counts (strict_attribution column of
# diagnosis_audit.csv aggregated by provider).
two_bucket = {
    "Sonnet 4.5 / OCR": {"OCR": 27, "LLM": 20},
    "GPT-4o / OCR":      {"OCR": 35, "LLM": 26},
}

# Four-bucket re-classification after applying the GT-ambiguity and
# LLM-inference rules above to diagnosis_audit.csv. Sums match the
# two-bucket totals per row (Sonnet 47, GPT-4o 61).
four_bucket = {
    "Sonnet 4.5 / OCR": {
        "Pure OCR":            26,
        "Pure LLM-extraction": 17,
        "LLM-inference":        1,
        "GT-ambiguity":         3,
    },
    "GPT-4o / OCR": {
        "Pure OCR":            31,
        "Pure LLM-extraction": 23,
        "LLM-inference":        4,
        "GT-ambiguity":         3,
    },
}

TWO_ORDER = ["OCR", "LLM"]
FOUR_ORDER = ["Pure OCR", "Pure LLM-extraction", "LLM-inference", "GT-ambiguity"]
TWO_FILLS  = ["#444444", "#bbbbbb"]
FOUR_FILLS = ["#333333", "#888888", "#bbbbbb", "#dddddd"]


def stacked(ax, title, mapping, order, fills):
    runs = list(mapping.keys())
    x = list(range(len(runs)))
    bottoms = [0] * len(runs)
    bars_per_cat = []
    for cat, fill in zip(order, fills):
        heights = [mapping[r][cat] for r in runs]
        bars = ax.bar(x, heights, bottom=bottoms,
                      color=fill, edgecolor="black", linewidth=0.7,
                      label=cat)
        for i, h in enumerate(heights):
            if h >= 2:
                ax.text(x[i], bottoms[i] + h / 2, str(h),
                        ha="center", va="center", fontsize=9,
                        color="white" if fill in ("#333333", "#444444") else "black")
        bottoms = [b + h for b, h in zip(bottoms, heights)]
        bars_per_cat.append(bars)

    ax.set_xticks(x)
    ax.set_xticklabels(runs, fontsize=10)
    ax.set_ylabel("non-correct fields  (count)")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_ylim(0, max(bottoms) + 4)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", fontsize=8.5, frameon=False, ncol=1)


def main() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.4))

    stacked(axes[0],
            "(a) Two-bucket heuristic\n(\\S\\ref{sec:design-evalframework-diagnosis})",
            two_bucket, TWO_ORDER, TWO_FILLS)
    stacked(axes[1],
            "(b) Four-bucket re-attribution\n(this chapter, \\S 7.7.2)",
            four_bucket, FOUR_ORDER, FOUR_FILLS)

    # The titles use \S\ref labels; matplotlib will render them as plain text
    # which is fine: this figure is also informative outside LaTeX.
    axes[0].set_title("(a) Two-bucket heuristic\n(diagnosis.json)",
                      fontsize=11, fontweight="bold")
    axes[1].set_title("(b) Four-bucket re-attribution\n(Chapter 7, this work)",
                      fontsize=11, fontweight="bold")

    fig.suptitle("Failure attribution: two-bucket vs. four-bucket",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
