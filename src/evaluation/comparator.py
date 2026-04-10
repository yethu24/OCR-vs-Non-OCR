"""Cross-run comparison: load multiple evaluation results and build accuracy
matrices, performance matrices, and slice comparison tables.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..schema import BillExtraction
from ..utils import read_json, write_json
from .metrics import evaluate_run

logger = logging.getLogger(__name__)


def _load_or_evaluate(run_dir: Path, gt_dir: Path) -> dict:
    """Load existing evaluation.json, or compute it on the fly if missing."""
    eval_path = run_dir / "evaluation.json"
    if eval_path.exists():
        return read_json(eval_path)
    logger.info("No evaluation.json in %s — running evaluation", run_dir)
    evaluate_run(run_dir, gt_dir)
    return read_json(eval_path)


def _load_run_performance(run_dir: Path) -> dict:
    """Aggregate timing and cost data across all documents in a run.
    Reads timings.json and metadata.json from each document directory."""
    docs_dir = run_dir / "documents"
    if not docs_dir.exists():
        return {}

    total_ms_list = []
    llm_ms_list = []
    ocr_ms_list = []
    total_cost = 0.0

    for doc_dir in sorted(docs_dir.iterdir()):
        if not doc_dir.is_dir():
            continue

        timings_path = doc_dir / "timings.json"
        if timings_path.exists():
            t = read_json(timings_path)
            total_ms_list.append(t.get("total_ms", 0))
            llm_ms_list.append(t.get("llm_call_ms", 0))
            ocr_ms_list.append(t.get("ocr_ms", 0))

        meta_path = doc_dir / "metadata.json"
        if meta_path.exists():
            m = read_json(meta_path)
            total_cost += m.get("estimated_cost_usd", 0.0)

    def _mean(lst):
        return round(sum(lst) / len(lst), 1) if lst else 0.0

    return {
        "mean_total_ms": _mean(total_ms_list),
        "mean_llm_call_ms": _mean(llm_ms_list),
        "mean_ocr_ms": _mean(ocr_ms_list),
        "total_estimated_cost_usd": round(total_cost, 4),
        "documents_timed": len(total_ms_list),
    }


def _run_label(run_dir: Path) -> str:
    """Derive a human-readable label from the run directory name."""
    return run_dir.name


def compare_runs(
    run_dirs: list[str | Path],
    gt_dir: str | Path,
    output_dir: str | Path = "results/reports",
) -> dict:
    """Compare multiple pipeline runs and write a comparison report.

    Loads or computes evaluation.json for each run, then builds:
      - Accuracy matrix (per-field accuracy across runs)
      - Performance matrix (mean timings + cost)
      - Null analysis (hallucination/omission counts)
      - Slice comparisons (by language, utility_type)

    Writes ``comparison.json`` to *output_dir*.
    """
    run_dirs = [Path(d) for d in run_dirs]
    gt_dir = Path(gt_dir)
    output_dir = Path(output_dir)

    evaluations: dict[str, dict] = {}
    performance: dict[str, dict] = {}

    for rd in run_dirs:
        label = _run_label(rd)
        evaluations[label] = _load_or_evaluate(rd, gt_dir)
        performance[label] = _load_run_performance(rd)

    # --- Accuracy matrix: run_id → {overall + 12 per-field accuracies} ---
    accuracy_matrix: dict[str, dict] = {}
    for label, ev in evaluations.items():
        row = {
            "overall_accuracy": ev.get("overall_accuracy", 0),
            "document_level_accuracy": ev.get("document_level_accuracy", 0),
        }
        for fname in BillExtraction.SCHEMA_FIELDS:
            row[fname] = ev.get("field_accuracies", {}).get(fname, 0)
        accuracy_matrix[label] = row

    # --- Performance matrix ---
    performance_matrix = performance

    # --- Null analysis ---
    null_analysis: dict[str, dict] = {}
    for label, ev in evaluations.items():
        null_analysis[label] = ev.get("null_summary", {})

    # --- Slice comparison ---
    slice_by_language: dict[str, dict] = {}
    slice_by_utility_type: dict[str, dict] = {}
    for label, ev in evaluations.items():
        slice_by_language[label] = ev.get("by_language", {})
        slice_by_utility_type[label] = ev.get("by_utility_type", {})

    report = {
        "runs": [str(rd) for rd in run_dirs],
        "accuracy_matrix": accuracy_matrix,
        "performance_matrix": performance_matrix,
        "null_analysis": null_analysis,
        "slice_by_language": slice_by_language,
        "slice_by_utility_type": slice_by_utility_type,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "comparison.json"
    write_json(out_path, report)
    logger.info("Wrote comparison report to %s", out_path)

    return report
