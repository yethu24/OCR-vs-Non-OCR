from abc import ABC, abstractmethod

from PIL import Image


class OCREngine(ABC):
    """Abstract interface for OCR engines.

    Implementations must accept a per-document language code so that a single
    batch run can process bills in multiple languages.
    """

    @abstractmethod
    def extract_text(self, image: Image.Image, language: str = "eng") -> str:
        """Run OCR on *image* using the given language code.

        Args:
            image: A PIL Image of a single page.
            language: Tesseract-style language code (e.g. ``"eng"``, ``"deu"``).
                      Implementations may also accept ISO 639-1 codes and map
                      them internally.

        Returns:
            The extracted text as a single string.
        """
        ...
