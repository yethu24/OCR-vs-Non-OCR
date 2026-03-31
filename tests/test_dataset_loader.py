import json
import pytest
from pathlib import Path

from src.dataset_loader import DatasetLoader


@pytest.fixture
def tmp_dataset(tmp_path):
    """Create a minimal valid dataset with manifest, PDFs, and ground truth."""
    bills_dir = tmp_path / "bills"
    gt_dir = tmp_path / "ground_truth"
    bills_dir.mkdir()
    gt_dir.mkdir()

    manifest_path = tmp_path / "manifest.csv"
    rows = [
        "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status",
        "GB_elec_001,en,electricity,British Gas,true,2,true,true,active",
        "DE_gas_001,de,gas,E.ON,false,1,true,true,active",
        "FR_water_001,fr,water,Veolia,true,3,true,false,active",
        "IT_elec_001,it,electricity,Enel,true,1,true,true,excluded",
    ]
    manifest_path.write_text("\n".join(rows), encoding="utf-8")

    for doc_id in ["GB_elec_001", "DE_gas_001"]:
        (bills_dir / f"{doc_id}.pdf").write_bytes(b"%PDF-fake")
        gt = {"document_id": doc_id, "fields": {"provider_name": "Test"}}
        (gt_dir / f"{doc_id}.json").write_text(json.dumps(gt), encoding="utf-8")

    return manifest_path, bills_dir, gt_dir


class TestDatasetLoaderHappyPath:
    def test_load_filters_to_active_annotated_verified(self, tmp_dataset):
        manifest_path, bills_dir, gt_dir = tmp_dataset
        loader = DatasetLoader(manifest_path, bills_dir, gt_dir)
        entries = loader.load_and_validate()

        ids = [e.document_id for e in entries]
        assert "GB_elec_001" in ids
        assert "DE_gas_001" in ids
        # FR is not verified, IT is excluded
        assert "FR_water_001" not in ids
        assert "IT_elec_001" not in ids

    def test_entry_fields_populated(self, tmp_dataset):
        manifest_path, bills_dir, gt_dir = tmp_dataset
        loader = DatasetLoader(manifest_path, bills_dir, gt_dir)
        entries = loader.load_and_validate()

        gb = next(e for e in entries if e.document_id == "GB_elec_001")
        assert gb.language == "en"
        assert gb.utility_type == "electricity"
        assert gb.provider == "British Gas"
        assert gb.digital_native is True
        assert gb.page_count == 2
        assert gb.pdf_path == bills_dir / "GB_elec_001.pdf"
        assert gb.ground_truth_path == gt_dir / "GB_elec_001.json"

    def test_language_lowercased(self, tmp_dataset):
        manifest_path, bills_dir, gt_dir = tmp_dataset
        loader = DatasetLoader(manifest_path, bills_dir, gt_dir)
        entries = loader.load_and_validate()
        for e in entries:
            assert e.language == e.language.lower()


