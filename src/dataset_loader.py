from __future__ import annotations

import csv
import logging
from pathlib import Path

from .schema import DocumentEntry

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = frozenset(
    {
        "document_id",
        "language",
        "utility_type",
        "provider",
        "digital_native",
        "page_count",
        "annotated",
        "verified",
        "status",
    }
)

VALID_LANGUAGES = {"en", "de", "fr", "it"}
VALID_UTILITY_TYPES = {"electricity", "gas", "water"}
VALID_STATUSES = {"active", "excluded"}


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes")


class DatasetLoader:
    """Loads, validates, filters, and resolves the dataset manifest CSV."""

    def __init__(
        self,
        manifest_path: str | Path,
        bills_dir: str | Path,
        ground_truth_dir: str | Path,
    ):
        self.manifest_path = Path(manifest_path)
        self.bills_dir = Path(bills_dir)
        self.ground_truth_dir = Path(ground_truth_dir)

    def load_and_validate(self) -> list[DocumentEntry]:
        """Load manifest, validate columns, filter to runnable documents,
        resolve file paths, and verify files exist on disk."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")

        rows = self._read_csv()
        self._validate_columns(rows)
        self._check_duplicate_ids(rows)
        self._validate_values(rows)
        filtered = self._filter_runnable(rows)

        if not filtered:
            raise ValueError(
                "No runnable documents in manifest "
                "(need status=active, annotated=true, verified=true)"
            )

        entries = self._resolve_paths(filtered)
        self._verify_files_exist(entries)
        logger.info(
            "Manifest loaded: %d total rows, %d runnable documents",
            len(rows),
            len(entries),
        )
        return entries

    def load_all(self) -> list[DocumentEntry]:
        """Load all documents regardless of status/annotated/verified flags.
        Still validates columns and checks for duplicates.
        Skips file-existence checks (useful for manifest inspection)."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")

        rows = self._read_csv()
        self._validate_columns(rows)
        self._check_duplicate_ids(rows)
        return self._resolve_paths(rows)

    # -- internal helpers --------------------------------------------------

    def _read_csv(self) -> list[dict[str, str]]:
        with open(self.manifest_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            raise ValueError(f"Manifest is empty: {self.manifest_path}")
        return rows

    def _validate_columns(self, rows: list[dict[str, str]]) -> None:
        actual = set(rows[0].keys())
        missing = REQUIRED_COLUMNS - actual
        if missing:
            raise ValueError(f"Manifest missing required columns: {sorted(missing)}")

    def _check_duplicate_ids(self, rows: list[dict[str, str]]) -> None:
        seen: dict[str, int] = {}
        for i, row in enumerate(rows, start=2):  # row 1 is header
            doc_id = row["document_id"].strip()
            if doc_id in seen:
                raise ValueError(
                    f"Duplicate document_id '{doc_id}' at rows {seen[doc_id]} and {i}"
                )
            seen[doc_id] = i

    def _validate_values(self, rows: list[dict[str, str]]) -> None:
        errors: list[str] = []
        for i, row in enumerate(rows, start=2):
            doc_id = row["document_id"].strip()
            lang = row["language"].strip().lower()
            utype = row["utility_type"].strip().lower()
            status = row["status"].strip().lower()

            if lang not in VALID_LANGUAGES:
                errors.append(f"Row {i} ({doc_id}): invalid language '{lang}'")
            if utype not in VALID_UTILITY_TYPES:
                errors.append(f"Row {i} ({doc_id}): invalid utility_type '{utype}'")
            if status not in VALID_STATUSES:
                errors.append(f"Row {i} ({doc_id}): invalid status '{status}'")
            try:
                int(row["page_count"].strip())
            except ValueError:
                errors.append(
                    f"Row {i} ({doc_id}): page_count '{row['page_count']}' is not an integer"
                )

        if errors:
            raise ValueError(
                "Manifest validation errors:\n" + "\n".join(errors)
            )

    def _filter_runnable(self, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        return [
            r
            for r in rows
            if r["status"].strip().lower() == "active"
            and _is_truthy(r["annotated"])
            and _is_truthy(r["verified"])
        ]

    def _resolve_paths(self, rows: list[dict[str, str]]) -> list[DocumentEntry]:
        entries: list[DocumentEntry] = []
        for r in rows:
            doc_id = r["document_id"].strip()
            entries.append(
                DocumentEntry(
                    document_id=doc_id,
                    language=r["language"].strip().lower(),
                    utility_type=r["utility_type"].strip().lower(),
                    provider=r["provider"].strip(),
                    digital_native=_is_truthy(r.get("digital_native", "false")),
                    page_count=int(r["page_count"].strip()),
                    pdf_path=self.bills_dir / f"{doc_id}.pdf",
                    ground_truth_path=self.ground_truth_dir / f"{doc_id}.json",
                )
            )
        return entries

    def _verify_files_exist(self, entries: list[DocumentEntry]) -> None:
        missing: list[str] = []
        for e in entries:
            if not e.pdf_path.exists():
                missing.append(f"  PDF missing: {e.pdf_path}")
            if not e.ground_truth_path.exists():
                missing.append(f"  Ground truth missing: {e.ground_truth_path}")
        if missing:
            raise FileNotFoundError(
                "Missing files for active+annotated+verified documents:\n"
                + "\n".join(missing)
            )
