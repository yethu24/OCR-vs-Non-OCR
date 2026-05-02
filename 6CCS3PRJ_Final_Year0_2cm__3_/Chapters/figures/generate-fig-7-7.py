"""Generate fig-7-7-dataset-composition.png.

Three-panel composition of the 40-document corpus:
  (a) language counts (en, de, it, fr)
  (b) utility-type counts (electricity, gas, water)
  (c) page-count distribution with the page-2 vision cap marked

Reads the manifest CSV directly so the figure is reproducible from
a checkout.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "fig-7-7-dataset-composition.png"
MANIFEST = Path("C:/Users/winye/OCR vs Non-OCR/data/dataset_manifest.csv")


def read_manifest() -> list[dict]:
    with MANIFEST.open(newline="", encoding="utf-8-sig") as fh:
        return [row for row in csv.DictReader(fh) if row["status"] == "active"]


def main() -> None:
    rows = read_manifest()

    by_lang = Counter(r["language"] for r in rows)
    by_util = Counter(r["utility_type"] for r in rows)
    pages = [int(r["page_count"]) for r in rows]
    page_buckets = Counter(pages)

    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.0))

    ax = axes[0]
    order = ["en", "de", "it", "fr"]
    counts = [by_lang.get(k, 0) for k in order]
    bars = ax.bar(order, counts, color="#666666", edgecolor="black", linewidth=0.8)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, c + 0.4, str(c),
                ha="center", va="bottom", fontsize=10)
    ax.set_title("(a) Language", fontsize=12, fontweight="bold")
    ax.set_ylabel("documents")
    ax.set_ylim(0, max(counts) + 3)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    order = ["electricity", "gas", "water"]
    counts = [by_util.get(k, 0) for k in order]
    bars = ax.bar(order, counts, color="#666666", edgecolor="black", linewidth=0.8)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, c + 0.4, str(c),
                ha="center", va="bottom", fontsize=10)
    ax.set_title("(b) Utility type", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(counts) + 3)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[2]
    page_keys = sorted(page_buckets.keys())
    counts = [page_buckets[k] for k in page_keys]
    bars = ax.bar(page_keys, counts,
                  color=["#666666" if k <= 2 else "#bbbbbb" for k in page_keys],
                  edgecolor="black", linewidth=0.8)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, c + 0.2, str(c),
                ha="center", va="bottom", fontsize=10)
    ax.axvline(2.5, color="black", linestyle="--", linewidth=1.2)
    ax.text(2.55, max(counts) - 0.5, "vision cap",
            ha="left", va="top", fontsize=9, style="italic")
    n_seen = sum(c for k, c in zip(page_keys, counts) if k <= 2)
    n_truncated = sum(c for k, c in zip(page_keys, counts) if k > 2)
    ax.set_title(
        f"(c) Page count   (vision sees full: {n_seen}; truncated: {n_truncated})",
        fontsize=12, fontweight="bold",
    )
    ax.set_xlabel("pages")
    ax.set_ylabel("documents")
    ax.set_xticks(page_keys)
    ax.set_ylim(0, max(counts) + 1.5)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
