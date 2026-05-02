"""Generate fig-7-11-modality-flip-counts.png.

Per-provider, per-field counts of within-document modality flips:
fields where one modality is correct and the other is wrong on the
same document. The figure visualises that the overall modality gap
is composed of per-field offsets that point in opposite directions,
which the per-field accuracy heatmap (fig-7-2) cannot show because
it averages over documents.

Reads results/reports/four_way_20260429/derived/flip_summary.csv,
which the chapter's analysis script writes from the four
evaluation.json files. Fields are ordered by total flip volume per
provider so the largest disagreements sit at the top.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "fig-7-11-modality-flip-counts.png"
FLIP_CSV = Path(
    "C:/Users/winye/OCR vs Non-OCR/results/reports/four_way_20260429/"
    "derived/flip_summary.csv"
)


def read_flips() -> dict:
    """Return {provider: {field: (ocr_only, vision_only)}}."""
    out: dict = defaultdict(dict)
    with FLIP_CSV.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            ocr_only = int(row["ocr_only_correct"])
            vision_only = int(row["vision_only_correct"])
            if ocr_only == 0 and vision_only == 0:
                continue
            out[row["provider"]][row["field"]] = (ocr_only, vision_only)
    return out


PROVIDER_LABEL = {
    "sonnet": "Sonnet 4.5",
    "gpt4o":  "GPT-4o",
}


def panel(ax, provider_key: str, fields: dict) -> None:
    items = sorted(
        fields.items(),
        key=lambda kv: kv[1][0] + kv[1][1],
        reverse=False,
    )
    field_names = [k for k, _ in items]
    ocr_vals = [-v[0] for _, v in items]
    vis_vals = [v[1] for _, v in items]

    y = list(range(len(items)))
    ax.barh(y, ocr_vals, color="#444444", edgecolor="black", linewidth=0.6,
            label="OCR-only correct")
    ax.barh(y, vis_vals, color="#bbbbbb", edgecolor="black", linewidth=0.6,
            label="Vision-only correct")

    for i, (o, v) in enumerate(zip(ocr_vals, vis_vals)):
        if o != 0:
            ax.text(o - 0.2, i, str(-o), ha="right", va="center",
                    fontsize=8, color="white")
        if v != 0:
            ax.text(v + 0.2, i, str(v), ha="left", va="center",
                    fontsize=8)

    ax.set_yticks(y)
    ax.set_yticklabels(field_names, fontsize=9)
    ax.axvline(0, color="black", linewidth=0.8)
    span = max(max(abs(o) for o in ocr_vals), max(v for v in vis_vals)) + 2
    ax.set_xlim(-span, span)
    ax.set_xlabel("count of documents (left: OCR-only;  right: Vision-only)",
                  fontsize=9)
    ax.set_title(PROVIDER_LABEL[provider_key], fontsize=11, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, axis="x", linestyle=":", linewidth=0.5, alpha=0.7)


def main() -> None:
    flips = read_flips()
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.6), sharey=False)
    panel(axes[0], "sonnet", flips["sonnet"])
    panel(axes[1], "gpt4o",  flips["gpt4o"])
    axes[0].legend(loc="lower right", fontsize=9, frameon=False)
    fig.suptitle(
        "Within-document modality flips, per provider and field",
        fontsize=13, fontweight="bold", y=1.02,
    )
    fig.tight_layout()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
