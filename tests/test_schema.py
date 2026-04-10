"""Comprehensive tests for src/schema.py — BillExtraction, PipelineResult, DocumentEntry."""

from datetime import date, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.schema import BillExtraction, DocumentEntry, PipelineResult


# =========================================================================
# BillExtraction
# =========================================================================


class TestBillExtractionDefaults:
    """All fields should be Optional and default to None."""

    def test_all_fields_default_to_none(self):
        extraction = BillExtraction()
        for field in BillExtraction.SCHEMA_FIELDS:
            assert getattr(extraction, field) is None

    def test_empty_extraction_is_valid(self):
        extraction = BillExtraction()
        assert extraction is not None

    def test_schema_fields_count(self):
        assert len(BillExtraction.SCHEMA_FIELDS) == 12

    def test_schema_fields_list(self):
        expected = [
            "provider_name", "utility_type", "bill_number", "bill_date",
            "billing_period_start", "billing_period_end", "due_date",
            "total_amount_due", "currency", "account_number",
            "consumption_amount", "consumption_unit",
        ]
        assert BillExtraction.SCHEMA_FIELDS == expected


class TestBillExtractionCreation:
    """Test creating BillExtraction with various field combinations."""

    def test_full_extraction(self):
        extraction = BillExtraction(
            provider_name="British Gas",
            utility_type="electricity",
            bill_number="INV-001",
            bill_date=date(2024, 11, 15),
            billing_period_start=date(2024, 10, 1),
            billing_period_end=date(2024, 10, 31),
            due_date=date(2024, 12, 1),
            total_amount_due=127.43,
            currency="GBP",
            account_number="850012345678",
            consumption_amount=412.5,
            consumption_unit="kWh",
        )
        assert extraction.provider_name == "British Gas"
        assert extraction.utility_type == "electricity"
        assert extraction.bill_number == "INV-001"
        assert extraction.bill_date == date(2024, 11, 15)
        assert extraction.billing_period_start == date(2024, 10, 1)
        assert extraction.billing_period_end == date(2024, 10, 31)
        assert extraction.due_date == date(2024, 12, 1)
        assert extraction.total_amount_due == 127.43
        assert extraction.currency == "GBP"
        assert extraction.account_number == "850012345678"
        assert extraction.consumption_amount == 412.5
        assert extraction.consumption_unit == "kWh"

    def test_partial_extraction(self):
        extraction = BillExtraction(
            provider_name="EDF",
            total_amount_due=99.99,
        )
        assert extraction.provider_name == "EDF"
        assert extraction.total_amount_due == 99.99
        assert extraction.bill_date is None
        assert extraction.currency is None

    def test_only_dates(self):
        extraction = BillExtraction(
            bill_date=date(2024, 6, 1),
            billing_period_start=date(2024, 5, 1),
            billing_period_end=date(2024, 5, 31),
            due_date=date(2024, 6, 15),
        )
        assert extraction.bill_date == date(2024, 6, 1)
        assert extraction.provider_name is None

    def test_only_floats(self):
        extraction = BillExtraction(
            total_amount_due=0.01,
            consumption_amount=0.0,
        )
        assert extraction.total_amount_due == 0.01
        assert extraction.consumption_amount == 0.0

    def test_zero_amount(self):
        extraction = BillExtraction(total_amount_due=0.0)
        assert extraction.total_amount_due == 0.0

    def test_negative_amount(self):
        """Negative amounts should be accepted (credit notes)."""
        extraction = BillExtraction(total_amount_due=-50.00)
        assert extraction.total_amount_due == -50.00

    def test_large_consumption(self):
        extraction = BillExtraction(consumption_amount=999999.99)
        assert extraction.consumption_amount == 999999.99


