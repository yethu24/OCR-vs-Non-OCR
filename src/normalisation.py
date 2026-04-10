"""Normalisation functions applied identically to pipeline outputs and ground truth.

Rules:
    - Dates   -> ISO 8601 (YYYY-MM-DD); unparseable strings kept as-is
    - Currency -> symbol/name map to ISO 4217; else valid 3-letter codes; else None
    - utility_type / consumption_unit -> synonym maps to canonical values; unknown -> string rules
    - Other strings -> NFC Unicode, stripped, lowercased, whitespace-collapsed
    - Floats   -> EU/US decimal parsing for strings, rounded to 2 decimal places
"""

from __future__ import annotations

import logging
import re
import unicodedata
from datetime import date, datetime
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# Candidate date formats tried in order by normalise_date();
# the first successful parse wins
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d.%m.%Y",
    "%d-%m-%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
    "%Y/%m/%d",
]

# Synonym maps: multilingual aliases → canonical English value.
# Covers EN, DE, FR, IT variants for the 4 supported languages.
_UTILITY_TYPE_MAP: dict[str, str] = {
    "electric": "electricity",
    "electricity": "electricity",
    "elettricità": "electricity",
    "elettrico": "electricity",
    "luce": "electricity",
    "energia elettrica": "electricity",
    "strom": "electricity",
    "electricité": "electricity",
    "electricite": "electricity",
    "power": "electricity",
    "gas": "gas",
    "gaz": "gas",
    "erdgas": "gas",
    "metano": "gas",
    "water": "water",
    "acqua": "water",
    "wasser": "water",
    "eau": "water",
    "agua": "water",
}

# Currency symbols and common names → ISO 4217 three-letter codes
_CURRENCY_MAP: dict[str, str] = {
    "€": "EUR",
    "euro": "EUR",
    "euros": "EUR",
    "eur": "EUR",
    "£": "GBP",
    "pound": "GBP",
    "pounds": "GBP",
    "sterling": "GBP",
    "gbp": "GBP",
    "$": "USD",
    "dollar": "USD",
    "dollars": "USD",
    "usd": "USD",
    "chf": "CHF",
    "franc": "CHF",
    "francs": "CHF",
}

# Consumption unit aliases → canonical spelling (e.g. "kilowatt hour" → "kWh")
_CONSUMPTION_UNIT_MAP: dict[str, str] = {
    "kwh": "kWh",
    "kw/h": "kWh",
    "kilowatt hour": "kWh",
    "kilowatt-hour": "kWh",
    "mwh": "MWh",
    "megawatt hour": "MWh",
    "gj": "GJ",
    "gigajoule": "GJ",
    "smc": "SMC",
    "sm3": "SMC",
    "standard cubic metre": "SMC",
    "standard cubic meter": "SMC",
    "m3": "m3",
    "m³": "m3",
    "m^3": "m3",
    "mc": "m3",
    "cubic metre": "m3",
    "cubic meter": "m3",
    "cubic metres": "m3",
    "cubic meters": "m3",
    "l": "L",
    "litre": "L",
    "liter": "L",
    "litres": "L",
    "gal": "gal",
    "gallon": "gal",
    "gallons": "gal",
}


def normalise_date(value: Optional[str | date]) -> Optional[str]:
    """Parse flexible date representations into YYYY-MM-DD, or return unparseable string."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return value


def normalise_string(value: Optional[str]) -> Optional[str]:
    """NFC Unicode, strip, lowercase, collapse internal whitespace."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = unicodedata.normalize("NFC", value)
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value if value else None


def normalise_utility_type(value: Optional[str]) -> Optional[str]:
    """Map synonyms to electricity | gas | water; otherwise same rules as strings."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    raw = unicodedata.normalize("NFC", value).strip()
    if not raw:
        return None
    mapped = _UTILITY_TYPE_MAP.get(raw.lower())
    if mapped is not None:
        return mapped
    return normalise_string(raw)


def normalise_currency(value: Optional[str]) -> Optional[str]:
    """Map symbols and names to ISO 4217; accept 3-letter codes; unknown -> None."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = unicodedata.normalize("NFC", value).strip()
    if not value:
        return None
    mapped = _CURRENCY_MAP.get(value.lower())
    if mapped is None and value in _CURRENCY_MAP:
        mapped = _CURRENCY_MAP[value]
    if mapped is not None:
        return mapped
    upper = value.upper()
    if re.fullmatch(r"[A-Z]{3}", upper):
        return upper
    logger.warning("normalise_currency: could not map %r — returning None", value)
    return None


def normalise_consumption_unit(value: Optional[str]) -> Optional[str]:
    """Map unit synonyms to canonical spelling; unknown units -> string normalisation."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    raw = unicodedata.normalize("NFC", value).strip()
    if not raw:
        return None
    key = raw.lower()
    mapped = _CONSUMPTION_UNIT_MAP.get(key)
    if mapped is not None:
        return mapped
    if raw in _CONSUMPTION_UNIT_MAP:
        return _CONSUMPTION_UNIT_MAP[raw]
    return normalise_string(raw)


def _parse_numeric_string(s: str) -> float:
    """Parse a numeric string with European or US thousands/decimal separators."""
    s = s.strip()
    if not s:
        raise ValueError("empty")
    # Determine separator roles by position:
    #   "1.234,56" → EU (dot=thousands, comma=decimal)
    #   "1,234.56" → US (comma=thousands, dot=decimal)
    #   "1234,56"  → EU with no thousands separator
    dot_pos = s.find(".")
    comma_pos = s.find(",")
    if dot_pos != -1 and comma_pos != -1:
        if dot_pos < comma_pos:
            # EU: 1.234,56 → remove dots, replace comma with dot
            s = s.replace(".", "").replace(",", ".")
        else:
            # US: 1,234.56 → remove commas
            s = s.replace(",", "")
    elif comma_pos != -1:
        # Comma only → treat as decimal separator (EU style)
        s = s.replace(",", ".")
    return float(s)


def normalise_float(value: Optional[float | str | int]) -> Optional[float]:
    """Parse number (EU/US string rules) and round to 2 decimal places."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, float):
        return round(value, 2)
    if isinstance(value, int):
        return round(float(value), 2)
    if isinstance(value, str):
        try:
            return round(_parse_numeric_string(value), 2)
        except (ValueError, TypeError):
            return None
    try:
        return round(float(value), 2)
    except (ValueError, TypeError):
        return None


# Maps each schema field to its normaliser function.
# Used by normalise_extraction() to apply the right transform per field.
FIELD_NORMALISERS: dict[str, Callable[[Any], Any]] = {
    "provider_name": normalise_string,
    "utility_type": normalise_utility_type,
    "bill_number": normalise_string,
    "bill_date": normalise_date,
    "billing_period_start": normalise_date,
    "billing_period_end": normalise_date,
    "due_date": normalise_date,
    "total_amount_due": normalise_float,
    "currency": normalise_currency,
    "account_number": normalise_string,
    "consumption_amount": normalise_float,
    "consumption_unit": normalise_consumption_unit,
}


def normalise_extraction(fields: dict) -> dict:
    """Apply the appropriate normaliser to every canonical field.

    Called on both predictions and ground truth before comparison
    so that format differences (e.g. "€" vs "EUR") don't count as errors.
    """
    result = {}
    for field_name, normaliser in FIELD_NORMALISERS.items():
        result[field_name] = normaliser(fields.get(field_name))
    return result
