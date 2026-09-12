"""
AI Engine package for Critic Minds.
Manages LLM providers, structured schemas, challenge generation, QA, and student evaluation.
"""
from .schemas import ChallengeSchema, EvidenceItem, RubricCriterion, EvaluationResult, QAResult
from .providers import get_llm_provider, LLMProviderError

__all__ = [
    "ChallengeSchema",
    "EvidenceItem",
    "RubricCriterion",
    "EvaluationResult",
    "QAResult",
    "get_llm_provider",
    "LLMProviderError",
]