class TestBillExtractionSerialisation:
    """Test JSON serialisation and deserialisation."""

    def test_roundtrip_full(self):
        original = BillExtraction(
            provider_name="EDF",
            utility_type="gas",
            bill_number="B-42",
            bill_date=date(2024, 6, 1),
            billing_period_start=date(2024, 5, 1),
            billing_period_end=date(2024, 5, 31),
            due_date=date(2024, 7, 1),
            total_amount_due=99.99,
            currency="EUR",
            account_number="ACC-999",
            consumption_amount=150.0,
            consumption_unit="m3",
        )
        as_json = original.model_dump_json()
        restored = BillExtraction.model_validate_json(as_json)
        assert restored == original

    def test_roundtrip_empty(self):
        original = BillExtraction()
        as_json = original.model_dump_json()
        restored = BillExtraction.model_validate_json(as_json)
        assert restored == original

    def test_roundtrip_partial(self):
        original = BillExtraction(provider_name="Test", total_amount_due=42.0)
        restored = BillExtraction.model_validate_json(original.model_dump_json())
        assert restored == original

    def test_model_dump_mode_json(self):
        extraction = BillExtraction(
            bill_date=date(2024, 3, 15),
            total_amount_due=100.0,
        )
        d = extraction.model_dump(mode="json")
        assert d["bill_date"] == "2024-03-15"
        assert d["total_amount_due"] == 100.0
        assert d["provider_name"] is None


class TestBillExtractionFromDict:
    """Test model_validate with dict/JSON-like inputs."""

    def test_from_dict_with_date_string(self):
        data = {"bill_date": "2024-11-15", "total_amount_due": 50.0}
        extraction = BillExtraction.model_validate(data)
        assert extraction.bill_date == date(2024, 11, 15)

    def test_from_dict_with_all_none(self):
        data = {field: None for field in BillExtraction.SCHEMA_FIELDS}
        extraction = BillExtraction.model_validate(data)
        for field in BillExtraction.SCHEMA_FIELDS:
            assert getattr(extraction, field) is None

    def test_from_dict_with_extra_fields_ignored(self):
        data = {"provider_name": "Test", "extra_field": "should be ignored"}
        extraction = BillExtraction.model_validate(data)
        assert extraction.provider_name == "Test"
        assert not hasattr(extraction, "extra_field")

    def test_from_empty_dict(self):
        extraction = BillExtraction.model_validate({})
        assert extraction.provider_name is None


class TestBillExtractionSchemaDescription:
    """Test the schema_description class method."""

    def test_contains_all_fields(self):
        desc = BillExtraction.schema_description()
        for field in BillExtraction.SCHEMA_FIELDS:
            assert field in desc

    def test_each_field_on_own_line(self):
        desc = BillExtraction.schema_description()
        lines = desc.strip().split("\n")
        assert len(lines) == 12

    def test_lines_start_with_dash(self):
        desc = BillExtraction.schema_description()
        for line in desc.strip().split("\n"):
            assert line.startswith("- ")

    def test_contains_type_hints(self):
        desc = BillExtraction.schema_description()
        assert "string" in desc
        assert "date" in desc
        assert "float" in desc
        assert "YYYY-MM-DD" in desc

    def test_contains_example_values(self):
        desc = BillExtraction.schema_description()
        assert "GBP" in desc or "EUR" in desc
        assert "kWh" in desc


class TestBillExtractionModelConfig:
    def test_json_schema_title(self):
        schema = BillExtraction.model_json_schema()
        assert schema["title"] == "Utility Bill Extraction"


# =========================================================================
# PipelineResult
# =========================================================================


class TestPipelineResultDefaults:
    def test_minimal_result(self):
        result = PipelineResult(
            document_id="test_001",
            extraction=BillExtraction(),
        )
        assert result.document_id == "test_001"
        assert result.raw_llm_output == ""
        assert result.ocr_text is None
        assert result.timings == {}
        assert result.token_usage == {}
        assert result.model_id == ""
        assert result.pipeline_mode == ""

    def test_extraction_is_required(self):
        with pytest.raises(ValidationError):
            PipelineResult(document_id="test_001")

    def test_document_id_is_required(self):
        with pytest.raises(ValidationError):
            PipelineResult(extraction=BillExtraction())


