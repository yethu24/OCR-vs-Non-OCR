"""Word-count rough estimator for the dissertation chapters.

Strips LaTeX commands and comments, then counts alphabetic word
tokens. Skips inactive chapter files (Body, Background2,
DesignSpecification) that are not included from report.tex.
"""
import re
from pathlib import Path

CHAPTERS_DIR = Path(__file__).resolve().parent.parent / "Chapters"
INACTIVE = {"Body.tex", "Background2.tex", "DesignSpecification.tex"}


def strip_latex(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    text = re.sub(r"[{}\[\]\\$~^_&]", " ", text)
    return text


def count(text: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z'-]+", text))


def main() -> None:
    total = 0
    for tex in sorted(CHAPTERS_DIR.glob("*.tex")):
        if tex.name in INACTIVE:
            continue
        body = strip_latex(tex.read_text(encoding="utf-8"))
        n = count(body)
        print(f"{tex.name:30s} {n:6d} words")
        total += n
    print(f"{'TOTAL':30s} {total:6d} words")


if __name__ == "__main__":
    main()
