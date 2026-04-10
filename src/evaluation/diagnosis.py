"""Failure diagnosis: attribute incorrect fields to OCR failure, LLM extraction
failure, or vision model failure.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from ..utils import write_json

logger = logging.getLogger(__name__)


@dataclass
class FieldDiagnosis:
    field_name: str
    ground_truth: object
    predicted: object
    failure_type: str  # "ocr_failure", "llm_extraction_failure", "vision_model_failure"


def _value_in_text(value, text: str) -> bool:
    """Check if a ground-truth value appears in OCR text (case-insensitive).
    If the GT value is present in the OCR output, Tesseract did its job
    and the error must be in the LLM's extraction."""
    if value is None:
        return False
    needle = str(value).strip().lower()
    if not needle:
        return False
    return needle in text.lower()


def diagnose_document(
    doc_id: str,
    doc_eval,  # DocumentResult from metrics
    doc_dir: str | Path,
    pipeline_mode: str,
) -> list[FieldDiagnosis]:
    """Diagnose each incorrect field in a document evaluation.

    For OCR-text mode:
      - GT value found in ocr_text.txt -> LLM extraction failure
      - GT value not found -> OCR failure

    For vision mode:
      - Any failure -> vision model failure

    Writes ``diagnosis.json`` into *doc_dir*.
    """
    doc_dir = Path(doc_dir)
    diagnoses: list[FieldDiagnosis] = []

    # Only diagnose fields that were wrong (skip correct and both_null)
    incorrect_fields = [fr for fr in doc_eval.fields if fr.category in ("incorrect", "hallucination", "omission")]
    if not incorrect_fields:
        return diagnoses

    if pipeline_mode == "ocr_text":
        # Load the OCR output to check whether Tesseract captured the value
        ocr_path = doc_dir / "ocr_text.txt"
        ocr_text = ocr_path.read_text(encoding="utf-8") if ocr_path.exists() else ""

        for fr in incorrect_fields:
            # If GT is in the OCR text → Tesseract saw it, so the LLM missed it
            # If GT is NOT in the OCR text → Tesseract failed to capture it
            if fr.ground_truth is None or _value_in_text(fr.ground_truth, ocr_text):
                failure_type = "llm_extraction_failure"
            else:
                failure_type = "ocr_failure"

            diagnoses.append(FieldDiagnosis(
                field_name=fr.field_name,
                ground_truth=fr.ground_truth,
                predicted=fr.predicted,
                failure_type=failure_type,
            ))
    else:
        # Vision mode — any failure is attributed to the vision model
        for fr in incorrect_fields:
            diagnoses.append(FieldDiagnosis(
                field_name=fr.field_name,
                ground_truth=fr.ground_truth,
                predicted=fr.predicted,
                failure_type="vision_model_failure",
            ))

    # Write diagnosis.json
    diag_data = [
        {
            "field_name": d.field_name,
            "ground_truth": d.ground_truth,
            "predicted": d.predicted,
            "failure_type": d.failure_type,
        }
        for d in diagnoses
    ]
    write_json(doc_dir / "diagnosis.json", diag_data)
    logger.info("Wrote diagnosis for %s (%d failures)", doc_id, len(diagnoses))

    return diagnoses