class TestPipelineResultFull:
    def test_full_result(self):
        extraction = BillExtraction(provider_name="Ovo", total_amount_due=150.0)
        result = PipelineResult(
            document_id="test_002",
            extraction=extraction,
            raw_llm_output='{"provider_name": "Ovo"}',
            ocr_text="Some OCR text here",
            timings={"total_ms": 5000, "llm_call_ms": 3000, "ocr_ms": 1000},
            token_usage={"input_tokens": 500, "output_tokens": 200},
            model_id="openai/gpt-4o",
            pipeline_mode="ocr_text",
        )
        assert result.ocr_text == "Some OCR text here"
        assert result.timings["total_ms"] == 5000
        assert result.token_usage["input_tokens"] == 500
        assert result.model_id == "openai/gpt-4o"
        assert result.pipeline_mode == "ocr_text"

    def test_vision_mode_no_ocr_text(self):
        result = PipelineResult(
            document_id="test_003",
            extraction=BillExtraction(),
            pipeline_mode="vision",
            model_id="anthropic/claude-3-5-sonnet",
        )
        assert result.ocr_text is None
        assert result.pipeline_mode == "vision"

    def test_serialisation_roundtrip(self):
        result = PipelineResult(
            document_id="test_004",
            extraction=BillExtraction(provider_name="Test", bill_date=date(2024, 1, 1)),
            raw_llm_output="raw",
            model_id="openai/gpt-4o",
            pipeline_mode="ocr_text",
        )
        restored = PipelineResult.model_validate_json(result.model_dump_json())
        assert restored.document_id == result.document_id
        assert restored.extraction.provider_name == "Test"


# =========================================================================
# DocumentEntry
# =========================================================================


class TestDocumentEntry:
    def test_creation(self):
        entry = DocumentEntry(
            document_id="GB_electricity_ovo_001",
            language="en",
            utility_type="electricity",
            provider="Ovo Energy",
            digital_native=True,
            page_count=2,
            pdf_path=Path("data/bills/GB_electricity_ovo_001.pdf"),
            ground_truth_path=Path("data/ground_truth/GB_electricity_ovo_001.json"),
        )
        assert entry.document_id == "GB_electricity_ovo_001"
        assert entry.language == "en"
        assert entry.utility_type == "electricity"
        assert entry.provider == "Ovo Energy"
        assert entry.digital_native is True
        assert entry.page_count == 2
        assert entry.pdf_path == Path("data/bills/GB_electricity_ovo_001.pdf")
        assert entry.ground_truth_path == Path("data/ground_truth/GB_electricity_ovo_001.json")

    def test_digital_native_false(self):
        entry = DocumentEntry(
            document_id="DE_gas_001",
            language="de",
            utility_type="gas",
            provider="E.ON",
            digital_native=False,
            page_count=1,
            pdf_path=Path("data/bills/DE_gas_001.pdf"),
            ground_truth_path=Path("data/ground_truth/DE_gas_001.json"),
        )
        assert entry.digital_native is False
        assert entry.page_count == 1

    def test_all_languages(self):
        for lang in ("en", "de", "fr", "it"):
            entry = DocumentEntry(
                document_id=f"test_{lang}",
                language=lang,
                utility_type="electricity",
                provider="Test",
                digital_native=True,
                page_count=1,
                pdf_path=Path("test.pdf"),
                ground_truth_path=Path("test.json"),
            )
            assert entry.language == lang

    def test_all_utility_types(self):
        for utype in ("electricity", "gas", "water"):
            entry = DocumentEntry(
                document_id=f"test_{utype}",
                language="en",
                utility_type=utype,
                provider="Test",
                digital_native=True,
                page_count=1,
                pdf_path=Path("test.pdf"),
                ground_truth_path=Path("test.json"),
            )
            assert entry.utility_type == utype
