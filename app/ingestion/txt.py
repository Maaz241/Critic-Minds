"""
txt.py
Extracts plain text and markdown documents with encoding detection and normalization.
"""
import re


class TXTExtractionError(Exception):
    pass


def extract_txt(file_bytes: bytes) -> str:
    """
    Decodes text file bytes using UTF-8 or Latin-1 fallback.
    Normalizes excessive whitespace.
    """
    text = ""
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            text = file_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if not text.strip():
        raise TXTExtractionError("The text file is empty or could not be decoded.")

    # Normalize carriage returns and excessive whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    return text
