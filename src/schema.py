from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import ClassVar, Optional

from pydantic import BaseModel, Field


# Pydantic model used as the single source of truth for the 12 fields
# extracted from every utility bill.  Both LLM providers and ground-truth
# files conform to this schema.
class BillExtraction(BaseModel):
    """Canonical 12-field schema for utility bill extraction."""

    # All fields are Optional because a bill may not contain every piece of data
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

    # Canonical field list used by evaluation, normalisation, and reporting
    # to iterate fields in a consistent order
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
        """Human-readable schema description injected into the LLM prompt
        via the {schema_description} placeholder."""
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


# Container returned by the pipeline for each processed document.
# Bundles the extracted fields with timing, token usage, and debug info.
class PipelineResult(BaseModel):
    """Complete result from processing a single document through a pipeline."""

    document_id: str
    extraction: BillExtraction       # the 12-field output
    raw_llm_output: str = ""         # verbatim LLM response (for debugging)
    ocr_text: Optional[str] = None   # Tesseract output (None in vision mode)
    timings: dict = Field(default_factory=dict)
    token_usage: dict = Field(default_factory=dict)
    model_id: str = ""
    pipeline_mode: str = ""          # "ocr_text" or "vision"


# Resolved row from dataset_manifest.csv — contains file paths and metadata
# for a single utility bill in the dataset.
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
