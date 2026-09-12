"""
retrieval.py
Pedagogical Evidence Retriever for Critic Minds.
Transforms teacher configuration into rich educational retrieval queries,
queries the vectorstore, and formats evidence items with explicit source attribution.
"""
from typing import List, Dict, Any, Optional
from app.rag.embeddings import get_embeddings_generator
from app.rag.vectorstore import VectorStore, SearchResult
from app.ingestion.unified import DocumentChunk


class PedagogicalRetriever:
    """Handles query expansion and contextual evidence retrieval."""

    def __init__(self, vectorstore: VectorStore):
        self.vectorstore = vectorstore
        self.embeddings_gen = get_embeddings_generator()

    @staticmethod
    def construct_query(
        subject: str,
        grade: str,
        topic: str,
        challenge_type: str,
        instructions: Optional[str] = None,
    ) -> str:
        """
        Builds a high-intent educational search query as required by Section 43 of requirements.md:
        Subject + Grade + Topic + Challenge Type + Learning Focus / Teacher Instruction.
        """
        type_intent = {
            "evidence_analysis": "evidence, data, experimental findings, conflicting interpretations, observations",
            "what_if": "causal relationships, variables, predictions, outcomes, changing conditions, effects",
            "case_analysis": "real-world scenario, core problem, practical dilemmas, decision making, trade-offs",
        }.get(challenge_type.lower().replace(" ", "_"), "principles, evidence, concepts, reasoning")

        if grade.isdigit():
            level_str = f"Grade {grade}"
        elif "Grade" in grade:
            level_str = grade
        else:
            level_str = f"Level: {grade}"

        parts = [
            f"{level_str} {subject}",
            f"Topic: {topic}",
            f"Focus: {type_intent}",
        ]
        if instructions and instructions.strip():
            parts.append(f"Teacher note: {instructions.strip()}")

        return " — ".join(parts)

    def retrieve(
        self,
        subject: str,
        grade: str,
        topic: str,
        challenge_type: str,
        instructions: Optional[str] = None,
        doc_id: Optional[str] = None,
        top_k: int = 4,
    ) -> List[SearchResult]:
        """Executes pedagogical retrieval against the vector store."""
        query_text = self.construct_query(subject, grade, topic, challenge_type, instructions)
        query_vector = self.embeddings_gen.embed_query(query_text)
        results = self.vectorstore.search(
            query_vector=query_vector,
            doc_id=doc_id,
            top_k=top_k,
            min_score=0.15,
        )

        # If strict search returned fewer than 2 chunks, fallback to top available chunks
        if len(results) < 2 and doc_id:
            all_chunks = self.vectorstore.get_chunks(doc_id)
            for ch in all_chunks[:top_k]:
                if not any(r.chunk.chunk_id == ch.chunk_id for r in results):
                    results.append(SearchResult(score=0.3, chunk=ch))

        return results[:top_k]

    @staticmethod
    def format_evidence_for_prompt(results: List[SearchResult]) -> str:
        """Formats retrieved chunks with citations for LLM prompt injection."""
        if not results:
            return "No specific document evidence retrieved."

        blocks = []
        for i, res in enumerate(results):
            chunk: DocumentChunk = res.chunk
            citation = chunk.citation
            blocks.append(
                f"--- EVIDENCE ITEM {i+1} [{citation}] ---\n"
                f"{chunk.text.strip()}\n"
            )
        return "\n".join(blocks)
