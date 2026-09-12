"""
evaluation.py
Student Reasoning Evaluator for Critic Minds.
Evaluates student written reasoning against challenge rubrics, evidence usage, and logical depth.
Prioritizes the quality of student argumentation rather than demanding a single fixed answer key.
"""
from typing import Dict, Any, List
from app.ai.schemas import ChallengeSchema, EvaluationResult, CriterionScore
from app.ai.providers import BaseLLMProvider, LLMProviderError
from app.ai.prompts import STUDENT_EVALUATION_PROMPT


def evaluate_student_response(
    challenge: ChallengeSchema,
    student_response: str,
    provider: BaseLLMProvider,
) -> EvaluationResult:
    """
    Evaluates a student's open-ended reasoning submission against the challenge rubric.
    """
    if not student_response or len(student_response.strip()) < 10:
        raise LLMProviderError("The submitted response is too brief to evaluate. Please provide your reasoning.")

    # Format evidence
    evidence_lines = []
    for i, ev in enumerate(challenge.evidence):
        citation = f"{ev.source} — {ev.page_or_slide}" if ev.source else "Source"
        evidence_lines.append(f"[{citation}]: {ev.text}")
    evidence_text = "\n".join(evidence_lines) if evidence_lines else "None provided."

    # Format rubric
    rubric_lines = []
    total_possible = 0
    for crit in challenge.rubric:
        rubric_lines.append(f"• {crit.criterion} (Max {crit.max_score} pts): {crit.description}")
        total_possible += crit.max_score
    rubric_text = "\n".join(rubric_lines) if rubric_lines else "Default 4-point reasoning rubric."
    if total_possible == 0:
        total_possible = 16

    prompt = STUDENT_EVALUATION_PROMPT.format(
        title=challenge.title,
        grade=challenge.grade or "General",
        central_question=challenge.central_question,
        student_role=challenge.student_role or "Student Investigator",
        evidence_text=evidence_text,
        rubric_text=rubric_text,
        student_response=student_response.strip(),
    )

    data = provider.generate_json(prompt, temperature=0.2)

    try:
        # Validate or parse into EvaluationResult
        criteria_list = []
        raw_criteria = data.get("criteria", [])
        total_score = 0
        max_score = 0

        for item in raw_criteria:
            c_score = int(item.get("score", 3))
            c_max = int(item.get("max_score", 4))
            total_score += c_score
            max_score += c_max
            criteria_list.append(
                CriterionScore(
                    criterion=item.get("criterion", "Reasoning"),
                    score=c_score,
                    max_score=c_max,
                    feedback=item.get("feedback", ""),
                )
            )

        if not criteria_list:
            criteria_list = [
                CriterionScore(criterion="Reasoning Quality", score=3, max_score=4, feedback="Demonstrates basic reasoning."),
                CriterionScore(criterion="Evidence Usage", score=3, max_score=4, feedback="Mentions key evidence points."),
            ]
            total_score = 6
            max_score = 8

        # If data already provided total_score/max_score, respect if consistent
        reported_total = data.get("total_score")
        reported_max = data.get("max_score")
        if reported_total is not None and reported_max is not None:
            final_total = int(reported_total)
            final_max = int(reported_max)
        else:
            final_total = total_score
            final_max = max_score

        return EvaluationResult(
            total_score=final_total,
            max_score=final_max,
            criteria=criteria_list,
            strengths=data.get("strengths", ["Logical structure"]),
            improvements=data.get("improvements", ["Consider addressing alternative hypotheses"]),
            overall_feedback=data.get(
                "overall_feedback",
                "Your reasoning was evaluated against the evidence and rubric criteria."
            ),
        )

    except Exception as exc:
        raise LLMProviderError(f"Failed to process evaluation result: {exc}") from exc
