"""TDD-style specification for src/ocr/ — OCREngine ABC and TesseractOCR.

Unit tests mock pytesseract so they run without Tesseract installed.
"""

from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

from src.ocr.base import OCREngine
from src.ocr.tesseract import TesseractOCR, LANGUAGE_MAP


# =========================================================================
# Spec: OCREngine ABC
# =========================================================================


class TestOCREngineShouldBeAbstract:
    """OCREngine is an abstract base class — it cannot be instantiated directly."""

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            OCREngine()

    def test_requires_extract_text(self):
        """A subclass that does not implement extract_text should not instantiate."""

        class IncompleteOCR(OCREngine):
            pass

        with pytest.raises(TypeError):
            IncompleteOCR()

    def test_concrete_subclass_instantiates(self):
        """A subclass that implements extract_text should instantiate."""

        class ConcreteOCR(OCREngine):
            def extract_text(self, image, language="eng"):
                return "text"

        engine = ConcreteOCR()
        assert engine.extract_text(None) == "text"


# =========================================================================
# Spec: LANGUAGE_MAP
# =========================================================================


class TestLanguageMapShouldMapISO639ToTesseract:
    """LANGUAGE_MAP should map 2-letter ISO codes to 3-letter Tesseract codes."""

    def test_english(self):
        assert LANGUAGE_MAP["en"] == "eng"

    def test_german(self):
        assert LANGUAGE_MAP["de"] == "deu"

    def test_french(self):
        assert LANGUAGE_MAP["fr"] == "fra"

    def test_italian(self):
        assert LANGUAGE_MAP["it"] == "ita"

    def test_has_four_entries(self):
        assert len(LANGUAGE_MAP) == 4


# =========================================================================
# Spec: TesseractOCR.extract_text
# =========================================================================


class TestTesseractOCRShouldMapLanguageCodes:
    """Given an ISO 639-1 language code, TesseractOCR should convert it
    to a Tesseract code before calling pytesseract."""

    @patch("src.ocr.tesseract.pytesseract")
    def test_maps_en_to_eng(self, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "text"
        engine = TesseractOCR()
        img = Image.new("RGB", (10, 10))
        engine.extract_text(img, language="en")
        mock_pytesseract.image_to_string.assert_called_once_with(img, lang="eng")

    @patch("src.ocr.tesseract.pytesseract")
    def test_maps_de_to_deu(self, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "text"
        engine = TesseractOCR()
        img = Image.new("RGB", (10, 10))
        engine.extract_text(img, language="de")
        mock_pytesseract.image_to_string.assert_called_once_with(img, lang="deu")

    @patch("src.ocr.tesseract.pytesseract")
    def test_maps_fr_to_fra(self, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "text"
        engine = TesseractOCR()
        img = Image.new("RGB", (10, 10))
        engine.extract_text(img, language="fr")
        mock_pytesseract.image_to_string.assert_called_once_with(img, lang="fra")

    @patch("src.ocr.tesseract.pytesseract")
    def test_maps_it_to_ita(self, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "text"
        engine = TesseractOCR()
        img = Image.new("RGB", (10, 10))
        engine.extract_text(img, language="it")
        mock_pytesseract.image_to_string.assert_called_once_with(img, lang="ita")


class TestTesseractOCRShouldPassThroughUnknownCodes:
    """Given a code not in LANGUAGE_MAP (e.g. native Tesseract 3-letter),
    TesseractOCR should pass it through unchanged."""

    @patch("src.ocr.tesseract.pytesseract")
    def test_passthrough_eng(self, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "text"
        engine = TesseractOCR()
        img = Image.new("RGB", (10, 10))
        engine.extract_text(img, language="eng")
        mock_pytesseract.image_to_string.assert_called_once_with(img, lang="eng")

    @patch("src.ocr.tesseract.pytesseract")
    def test_passthrough_spa(self, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "text"
        engine = TesseractOCR()
        img = Image.new("RGB", (10, 10))
        engine.extract_text(img, language="spa")
        mock_pytesseract.image_to_string.assert_called_once_with(img, lang="spa")


class TestTesseractOCRShouldReturnString:
    """Given an image, extract_text should return the OCR output as a string."""

    @patch("src.ocr.tesseract.pytesseract")
    def test_returns_extracted_text(self, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "Invoice #123\nAmount: €50"
        engine = TesseractOCR()
        img = Image.new("RGB", (10, 10))
        result = engine.extract_text(img, language="en")
        assert result == "Invoice #123\nAmount: €50"

    @patch("src.ocr.tesseract.pytesseract")
    def test_default_language_is_eng(self, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "text"
        engine = TesseractOCR()
        img = Image.new("RGB", (10, 10))
        engine.extract_text(img)
        mock_pytesseract.image_to_string.assert_called_once_with(img, lang="eng")


class TestTesseractOCRShouldBeAnOCREngine:
    """TesseractOCR should be a subclass of OCREngine."""

    def test_is_subclass(self):
        assert issubclass(TesseractOCR, OCREngine)

    @patch("src.ocr.tesseract.pytesseract")
    def test_is_instance(self, mock_pytesseract):
        engine = TesseractOCR()
        assert isinstance(engine, OCREngine)
