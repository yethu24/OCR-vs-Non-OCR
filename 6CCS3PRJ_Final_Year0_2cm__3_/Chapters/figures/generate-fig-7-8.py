"""Generate fig-7-8-page-cap-coverage.png.

Per-document horizontal bar of pages-seen-by-both-pipelines
(always min(2, n)) versus pages-total. Both the OCR and the vision
pipeline are bounded to the first two pages of every document; the
cap is a deliberate baseline reflecting the fact that every required
field appears within the first two pages of every bill in this
corpus. Documents are ordered by page count so the not-seen tail is
visually obvious.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "fig-7-8-page-cap-coverage.png"
MANIFEST = Path("C:/Users/winye/OCR vs Non-OCR/data/dataset_manifest.csv")
VISION_CAP = 2


def read_manifest() -> list[dict]:
    with MANIFEST.open(newline="", encoding="utf-8-sig") as fh:
        return [row for row in csv.DictReader(fh) if row["status"] == "active"]


def main() -> None:
    rows = read_manifest()
    rows.sort(key=lambda r: (int(r["page_count"]), r["document_id"]))

    labels = [r["document_id"] for r in rows]
    pages = [int(r["page_count"]) for r in rows]
    seen = [min(VISION_CAP, p) for p in pages]
    truncated = [p - s for p, s in zip(pages, seen)]

    fig, ax = plt.subplots(figsize=(10.0, 11.0))
    y = list(range(len(rows)))
    ax.barh(y, seen, color="#444444", edgecolor="black", linewidth=0.5,
            label="seen by both pipelines (cap = 2)")
    ax.barh(y, truncated, left=seen, color="#cccccc", edgecolor="black",
            linewidth=0.5, label="not seen")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("pages")
    ax.set_xlim(0, max(pages) + 0.5)
    ax.invert_yaxis()
    ax.axvline(VISION_CAP + 0.0, color="black", linestyle="--", linewidth=1.0)
    ax.legend(loc="lower right", fontsize=9, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)

    n_full = sum(1 for p in pages if p <= VISION_CAP)
    n_trunc = len(pages) - n_full
    ax.set_title(
        f"Two-page cap, applied to both pipelines"
        f"  (full: {n_full}/{len(pages)};"
        f" truncated: {n_trunc}/{len(pages)})",
        fontsize=11, fontweight="bold",
    )

    fig.tight_layout()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
