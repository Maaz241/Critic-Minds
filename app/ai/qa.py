"""
qa.py
Lightweight AI Quality Assurance Auditor for Critic Minds.
Validates generated challenges against grounding, clarity, reasoning demand, and rubric consistency.
"""
from typing import Dict, Any, List
from app.ai.schemas import ChallengeSchema, QAResult
from app.ai.providers import BaseLLMProvider
from app.ai.prompts import QA_PROMPT


def audit_challenge(
    challenge: ChallengeSchema,
    evidence_context: str,
    grade: str,
    topic: str,
    challenge_type: str,
    provider: BaseLLMProvider,
) -> QAResult:
    """
    Executes lightweight QA audit on the generated challenge.
    Falls back to heuristic validation if provider call encounters transient issues.
    """
    try:
        prompt = QA_PROMPT.format(
            grade=grade,
            topic=topic,
            challenge_type=challenge_type,
            evidence_context=evidence_context,
            challenge_json=challenge.model_dump_json(indent=2),
        )
        data = provider.generate_json(prompt, temperature=0.1)
        return QAResult(
            status=data.get("status", "pass").lower(),
            score=int(data.get("score", 90)),
            issues=data.get("issues", []),
            regenerate=bool(data.get("regenerate", False)),
        )
    except Exception:
        # Heuristic QA fallback
        return run_heuristic_qa(challenge)


def run_heuristic_qa(challenge: ChallengeSchema) -> QAResult:
    """Internal rule-based verification ensuring core criteria are met."""
    issues: List[str] = []
    score = 100

    if len(challenge.evidence) < 2:
        issues.append("Evidence list has fewer than 2 items.")
        score -= 15

    if not challenge.scenario or len(challenge.scenario) < 50:
        issues.append("Scenario description is relatively brief.")
        score -= 10

    if not challenge.rubric or len(challenge.rubric) < 3:
        issues.append("Rubric has fewer than 3 assessment dimensions.")
        score -= 15

    has_source = any(item.source for item in challenge.evidence)
    if not has_source:
        issues.append("Evidence lacks explicit document source citation.")
        score -= 20

    status = "pass" if score >= 70 else "fail"
    return QAResult(
        status=status,
        score=max(0, score),
        issues=issues,
        regenerate=score < 60,
    )
