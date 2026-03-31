from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import ClassVar, Optional

from pydantic import BaseModel, Field


class BillExtraction(BaseModel):
    """Canonical 12-field schema for utility bill extraction."""

    provider_name: Optional[str] = None
    utility_type: Optional[str] = None
    bill_number: Optional[str] = None
    bill_date: Optional[date] = None
    billing_period_start: Optional[date] = None
    billing_period_end: Optional[date] = None
    due_date: Optional[date] = None
    total_amount_due: Optional[float] = None
    currency: Optional[str] = None
    account_number: Optional[str] = None
    consumption_amount: Optional[float] = None
    consumption_unit: Optional[str] = None

    SCHEMA_FIELDS: ClassVar[list[str]] = [
        "provider_name",
        "utility_type",
        "bill_number",
        "bill_date",
        "billing_period_start",
        "billing_period_end",
        "due_date",
        "total_amount_due",
        "currency",
        "account_number",
        "consumption_amount",
        "consumption_unit",
    ]

    model_config = {"json_schema_extra": {"title": "Utility Bill Extraction"}}

    @classmethod
    def schema_description(cls) -> str:
        """Human-readable schema description for use in LLM prompts."""
        lines = [
            "provider_name (string): Utility company name",
            "utility_type (string): electricity / gas / water",
            "bill_number (string): Invoice or bill reference number",
            "bill_date (date, YYYY-MM-DD): Date the bill was issued",
            "billing_period_start (date, YYYY-MM-DD): Start of billing period",
            "billing_period_end (date, YYYY-MM-DD): End of billing period",
            "due_date (date, YYYY-MM-DD): Payment due date",
            "total_amount_due (float): Total amount to pay",
            "currency (string): ISO 4217 currency code (e.g. GBP, EUR)",
            "account_number (string): Customer account reference",
            "consumption_amount (float): Usage quantity",
            "consumption_unit (string): Unit of consumption (kWh, m³, litres, etc.)",
        ]
        return "\n".join(f"- {line}" for line in lines)


class PipelineResult(BaseModel):
    """Complete result from processing a single document through a pipeline."""

    document_id: str
    extraction: BillExtraction
    raw_llm_output: str = ""
    ocr_text: Optional[str] = None
    timings: dict = Field(default_factory=dict)
    token_usage: dict = Field(default_factory=dict)
    model_id: str = ""
    pipeline_mode: str = ""  # "ocr_text" or "vision"


@dataclass
class DocumentEntry:
    """A single document record resolved from the dataset manifest."""

    document_id: str
    language: str
    utility_type: str
    provider: str
    digital_native: bool
    page_count: int
    pdf_path: Path
    ground_truth_path: Path
