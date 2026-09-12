"""
Ingestion module for Critic Minds
Supports PDF, DOCX, TXT, and PPTX with unified metadata preservation.
"""
from .unified import extract_and_chunk, UnifiedDocument, DocumentChunk, ExtractionError

__all__ = ["extract_and_chunk", "UnifiedDocument", "DocumentChunk", "ExtractionError"]
