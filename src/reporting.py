"""Session 6: report generation — charts (PNG) and text summary."""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend; avoids Tk errors on Windows
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .schema import BillExtraction
from .utils import read_json

logger = logging.getLogger(__name__)

# Maps run-ID suffixes to short human-readable labels for chart axes
_LABELS = {
    "openai_gpt4o_ocr_text":                    "GPT-4o OCR",
    "openai_gpt4o_vision":                       "GPT-4o Vision",
    "anthropic_claudesonnet4520250929_ocr_text": "Sonnet 4.5 OCR",
    "anthropic_claudesonnet4520250929_vision":   "Sonnet 4.5 Vision",
}


def _label(run_id: str) -> str:
    """Map a run ID to a short readable label."""
    for suffix, name in _LABELS.items():
        if run_id.endswith(suffix):
            return name
    return run_id[-30:]  # fallback


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", path)


def generate_report(comparison_path: Path, output_dir: Path) -> Path:
    """Read comparison.json, produce 6 charts + summary.txt."""
    data = read_json(comparison_path)
    fig_dir = output_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid")

    # --- Build DataFrames once, reuse across all 6 charts ---

    # accuracy_df: transpose so rows = conditions, columns = fields.
    # JSON has {run_id: {field: score}}, pd.DataFrame makes run_ids columns,
    # .T flips to run_ids as rows.  × 100 converts fractions to %.
    accuracy_df = pd.DataFrame(data["accuracy_matrix"]).T * 100
    accuracy_df.index = [_label(r) for r in accuracy_df.index]  # short readable labels

    # perf_df: same transpose trick for timing/cost data
    perf_df = pd.DataFrame(data["performance_matrix"]).T
    perf_df.index = accuracy_df.index
    # Convert ms → seconds for the stacked bar chart
    perf_df["ocr_s"] = perf_df["mean_ocr_ms"] / 1000
    perf_df["llm_s"] = perf_df["mean_llm_call_ms"] / 1000

    # --- Chart 1: Overall accuracy bar (one bar per condition) ---
    ax = accuracy_df["overall_accuracy"].plot(
        kind="bar", figsize=(8, 5), color=sns.color_palette("muted", 4), rot=15
    )
    ax.set_ylabel("Overall Accuracy (%)")
    ax.set_title("Overall Extraction Accuracy by Condition")
    ax.set_ylim(0, 105)
    # Add value labels above each bar
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{bar.get_height():.1f}%", ha="center", va="bottom", fontsize=9)
    _save(ax.get_figure(), fig_dir / "overall_accuracy.png")

    # --- Chart 2: Field accuracy heatmap (fields × conditions) ---
    fields = BillExtraction.SCHEMA_FIELDS
    field_df = accuracy_df[fields]  # drop overall_accuracy, keep 12 fields
    fig, ax = plt.subplots(figsize=(8, 7))
    # Transpose so fields are rows and conditions are columns
    sns.heatmap(field_df.T, annot=True, fmt=".0f", cmap="YlGn",
                vmin=0, vmax=100, linewidths=0.5, ax=ax)
    ax.set_title("Field-Level Accuracy (%) by Condition")
    _save(fig, fig_dir / "field_accuracy_heatmap.png")

    # --- Chart 3: Timing stacked bar (OCR time + LLM time per condition) ---
    # Vision conditions have ocr_s=0 since Tesseract is skipped
    ax = perf_df[["ocr_s", "llm_s"]].plot(
        kind="bar", stacked=True, figsize=(8, 5),
        color=sns.color_palette("muted", 2), rot=15,
        label=["OCR", "LLM Call"]
    )
    ax.set_ylabel("Mean Time per Document (s)")
    ax.set_title("Processing Time Breakdown")
    ax.legend(["OCR", "LLM Call"])
    _save(ax.get_figure(), fig_dir / "timing_breakdown.png")

    # --- Chart 4: Cost bar ---
    # Use documents_timed (from comparator) to label chart correctly.
    doc_counts = sorted({int(x) for x in perf_df.get("documents_timed", []) if pd.notna(x)})
    if not doc_counts:
        doc_label = ""
    elif len(doc_counts) == 1:
        doc_label = f" ({doc_counts[0]} documents)"
    else:
        doc_label = f" ({doc_counts[0]}–{doc_counts[-1]} documents)"

    ax = perf_df["total_estimated_cost_usd"].plot(
        kind="bar", figsize=(8, 5), color=sns.color_palette("muted", 4), rot=15
    )
    ax.set_ylabel("Total Cost (USD)")
    ax.set_title(f"API Cost Comparison{doc_label}")
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                f"${bar.get_height():.4f}", ha="center", va="bottom", fontsize=9)
    _save(ax.get_figure(), fig_dir / "cost_comparison.png")

    # --- Chart 5: Accuracy by language (grouped bar) ---
    # Flatten nested JSON {run_id: {lang: {accuracy: ...}}} into a flat list,
    # then pivot into a DataFrame with conditions as rows, languages as columns
    lang_rows = [
        {"condition": _label(r), "language": lang.upper(),
         "accuracy": vals["accuracy"] * 100}
        for r, langs in data["slice_by_language"].items()
        for lang, vals in langs.items()
    ]
    lang_df = pd.DataFrame(lang_rows).pivot(
        index="condition", columns="language", values="accuracy"
    )
    ax = lang_df.plot(kind="bar", figsize=(8, 5),
                      color=sns.color_palette("muted", len(lang_df.columns)), rot=15)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Accuracy by Language")
    ax.set_ylim(0, 105)
    _save(ax.get_figure(), fig_dir / "accuracy_by_language.png")

    # --- Chart 6: Accuracy by utility type (grouped bar, same pattern as Chart 5) ---
    ut_rows = [
        {"condition": _label(r), "utility_type": ut.title(),
         "accuracy": vals["accuracy"] * 100}
        for r, uts in data["slice_by_utility_type"].items()
        for ut, vals in uts.items()
    ]
    ut_df = pd.DataFrame(ut_rows).pivot(
        index="condition", columns="utility_type", values="accuracy"
    )
    ax = ut_df.plot(kind="bar", figsize=(8, 5),
                    color=sns.color_palette("muted", len(ut_df.columns)), rot=15)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Accuracy by Utility Type")
    ax.set_ylim(0, 105)
    _save(ax.get_figure(), fig_dir / "accuracy_by_utility_type.png")

    # --- Text summary: human-readable report written to summary.txt ---
    run_ids = list(data["accuracy_matrix"].keys())
    labels = list(accuracy_df.index)
    null = data["null_analysis"]

    lines = ["=" * 72, "EXTRACTION PIPELINE — COMPARISON SUMMARY", "=" * 72, ""]
    lines += ["RESULTS OVERVIEW", "-" * 72,
              f"{'Condition':<22} {'Accuracy':>9} {'Doc-Lvl':>8} {'LLM (s)':>8} {'Cost ($)':>9}",
              "-" * 72]
    for rid, label in zip(run_ids, labels):
        lines.append(
            f"{label:<22} {accuracy_df.loc[label, 'overall_accuracy']:>8.1f}%"
            f" {accuracy_df.loc[label, 'document_level_accuracy']:>7.1f}%"
            f" {perf_df.loc[label, 'llm_s']:>7.1f}s"
            f" ${perf_df.loc[label, 'total_estimated_cost_usd']:>8.4f}"
        )
    lines.append("")

    best = accuracy_df["overall_accuracy"].idxmax()
    worst = accuracy_df["overall_accuracy"].idxmin()
    lines += [f"Best overall accuracy:  {best} ({accuracy_df.loc[best, 'overall_accuracy']:.1f}%)",
              f"Worst overall accuracy: {worst} ({accuracy_df.loc[worst, 'overall_accuracy']:.1f}%)"]

    field_means = field_df.mean()
    lines += [f"Easiest field: {field_means.idxmax()} ({field_means.max():.1f}%)",
              f"Hardest field: {field_means.idxmin()} ({field_means.min():.1f}%)", ""]

    lines += ["NULL ANALYSIS", "-" * 72]
    for rid, label in zip(run_ids, labels):
        n = null[rid]
        lines.append(f"{label:<22}  hallucinations={n['hallucinations']}"
                     f"  omissions={n['omissions']}  both_null={n['both_null']}")
    lines.append("")

    lines += ["ACCURACY BY LANGUAGE", "-" * 72]
    lines.append(lang_df.to_string(float_format=lambda x: f"{x:.1f}%"))
    lines.append("")

    lines += ["ACCURACY BY UTILITY TYPE", "-" * 72]
    lines.append(ut_df.to_string(float_format=lambda x: f"{x:.1f}%"))
    lines.append("")

    lines += ["FIELD-LEVEL ACCURACY (%)", "-" * 72]
    lines.append(field_df.T.to_string(float_format=lambda x: f"{x:.1f}%"))
    lines.append("")
    lines.append("=" * 72)

    summary_path = output_dir / "summary.txt"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Saved %s", summary_path)

    return output_dir
