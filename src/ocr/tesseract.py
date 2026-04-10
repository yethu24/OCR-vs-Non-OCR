from __future__ import annotations

import logging

import pytesseract
from PIL import Image

from .base import OCREngine

logger = logging.getLogger(__name__)

# ISO 639-1 → Tesseract language codes (the dataset uses ISO codes)
LANGUAGE_MAP: dict[str, str] = {
    "en": "eng",
    "de": "deu",
    "fr": "fra",
    "it": "ita",
}


class TesseractOCR(OCREngine):
    """Tesseract OCR engine wrapper.

    Accepts both ISO 639-1 codes (``"en"``, ``"de"``) and native Tesseract
    codes (``"eng"``, ``"deu"``).  ISO codes are mapped automatically via
    ``LANGUAGE_MAP``.
    """

    def extract_text(self, image: Image.Image, language: str = "eng") -> str:
        # Convert ISO code to Tesseract code if needed, otherwise pass through
        tess_lang = LANGUAGE_MAP.get(language, language)
        try:
            text = pytesseract.image_to_string(image, lang=tess_lang)
            return text
        except pytesseract.TesseractNotFoundError:
            raise RuntimeError(
                "Tesseract not found. Install it and ensure it's on PATH."
            ) from None
        except pytesseract.TesseractError as e:
            logger.warning("Tesseract failed for lang=%s: %s", tess_lang, e)
            return "" 

