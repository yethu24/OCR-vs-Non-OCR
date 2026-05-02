"""TDD-style specification for src/normalisation.py.

Each test class specifies one behaviour contract of a normalisation function.
Structure: Given [input], the normaliser should [produce expected output].
"""

from datetime import date, datetime

import pytest

from src.normalisation import (
    FIELD_NORMALISERS,
    _parse_numeric_string,
    normalise_consumption_unit,
    normalise_currency,
    normalise_date,
    normalise_extraction,
    normalise_float,
    normalise_provider_name,
    normalise_string,
    normalise_utility_type,
)


# =========================================================================
# Spec: normalise_date
# =========================================================================


class TestNormaliseDateShouldParseKnownFormats:
    """Given a date string in any supported format, normalise_date should
    return an ISO 8601 string (YYYY-MM-DD)."""

    @pytest.mark.parametrize("input_val, expected", [
        ("2024-11-15", "2024-11-15"),           # ISO 8601
        ("15/11/2024", "2024-11-15"),           # DD/MM/YYYY
        ("11/15/2024", "2024-11-15"),           # MM/DD/YYYY
        ("15.11.2024", "2024-11-15"),           # DD.MM.YYYY (EU)
        ("15-11-2024", "2024-11-15"),           # DD-MM-YYYY
        ("November 15, 2024", "2024-11-15"),    # Full month name
        ("Nov 15, 2024", "2024-11-15"),         # Abbreviated month
        ("15 November 2024", "2024-11-15"),     # DD Month YYYY
        ("15 Nov 2024", "2024-11-15"),          # DD Mon YYYY
        ("2024/11/15", "2024-11-15"),           # YYYY/MM/DD
    ])
    def test_format(self, input_val, expected):
        assert normalise_date(input_val) == expected


class TestNormaliseDateShouldHandleDateObjects:
    """Given a Python date or datetime, normalise_date should return ISO string."""

    def test_date_object(self):
        assert normalise_date(date(2024, 3, 1)) == "2024-03-01"

    def test_datetime_object(self):
        assert normalise_date(datetime(2024, 3, 1, 14, 30)) == "2024-03-01"


class TestNormaliseDateShouldReturnNoneForEmpty:
    """Given None, empty, or whitespace-only input, should return None."""

    def test_none(self):
        assert normalise_date(None) is None

    def test_empty_string(self):
        assert normalise_date("") is None

    def test_whitespace_only(self):
        assert normalise_date("   ") is None

    def test_non_string_non_date(self):
        assert normalise_date(12345) is None


class TestNormaliseDateShouldKeepUnparseable:
    """Given a string that doesn't match any known format, return it as-is."""

    def test_quarter_notation(self):
        assert normalise_date("Q4 2024") == "Q4 2024"

    def test_relative_date(self):
        assert normalise_date("last month") == "last month"

    def test_partial_date(self):
        assert normalise_date("March 2024") == "March 2024"


# =========================================================================
# Spec: normalise_string
# =========================================================================


class TestNormaliseStringShouldNormalise:
    """Given a string, normalise_string should NFC-normalise, strip, lowercase,
    and collapse internal whitespace."""

    def test_strips_and_lowercases(self):
        assert normalise_string("  British Gas  ") == "british gas"

    def test_collapses_whitespace(self):
        assert normalise_string("Ovo   Energy   Ltd") == "ovo energy ltd"

    def test_nfc_normalisation(self):
        precomposed = "caf\u00e9"
        decomposed = "cafe\u0301"
        assert normalise_string(precomposed) == normalise_string(decomposed)

    def test_tabs_and_newlines_collapsed(self):
        assert normalise_string("hello\t\n  world") == "hello world"


class TestNormaliseStringShouldReturnNone:
    """Given None or empty-after-strip input, should return None."""

    def test_none(self):
        assert normalise_string(None) is None

    def test_empty(self):
        assert normalise_string("") is None

    def test_whitespace_only(self):
        assert normalise_string("   ") is None


class TestNormaliseStringShouldCastNonStrings:
    """Given a non-string value, should cast to string first."""

    def test_integer(self):
        assert normalise_string(12345) == "12345"

    def test_float(self):
        assert normalise_string(3.14) == "3.14"


