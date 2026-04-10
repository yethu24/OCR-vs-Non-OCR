"""TDD-style specification for src/dataset_loader.py.

Each test class specifies one behaviour of the DatasetLoader.
Tests are written as contracts: given a manifest with certain properties,
the loader should produce specific results or raise specific errors.
"""

import json

import pytest
from pathlib import Path

from src.dataset_loader import DatasetLoader, _is_truthy, REQUIRED_COLUMNS

HEADER = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status"


def _manifest(tmp_path: Path, rows: list[str]) -> Path:
    p = tmp_path / "manifest.csv"
    p.write_text("\n".join(rows), encoding="utf-8")
    return p


def _stub_files(bills: Path, gt: Path, ids: list[str]):
    bills.mkdir(exist_ok=True)
    gt.mkdir(exist_ok=True)
    for did in ids:
        (bills / f"{did}.pdf").write_bytes(b"%PDF-fake")
        (gt / f"{did}.json").write_text(
            json.dumps({"document_id": did, "fields": {"provider_name": "X"}}),
            encoding="utf-8",
        )


# =========================================================================
# Spec: _is_truthy helper
# =========================================================================


class TestIsTruthyShouldReturnTrue:
    """Given a string that means 'yes', _is_truthy should return True."""

    @pytest.mark.parametrize("val", ["true", "True", "TRUE", "1", "yes", "Yes", "YES"])
    def test_truthy_values(self, val):
        assert _is_truthy(val) is True

    def test_truthy_with_surrounding_whitespace(self):
        assert _is_truthy("  true  ") is True
        assert _is_truthy(" 1 ") is True


class TestIsTruthyShouldReturnFalse:
    """Given a string that does not mean 'yes', _is_truthy should return False."""

    @pytest.mark.parametrize("val", ["false", "False", "0", "no", "No", "", "maybe", "2"])
    def test_falsy_values(self, val):
        assert _is_truthy(val) is False


# =========================================================================
# Spec: load_and_validate should filter to runnable documents
# =========================================================================


@pytest.fixture
def valid_dataset(tmp_path):
    """A dataset with 4 rows: 2 runnable, 1 not verified, 1 excluded."""
    bills = tmp_path / "bills"
    gt = tmp_path / "gt"
    rows = [
        HEADER,
        "GB_elec_001,en,electricity,British Gas,true,2,true,true,active",
        "DE_gas_001,de,gas,E.ON,false,1,true,true,active",
        "FR_water_001,fr,water,Veolia,true,3,true,false,active",
        "IT_elec_001,it,electricity,Enel,true,1,true,true,excluded",
    ]
    m = _manifest(tmp_path, rows)
    _stub_files(bills, gt, ["GB_elec_001", "DE_gas_001"])
    return m, bills, gt


class TestLoadAndValidateShouldOnlyReturnRunnableDocuments:
    """Given a manifest with mixed statuses, load_and_validate should return
    only documents that are active, annotated, AND verified."""

    def test_returns_only_active_annotated_verified(self, valid_dataset):
        m, b, g = valid_dataset
        entries = DatasetLoader(m, b, g).load_and_validate()
        ids = {e.document_id for e in entries}
        assert ids == {"GB_elec_001", "DE_gas_001"}

    def test_excludes_unverified(self, valid_dataset):
        m, b, g = valid_dataset
        entries = DatasetLoader(m, b, g).load_and_validate()
        assert "FR_water_001" not in {e.document_id for e in entries}

    def test_excludes_excluded_status(self, valid_dataset):
        m, b, g = valid_dataset
        entries = DatasetLoader(m, b, g).load_and_validate()
        assert "IT_elec_001" not in {e.document_id for e in entries}


# =========================================================================
# Spec: DocumentEntry fields should be correctly populated
# =========================================================================


class TestDocumentEntryShouldHaveCorrectFields:
    """Given a valid manifest row, the resulting DocumentEntry should have
    all fields populated with correct types and values."""

    def test_string_fields(self, valid_dataset):
        m, b, g = valid_dataset
        entries = DatasetLoader(m, b, g).load_and_validate()
        gb = next(e for e in entries if e.document_id == "GB_elec_001")
        assert gb.language == "en"
        assert gb.utility_type == "electricity"
        assert gb.provider == "British Gas"

    def test_boolean_field(self, valid_dataset):
        m, b, g = valid_dataset
        entries = DatasetLoader(m, b, g).load_and_validate()
        gb = next(e for e in entries if e.document_id == "GB_elec_001")
        assert gb.digital_native is True
        de = next(e for e in entries if e.document_id == "DE_gas_001")
        assert de.digital_native is False

    def test_integer_field(self, valid_dataset):
        m, b, g = valid_dataset
        entries = DatasetLoader(m, b, g).load_and_validate()
        gb = next(e for e in entries if e.document_id == "GB_elec_001")
        assert gb.page_count == 2
        assert isinstance(gb.page_count, int)

    def test_path_fields(self, valid_dataset):
        m, b, g = valid_dataset
        entries = DatasetLoader(m, b, g).load_and_validate()
        gb = next(e for e in entries if e.document_id == "GB_elec_001")
        assert gb.pdf_path == b / "GB_elec_001.pdf"
        assert gb.ground_truth_path == g / "GB_elec_001.json"


