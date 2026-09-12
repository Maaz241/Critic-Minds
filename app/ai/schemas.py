"""
schemas.py
Strict Pydantic data schemas for Critic Minds.
Defines contracts for Challenge Generation, Rubrics, Quality Assurance, and Student Evaluation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    text: str = Field(description="The factual evidence statement excerpted or synthesized from curriculum")
    source: str = Field(description="The source document filename")
    page_or_slide: str = Field(description="Page or slide identifier, e.g. Page 42 or Slide 12")


class RubricCriterion(BaseModel):
    criterion: str = Field(description="Name of the rubric dimension, e.g. Evidence Selection")
    description: str = Field(description="Description of what constitutes high performance")
    max_score: int = Field(default=4, description="Maximum points for this criterion")
    weight: float = Field(default=0.25, description="Weight proportion (e.g. 0.25)")


class ChallengeSchema(BaseModel):
    title: str = Field(description="Engaging title for the critical-thinking challenge")
    challenge_type: str = Field(description="evidence_analysis | what_if | case_analysis")
    grade: str = Field(description="Target grade level, e.g. 8")
    difficulty: str = Field(description="easy | medium | hard")
    estimated_time_minutes: int = Field(default=15, description="Expected time in minutes")
    learning_focus: str = Field(description="Pedagogical objective and core reasoning competency")
    scenario: str = Field(description="Realistic, narrative situation setting up the critical dilemma")
    student_role: str = Field(description="Role assigned to the student (e.g. Agricultural Consultant, Lead Scientist)")
    central_question: str = Field(description="Core open-ended question requiring justification and evidence")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Array of evidence statements with citations")
    task_instructions: List[str] = Field(default_factory=list, description="Step-by-step tasks for the student")
    response_requirements: List[str] = Field(default_factory=list, description="Explicit criteria for the student answer")
    hints: List[str] = Field(default_factory=list, description="Scaffolding hints that prompt deeper thinking")
    extension_question: str = Field(default="", description="Follow-up question for higher-order inquiry")
    possible_interpretations: List[str] = Field(default_factory=list, description="Valid viewpoints or hypotheses")
    rubric: List[RubricCriterion] = Field(default_factory=list, description="Assessment criteria")
    # Critical Thinking Taxonomy Fields
    pattern: str = Field(default="", description="Specific critical thinking pattern name (e.g. Cause vs. Correlation)")
    pattern_cluster: str = Field(default="", description="Parent cluster (e.g. Causal Reasoning, Evidence & Data)")
    tier: str = Field(default="Tier 1: Direct application", description="Cognitive complexity tier")
    skill_targeted: str = Field(default="", description="Specific cognitive reasoning skill targeted")
    question_number: int = Field(default=1, description="Question number in sequence")


class ChallengeSetSchema(BaseModel):
    title: str = Field(description="Overall set or lesson challenge title")
    subject: str = Field(description="Subject domain")
    grade: str = Field(description="Grade level")
    topic: str = Field(description="Curriculum topic")
    overview_scenario: str = Field(default="", description="Overarching background scenario connecting the questions")
    challenges: List[ChallengeSchema] = Field(default_factory=list, description="List of individual question challenges")


class QAResult(BaseModel):
    status: str = Field(default="pass", description="pass | fail")
    score: int = Field(default=90, description="Quality score 0-100")
    issues: List[str] = Field(default_factory=list, description="Any detected issues")
    regenerate: bool = Field(default=False, description="Whether regeneration is recommended")


class CriterionScore(BaseModel):
    criterion: str = Field(description="Rubric criterion name")
    score: int = Field(description="Awarded points")
    max_score: int = Field(default=4, description="Maximum points possible")
    feedback: str = Field(description="Specific constructive feedback for this criterion")


class EvaluationResult(BaseModel):
    total_score: int = Field(description="Total points awarded")
    max_score: int = Field(default=20, description="Total maximum points possible")
    criteria: List[CriterionScore] = Field(default_factory=list, description="Breakdown per criterion")
    strengths: List[str] = Field(default_factory=list, description="Highlighted reasoning strengths")
    improvements: List[str] = Field(default_factory=list, description="Specific recommendations for deeper reasoning")
    overall_feedback: str = Field(description="Holistic appraisal of the student's critical argument")