# =========================================================================
# Spec: normalise_utility_type
# =========================================================================


class TestNormaliseUtilityTypeShouldMapSynonyms:
    """Given a synonym for electricity/gas/water in any language,
    should return the canonical English value."""

    @pytest.mark.parametrize("input_val, expected", [
        # English
        ("electric", "electricity"),
        ("electricity", "electricity"),
        ("power", "electricity"),
        ("gas", "gas"),
        ("water", "water"),
        # German
        ("strom", "electricity"),
        ("erdgas", "gas"),
        ("wasser", "water"),
        # French
        ("electricité", "electricity"),
        ("electricite", "electricity"),
        ("gaz", "gas"),
        ("eau", "water"),
        # Italian
        ("elettricità", "electricity"),
        ("elettrico", "electricity"),
        ("luce", "electricity"),
        ("energia elettrica", "electricity"),
        ("metano", "gas"),
        ("acqua", "water"),
        # Spanish
        ("agua", "water"),
    ])
    def test_synonym(self, input_val, expected):
        assert normalise_utility_type(input_val) == expected

    def test_case_insensitive(self):
        assert normalise_utility_type("ELECTRICITY") == "electricity"
        assert normalise_utility_type("Gas") == "gas"
        assert normalise_utility_type("Luce") == "electricity"


class TestNormaliseUtilityTypeShouldFallbackToStringNorm:
    """Given an unknown utility type, should apply standard string normalisation."""

    def test_unknown_type(self):
        assert normalise_utility_type("heating") == "heating"


class TestNormaliseUtilityTypeShouldReturnNone:
    def test_none(self):
        assert normalise_utility_type(None) is None

    def test_empty(self):
        assert normalise_utility_type("") is None

    def test_whitespace(self):
        assert normalise_utility_type("   ") is None


# =========================================================================
# Spec: normalise_currency
# =========================================================================


class TestNormaliseCurrencyShouldMapSymbolsAndNames:
    """Given a currency symbol or common name, should return the ISO 4217 code."""

    @pytest.mark.parametrize("input_val, expected", [
        ("€", "EUR"), ("euro", "EUR"), ("euros", "EUR"), ("eur", "EUR"),
        ("£", "GBP"), ("pound", "GBP"), ("pounds", "GBP"), ("sterling", "GBP"), ("gbp", "GBP"),
        ("$", "USD"), ("dollar", "USD"), ("dollars", "USD"), ("usd", "USD"),
        ("chf", "CHF"), ("franc", "CHF"), ("francs", "CHF"),
    ])
    def test_maps_to_iso(self, input_val, expected):
        assert normalise_currency(input_val) == expected

    def test_case_insensitive(self):
        assert normalise_currency("GBP") == "GBP"
        assert normalise_currency("gbp") == "GBP"
        assert normalise_currency("Gbp") == "GBP"


class TestNormaliseCurrencyShouldAcceptUnknown3LetterCodes:
    """Given a valid 3-letter code not in the map, should uppercase and return it."""

    @pytest.mark.parametrize("code", ["SEK", "sek", "JPY", "jpy", "AUD", "INR"])
    def test_unknown_iso_code(self, code):
        result = normalise_currency(code)
        assert result == code.upper()
        assert len(result) == 3


class TestNormaliseCurrencyShouldReturnNone:
    def test_none(self):
        assert normalise_currency(None) is None

    def test_empty(self):
        assert normalise_currency("") is None

    def test_whitespace(self):
        assert normalise_currency("   ") is None

    def test_garbage(self):
        assert normalise_currency("not money") is None

    def test_two_letter_code(self):
        assert normalise_currency("GB") is None

    def test_four_letter_string(self):
        assert normalise_currency("ABCD") is None


# =========================================================================
# Spec: normalise_consumption_unit
# =========================================================================


