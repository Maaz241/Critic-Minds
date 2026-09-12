"""
generation.py
Challenge Generator for Critic Minds.
Transforms retrieved curriculum evidence and teacher specifications into
curriculum-grounded critical-thinking challenges (Evidence Analysis, What-If, Case Analysis)
guided by the 8-cluster Critical-Thinking Questioning Taxonomy.
"""
from typing import Tuple, List, Optional, Union
from app.ai.schemas import ChallengeSchema, ChallengeSetSchema, QAResult
from app.ai.providers import BaseLLMProvider, LLMProviderError
from app.ai.prompts import CHALLENGE_GENERATION_PROMPT, MULTI_CHALLENGE_GENERATION_PROMPT
from app.ai.patterns import (
    select_patterns_for_generation,
    format_patterns_prompt_section,
    CRITICAL_PATTERNS,
)
from app.ai.qa import audit_challenge
from app.rag.retrieval import PedagogicalRetriever
from app.rag.vectorstore import SearchResult


def generate_challenge_set(
    subject: str,
    grade: str,
    topic: str,
    challenge_type: str,
    difficulty: str,
    estimated_time: int,
    teacher_instructions: str,
    retrieved_results: List[SearchResult],
    provider: BaseLLMProvider,
    num_questions: int = 1,
    pattern_cluster: str = "All Clusters (Diverse Reasoning)",
    tier: str = "Tier 1: Direct application",
    specific_pattern: Optional[str] = None,
) -> Tuple[ChallengeSetSchema, List[QAResult]]:
    """
    Generates a coherent set of 1 to 5 curriculum-grounded critical-thinking challenge questions
    with quality assurance audits.
    """
    if not retrieved_results:
        raise LLMProviderError(
            "Insufficient source material to confidently generate this challenge. "
            "Please upload more relevant material or adjust the topic."
        )

    evidence_context = PedagogicalRetriever.format_evidence_for_prompt(retrieved_results)

    # Select critical thinking patterns for the questions
    selected_patterns = select_patterns_for_generation(
        cluster_name=pattern_cluster,
        num_questions=num_questions,
        specific_pattern_name=specific_pattern,
    )
    pattern_guidance = format_patterns_prompt_section(selected_patterns, tier=tier)

    # 1. Build prompt based on question count
    if num_questions <= 1:
        prompt = CHALLENGE_GENERATION_PROMPT.format(
            subject=subject,
            grade=grade,
            topic=topic,
            challenge_type=challenge_type,
            difficulty=difficulty,
            estimated_time=estimated_time,
            instructions=teacher_instructions if teacher_instructions.strip() else "None provided.",
            pattern_guidance=pattern_guidance,
            evidence_context=evidence_context,
            tier=tier,
        )

        data = provider.generate_json(prompt, temperature=0.25)
        try:
            # Handle if model returned an object with 'challenges' or a single challenge
            if "challenges" in data and isinstance(data["challenges"], list) and len(data["challenges"]) > 0:
                single_data = data["challenges"][0]
            else:
                single_data = data

            single_challenge = ChallengeSchema.model_validate(single_data)
            if not single_challenge.pattern and selected_patterns:
                single_challenge.pattern = selected_patterns[0].name
                single_challenge.pattern_cluster = selected_patterns[0].cluster
                single_challenge.skill_targeted = selected_patterns[0].skill_targeted
            single_challenge.tier = tier
            single_challenge.question_number = 1

            challenges = [single_challenge]
            challenge_set = ChallengeSetSchema(
                title=single_challenge.title,
                subject=subject,
                grade=grade,
                topic=topic,
                overview_scenario=single_challenge.scenario,
                challenges=challenges,
            )
        except Exception as exc:
            raise LLMProviderError(f"Generated challenge failed schema validation: {exc}") from exc

    else:
        # Multi-question generation
        single_est = max(5, round(estimated_time / num_questions))
        prompt = MULTI_CHALLENGE_GENERATION_PROMPT.format(
            subject=subject,
            grade=grade,
            topic=topic,
            challenge_type=challenge_type,
            difficulty=difficulty,
            estimated_time=estimated_time,
            single_est_time=single_est,
            num_questions=num_questions,
            instructions=teacher_instructions if teacher_instructions.strip() else "None provided.",
            pattern_guidance=pattern_guidance,
            evidence_context=evidence_context,
            tier=tier,
        )

        data = provider.generate_json(prompt, temperature=0.3)
        try:
            # Validate as ChallengeSetSchema
            if "challenges" in data and isinstance(data["challenges"], list):
                challenge_set = ChallengeSetSchema.model_validate(data)
            else:
                # Model returned a single challenge dict or unexpected wrapper
                if "title" in data:
                    c = ChallengeSchema.model_validate(data)
                    challenge_set = ChallengeSetSchema(
                        title=c.title,
                        subject=subject,
                        grade=grade,
                        topic=topic,
                        overview_scenario=c.scenario,
                        challenges=[c],
                    )
                else:
                    raise ValueError("JSON missing 'challenges' array")
        except Exception as exc:
            raise LLMProviderError(f"Generated multi-question challenge set failed validation: {exc}") from exc

    # 2. Ensure each challenge in set is well-grounded and has valid metadata
    for idx, ch in enumerate(challenge_set.challenges):
        ch.question_number = idx + 1
        if not ch.tier:
            ch.tier = tier
        if idx < len(selected_patterns):
            if not ch.pattern:
                ch.pattern = selected_patterns[idx].name
            if not ch.pattern_cluster:
                ch.pattern_cluster = selected_patterns[idx].cluster
            if not ch.skill_targeted:
                ch.skill_targeted = selected_patterns[idx].skill_targeted

        # Backfill evidence if empty
        if not ch.evidence or len(ch.evidence) == 0:
            for res in retrieved_results[:3]:
                chunk = res.chunk
                ch.evidence.append(
                    {
                        "text": chunk.text[:250] + "...",
                        "source": chunk.filename,
                        "page_or_slide": chunk.page_or_slide,
                    }
                )

    # 3. Run QA Audit on all challenges
    qa_results: List[QAResult] = []
    for ch in challenge_set.challenges:
        qa_res = audit_challenge(
            challenge=ch,
            evidence_context=evidence_context,
            grade=grade,
            topic=topic,
            challenge_type=ch.challenge_type or challenge_type,
            provider=provider,
        )
        qa_results.append(qa_res)

    return challenge_set, qa_results


