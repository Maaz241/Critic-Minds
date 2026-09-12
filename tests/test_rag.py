"""
test_rag.py
Unit tests for the Critic Minds RAG vectorstore, embeddings, and pedagogical retriever.
"""
import unittest
import numpy as np
from app.rag.vectorstore import VectorStore
from app.rag.retrieval import PedagogicalRetriever
from data.sample_demo import load_demo_document


class TestRAG(unittest.TestCase):

    def setUp(self):
        self.store = VectorStore()
        self.doc = load_demo_document()

    def test_vectorstore_add_and_search(self):
        # Create deterministic pseudo-embeddings for testing
        num_chunks = len(self.doc.chunks)
        dim = 384
        vectors = np.zeros((num_chunks, dim), dtype=np.float32)
        vectors[0, 0] = 1.0  # chunk 0 points in direction 0
        vectors[1, 1] = 1.0  # chunk 1 points in direction 1
        vectors[2, 2] = 1.0  # chunk 2 points in direction 2

        self.store.add_document(self.doc, vectors)
        self.assertEqual(len(self.store.list_documents()), 1)

        # Search with a query pointing towards direction 0
        query_vec = np.zeros(dim, dtype=np.float32)
        query_vec[0] = 1.0

        results = self.store.search(query_vec, top_k=2, min_score=0.1)
        self.assertGreater(len(results), 0)
        top_result = results[0]
        self.assertAlmostEqual(top_result.score, 1.0, places=3)
        self.assertEqual(top_result.chunk.chunk_id, "demo-bio-c0")
        self.assertTrue("Page 42" in top_result.chunk.citation)

    def test_pedagogical_retrieval_query_construction(self):
        query = PedagogicalRetriever.construct_query(
            subject="Biology",
            grade="8",
            topic="Photosynthesis",
            challenge_type="evidence_analysis",
            instructions="Focus on light intensity",
        )
        self.assertIn("Grade 8 Biology", query)
        self.assertIn("Photosynthesis", query)
        self.assertIn("evidence", query.lower())
        self.assertIn("Focus on light intensity", query)


if __name__ == "__main__":
    unittest.main()