class TestNormaliseConsumptionUnitShouldMapSynonyms:
    """Given a synonym for a consumption unit, should return the canonical form."""

    @pytest.mark.parametrize("input_val, expected", [
        # kWh
        ("kwh", "kWh"), ("kw/h", "kWh"), ("kilowatt hour", "kWh"),
        ("kilowatt-hour", "kWh"),
        # MWh
        ("mwh", "MWh"), ("megawatt hour", "MWh"),
        # GJ
        ("gj", "GJ"), ("gigajoule", "GJ"),
        # SMC
        ("smc", "SMC"), ("sm3", "SMC"), ("standard cubic metre", "SMC"),
        ("standard cubic meter", "SMC"),
        # m3
        ("m3", "m3"), ("m³", "m3"), ("m^3", "m3"), ("mc", "m3"),
        ("cubic metre", "m3"), ("cubic meter", "m3"),
        ("cubic metres", "m3"), ("cubic meters", "m3"),
        # Litres
        ("l", "L"), ("litre", "L"), ("liter", "L"), ("litres", "L"),
        # Gallons
        ("gal", "gal"), ("gallon", "gal"), ("gallons", "gal"),
    ])
    def test_synonym(self, input_val, expected):
        assert normalise_consumption_unit(input_val) == expected


class TestNormaliseConsumptionUnitShouldFallbackToStringNorm:
    """Given an unknown unit, should apply standard string normalisation."""

    def test_unknown_unit(self):
        assert normalise_consumption_unit("therms") == "therms"

    def test_unknown_unit_with_whitespace(self):
        assert normalise_consumption_unit("  THERMS  ") == "therms"


class TestNormaliseConsumptionUnitShouldReturnNone:
    def test_none(self):
        assert normalise_consumption_unit(None) is None

    def test_empty(self):
        assert normalise_consumption_unit("") is None

    def test_whitespace(self):
        assert normalise_consumption_unit("   ") is None


# =========================================================================
# Spec: _parse_numeric_string
# =========================================================================


class TestParseNumericStringShouldHandleFormats:
    """Given a numeric string with EU or US separators, should return a float."""

    def test_plain_integer(self):
        assert _parse_numeric_string("42") == 42.0

    def test_plain_decimal(self):
        assert _parse_numeric_string("42.50") == 42.5

    def test_european_format_dot_thousands_comma_decimal(self):
        # 1.234,56 → 1234.56
        assert _parse_numeric_string("1.234,56") == 1234.56

    def test_us_format_comma_thousands_dot_decimal(self):
        # 1,234.56 → 1234.56
        assert _parse_numeric_string("1,234.56") == 1234.56

    def test_simple_comma_as_decimal(self):
        # 65,88 → 65.88
        assert _parse_numeric_string("65,88") == 65.88

    def test_whitespace_stripped(self):
        assert _parse_numeric_string("  42.5  ") == 42.5

    def test_negative_number(self):
        assert _parse_numeric_string("-100.50") == -100.5


class TestParseNumericStringShouldRaiseOnInvalid:
    def test_empty_string(self):
        with pytest.raises(ValueError):
            _parse_numeric_string("")

    def test_whitespace_only(self):
        with pytest.raises(ValueError):
            _parse_numeric_string("   ")

    def test_not_a_number(self):
        with pytest.raises(ValueError):
            _parse_numeric_string("abc")


# =========================================================================
# Spec: normalise_float
# =========================================================================


class TestNormaliseFloatShouldRoundTo2Decimals:
    """Given a numeric value, should return a float rounded to 2 decimal places."""

    def test_float_input(self):
        assert normalise_float(127.4321) == 127.43

    def test_float_rounds_up(self):
        assert normalise_float(99.999) == 100.0

    def test_int_input(self):
        assert normalise_float(100) == 100.0

    def test_string_input(self):
        assert normalise_float("99.999") == 100.0

    def test_european_string(self):
        assert normalise_float("1.234,56") == 1234.56

    def test_us_string(self):
        assert normalise_float("1,234.56") == 1234.56

    def test_simple_comma_decimal(self):
        assert normalise_float("65,88") == 65.88

    def test_zero(self):
        assert normalise_float(0) == 0.0

    def test_negative(self):
        assert normalise_float(-50.5) == -50.5


class TestNormaliseFloatShouldReturnNone:
    """Given None, bool, or unparseable input, should return None."""

    def test_none(self):
        assert normalise_float(None) is None

    def test_bool_true(self):
        assert normalise_float(True) is None

    def test_bool_false(self):
        assert normalise_float(False) is None

    def test_invalid_string(self):
        assert normalise_float("not a number") is None

    def test_empty_string(self):
        assert normalise_float("") is None


