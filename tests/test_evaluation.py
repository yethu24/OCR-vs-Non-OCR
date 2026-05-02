"""TDD-style specification for src/evaluation/ — metrics, diagnosis, comparator.

Each test class specifies one behavioural contract.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.metrics import (
    FieldResult,
    DocumentResult,
    RunEvaluation,
    compare_field,
    evaluate_document,
    evaluate_run,
    _compute_accuracy,
)
from src.evaluation.diagnosis import (
    FieldDiagnosis,
    diagnose_document,
    _value_in_text,
)
from src.evaluation.comparator import compare_runs


# =========================================================================
# Spec: compare_field — null table
# =========================================================================


class TestCompareFieldBothNullShouldMatch:
    """Given both predicted and ground truth are None, should be 'both_null'
    with match=True and similarity=1.0."""

    def test_both_null(self):
        r = compare_field("bill_number", None, None)
        assert r.match is True
        assert r.category == "both_null"
        assert r.similarity == 1.0

    def test_both_null_any_field(self):
        for f in ("provider_name", "currency", "total_amount_due", "bill_date"):
            r = compare_field(f, None, None)
            assert r.category == "both_null"


class TestCompareFieldHallucinationShouldNotMatch:
    """Given predicted has a value but ground truth is None, should be 'hallucination'."""

    def test_string_hallucination(self):
        r = compare_field("bill_number", "INV-001", None)
        assert r.match is False
        assert r.category == "hallucination"
        assert r.similarity == 0.0

    def test_float_hallucination(self):
        r = compare_field("total_amount_due", 42.0, None)
        assert r.match is False
        assert r.category == "hallucination"


class TestCompareFieldOmissionShouldNotMatch:
    """Given predicted is None but ground truth has a value, should be 'omission'."""

    def test_string_omission(self):
        r = compare_field("bill_number", None, "INV-001")
        assert r.match is False
        assert r.category == "omission"
        assert r.similarity == 0.0

    def test_float_omission(self):
        r = compare_field("total_amount_due", None, 100.0)
        assert r.match is False
        assert r.category == "omission"


# =========================================================================
# Spec: compare_field — float fields
# =========================================================================


class TestCompareFieldFloatShouldUse001Tolerance:
    """Float fields (total_amount_due, consumption_amount) should match
    within 0.01 absolute tolerance."""

    def test_exact_match(self):
        r = compare_field("total_amount_due", 42.50, 42.50)
        assert r.match is True
        assert r.category == "correct"

    def test_within_tolerance(self):
        r = compare_field("total_amount_due", 42.505, 42.50)
        assert r.match is True

    def test_at_boundary(self):
        r = compare_field("total_amount_due", 42.51, 42.50)
        assert r.match is True  # diff = 0.01, exactly at boundary

    def test_outside_tolerance(self):
        r = compare_field("total_amount_due", 42.52, 42.50)
        assert r.match is False
        assert r.category == "incorrect"

    def test_consumption_amount_within_tolerance(self):
        r = compare_field("consumption_amount", 572.50, 572.502)
        assert r.match is True

    def test_consumption_amount_outside_tolerance(self):
        r = compare_field("consumption_amount", 572.50, 572.52)
        assert r.match is False

    def test_float_similarity_is_binary(self):
        """Float similarity should be 1.0 for match, 0.0 for mismatch."""
        r_match = compare_field("total_amount_due", 100.0, 100.0)
        assert r_match.similarity == 1.0
        r_miss = compare_field("total_amount_due", 100.0, 200.0)
        assert r_miss.similarity == 0.0


# =========================================================================
# Spec: compare_field — date fields
# =========================================================================


class TestCompareFieldDateShouldExactMatch:
    """Date fields should use exact string comparison."""

    def test_exact_match(self):
        r = compare_field("bill_date", "2024-01-15", "2024-01-15")
        assert r.match is True
        assert r.category == "correct"

    def test_mismatch(self):
        r = compare_field("bill_date", "2024-01-16", "2024-01-15")
        assert r.match is False
        assert r.category == "incorrect"

    def test_all_date_fields(self):
        for f in ("bill_date", "billing_period_start", "billing_period_end", "due_date"):
            r = compare_field(f, "2024-01-01", "2024-01-01")
            assert r.match is True

    def test_date_similarity_is_binary(self):
        r = compare_field("bill_date", "2024-01-01", "2024-01-02")
        assert r.similarity == 0.0


# =========================================================================
# Spec: compare_field — string fields
# =========================================================================


class TestCompareFieldStringShouldExactMatchWithLevenshtein:
    """String fields should use exact match for match/category, and
    Levenshtein ratio for similarity."""

    def test_exact_match(self):
        r = compare_field("provider_name", "ovo energy", "ovo energy")
        assert r.match is True
        assert r.similarity == 1.0

    def test_mismatch_with_high_similarity(self):
        r = compare_field("provider_name", "ovo energy", "ovo energ")
        assert r.match is False
        assert r.category == "incorrect"
        assert 0.5 < r.similarity < 1.0

    def test_completely_different(self):
        r = compare_field("provider_name", "abc", "xyz")
        assert r.match is False
        assert r.similarity < 0.5

    def test_currency_exact_match(self):
        r = compare_field("currency", "GBP", "GBP")
        assert r.match is True

    def test_currency_mismatch(self):
        r = compare_field("currency", "EUR", "GBP")
        assert r.match is False


# =========================================================================
# Spec: compare_field — FieldResult dataclass
# =========================================================================


class TestFieldResultShouldContainAllInfo:
    def test_has_all_attributes(self):
        r = compare_field("provider_name", "test", "test")
        assert hasattr(r, "field_name")
        assert hasattr(r, "predicted")
        assert hasattr(r, "ground_truth")
        assert hasattr(r, "match")
        assert hasattr(r, "category")
        assert hasattr(r, "similarity")

    def test_stores_values(self):
        r = compare_field("bill_number", "A", "B")
        assert r.field_name == "bill_number"
        assert r.predicted == "A"
        assert r.ground_truth == "B"


# =========================================================================
# Spec: evaluate_document
# =========================================================================


class TestEvaluateDocumentShouldEvaluateAll12Fields:
    """evaluate_document should compare all 12 schema fields and return
    a DocumentResult with counts and per-field results."""

    def test_perfect_document(self):
        fields = {
            "provider_name": "OVO Energy",
            "utility_type": "electricity",
            "bill_number": None,
            "bill_date": "2024-01-15",
            "billing_period_start": "2023-12-01",
            "billing_period_end": "2024-01-01",
            "due_date": None,
            "total_amount_due": 177.53,
            "currency": "GBP",
            "account_number": "26447122",
            "consumption_amount": 572.50,
            "consumption_unit": "kWh",
        }
        dr = evaluate_document("doc_001", dict(fields), dict(fields))
        assert dr.all_correct is True
        assert dr.incorrect == 0
        assert dr.hallucination == 0
        assert dr.omission == 0
        assert len(dr.fields) == 12

    def test_one_incorrect(self):
        pred = {"provider_name": "Wrong", "utility_type": "electricity"}
        gt = {"provider_name": "Correct", "utility_type": "electricity"}
        dr = evaluate_document("doc", pred, gt)
        assert dr.all_correct is False
        assert dr.incorrect >= 1

    def test_hallucination_prevents_all_correct(self):
        pred = {"bill_number": "INV-999"}
        gt = {"bill_number": None}
        dr = evaluate_document("doc", pred, gt)
        assert dr.all_correct is False
        assert dr.hallucination >= 1

    def test_omission_prevents_all_correct(self):
        pred = {"bill_number": None}
        gt = {"bill_number": "INV-999"}
        dr = evaluate_document("doc", pred, gt)
        assert dr.all_correct is False
        assert dr.omission >= 1


class TestEvaluateDocumentShouldNormaliseBothSides:
    """Both prediction and ground truth should be normalised before comparison."""

    def test_whitespace_normalised(self):
        pred = {"provider_name": "  OVO Energy Ltd  "}
        gt = {"provider_name": "ovo energy"}
        dr = evaluate_document("doc", pred, gt)
        fr = next(f for f in dr.fields if f.field_name == "provider_name")
        assert fr.match is True

    def test_currency_normalised(self):
        pred = {"currency": "gbp"}
        gt = {"currency": "GBP"}
        dr = evaluate_document("doc", pred, gt)
        fr = next(f for f in dr.fields if f.field_name == "currency")
        assert fr.match is True

    def test_date_format_normalised(self):
        pred = {"bill_date": "15/01/2024"}
        gt = {"bill_date": "2024-01-15"}
        dr = evaluate_document("doc", pred, gt)
        fr = next(f for f in dr.fields if f.field_name == "bill_date")
        assert fr.match is True


class TestEvaluateDocumentBothNullShouldNotPreventAllCorrect:
    """both_null fields should not prevent all_correct from being True."""

    def test_all_null_is_all_correct(self):
        dr = evaluate_document("doc", {}, {})
        assert dr.all_correct is True
        assert dr.both_null == 12


# =========================================================================
# Spec: _compute_accuracy
# =========================================================================


class TestComputeAccuracy:
    def test_perfect(self):
        assert _compute_accuracy(10, 10) == 1.0

    def test_half(self):
        assert _compute_accuracy(5, 10) == 0.5

    def test_zero_total(self):
        assert _compute_accuracy(0, 0) == 0.0

    def test_rounded_to_4_places(self):
        result = _compute_accuracy(1, 3)
        assert result == round(1 / 3, 4)


# =========================================================================
# Spec: evaluate_run
# =========================================================================


def _create_mock_run(tmp_path, docs: dict[str, dict], gt_fields: dict[str, dict],
                     metadata: dict[str, dict] | None = None):
    """Helper: create run_dir and gt_dir with extraction/metadata/timings files."""
    run_dir = tmp_path / "run"
    gt_dir = tmp_path / "gt"
    gt_dir.mkdir(parents=True)

    for doc_id, extraction in docs.items():
        doc_dir = run_dir / "documents" / doc_id
        doc_dir.mkdir(parents=True)
        (doc_dir / "extraction.json").write_text(json.dumps(extraction))
        meta = (metadata or {}).get(doc_id, {
            "language": "en", "utility_type": "electricity", "pipeline_mode": "ocr_text"
        })
        (doc_dir / "metadata.json").write_text(json.dumps(meta))
        (doc_dir / "timings.json").write_text(
            json.dumps({"total_ms": 5000, "llm_call_ms": 3000, "ocr_ms": 1000})
        )

    for doc_id, fields in gt_fields.items():
        (gt_dir / f"{doc_id}.json").write_text(
            json.dumps({"document_id": doc_id, "fields": fields})
        )

    return run_dir, gt_dir


class TestEvaluateRunShouldProduceRunEvaluation:
    """Given a run directory with extraction results and a ground truth directory,
    evaluate_run should produce a RunEvaluation and write evaluation.json."""

    def test_writes_evaluation_json(self, tmp_path):
        ext = {"provider_name": "Test", "total_amount_due": 100.0}
        run_dir, gt_dir = _create_mock_run(tmp_path, {"d1": ext}, {"d1": ext})
        evaluate_run(run_dir, gt_dir)
        assert (run_dir / "evaluation.json").exists()

    def test_overall_accuracy_between_0_and_1(self, tmp_path):
        ext = {"provider_name": "Test"}
        run_dir, gt_dir = _create_mock_run(tmp_path, {"d1": ext}, {"d1": ext})
        ev = evaluate_run(run_dir, gt_dir)
        assert 0.0 <= ev.overall_accuracy <= 1.0

    def test_perfect_run(self, tmp_path):
        ext = {"provider_name": "Test", "total_amount_due": 100.0, "currency": "GBP"}
        run_dir, gt_dir = _create_mock_run(tmp_path, {"d1": ext}, {"d1": ext})
        ev = evaluate_run(run_dir, gt_dir)
        assert ev.document_level_accuracy == 1.0

    def test_document_level_accuracy(self, tmp_path):
        ext = {"provider_name": "Test", "total_amount_due": 100.0}
        ext_wrong = {"provider_name": "Wrong", "total_amount_due": 999.0}
        run_dir, gt_dir = _create_mock_run(
            tmp_path,
            {"d1": ext, "d2": ext_wrong},
            {"d1": ext, "d2": ext},
            metadata={
                "d1": {"language": "en", "utility_type": "electricity", "pipeline_mode": "ocr_text"},
                "d2": {"language": "de", "utility_type": "gas", "pipeline_mode": "ocr_text"},
            },
        )
        ev = evaluate_run(run_dir, gt_dir)
        assert ev.document_level_accuracy == 0.5


class TestEvaluateRunShouldSliceByLanguageAndUtilityType:
    def test_slices_by_language(self, tmp_path):
        ext = {"provider_name": "Test"}
        run_dir, gt_dir = _create_mock_run(
            tmp_path,
            {"d1": ext, "d2": ext},
            {"d1": ext, "d2": ext},
            metadata={
                "d1": {"language": "en", "utility_type": "electricity", "pipeline_mode": "ocr_text"},
                "d2": {"language": "de", "utility_type": "gas", "pipeline_mode": "ocr_text"},
            },
        )
        ev = evaluate_run(run_dir, gt_dir)
        assert "en" in ev.by_language
        assert "de" in ev.by_language

    def test_slices_by_utility_type(self, tmp_path):
        ext = {"provider_name": "Test"}
        run_dir, gt_dir = _create_mock_run(
            tmp_path,
            {"d1": ext, "d2": ext},
            {"d1": ext, "d2": ext},
            metadata={
                "d1": {"language": "en", "utility_type": "electricity", "pipeline_mode": "ocr_text"},
                "d2": {"language": "en", "utility_type": "water", "pipeline_mode": "ocr_text"},
            },
        )
        ev = evaluate_run(run_dir, gt_dir)
        assert "electricity" in ev.by_utility_type
        assert "water" in ev.by_utility_type


class TestEvaluateRunShouldSkipErroredDocuments:
    """Documents with error.json should be skipped and added to errors_skipped."""

    def test_error_doc_skipped(self, tmp_path):
        run_dir = tmp_path / "run"
        gt_dir = tmp_path / "gt"
        doc_dir = run_dir / "documents" / "doc_err"
        doc_dir.mkdir(parents=True)
        (doc_dir / "error.json").write_text('{"error": "boom"}')
        gt_dir.mkdir(parents=True)
        (gt_dir / "doc_err.json").write_text('{"fields": {}}')

        ev = evaluate_run(run_dir, gt_dir)
        assert "doc_err" in ev.errors_skipped
        assert len(ev.documents) == 0

    def test_doc_without_extraction_skipped(self, tmp_path):
        run_dir = tmp_path / "run"
        gt_dir = tmp_path / "gt"
        doc_dir = run_dir / "documents" / "doc_noext"
        doc_dir.mkdir(parents=True)
        gt_dir.mkdir(parents=True)
        (gt_dir / "doc_noext.json").write_text('{"fields": {}}')

        ev = evaluate_run(run_dir, gt_dir)
        assert "doc_noext" in ev.errors_skipped


class TestEvaluateRunShouldRaiseOnMissingDocsDir:
    def test_no_documents_dir(self, tmp_path):
        run_dir = tmp_path / "empty_run"
        run_dir.mkdir()
        with pytest.raises(FileNotFoundError, match="No documents directory"):
            evaluate_run(run_dir, tmp_path)


class TestEvaluateRunShouldComputeFieldAccuracies:
    def test_field_accuracies_for_all_12_fields(self, tmp_path):
        ext = {"provider_name": "Test", "total_amount_due": 100.0}
        run_dir, gt_dir = _create_mock_run(tmp_path, {"d1": ext}, {"d1": ext})
        ev = evaluate_run(run_dir, gt_dir)
        from src.schema import BillExtraction
        for fname in BillExtraction.SCHEMA_FIELDS:
            assert fname in ev.field_accuracies


class TestEvaluateRunNullSummary:
    def test_counts_hallucinations_omissions_both_null(self, tmp_path):
        pred = {"provider_name": "Test", "bill_number": "INV-1"}  # bill_number hallucinated
        gt = {"provider_name": "Test", "bill_number": None}
        run_dir, gt_dir = _create_mock_run(tmp_path, {"d1": pred}, {"d1": gt})
        ev = evaluate_run(run_dir, gt_dir)
        assert ev.null_summary["hallucinations"] >= 1


# =========================================================================
# Spec: _value_in_text helper (diagnosis)
# =========================================================================


class TestValueInTextShouldCheckSubstring:
    def test_found(self):
        assert _value_in_text("OVO Energy", "Invoice from OVO Energy Ltd") is True

    def test_case_insensitive(self):
        assert _value_in_text("ovo energy", "Invoice from OVO Energy") is True

    def test_not_found(self):
        assert _value_in_text("EDF", "Invoice from OVO Energy") is False

    def test_none_value(self):
        assert _value_in_text(None, "text") is False

    def test_empty_value(self):
        assert _value_in_text("", "text") is False

    def test_numeric_value(self):
        assert _value_in_text(42.5, "Amount: 42.5") is True


# =========================================================================
# Spec: diagnose_document — OCR-text mode
# =========================================================================


def _make_doc_result(incorrect_fields, category="incorrect"):
    """Build a minimal DocumentResult with given incorrect field results."""
    fields = []
    for fname, pred, gt in incorrect_fields:
        fields.append(FieldResult(
            field_name=fname, predicted=pred, ground_truth=gt,
            match=False, category=category, similarity=0.5,
        ))
    return DocumentResult(
        document_id="test_doc", fields=fields, all_correct=False,
        incorrect=len(fields) if category == "incorrect" else 0,
        hallucination=len(fields) if category == "hallucination" else 0,
        omission=len(fields) if category == "omission" else 0,
    )


class TestDiagnoseDocumentOCRModeShouldAttributeToLLMWhenValueInOCR:
    """In OCR mode, if the ground truth value appears in the OCR text,
    the failure is an LLM extraction failure (OCR captured it, LLM missed it)."""

    def test_value_in_ocr_text(self, tmp_path):
        doc_dir = tmp_path / "doc"
        doc_dir.mkdir()
        (doc_dir / "ocr_text.txt").write_text("Invoice from OVO Energy Ltd dated 2024-01-15")

        dr = _make_doc_result([("provider_name", "wrong", "ovo energy")])
        diags = diagnose_document("test_doc", dr, doc_dir, "ocr_text")
        assert len(diags) == 1
        assert diags[0].failure_type == "llm_extraction_failure"


class TestDiagnoseDocumentOCRModeShouldAttributeToOCRWhenValueNotInText:
    """In OCR mode, if the ground truth value is NOT in the OCR text,
    the failure is an OCR failure (OCR didn't capture it)."""

    def test_value_not_in_ocr_text(self, tmp_path):
        doc_dir = tmp_path / "doc"
        doc_dir.mkdir()
        (doc_dir / "ocr_text.txt").write_text("Garbled text with no useful info")

        dr = _make_doc_result([("provider_name", "wrong", "ovo energy")])
        diags = diagnose_document("test_doc", dr, doc_dir, "ocr_text")
        assert len(diags) == 1
        assert diags[0].failure_type == "ocr_failure"


class TestDiagnoseDocumentOCRModeHallucinationShouldBecomeLLMFailure:
    """In OCR mode, a hallucination (GT=None) should be attributed to
    LLM extraction failure, not OCR failure."""

    def test_hallucination_is_llm_failure(self, tmp_path):
        doc_dir = tmp_path / "doc"
        doc_dir.mkdir()
        (doc_dir / "ocr_text.txt").write_text("some text")

        fields = [FieldResult(
            field_name="consumption_unit", predicted="kWh", ground_truth=None,
            match=False, category="hallucination", similarity=0.0,
        )]
        dr = DocumentResult(
            document_id="test_doc", fields=fields, all_correct=False,
            hallucination=1,
        )
        diags = diagnose_document("test_doc", dr, doc_dir, "ocr_text")
        assert len(diags) == 1
        assert diags[0].failure_type == "llm_extraction_failure"


class TestDiagnoseDocumentOCRModeNoOCRFile:
    """If ocr_text.txt doesn't exist, should treat as empty OCR text
    (all GT values not found → OCR failure)."""

    def test_no_ocr_file(self, tmp_path):
        doc_dir = tmp_path / "doc"
        doc_dir.mkdir()
        # No ocr_text.txt

        dr = _make_doc_result([("provider_name", "wrong", "ovo energy")])
        diags = diagnose_document("test_doc", dr, doc_dir, "ocr_text")
        assert diags[0].failure_type == "ocr_failure"


# =========================================================================
# Spec: diagnose_document — vision mode
# =========================================================================


class TestDiagnoseDocumentVisionModeShouldAlwaysBeVisionFailure:
    """In vision mode, any failure should be attributed to 'vision_model_failure'."""

    def test_single_failure(self, tmp_path):
        doc_dir = tmp_path / "doc"
        doc_dir.mkdir()

        dr = _make_doc_result([("provider_name", "wrong", "correct")])
        diags = diagnose_document("test_doc", dr, doc_dir, "vision")
        assert len(diags) == 1
        assert diags[0].failure_type == "vision_model_failure"

    def test_multiple_failures(self, tmp_path):
        doc_dir = tmp_path / "doc"
        doc_dir.mkdir()

        dr = _make_doc_result([
            ("provider_name", "wrong", "correct"),
            ("currency", "eur", "gbp"),
        ])
        diags = diagnose_document("test_doc", dr, doc_dir, "vision")
        assert len(diags) == 2
        assert all(d.failure_type == "vision_model_failure" for d in diags)


# =========================================================================
# Spec: diagnose_document — no failures
# =========================================================================


class TestDiagnoseDocumentShouldReturnEmptyIfNoFailures:
    def test_all_correct(self, tmp_path):
        doc_dir = tmp_path / "doc"
        doc_dir.mkdir()

        fields = [FieldResult(
            field_name="provider_name", predicted="test", ground_truth="test",
            match=True, category="correct", similarity=1.0,
        )]
        dr = DocumentResult(
            document_id="test_doc", fields=fields, all_correct=True,
        )
        diags = diagnose_document("test_doc", dr, doc_dir, "ocr_text")
        assert len(diags) == 0


# =========================================================================
# Spec: diagnose_document should write diagnosis.json
# =========================================================================


class TestDiagnoseDocumentShouldWriteDiagnosisJson:
    def test_writes_file(self, tmp_path):
        doc_dir = tmp_path / "doc"
        doc_dir.mkdir()
        (doc_dir / "ocr_text.txt").write_text("nothing useful")

        dr = _make_doc_result([("currency", "eur", "gbp")])
        diagnose_document("test_doc", dr, doc_dir, "ocr_text")
        assert (doc_dir / "diagnosis.json").exists()

    def test_file_contains_failure_data(self, tmp_path):
        doc_dir = tmp_path / "doc"
        doc_dir.mkdir()
        (doc_dir / "ocr_text.txt").write_text("nothing")

        dr = _make_doc_result([("currency", "eur", "gbp")])
        diagnose_document("test_doc", dr, doc_dir, "ocr_text")
        data = json.loads((doc_dir / "diagnosis.json").read_text())
        assert len(data) == 1
        assert data[0]["field_name"] == "currency"
        assert "failure_type" in data[0]


# =========================================================================
# Spec: compare_runs
# =========================================================================


@pytest.fixture
def two_runs(tmp_path):
    """Two mock runs: run_a is perfect, run_b has one wrong field."""
    gt_dir = tmp_path / "gt"
    gt_dir.mkdir()

    extraction = {
        "provider_name": "Test Co",
        "utility_type": "electricity",
        "bill_number": None,
        "bill_date": "2024-01-15",
        "billing_period_start": None,
        "billing_period_end": None,
        "due_date": None,
        "total_amount_due": 100.0,
        "currency": "GBP",
        "account_number": "12345",
        "consumption_amount": None,
        "consumption_unit": None,
    }
    (gt_dir / "doc_001.json").write_text(
        json.dumps({"document_id": "doc_001", "fields": extraction})
    )

    runs = []
    for i, name in enumerate(["run_a", "run_b"]):
        run_dir = tmp_path / name
        doc_dir = run_dir / "documents" / "doc_001"
        doc_dir.mkdir(parents=True)
        ext = dict(extraction)
        if i == 1:
            ext["provider_name"] = "Wrong"
        (doc_dir / "extraction.json").write_text(json.dumps(ext))
        (doc_dir / "metadata.json").write_text(json.dumps({
            "language": "en", "utility_type": "electricity",
            "pipeline_mode": "vision", "estimated_cost_usd": 0.01,
        }))
        (doc_dir / "timings.json").write_text(json.dumps({
            "total_ms": 5000, "llm_call_ms": 3000, "ocr_ms": 0,
        }))
        runs.append(run_dir)

    return runs, gt_dir


class TestCompareRunsShouldWriteComparisonJson:
    def test_writes_file(self, two_runs, tmp_path):
        runs, gt_dir = two_runs
        output = tmp_path / "reports"
        compare_runs(runs, gt_dir, output)
        assert (output / "comparison.json").exists()


class TestCompareRunsShouldBuildAccuracyMatrix:
    def test_contains_all_runs(self, two_runs, tmp_path):
        runs, gt_dir = two_runs
        output = tmp_path / "reports"
        report = compare_runs(runs, gt_dir, output)
        assert "run_a" in report["accuracy_matrix"]
        assert "run_b" in report["accuracy_matrix"]

    def test_run_a_higher_accuracy(self, two_runs, tmp_path):
        runs, gt_dir = two_runs
        output = tmp_path / "reports"
        report = compare_runs(runs, gt_dir, output)
        acc_a = report["accuracy_matrix"]["run_a"]["overall_accuracy"]
        acc_b = report["accuracy_matrix"]["run_b"]["overall_accuracy"]
        assert acc_a > acc_b

    def test_accuracy_matrix_has_field_keys(self, two_runs, tmp_path):
        runs, gt_dir = two_runs
        output = tmp_path / "reports"
        report = compare_runs(runs, gt_dir, output)
        from src.schema import BillExtraction
        for fname in BillExtraction.SCHEMA_FIELDS:
            assert fname in report["accuracy_matrix"]["run_a"]


class TestCompareRunsShouldBuildPerformanceMatrix:
    def test_contains_timing_data(self, two_runs, tmp_path):
        runs, gt_dir = two_runs
        output = tmp_path / "reports"
        report = compare_runs(runs, gt_dir, output)
        perf = report["performance_matrix"]["run_a"]
        assert "mean_total_ms" in perf
        assert "mean_llm_call_ms" in perf
        assert "total_estimated_cost_usd" in perf


class TestCompareRunsShouldBuildNullAnalysis:
    def test_contains_null_counts(self, two_runs, tmp_path):
        runs, gt_dir = two_runs
        output = tmp_path / "reports"
        report = compare_runs(runs, gt_dir, output)
        for label in ("run_a", "run_b"):
            null = report["null_analysis"][label]
            assert "hallucinations" in null
            assert "omissions" in null
            assert "both_null" in null


class TestCompareRunsShouldBuildSliceTables:
    def test_slice_by_language(self, two_runs, tmp_path):
        runs, gt_dir = two_runs
        output = tmp_path / "reports"
        report = compare_runs(runs, gt_dir, output)
        assert "run_a" in report["slice_by_language"]

    def test_slice_by_utility_type(self, two_runs, tmp_path):
        runs, gt_dir = two_runs
        output = tmp_path / "reports"
        report = compare_runs(runs, gt_dir, output)
        assert "run_a" in report["slice_by_utility_type"]


# =========================================================================
# Spec: compare_runs — single run (degenerate comparison)
# =========================================================================


def _create_single_run(tmp_path, run_name="single_run"):
    """Create a single run directory with one perfectly-matched document."""
    gt_dir = tmp_path / "gt"
    gt_dir.mkdir(exist_ok=True)
    extraction = {
        "provider_name": "Test Co",
        "utility_type": "electricity",
        "bill_number": None,
        "bill_date": "2024-01-15",
        "billing_period_start": None,
        "billing_period_end": None,
        "due_date": None,
        "total_amount_due": 100.0,
        "currency": "GBP",
        "account_number": "12345",
        "consumption_amount": None,
        "consumption_unit": None,
    }
    (gt_dir / "doc_001.json").write_text(
        json.dumps({"document_id": "doc_001", "fields": extraction})
    )

    run_dir = tmp_path / run_name
    doc_dir = run_dir / "documents" / "doc_001"
    doc_dir.mkdir(parents=True)
    (doc_dir / "extraction.json").write_text(json.dumps(extraction))
    (doc_dir / "metadata.json").write_text(json.dumps({
        "language": "en", "utility_type": "electricity",
        "pipeline_mode": "ocr_text", "estimated_cost_usd": 0.01,
    }))
    (doc_dir / "timings.json").write_text(json.dumps({
        "total_ms": 5000, "llm_call_ms": 3000, "ocr_ms": 1000,
    }))

    return run_dir, gt_dir


class TestCompareRunsSingleRun:
    """compare_runs should work with exactly one run, producing a valid
    (though non-comparative) comparison report."""

    def test_single_run_writes_comparison(self, tmp_path):
        run_dir, gt_dir = _create_single_run(tmp_path)
        output = tmp_path / "reports"
        report = compare_runs([run_dir], gt_dir, output)

        assert (output / "comparison.json").exists()
        assert "single_run" in report["accuracy_matrix"]
        assert len(report["accuracy_matrix"]) == 1

    def test_single_run_has_valid_accuracy(self, tmp_path):
        run_dir, gt_dir = _create_single_run(tmp_path)
        output = tmp_path / "reports"
        report = compare_runs([run_dir], gt_dir, output)

        acc = report["accuracy_matrix"]["single_run"]["overall_accuracy"]
        assert 0.0 <= acc <= 1.0

    def test_single_run_performance_matrix(self, tmp_path):
        run_dir, gt_dir = _create_single_run(tmp_path)
        output = tmp_path / "reports"
        report = compare_runs([run_dir], gt_dir, output)

        perf = report["performance_matrix"]["single_run"]
        assert "mean_total_ms" in perf
        assert perf["documents_timed"] == 1

    def test_single_run_null_analysis(self, tmp_path):
        run_dir, gt_dir = _create_single_run(tmp_path)
        output = tmp_path / "reports"
        report = compare_runs([run_dir], gt_dir, output)

        null = report["null_analysis"]["single_run"]
        assert "hallucinations" in null
        assert "omissions" in null
        assert "both_null" in null


# =========================================================================
# Spec: compare_runs — auto-evaluate when evaluation.json is missing
# =========================================================================


class TestCompareRunsAutoEvaluate:
    """When evaluation.json is missing from a run directory, compare_runs
    should automatically run evaluate_run first."""

    def test_generates_evaluation_json(self, tmp_path):
        run_dir, gt_dir = _create_single_run(tmp_path, "auto_eval_run")

        assert not (run_dir / "evaluation.json").exists()

        output = tmp_path / "reports"
        compare_runs([run_dir], gt_dir, output)

        assert (run_dir / "evaluation.json").exists()

    def test_uses_pre_existing_evaluation_json(self, tmp_path):
        run_dir, gt_dir = _create_single_run(tmp_path, "pre_eval_run")

        evaluate_run(run_dir, gt_dir)
        assert (run_dir / "evaluation.json").exists()
        mtime_before = (run_dir / "evaluation.json").stat().st_mtime

        import time
        time.sleep(0.1)

        output = tmp_path / "reports"
        compare_runs([run_dir], gt_dir, output)

        mtime_after = (run_dir / "evaluation.json").stat().st_mtime
        assert mtime_before == mtime_after


# =========================================================================
# Spec: evaluate_run — zero evaluated documents
# =========================================================================


class TestEvaluateRunZeroEvaluatedDocuments:
    """When all documents are skipped (errors or missing GT), evaluate_run
    should return zero accuracies and an empty documents dict."""

    def test_all_error_docs(self, tmp_path):
        run_dir = tmp_path / "run"
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir(parents=True)

        for did in ("doc_a", "doc_b"):
            doc_dir = run_dir / "documents" / did
            doc_dir.mkdir(parents=True)
            (doc_dir / "error.json").write_text('{"error": "boom"}')
            (gt_dir / f"{did}.json").write_text(
                json.dumps({"fields": {"provider_name": "Test"}})
            )

        ev = evaluate_run(run_dir, gt_dir)
        assert ev.overall_accuracy == 0.0
        assert ev.document_level_accuracy == 0.0
        assert len(ev.documents) == 0
        assert len(ev.errors_skipped) == 2

    def test_all_missing_gt(self, tmp_path):
        run_dir = tmp_path / "run"
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir(parents=True)

        doc_dir = run_dir / "documents" / "doc_a"
        doc_dir.mkdir(parents=True)
        (doc_dir / "extraction.json").write_text('{"provider_name": "Test"}')

        ev = evaluate_run(run_dir, gt_dir)
        assert ev.overall_accuracy == 0.0
        assert len(ev.documents) == 0
        assert "doc_a" in ev.errors_skipped

    def test_writes_evaluation_json_even_when_empty(self, tmp_path):
        run_dir = tmp_path / "run"
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir(parents=True)

        doc_dir = run_dir / "documents" / "doc_a"
        doc_dir.mkdir(parents=True)
        (doc_dir / "error.json").write_text('{"error": "boom"}')
        (gt_dir / "doc_a.json").write_text('{"fields": {}}')

        evaluate_run(run_dir, gt_dir)
        assert (run_dir / "evaluation.json").exists()

    def test_field_accuracies_all_zero(self, tmp_path):
        from src.schema import BillExtraction as Schema

        run_dir = tmp_path / "run"
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir(parents=True)

        doc_dir = run_dir / "documents" / "doc_a"
        doc_dir.mkdir(parents=True)
        (doc_dir / "error.json").write_text('{"error": "boom"}')
        (gt_dir / "doc_a.json").write_text('{"fields": {}}')

        ev = evaluate_run(run_dir, gt_dir)
        for fname in Schema.SCHEMA_FIELDS:
            assert ev.field_accuracies[fname] == 0.0


# =========================================================================
# Spec: evaluate_run — corrupt extraction.json
# =========================================================================


class TestEvaluateRunCorruptExtraction:
    """A document with invalid JSON in extraction.json should cause
    evaluate_run to raise json.JSONDecodeError (no per-doc error handling)."""

    def test_invalid_json_raises(self, tmp_path):
        run_dir = tmp_path / "run"
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir(parents=True)

        doc_dir = run_dir / "documents" / "doc_a"
        doc_dir.mkdir(parents=True)
        (doc_dir / "extraction.json").write_text("not valid json {{{")
        (doc_dir / "metadata.json").write_text(json.dumps({
            "language": "en", "utility_type": "electricity",
            "pipeline_mode": "ocr_text",
        }))
        (gt_dir / "doc_a.json").write_text(
            json.dumps({"fields": {"provider_name": "Test"}})
        )

        with pytest.raises(json.JSONDecodeError):
            evaluate_run(run_dir, gt_dir)


# =========================================================================
# Spec: evaluate_run — mixed error and valid documents
# =========================================================================


class TestEvaluateRunMixedErrorAndValid:
    """When some documents have errors and some are valid, evaluate_run should
    evaluate the valid ones and skip the errored ones."""

    def test_mixed_docs(self, tmp_path):
        ext = {"provider_name": "Test", "total_amount_due": 100.0}
        run_dir = tmp_path / "run"
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir(parents=True)

        ok_dir = run_dir / "documents" / "doc_ok"
        ok_dir.mkdir(parents=True)
        (ok_dir / "extraction.json").write_text(json.dumps(ext))
        (ok_dir / "metadata.json").write_text(json.dumps({
            "language": "en", "utility_type": "electricity",
            "pipeline_mode": "ocr_text",
        }))
        (ok_dir / "timings.json").write_text(json.dumps({
            "total_ms": 5000, "llm_call_ms": 3000, "ocr_ms": 1000,
        }))
        (gt_dir / "doc_ok.json").write_text(
            json.dumps({"document_id": "doc_ok", "fields": ext})
        )

        err_dir = run_dir / "documents" / "doc_err"
        err_dir.mkdir(parents=True)
        (err_dir / "error.json").write_text('{"error": "API down"}')
        (gt_dir / "doc_err.json").write_text(
            json.dumps({"document_id": "doc_err", "fields": ext})
        )

        ev = evaluate_run(run_dir, gt_dir)
        assert len(ev.documents) == 1
        assert "doc_ok" in ev.documents
        assert "doc_err" in ev.errors_skipped
        assert ev.overall_accuracy > 0.0
