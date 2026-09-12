"""
embeddings.py
Generates vector representations for document passages and search queries.
Uses sentence-transformers with 'all-MiniLM-L6-v2' (CPU-friendly 384-dim model).
Includes a TF-IDF vectorizer fallback if transformers model is loading or in offline mode.
"""
from typing import List, Optional, Callable
import numpy as np

_EMBED_MODEL = None
_FALLBACK_VECTORIZER = None


def _get_sentence_transformer_model():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Uses fast, lightweight 384-dim MiniLM model
            _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _EMBED_MODEL = False
    return _EMBED_MODEL if _EMBED_MODEL is not False else None


class EmbeddingsGenerator:
    """Provides methods to embed passages and queries."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.dimension = 384

    def embed_passages(
        self,
        texts: List[str],
        batch_size: int = 64,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> np.ndarray:
        """Embeds a list of text passages with batched processing and progress feedback."""
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)

        model = _get_sentence_transformer_model()
        if model is not None:
            try:
                total_texts = len(texts)
                if total_texts <= batch_size or not progress_callback:
                    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)
                    return embeddings.astype(np.float32)

                all_vecs = []
                for i in range(0, total_texts, batch_size):
                    batch = texts[i : i + batch_size]
                    current_count = min(i + len(batch), total_texts)
                    progress_callback(current_count, total_texts, f"Generating vector embeddings ({current_count}/{total_texts} chunks)...")
                    vecs = model.encode(batch, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)
                    all_vecs.append(vecs)
                return np.vstack(all_vecs).astype(np.float32)
            except Exception:
                pass

        # Fallback using scikit-learn TF-IDF to 384-dim dense array
        return self._tfidf_fallback_embed(texts)

    def embed_query(self, query: str) -> np.ndarray:
        """Embeds a single query string. Returns (D,) float32 array."""
        model = _get_sentence_transformer_model()
        if model is not None:
            try:
                vec = model.encode([query], show_progress_bar=False, convert_to_numpy=True)[0]
                return vec.astype(np.float32)
            except Exception:
                pass

        return self._tfidf_fallback_embed([query])[0]

    def _tfidf_fallback_embed(self, texts: List[str]) -> np.ndarray:
        """Fallback dense embedding generator using TF-IDF."""
        global _FALLBACK_VECTORIZER
        from sklearn.feature_extraction.text import TfidfVectorizer

        try:
            if _FALLBACK_VECTORIZER is None:
                _FALLBACK_VECTORIZER = TfidfVectorizer(max_features=self.dimension)
                _FALLBACK_VECTORIZER.fit(texts)

            sparse_matrix = _FALLBACK_VECTORIZER.transform(texts)
            dense_matrix = sparse_matrix.toarray().astype(np.float32)
            # Pad with zeros if less than dimension
            if dense_matrix.shape[1] < self.dimension:
                pad_width = ((0, 0), (0, self.dimension - dense_matrix.shape[1]))
                dense_matrix = np.pad(dense_matrix, pad_width, mode="constant")
            return dense_matrix
        except Exception:
            # Deterministic pseudo-embedding for emergency fallback
            out = np.zeros((len(texts), self.dimension), dtype=np.float32)
            for i, t in enumerate(texts):
                for j, char in enumerate(t[:self.dimension]):
                    out[i, j % self.dimension] += ord(char) / 255.0
            return out


_generator = None


def get_embeddings_generator() -> EmbeddingsGenerator:
    global _generator
    if _generator is None:
        _generator = EmbeddingsGenerator()
    return _generator