class TestDatasetLoaderValidation:
    def test_missing_manifest_raises(self, tmp_path):
        loader = DatasetLoader(
            tmp_path / "nonexistent.csv",
            tmp_path / "bills",
            tmp_path / "gt",
        )
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            loader.load_and_validate()

    def test_empty_manifest_raises(self, tmp_path):
        manifest = tmp_path / "empty.csv"
        manifest.write_text("", encoding="utf-8")
        loader = DatasetLoader(manifest, tmp_path, tmp_path)
        with pytest.raises(ValueError, match="empty"):
            loader.load_and_validate()

    def test_missing_columns_raises(self, tmp_path):
        manifest = tmp_path / "bad.csv"
        manifest.write_text("document_id,language\nfoo,en\n", encoding="utf-8")
        loader = DatasetLoader(manifest, tmp_path, tmp_path)
        with pytest.raises(ValueError, match="missing required columns"):
            loader.load_and_validate()

    def test_duplicate_ids_raises(self, tmp_path):
        manifest = tmp_path / "dupes.csv"
        header = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status"
        rows = [
            header,
            "doc_001,en,electricity,Test,true,1,true,true,active",
            "doc_001,de,gas,Test2,false,2,true,true,active",
        ]
        manifest.write_text("\n".join(rows), encoding="utf-8")
        loader = DatasetLoader(manifest, tmp_path, tmp_path)
        with pytest.raises(ValueError, match="Duplicate document_id"):
            loader.load_and_validate()

    def test_invalid_language_raises(self, tmp_path):
        manifest = tmp_path / "bad_lang.csv"
        header = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status"
        rows = [header, "doc_001,xx,electricity,Test,true,1,true,true,active"]
        manifest.write_text("\n".join(rows), encoding="utf-8")
        loader = DatasetLoader(manifest, tmp_path, tmp_path)
        with pytest.raises(ValueError, match="invalid language"):
            loader.load_and_validate()

    def test_invalid_utility_type_raises(self, tmp_path):
        manifest = tmp_path / "bad_type.csv"
        header = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status"
        rows = [header, "doc_001,en,steam,Test,true,1,true,true,active"]
        manifest.write_text("\n".join(rows), encoding="utf-8")
        loader = DatasetLoader(manifest, tmp_path, tmp_path)
        with pytest.raises(ValueError, match="invalid utility_type"):
            loader.load_and_validate()

    def test_invalid_status_raises(self, tmp_path):
        manifest = tmp_path / "bad_status.csv"
        header = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status"
        rows = [header, "doc_001,en,electricity,Test,true,1,true,true,maybe"]
        manifest.write_text("\n".join(rows), encoding="utf-8")
        loader = DatasetLoader(manifest, tmp_path, tmp_path)
        with pytest.raises(ValueError, match="invalid status"):
            loader.load_and_validate()


class TestDatasetLoaderFileMissing:
    def test_missing_pdf_raises(self, tmp_path):
        bills_dir = tmp_path / "bills"
        gt_dir = tmp_path / "gt"
        bills_dir.mkdir()
        gt_dir.mkdir()

        manifest = tmp_path / "manifest.csv"
        header = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status"
        rows = [header, "doc_001,en,electricity,Test,true,1,true,true,active"]
        manifest.write_text("\n".join(rows), encoding="utf-8")

        (gt_dir / "doc_001.json").write_text("{}", encoding="utf-8")
        # Deliberately do NOT create the PDF

        loader = DatasetLoader(manifest, bills_dir, gt_dir)
        with pytest.raises(FileNotFoundError, match="PDF missing"):
            loader.load_and_validate()

    def test_missing_ground_truth_raises(self, tmp_path):
        bills_dir = tmp_path / "bills"
        gt_dir = tmp_path / "gt"
        bills_dir.mkdir()
        gt_dir.mkdir()

        manifest = tmp_path / "manifest.csv"
        header = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status"
        rows = [header, "doc_001,en,electricity,Test,true,1,true,true,active"]
        manifest.write_text("\n".join(rows), encoding="utf-8")

        (bills_dir / "doc_001.pdf").write_bytes(b"%PDF-fake")
        # Deliberately do NOT create the ground truth

        loader = DatasetLoader(manifest, bills_dir, gt_dir)
        with pytest.raises(FileNotFoundError, match="Ground truth missing"):
            loader.load_and_validate()


class TestDatasetLoaderNoRunnable:
    def test_all_excluded_raises(self, tmp_path):
        manifest = tmp_path / "manifest.csv"
        header = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status"
        rows = [header, "doc_001,en,electricity,Test,true,1,true,true,excluded"]
        manifest.write_text("\n".join(rows), encoding="utf-8")

        loader = DatasetLoader(manifest, tmp_path, tmp_path)
        with pytest.raises(ValueError, match="No runnable documents"):
            loader.load_and_validate()

    def test_none_verified_raises(self, tmp_path):
        manifest = tmp_path / "manifest.csv"
        header = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status"
        rows = [header, "doc_001,en,electricity,Test,true,1,true,false,active"]
        manifest.write_text("\n".join(rows), encoding="utf-8")

        loader = DatasetLoader(manifest, tmp_path, tmp_path)
        with pytest.raises(ValueError, match="No runnable documents"):
            loader.load_and_validate()
