"""
vectorstore.py
In-memory Vector Database for Critic Minds.
Extended and adapted from DocuMind-AI's vectorstore.
Stores document chunks with rich educational metadata and performs cosine-similarity search.
Requires no external database services (ChromaDB/Postgres/Pinecone) — perfect for hackathon & free-tier Streamlit Cloud.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import numpy as np
import time
from app.ingestion.unified import DocumentChunk, UnifiedDocument


@dataclass
class SearchResult:
    score: float
    chunk: DocumentChunk


@dataclass
class StoredDocumentMeta:
    document_id: str
    filename: str
    file_type: str
    num_chunks: int
    raw_text_length: int
    uploaded_at: float = field(default_factory=time.time)


class VectorStore:
    """In-memory vector store that holds documents, chunks, and embeddings."""

    def __init__(self):
        self._documents: Dict[str, StoredDocumentMeta] = {}
        self._chunks: Dict[str, List[DocumentChunk]] = {}  # doc_id -> list of chunks
        self._vectors: Dict[str, np.ndarray] = {}  # doc_id -> (N, D) matrix

    def add_document(self, doc: UnifiedDocument, vectors: np.ndarray) -> StoredDocumentMeta:
        """Stores a parsed document, its chunks, and associated embedding matrix."""
        meta = StoredDocumentMeta(
            document_id=doc.document_id,
            filename=doc.filename,
            file_type=doc.file_type,
            num_chunks=len(doc.chunks),
            raw_text_length=doc.raw_text_length,
        )
        self._documents[doc.document_id] = meta
        self._chunks[doc.document_id] = doc.chunks
        self._vectors[doc.document_id] = vectors
        return meta

    def delete_document(self, doc_id: str) -> bool:
        """Removes a document and its embeddings from the store."""
        if doc_id in self._documents:
            del self._documents[doc_id]
            del self._chunks[doc_id]
            del self._vectors[doc_id]
            return True
        return False

    def clear(self):
        """Clears all documents from the store."""
        self._documents.clear()
        self._chunks.clear()
        self._vectors.clear()

    def list_documents(self) -> List[StoredDocumentMeta]:
        """Returns all documents sorted by upload time (newest first)."""
        return sorted(self._documents.values(), key=lambda d: d.uploaded_at, reverse=True)

    def get_document(self, doc_id: str) -> Optional[StoredDocumentMeta]:
        return self._documents.get(doc_id)

    def get_chunks(self, doc_id: str) -> List[DocumentChunk]:
        return self._chunks.get(doc_id, [])

    def search(
        self,
        query_vector: np.ndarray,
        doc_id: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.25,
    ) -> List[SearchResult]:
        """
        Cosine-similarity search across chunks.
        If doc_id is specified (and not 'all'), searches only within that document.
        """
        target_doc_ids = [doc_id] if (doc_id and doc_id != "all") else list(self._documents.keys())
        results: List[SearchResult] = []

        for did in target_doc_ids:
            vectors = self._vectors.get(did)
            chunks = self._chunks.get(did)
            if vectors is None or len(chunks) == 0 or vectors.shape[0] == 0:
                continue

            sims = _cosine_similarity(query_vector, vectors)
            for idx, score in enumerate(sims):
                score_float = float(score)
                if score_float >= min_score:
                    results.append(SearchResult(score=score_float, chunk=chunks[idx]))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]


def _cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Computes cosine similarity between a 1D query vector and a 2D matrix of vectors."""
    q_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    m_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    return m_norm @ q_norm
