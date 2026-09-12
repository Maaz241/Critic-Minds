"""
pdf.py
Extracts text from PDF documents page by page, preserving page numbers for citation.
Uses PyMuPDF (fitz) with optimized OCR fallback via Gemini Vision only on pages that contain images.
Supports page range selection and real-time progress reporting for large multi-page PDFs.
"""
import io
from typing import List, Tuple, Optional, Callable


class PDFExtractionError(Exception):
    pass


def _get_active_gemini_key() -> Optional[str]:
    """Helper to retrieve an active Gemini API key from session state or environment config."""
    try:
        import streamlit as st
        user_key = st.session_state.get("user_api_key")
        if user_key and user_key.strip():
            return user_key.strip()
    except Exception:
        pass

    from app.config import AppConfig
    return AppConfig.get_default_key("gemini")


def _ocr_page_image(img_bytes: bytes) -> str:
    """Uses Gemini Vision to OCR a rendered PDF page image."""
    api_key = _get_active_gemini_key()
    if not api_key:
        return ""

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        part = types.Part.from_bytes(data=img_bytes, mime_type="image/png")
        prompt = (
            "Transcribe all readable text from this page image verbatim. "
            "Preserve headings, numbers, and paragraph structure. "
            "Do not include conversational introductions or explanations."
        )

        for model_name in ("gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[part, prompt],
                )
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue
    except Exception:
        pass

    return ""


def get_pdf_page_count(file_bytes: bytes) -> int:
    """Quickly returns total page count without full text extraction."""
    try:
        import pymupdf
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        count = len(doc)
        doc.close()
        return count
    except Exception:
        try:
            from pypdf import PdfReader
            return len(PdfReader(io.BytesIO(file_bytes)).pages)
        except Exception:
            return 1


def extract_pdf_pages(
    file_bytes: bytes,
    page_range: Optional[Tuple[int, int]] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> List[Tuple[int, str]]:
    """
    Extracts text page by page from PDF bytes.
    Returns a list of tuples: (page_number, page_text).
    Page numbering is 1-indexed.
    
    Parameters:
      - page_range: Optional (start_page, end_page) 1-indexed inclusive range.
      - progress_callback: Optional callback(current, total, status_text).
    """
    pages: List[Tuple[int, str]] = []

    try:
        import pymupdf

        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        total_in_doc = len(doc)

        start_page = 1
        end_page = total_in_doc
        if page_range:
            start_page = max(1, min(page_range[0], total_in_doc))
            end_page = max(start_page, min(page_range[1], total_in_doc))

        selected_indices = list(range(start_page - 1, end_page))
        total_selected = len(selected_indices)

        for step, i in enumerate(selected_indices):
            page_num = i + 1
            page = doc[i]

            if progress_callback:
                progress_callback(step + 1, total_selected, f"Extracting page {page_num} of {total_in_doc}...")

            text = page.get_text("text").strip()
            images = page.get_images()

            # 1. Page has sufficient digital text layer: use immediately
            if len(text) >= 25:
                pages.append((page_num, text))
            elif not images:
                # 2. Page has no images: if it has any short text (e.g. title), keep it; if totally empty, skip
                if text:
                    pages.append((page_num, text))
            else:
                # 3. Page has images and virtually no text: attempt Vision OCR
                if progress_callback:
                    progress_callback(step + 1, total_selected, f"Running Vision OCR on scanned page {page_num}...")
                try:
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    ocr_text = _ocr_page_image(img_bytes)
                    if ocr_text:
                        pages.append((page_num, ocr_text))
                    elif text:
                        pages.append((page_num, text))
                except Exception:
                    if text:
                        pages.append((page_num, text))

        doc.close()
    except Exception as exc:
        pages.clear()

    # Attempt fallback to pypdf if pymupdf completely failed
    if not pages:
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(file_bytes))
            for i, page in enumerate(reader.pages):
                text = (page.extract_text() or "").strip()
                if text:
                    pages.append((i + 1, text))
        except Exception:
            pass

    if not pages:
        has_key = bool(_get_active_gemini_key())
        if not has_key:
            raise PDFExtractionError(
                "No digital text layer found in this PDF (it appears to be a scanned image). "
                "Please configure a Gemini API key in 'AI Settings' to enable automatic Vision OCR extraction."
            )
        else:
            raise PDFExtractionError(
                "No readable text could be extracted or OCR'd from this PDF. "
                "Please ensure the document contains legible educational content."
            )

    return pages
