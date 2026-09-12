"""
unified.py
Unified content representation and chunking pipeline for Critic Minds.
Converts any supported format (PDF, DOCX, TXT, PPTX) into standardized,
metadata-enriched chunks ready for vector indexing and citation tracking.
"""
import uuid
import re
from dataclasses import dataclass, field
from typing import List, Optional
from .pdf import extract_pdf_pages, get_pdf_page_count, PDFExtractionError
from .docx import extract_docx_sections, DOCXExtractionError
from .txt import extract_txt, TXTExtractionError
from .pptx import extract_pptx_slides, PPTXExtractionError
from typing import List, Optional, Tuple, Callable


class ExtractionError(Exception):
    pass


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    filename: str
    file_type: str
    page_or_slide: str
    section: str
    chunk_index: int
    text: str

    @property
    def citation(self) -> str:
        """Returns a clean citation label (e.g. 'Photosynthesis.pdf — Page 4')."""
        if self.page_or_slide:
            return f"{self.filename} — {self.page_or_slide}"
        elif self.section and self.section != "General":
            return f"{self.filename} — {self.section}"
        return self.filename


@dataclass
class UnifiedDocument:
    document_id: str
    filename: str
    file_type: str
    chunks: List[DocumentChunk] = field(default_factory=list)
    raw_text_length: int = 0


def _split_into_chunks(text: str, max_words: int = 300, overlap_words: int = 50) -> List[str]:
    """
    Sentence-aware chunking with word count limits and overlap.
    Preserves whole sentences where possible.
    """
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    if not text:
        return []

    # Split by paragraphs first
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: List[str] = []
    current_words: List[str] = []

    for para in paragraphs:
        para_words = para.split()
        if len(current_words) + len(para_words) <= max_words:
            current_words.extend(para_words)
        else:
            if current_words:
                chunks.append(" ".join(current_words))
                # retain overlap from the tail of current_words
                overlap = current_words[-overlap_words:] if len(current_words) > overlap_words else current_words
                current_words = list(overlap)
            
            # If paragraph itself is larger than max_words, break it up
            if len(para_words) > max_words:
                for i in range(0, len(para_words), max_words - overlap_words):
                    sub_chunk = para_words[i : i + max_words]
                    if sub_chunk:
                        chunks.append(" ".join(sub_chunk))
                current_words = []
            else:
                current_words.extend(para_words)

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def extract_and_chunk(
    file_bytes: bytes,
    filename: str,
    doc_id: Optional[str] = None,
    page_range: Optional[Tuple[int, int]] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> UnifiedDocument:
    """
    Unified entry point for document ingestion.
    Parses PDF, DOCX, TXT, or PPTX and generates structured DocumentChunks with metadata.
    """
    if not doc_id:
        doc_id = str(uuid.uuid4())[:8]

    lower = filename.lower()
    chunks: List[DocumentChunk] = []
    total_length = 0

    try:
        if lower.endswith(".pdf"):
            file_type = "pdf"
            pages = extract_pdf_pages(file_bytes, page_range=page_range, progress_callback=progress_callback)
            chunk_idx = 0
            for page_num, page_text in pages:
                total_length += len(page_text)
                sub_chunks = _split_into_chunks(page_text, max_words=300)
                for sc in sub_chunks:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{doc_id}-c{chunk_idx}",
                            document_id=doc_id,
                            filename=filename,
                            file_type=file_type,
                            page_or_slide=f"Page {page_num}",
                            section=f"Page {page_num}",
                            chunk_index=chunk_idx,
                            text=sc,
                        )
                    )
                    chunk_idx += 1

        elif lower.endswith(".docx"):
            file_type = "docx"
            sections = extract_docx_sections(file_bytes)
            chunk_idx = 0
            for sec_title, sec_text in sections:
                total_length += len(sec_text)
                sub_chunks = _split_into_chunks(sec_text, max_words=300)
                for sc in sub_chunks:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{doc_id}-c{chunk_idx}",
                            document_id=doc_id,
                            filename=filename,
                            file_type=file_type,
                            page_or_slide=f"Section: {sec_title}",
                            section=sec_title,
                            chunk_index=chunk_idx,
                            text=sc,
                        )
                    )
                    chunk_idx += 1

        elif lower.endswith((".txt", ".md")):
            file_type = "txt"
            raw_text = extract_txt(file_bytes)
            total_length += len(raw_text)
            sub_chunks = _split_into_chunks(raw_text, max_words=300)
            for chunk_idx, sc in enumerate(sub_chunks):
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc_id}-c{chunk_idx}",
                        document_id=doc_id,
                        filename=filename,
                        file_type=file_type,
                        page_or_slide=f"Part {chunk_idx + 1}",
                        section="General",
                        chunk_index=chunk_idx,
                        text=sc,
                    )
                )

        elif lower.endswith((".pptx", ".ppt")):
            file_type = "pptx"
            slides = extract_pptx_slides(file_bytes)
            chunk_idx = 0
            for slide_num, slide_title, slide_text in slides:
                total_length += len(slide_text)
                sub_chunks = _split_into_chunks(slide_text, max_words=300)
                for sc in sub_chunks:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{doc_id}-c{chunk_idx}",
                            document_id=doc_id,
                            filename=filename,
                            file_type=file_type,
                            page_or_slide=f"Slide {slide_num}",
                            section=slide_title,
                            chunk_index=chunk_idx,
                            text=sc,
                        )
                    )
                    chunk_idx += 1

        else:
            raise ExtractionError(
                f"Unsupported file format '{filename}'. Please upload a PDF, DOCX, TXT, or PPTX document."
            )

    except (PDFExtractionError, DOCXExtractionError, TXTExtractionError, PPTXExtractionError) as exc:
        raise ExtractionError(str(exc)) from exc
    except Exception as exc:
        raise ExtractionError(f"Unexpected error processing '{filename}': {exc}") from exc

    if not chunks:
        raise ExtractionError(f"No extractable text found in '{filename}'.")

    return UnifiedDocument(
        document_id=doc_id,
        filename=filename,
        file_type=file_type,
        chunks=chunks,
        raw_text_length=total_length,
    )
