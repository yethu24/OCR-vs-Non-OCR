"""Evaluation metrics: field-level comparison, document-level and run-level
aggregation with null handling and Levenshtein similarity.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from Levenshtein import ratio as levenshtein_ratio

from ..normalisation import normalise_extraction
from ..schema import BillExtraction
from ..utils import read_json, write_json

logger = logging.getLogger(__name__)

# Field type groups — determine which comparison strategy to use
_FLOAT_FIELDS = {"total_amount_due", "consumption_amount"}  # ±0.01 tolerance
_DATE_FIELDS = {"bill_date", "billing_period_start", "billing_period_end", "due_date"}  # exact ISO match


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class FieldResult:
    field_name: str
    predicted: object
    ground_truth: object
    match: bool
    category: str  # "correct", "incorrect", "hallucination", "omission", "both_null"
    similarity: float  # 0.0–1.0


@dataclass
class DocumentResult:
    document_id: str
    fields: list[FieldResult]
    all_correct: bool
    correct: int = 0
    incorrect: int = 0
    hallucination: int = 0
    omission: int = 0
    both_null: int = 0


@dataclass
class RunEvaluation:
    run_id: str
    overall_accuracy: float #what fraction of individual fields were correct across the entire run
    document_level_accuracy: float #what fraction of documents were fully correct
    field_accuracies: dict[str, float] #per-field breakdown, one accuracy score per field
    documents: dict[str, DocumentResult]
    by_language: dict[str, dict]
    by_utility_type: dict[str, dict]
    null_summary: dict[str, int]
    errors_skipped: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Field comparison
# ---------------------------------------------------------------------------


def compare_field(field_name: str, predicted, ground_truth) -> FieldResult:
    """Compare a single field value between prediction and ground truth.

    Returns a FieldResult with match status, category, and similarity score.
    """
    pred_null = predicted is None
    gt_null = ground_truth is None

    # --- Null table (2×2 matrix for None/not-None) ---
    # Determines category before any value comparison happens
    if gt_null and pred_null:
        return FieldResult(
            field_name=field_name,
            predicted=predicted,
            ground_truth=ground_truth,
            match=True,
            category="both_null",
            similarity=1.0,
        )
    # GT is null but LLM returned a value → LLM made something up
    if gt_null and not pred_null:
        return FieldResult(
            field_name=field_name,
            predicted=predicted,
            ground_truth=ground_truth,
            match=False,
            category="hallucination",
            similarity=0.0,
        )
    # GT has a value but LLM returned nothing → LLM missed it
    if not gt_null and pred_null:
        return FieldResult(
            field_name=field_name,
            predicted=predicted,
            ground_truth=ground_truth,
            match=False,
            category="omission",
            similarity=0.0,
        )

    # --- Both have values — compare by field type ---
    if field_name in _FLOAT_FIELDS:
        # Allow ±0.01 tolerance to absorb rounding differences
        try:
            diff = abs(float(predicted) - float(ground_truth))
            is_match = diff <= 0.01
        except (ValueError, TypeError):
            is_match = False
            diff = float("inf")
        similarity = 1.0 if is_match else 0.0
    elif field_name in _DATE_FIELDS:
        # Dates are pre-normalised to ISO strings — exact match only
        is_match = str(predicted) == str(ground_truth)
        similarity = 1.0 if is_match else 0.0
    else:
        # String comparison: exact match + Levenshtein ratio for partial credit
        p_str = str(predicted)
        g_str = str(ground_truth)
        is_match = p_str == g_str
        similarity = levenshtein_ratio(p_str, g_str)

    category = "correct" if is_match else "incorrect"
    return FieldResult(
        field_name=field_name,
        predicted=predicted,
        ground_truth=ground_truth,
        match=is_match,
        category=category,
        similarity=similarity,
    )


# ---------------------------------------------------------------------------
# Document-level evaluation
# ---------------------------------------------------------------------------


def evaluate_document(
    document_id: str, prediction: dict, ground_truth_fields: dict
) -> DocumentResult:
    """Evaluate all 12 fields for one document.

    Both *prediction* and *ground_truth_fields* are normalised before comparison.
    """
    # Normalise both sides identically (e.g. "€" → "EUR") before comparing
    pred_norm = normalise_extraction(prediction)
    gt_norm = normalise_extraction(ground_truth_fields)

    # Compare all 12 schema fields, using SCHEMA_FIELDS as the canonical order
    field_results: list[FieldResult] = []
    for fname in BillExtraction.SCHEMA_FIELDS:
        fr = compare_field(fname, pred_norm.get(fname), gt_norm.get(fname))
        field_results.append(fr)

    # Tally each category so DocumentResult holds pre-computed counts
    counts = {"correct": 0, "incorrect": 0, "hallucination": 0, "omission": 0, "both_null": 0}
    for fr in field_results:
        counts[fr.category] += 1

    # all_correct only if zero errors — both_null fields don't count against it
    all_correct = counts["incorrect"] == 0 and counts["hallucination"] == 0 and counts["omission"] == 0

    return DocumentResult(
        document_id=document_id,
        fields=field_results,
        all_correct=all_correct,
        **counts,
    )


# ---------------------------------------------------------------------------
# Run-level evaluation
# ---------------------------------------------------------------------------


def _compute_accuracy(correct: int, total: int) -> float:
    return round(correct / total, 4) if total > 0 else 0.0  # guard against zero-division


def _aggregate_slice(doc_results: list[DocumentResult]) -> dict:
    """Compute accuracy stats for a slice of documents (e.g. by language or utility type)."""
    total_correct = sum(d.correct for d in doc_results)
    # both_null excluded from denominator — not a success or failure, just absent
    total_evaluated = sum(d.correct + d.incorrect + d.hallucination + d.omission for d in doc_results)
    docs_all_correct = sum(1 for d in doc_results if d.all_correct)
    return {
        "accuracy": _compute_accuracy(total_correct, total_evaluated),
        "document_level_accuracy": _compute_accuracy(docs_all_correct, len(doc_results)),
        "documents": len(doc_results),
    }


def evaluate_run(run_dir: str | Path, gt_dir: str | Path) -> RunEvaluation:
    """Evaluate an entire pipeline run against ground truth.

    Walks ``run_dir/documents/*/extraction.json``, loads matching ground truth
    from ``gt_dir/{document_id}.json``, and aggregates results.

    Writes ``{run_dir}/evaluation.json`` with the full report.
    """
    run_dir = Path(run_dir)
    gt_dir = Path(gt_dir)

    # Derive run_id from directory name
    run_id = run_dir.name

    documents_dir = run_dir / "documents"
    if not documents_dir.exists():
        raise FileNotFoundError(f"No documents directory in {run_dir}")

    doc_results: dict[str, DocumentResult] = {}
    doc_metadata: dict[str, dict] = {}
    errors_skipped: list[str] = []

    for doc_dir in sorted(documents_dir.iterdir()):
        if not doc_dir.is_dir():
            continue
        doc_id = doc_dir.name

        # Skip documents that failed during the pipeline run
        if (doc_dir / "error.json").exists():
            logger.warning("Skipping %s (has error.json)", doc_id)
            errors_skipped.append(doc_id)
            continue

        extraction_path = doc_dir / "extraction.json"
        if not extraction_path.exists():
            logger.warning("Skipping %s (no extraction.json)", doc_id)
            errors_skipped.append(doc_id)
            continue

        gt_path = gt_dir / f"{doc_id}.json"
        if not gt_path.exists():
            logger.warning("Skipping %s (no ground truth file)", doc_id)
            errors_skipped.append(doc_id)
            continue

        prediction = read_json(extraction_path)
        gt_data = read_json(gt_path)
        gt_fields = gt_data.get("fields", gt_data)  # support {fields: {...}} or flat dict

        dr = evaluate_document(doc_id, prediction, gt_fields)
        doc_results[doc_id] = dr

        # Load metadata for language/utility_type slicing later
        meta_path = doc_dir / "metadata.json"
        if meta_path.exists():
            doc_metadata[doc_id] = read_json(meta_path)

    if not doc_results:
        logger.warning("No documents evaluated in %s", run_dir)

    # --- Field-level accuracy ---
    # For each field, accuracy = correct / evaluated (both_null excluded from
    # the denominator since they are neither a success nor a failure)
    field_accuracies: dict[str, float] = {}
    for fname in BillExtraction.SCHEMA_FIELDS:
        correct = 0
        evaluated = 0
        for dr in doc_results.values():
            fr = next(f for f in dr.fields if f.field_name == fname)
            if fr.category != "both_null":  # don't penalise or reward absent fields
                evaluated += 1
                if fr.match:
                    correct += 1
        field_accuracies[fname] = _compute_accuracy(correct, evaluated)

    # --- Document-level accuracy: fraction of documents with all 12 fields correct ---
    all_docs = list(doc_results.values())
    docs_all_correct = sum(1 for d in all_docs if d.all_correct)
    document_level_accuracy = _compute_accuracy(docs_all_correct, len(all_docs))

    # --- Overall accuracy: fraction of individual fields correct across all documents ---
    total_correct = sum(d.correct for d in all_docs)
    total_evaluated = sum(d.correct + d.incorrect + d.hallucination + d.omission for d in all_docs)
    overall_accuracy = _compute_accuracy(total_correct, total_evaluated)

    # --- Null summary: count failure types across the whole run ---
    null_summary = {
        "hallucinations": sum(d.hallucination for d in all_docs),
        "omissions": sum(d.omission for d in all_docs),
        "both_null": sum(d.both_null for d in all_docs),
    }

    # --- Slicing: group documents by language and utility type ---
    # Enables charts like "accuracy by language" in the report
    by_language: dict[str, dict] = {}
    by_utility_type: dict[str, dict] = {}

    for doc_id, dr in doc_results.items():
        meta = doc_metadata.get(doc_id, {})
        lang = meta.get("language", "unknown")
        utype = meta.get("utility_type", "unknown")

        by_language.setdefault(lang, []).append(dr)
        by_utility_type.setdefault(utype, []).append(dr)

    # Aggregate each slice from list[DocumentResult] → summary dict
    by_language = {k: _aggregate_slice(v) for k, v in by_language.items()}
    by_utility_type = {k: _aggregate_slice(v) for k, v in by_utility_type.items()}

    evaluation = RunEvaluation(
        run_id=run_id,
        overall_accuracy=overall_accuracy,
        document_level_accuracy=document_level_accuracy,
        field_accuracies=field_accuracies,
        documents=doc_results,
        by_language=by_language,
        by_utility_type=by_utility_type,
        null_summary=null_summary,
        errors_skipped=errors_skipped,
    )

    # --- Write evaluation.json ---
    eval_data = {
        "run_id": run_id,
        "overall_accuracy": overall_accuracy,
        "document_level_accuracy": document_level_accuracy,
        "field_accuracies": field_accuracies,
        "by_language": by_language,
        "by_utility_type": by_utility_type,
        "documents": {},
        "null_summary": null_summary,
        "errors_skipped": errors_skipped,
    }
    for doc_id, dr in doc_results.items():
        eval_data["documents"][doc_id] = {
            "all_correct": dr.all_correct,
            "fields": [
                {
                    "field_name": fr.field_name,
                    "predicted": fr.predicted,
                    "ground_truth": fr.ground_truth,
                    "match": fr.match,
                    "category": fr.category,
                    "similarity": round(fr.similarity, 4),
                }
                for fr in dr.fields
            ],
        }

    write_json(run_dir / "evaluation.json", eval_data)
    logger.info("Wrote %s", run_dir / "evaluation.json")

    return evaluation