# =========================================================================
# Spec: language and utility_type should be lowercased
# =========================================================================


class TestFieldsShouldBeLowercased:
    """Given a manifest with mixed-case language/utility_type, the loader
    should normalise them to lowercase."""

    def test_uppercase_language(self, tmp_path):
        bills, gt = tmp_path / "b", tmp_path / "g"
        m = _manifest(tmp_path, [HEADER, "d1,EN,electricity,T,true,1,true,true,active"])
        _stub_files(bills, gt, ["d1"])
        entries = DatasetLoader(m, bills, gt).load_and_validate()
        assert entries[0].language == "en"

    def test_mixed_case_utility_type(self, tmp_path):
        bills, gt = tmp_path / "b", tmp_path / "g"
        m = _manifest(tmp_path, [HEADER, "d1,en,Electricity,T,true,1,true,true,active"])
        _stub_files(bills, gt, ["d1"])
        entries = DatasetLoader(m, bills, gt).load_and_validate()
        assert entries[0].utility_type == "electricity"


# =========================================================================
# Spec: digital_native should accept various truthy representations
# =========================================================================


class TestDigitalNativeShouldParseTruthyValues:
    @pytest.mark.parametrize("val,expected", [
        ("true", True), ("True", True), ("1", True), ("yes", True),
        ("false", False), ("0", False), ("no", False),
    ])
    def test_digital_native_variants(self, tmp_path, val, expected):
        bills, gt = tmp_path / "b", tmp_path / "g"
        m = _manifest(tmp_path, [HEADER, f"d1,en,electricity,T,{val},1,true,true,active"])
        _stub_files(bills, gt, ["d1"])
        entries = DatasetLoader(m, bills, gt).load_and_validate()
        assert entries[0].digital_native is expected


# =========================================================================
# Spec: missing manifest should raise FileNotFoundError
# =========================================================================


class TestMissingManifestShouldRaise:
    def test_load_and_validate(self, tmp_path):
        loader = DatasetLoader(tmp_path / "missing.csv", tmp_path, tmp_path)
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            loader.load_and_validate()

    def test_load_all(self, tmp_path):
        loader = DatasetLoader(tmp_path / "missing.csv", tmp_path, tmp_path)
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            loader.load_all()


# =========================================================================
# Spec: empty manifest should raise ValueError
# =========================================================================


class TestEmptyManifestShouldRaise:
    def test_completely_empty(self, tmp_path):
        m = tmp_path / "empty.csv"
        m.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="empty"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()

    def test_header_only_no_data(self, tmp_path):
        m = _manifest(tmp_path, [HEADER])
        with pytest.raises(ValueError):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()


# =========================================================================
# Spec: missing columns should raise ValueError listing the missing ones
# =========================================================================


