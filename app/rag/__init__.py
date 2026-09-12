"""
RAG package for Critic Minds.
Handles embedding generation, in-memory vector storage, and pedagogical evidence retrieval.
"""
from .embeddings import get_embeddings_generator
from .vectorstore import VectorStore, SearchResult
from .retrieval import PedagogicalRetriever

__all__ = ["get_embeddings_generator", "VectorStore", "SearchResult", "PedagogicalRetriever"]
