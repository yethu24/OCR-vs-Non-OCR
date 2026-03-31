import pytest

from src.normalisation import (
    normalise_currency,
    normalise_date,
    normalise_extraction,
    normalise_float,
    normalise_string,
)


class TestNormaliseDate:
    @pytest.mark.parametrize(
        "input_val, expected",
        [
            ("2024-11-15", "2024-11-15"),
            ("15/11/2024", "2024-11-15"),
            ("15.11.2024", "2024-11-15"),
            ("15-11-2024", "2024-11-15"),
            ("November 15, 2024", "2024-11-15"),
            ("Nov 15, 2024", "2024-11-15"),
            ("15 November 2024", "2024-11-15"),
            ("15 Nov 2024", "2024-11-15"),
            ("2024/11/15", "2024-11-15"),
        ],
    )
    def test_various_formats(self, input_val, expected):
        assert normalise_date(input_val) == expected

    def test_none_returns_none(self):
        assert normalise_date(None) is None

    def test_empty_string_returns_none(self):
        assert normalise_date("") is None
        assert normalise_date("   ") is None

    def test_date_object(self):
        from datetime import date

        assert normalise_date(date(2024, 3, 1)) == "2024-03-01"

    def test_unrecognised_format_returned_as_is(self):
        assert normalise_date("Q4 2024") == "Q4 2024"


class TestNormaliseString:
    def test_basic(self):
        assert normalise_string("  British Gas  ") == "british gas"

    def test_collapses_whitespace(self):
        assert normalise_string("Ovo   Energy   Ltd") == "ovo energy ltd"

    def test_none_returns_none(self):
        assert normalise_string(None) is None

    def test_empty_returns_none(self):
        assert normalise_string("") is None
        assert normalise_string("   ") is None

    def test_non_string_cast(self):
        assert normalise_string(12345) == "12345"


class TestNormaliseCurrency:
    def test_basic(self):
        assert normalise_currency("gbp") == "GBP"
        assert normalise_currency("  eur ") == "EUR"

    def test_none(self):
        assert normalise_currency(None) is None

    def test_empty(self):
        assert normalise_currency("") is None


class TestNormaliseFloat:
    def test_basic(self):
        assert normalise_float(127.4321) == 127.43

    def test_string_input(self):
        assert normalise_float("99.999") == 100.0

    def test_int_input(self):
        assert normalise_float(100) == 100.0

    def test_none(self):
        assert normalise_float(None) is None

    def test_invalid_string(self):
        assert normalise_float("not a number") is None


class TestNormaliseExtraction:
    def test_full_extraction(self):
        raw = {
            "provider_name": "  British Gas  ",
            "utility_type": "Electricity",
            "bill_number": "INV-001",
            "bill_date": "15/11/2024",
            "billing_period_start": "2024-10-01",
            "billing_period_end": "2024-10-31",
            "due_date": "01 December 2024",
            "total_amount_due": 127.4321,
            "currency": "gbp",
            "account_number": "ACC-123",
            "consumption_amount": "412.567",
            "consumption_unit": " kWh ",
        }
        result = normalise_extraction(raw)
        assert result["provider_name"] == "british gas"
        assert result["utility_type"] == "electricity"
        assert result["bill_date"] == "2024-11-15"
        assert result["due_date"] == "2024-12-01"
        assert result["total_amount_due"] == 127.43
        assert result["currency"] == "GBP"
        assert result["consumption_amount"] == 412.57
        assert result["consumption_unit"] == "kwh"

    def test_missing_fields_become_none(self):
        result = normalise_extraction({})
        assert all(v is None for v in result.values())
        assert len(result) == 12

    def test_null_fields_stay_none(self):
        raw = {field: None for field in normalise_extraction({}).keys()}
        result = normalise_extraction(raw)
        assert all(v is None for v in result.values())
