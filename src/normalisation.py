"""Normalisation functions applied identically to pipeline outputs and ground truth.

Rules:
    - Dates   -> ISO 8601 (YYYY-MM-DD)
    - Currency -> uppercase ISO 4217
    - Strings  -> stripped, lowercased, whitespace-collapsed
    - Floats   -> rounded to 2 decimal places
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

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


def normalise_date(value: Optional[str | date]) -> Optional[str]:
    """Parse flexible date representations into YYYY-MM-DD, or return None."""
    if value is None:
        return None
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
    """Strip, lowercase, and collapse internal whitespace."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value if value else None


def normalise_currency(value: Optional[str]) -> Optional[str]:
    """Uppercase and strip whitespace to produce an ISO 4217 code."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip().upper()
    return value if value else None


def normalise_float(value: Optional[float | str | int]) -> Optional[float]:
    """Cast to float and round to 2 decimal places."""
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (ValueError, TypeError):
        return None


FIELD_NORMALISERS: dict[str, callable] = {
    "provider_name": normalise_string,
    "utility_type": normalise_string,
    "bill_number": normalise_string,
    "bill_date": normalise_date,
    "billing_period_start": normalise_date,
    "billing_period_end": normalise_date,
    "due_date": normalise_date,
    "total_amount_due": normalise_float,
    "currency": normalise_currency,
    "account_number": normalise_string,
    "consumption_amount": normalise_float,
    "consumption_unit": normalise_string,
}


def normalise_extraction(fields: dict) -> dict:
    """Apply the appropriate normaliser to every canonical field."""
    result = {}
    for field_name, normaliser in FIELD_NORMALISERS.items():
        result[field_name] = normaliser(fields.get(field_name))
    return result
