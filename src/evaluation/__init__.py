"""Evaluation package — metrics, diagnosis, and cross-run comparison."""

from .metrics import (
    FieldResult,
    DocumentResult,
    RunEvaluation,
    compare_field,
    evaluate_document,
    evaluate_run,
)
from .diagnosis import FieldDiagnosis, diagnose_document
from .comparator import compare_runs
