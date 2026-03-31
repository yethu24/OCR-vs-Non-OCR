from datetime import date

from src.schema import BillExtraction, DocumentEntry, PipelineResult


class TestBillExtraction:
    def test_all_fields_optional(self):
        """Every field should default to None — a fully empty extraction is valid."""
        extraction = BillExtraction()
        assert extraction.provider_name is None
        assert extraction.total_amount_due is None
        assert extraction.bill_date is None

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
        assert extraction.total_amount_due == 127.43
        assert extraction.bill_date == date(2024, 11, 15)

    def test_serialisation_roundtrip(self):
        original = BillExtraction(
            provider_name="EDF",
            total_amount_due=99.99,
            bill_date=date(2024, 6, 1),
        )
        as_json = original.model_dump_json()
        restored = BillExtraction.model_validate_json(as_json)
        assert restored == original

    def test_schema_description_contains_all_fields(self):
        desc = BillExtraction.schema_description()
        for field in BillExtraction.SCHEMA_FIELDS:
            assert field in desc

    def test_from_dict_with_date_string(self):
        data = {"bill_date": "2024-11-15", "total_amount_due": 50.0}
        extraction = BillExtraction.model_validate(data)
        assert extraction.bill_date == date(2024, 11, 15)


class TestPipelineResult:
    def test_minimal_result(self):
        result = PipelineResult(
            document_id="test_001",
            extraction=BillExtraction(),
            model_id="gpt-4o",
            pipeline_mode="vision",
        )
        assert result.document_id == "test_001"
        assert result.ocr_text is None
        assert result.timings == {}
        assert result.token_usage == {}

    def test_full_result(self):
        result = PipelineResult(
            document_id="test_002",
            extraction=BillExtraction(provider_name="Ovo"),
            raw_llm_output='{"provider_name": "Ovo"}',
            ocr_text="Some OCR text here",
            timings={"ocr": 1.5, "llm": 2.3},
            token_usage={"input": 500, "output": 200},
            model_id="gpt-4o",
            pipeline_mode="ocr_text",
        )
        assert result.ocr_text == "Some OCR text here"
        assert result.timings["ocr"] == 1.5


class TestDocumentEntry:
    def test_creation(self):
        from pathlib import Path

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
        assert entry.digital_native is True