# =========================================================================
# Spec: FIELD_NORMALISERS mapping
# =========================================================================


class TestFieldNormalisersMapping:
    """FIELD_NORMALISERS should map each of the 12 schema fields
    to the correct normaliser function."""

    def test_has_12_entries(self):
        assert len(FIELD_NORMALISERS) == 12

    def test_date_fields_use_normalise_date(self):
        for f in ("bill_date", "billing_period_start", "billing_period_end", "due_date"):
            assert FIELD_NORMALISERS[f] is normalise_date

    def test_float_fields_use_normalise_float(self):
        for f in ("total_amount_due", "consumption_amount"):
            assert FIELD_NORMALISERS[f] is normalise_float

    def test_string_fields_use_normalise_string(self):
        for f in ("bill_number", "account_number"):
            assert FIELD_NORMALISERS[f] is normalise_string

    def test_provider_name_uses_normalise_provider_name(self):
        assert FIELD_NORMALISERS["provider_name"] is normalise_provider_name

    def test_utility_type_uses_normalise_utility_type(self):
        assert FIELD_NORMALISERS["utility_type"] is normalise_utility_type

    def test_currency_uses_normalise_currency(self):
        assert FIELD_NORMALISERS["currency"] is normalise_currency

    def test_consumption_unit_uses_normalise_consumption_unit(self):
        assert FIELD_NORMALISERS["consumption_unit"] is normalise_consumption_unit


# =========================================================================
# Spec: normalise_extraction
# =========================================================================


class TestNormaliseExtractionShouldNormaliseAllFields:
    """Given a dict of raw extraction fields, normalise_extraction should
    apply the correct normaliser to each field and return a 12-key dict."""

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
        assert result["bill_number"] == "inv-001"
        assert result["bill_date"] == "2024-11-15"
        assert result["billing_period_start"] == "2024-10-01"
        assert result["billing_period_end"] == "2024-10-31"
        assert result["due_date"] == "2024-12-01"
        assert result["total_amount_due"] == 127.43
        assert result["currency"] == "GBP"
        assert result["account_number"] == "acc-123"
        assert result["consumption_amount"] == 412.57
        assert result["consumption_unit"] == "kWh"


class TestNormaliseExtractionShouldAlwaysReturn12Keys:
    """Given any input (including empty dict), should return exactly 12 keys."""

    def test_empty_dict(self):
        result = normalise_extraction({})
        assert len(result) == 12
        assert all(v is None for v in result.values())

    def test_partial_dict(self):
        result = normalise_extraction({"provider_name": "Test"})
        assert len(result) == 12
        assert result["provider_name"] == "test"
        assert result["currency"] is None

    def test_all_none(self):
        raw = {field: None for field in FIELD_NORMALISERS}
        result = normalise_extraction(raw)
        assert len(result) == 12
        assert all(v is None for v in result.values())


class TestNormaliseExtractionSynonyms:
    """Given foreign-language synonyms, normalise_extraction should map them."""

    def test_italian_utility_type(self):
        result = normalise_extraction({"utility_type": "Luce"})
        assert result["utility_type"] == "electricity"

    def test_german_utility_type(self):
        result = normalise_extraction({"utility_type": "Strom"})
        assert result["utility_type"] == "electricity"

    def test_consumption_unit_mc(self):
        result = normalise_extraction({"consumption_unit": "mc"})
        assert result["consumption_unit"] == "m3"

    def test_consumption_unit_cubic_metres(self):
        result = normalise_extraction({"consumption_unit": "cubic metres"})
        assert result["consumption_unit"] == "m3"

    def test_currency_symbol(self):
        result = normalise_extraction({"currency": "€"})
        assert result["currency"] == "EUR"

    def test_extra_keys_ignored(self):
        """Keys not in the 12 schema fields should be silently ignored."""
        result = normalise_extraction({"provider_name": "X", "extra": "ignored"})
        assert "extra" not in result
        assert result["provider_name"] == "x"
