from __future__ import annotations

import logging

import pytesseract
from PIL import Image

from .base import OCREngine

logger = logging.getLogger(__name__)

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
        tess_lang = LANGUAGE_MAP.get(language, language)
        logger.debug("Running Tesseract with lang=%s", tess_lang)
        text: str = pytesseract.image_to_string(image, lang=tess_lang)
        return text