class TestMissingColumnsShouldRaise:
    def test_partial_columns(self, tmp_path):
        m = tmp_path / "bad.csv"
        m.write_text("document_id,language\nfoo,en\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing required columns"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()

    def test_error_lists_missing_column_names(self, tmp_path):
        m = tmp_path / "bad.csv"
        m.write_text("document_id,language,utility_type\nfoo,en,gas\n", encoding="utf-8")
        with pytest.raises(ValueError) as exc_info:
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()
        msg = str(exc_info.value)
        assert "status" in msg
        assert "annotated" in msg


# =========================================================================
# Spec: duplicate document_ids should raise ValueError
# =========================================================================


class TestDuplicateIdsShouldRaise:
    def test_raises_with_document_id(self, tmp_path):
        rows = [
            HEADER,
            "doc_001,en,electricity,T,true,1,true,true,active",
            "doc_001,de,gas,T2,false,2,true,true,active",
        ]
        m = _manifest(tmp_path, rows)
        with pytest.raises(ValueError, match="Duplicate document_id.*doc_001"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()

    def test_reports_row_numbers(self, tmp_path):
        rows = [
            HEADER,
            "d1,en,electricity,T,true,1,true,true,active",
            "d1,de,gas,T,false,1,true,true,active",
        ]
        m = _manifest(tmp_path, rows)
        with pytest.raises(ValueError, match="rows 2 and 3"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()


# =========================================================================
# Spec: invalid field values should raise ValueError
# =========================================================================


class TestInvalidValuesShouldRaise:
    def test_invalid_language(self, tmp_path):
        m = _manifest(tmp_path, [HEADER, "d1,xx,electricity,T,true,1,true,true,active"])
        with pytest.raises(ValueError, match="invalid language"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()

    def test_invalid_utility_type(self, tmp_path):
        m = _manifest(tmp_path, [HEADER, "d1,en,steam,T,true,1,true,true,active"])
        with pytest.raises(ValueError, match="invalid utility_type"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()

    def test_invalid_status(self, tmp_path):
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,T,true,1,true,true,maybe"])
        with pytest.raises(ValueError, match="invalid status"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()

    def test_non_integer_page_count(self, tmp_path):
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,T,true,abc,true,true,active"])
        with pytest.raises(ValueError, match="page_count"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()

    def test_multiple_errors_collected_in_one_raise(self, tmp_path):
        """Given a row with several bad values, all errors should be reported at once."""
        m = _manifest(tmp_path, [HEADER, "d1,zz,steam,T,true,abc,true,true,nope"])
        with pytest.raises(ValueError) as exc_info:
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()
        msg = str(exc_info.value)
        assert "language" in msg
        assert "utility_type" in msg
        assert "status" in msg
        assert "page_count" in msg


# =========================================================================
# Spec: missing PDF or ground truth should raise FileNotFoundError
# =========================================================================


class TestMissingFilesShouldRaise:
    def test_missing_pdf(self, tmp_path):
        bills, gt = tmp_path / "b", tmp_path / "g"
        bills.mkdir(); gt.mkdir()
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,T,true,1,true,true,active"])
        (gt / "d1.json").write_text("{}", encoding="utf-8")
        with pytest.raises(FileNotFoundError, match="PDF missing"):
            DatasetLoader(m, bills, gt).load_and_validate()

    def test_missing_ground_truth(self, tmp_path):
        bills, gt = tmp_path / "b", tmp_path / "g"
        bills.mkdir(); gt.mkdir()
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,T,true,1,true,true,active"])
        (bills / "d1.pdf").write_bytes(b"%PDF")
        with pytest.raises(FileNotFoundError, match="Ground truth missing"):
            DatasetLoader(m, bills, gt).load_and_validate()

    def test_both_missing_reports_both(self, tmp_path):
        bills, gt = tmp_path / "b", tmp_path / "g"
        bills.mkdir(); gt.mkdir()
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,T,true,1,true,true,active"])
        with pytest.raises(FileNotFoundError) as exc_info:
            DatasetLoader(m, bills, gt).load_and_validate()
        msg = str(exc_info.value)
        assert "PDF missing" in msg
        assert "Ground truth missing" in msg


# =========================================================================
# Spec: no runnable documents should raise ValueError
# =========================================================================


class TestNoRunnableShouldRaise:
    def test_all_excluded(self, tmp_path):
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,T,true,1,true,true,excluded"])
        with pytest.raises(ValueError, match="No runnable documents"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()

    def test_none_verified(self, tmp_path):
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,T,true,1,true,false,active"])
        with pytest.raises(ValueError, match="No runnable documents"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()

    def test_none_annotated(self, tmp_path):
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,T,true,1,false,true,active"])
        with pytest.raises(ValueError, match="No runnable documents"):
            DatasetLoader(m, tmp_path, tmp_path).load_and_validate()


# =========================================================================
# Spec: load_all should return all rows without filtering or file checks
# =========================================================================


class TestLoadAllShouldReturnEverything:
    def test_returns_all_regardless_of_status(self, tmp_path):
        rows = [
            HEADER,
            "d1,en,electricity,T,true,1,true,true,active",
            "d2,de,gas,T,false,2,true,true,excluded",
            "d3,fr,water,T,true,3,false,false,active",
        ]
        m = _manifest(tmp_path, rows)
        entries = DatasetLoader(m, tmp_path, tmp_path).load_all()
        assert len(entries) == 3

    def test_does_not_check_file_existence(self, tmp_path):
        """load_all should succeed even when no PDF/GT files exist on disk."""
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,T,true,1,true,true,active"])
        entries = DatasetLoader(m, tmp_path, tmp_path).load_all()
        assert len(entries) == 1

    def test_still_validates_columns(self, tmp_path):
        m = tmp_path / "bad.csv"
        m.write_text("document_id,language\nfoo,en\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing required columns"):
            DatasetLoader(m, tmp_path, tmp_path).load_all()

    def test_still_checks_duplicate_ids(self, tmp_path):
        rows = [
            HEADER,
            "d1,en,electricity,T,true,1,true,true,active",
            "d1,de,gas,T,false,2,true,true,active",
        ]
        m = _manifest(tmp_path, rows)
        with pytest.raises(ValueError, match="Duplicate"):
            DatasetLoader(m, tmp_path, tmp_path).load_all()


# =========================================================================
# Spec: whitespace in manifest fields should be stripped
# =========================================================================


class TestWhitespaceHandling:
    def test_strips_document_id(self, tmp_path):
        bills, gt = tmp_path / "b", tmp_path / "g"
        m = _manifest(tmp_path, [HEADER, "  d1  ,en,electricity,T,true,1,true,true,active"])
        _stub_files(bills, gt, ["d1"])
        entries = DatasetLoader(m, bills, gt).load_and_validate()
        assert entries[0].document_id == "d1"

    def test_strips_provider_name(self, tmp_path):
        bills, gt = tmp_path / "b", tmp_path / "g"
        m = _manifest(tmp_path, [HEADER, "d1,en,electricity,  Test Co  ,true,1,true,true,active"])
        _stub_files(bills, gt, ["d1"])
        entries = DatasetLoader(m, bills, gt).load_and_validate()
        assert entries[0].provider == "Test Co"