def generate_challenge(
    subject: str,
    grade: str,
    topic: str,
    challenge_type: str,
    difficulty: str,
    estimated_time: int,
    teacher_instructions: str,
    retrieved_results: List[SearchResult],
    provider: BaseLLMProvider,
    num_questions: int = 1,
    pattern_cluster: str = "All Clusters (Diverse Reasoning)",
    tier: str = "Tier 1: Direct application",
    specific_pattern: Optional[str] = None,
) -> Union[Tuple[ChallengeSchema, QAResult], Tuple[ChallengeSetSchema, List[QAResult]]]:
    """
    Main entry point for challenge generation.
    Returns (ChallengeSchema, QAResult) when num_questions == 1 for backwards-compatibility,
    or (ChallengeSetSchema, List[QAResult]) when num_questions > 1.
    """
    challenge_set, qa_results = generate_challenge_set(
        subject=subject,
        grade=grade,
        topic=topic,
        challenge_type=challenge_type,
        difficulty=difficulty,
        estimated_time=estimated_time,
        teacher_instructions=teacher_instructions,
        retrieved_results=retrieved_results,
        provider=provider,
        num_questions=num_questions,
        pattern_cluster=pattern_cluster,
        tier=tier,
        specific_pattern=specific_pattern,
    )

    if num_questions == 1 and len(challenge_set.challenges) > 0:
        return challenge_set.challenges[0], qa_results[0]

    return challenge_set, qa_results
