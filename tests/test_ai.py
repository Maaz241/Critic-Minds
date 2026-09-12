"""
test_ai.py
Unit tests for AI schemas, prompts, and evaluation data structures.
"""
import unittest
from app.ai.schemas import (
    ChallengeSchema,
    EvidenceItem,
    RubricCriterion,
    EvaluationResult,
    CriterionScore,
    QAResult,
)
from app.ai.qa import run_heuristic_qa


class TestAI(unittest.TestCase):

    def test_challenge_schema_validation(self):
        challenge_data = {
            "title": "The Greenhouse Paradox",
            "challenge_type": "evidence_analysis",
            "grade": "8",
            "difficulty": "medium",
            "estimated_time_minutes": 15,
            "learning_focus": "Analyzing limiting factors",
            "scenario": "A greenhouse operator notices that adding more lamps does not increase yields.",
            "student_role": "Agricultural Consultant",
            "central_question": "Which environmental factor is currently limiting yield, and how do you know?",
            "evidence": [
                {
                    "text": "Beyond 0.10% CO2, bubble production plateaus at 84 bubbles/min.",
                    "source": "Biology_Chapter4.pdf",
                    "page_or_slide": "Page 43",
                }
            ],
            "task_instructions": ["Examine the CO2 data", "Explain the plateau"],
            "response_requirements": ["Cite the bubble rate"],
            "hints": ["Consider Blackman's law of limiting factors"],
            "extension_question": "What happens if temperature exceeds 38C?",
            "possible_interpretations": ["Light is limiting", "CO2 is limiting"],
            "rubric": [
                {
                    "criterion": "Evidence Selection",
                    "description": "Cites page 43 data correctly",
                    "max_score": 4,
                    "weight": 0.5,
                }
            ],
        }
        ch = ChallengeSchema.model_validate(challenge_data)
        self.assertEqual(ch.title, "The Greenhouse Paradox")
        self.assertEqual(len(ch.evidence), 1)
        self.assertEqual(ch.evidence[0].page_or_slide, "Page 43")

    def test_heuristic_qa_audit(self):
        # Create a challenge with proper fields
        challenge = ChallengeSchema(
            title="Test Challenge",
            challenge_type="what_if",
            grade="8",
            difficulty="medium",
            estimated_time_minutes=15,
            learning_focus="Reasoning",
            scenario="A detailed scenario describing the environmental situation and plant response under heat stress conditions.",
            student_role="Plant Biologist",
            central_question="What will happen if temperature rises to 40C?",
            evidence=[
                EvidenceItem(text="RuBisCO denatures above 38C", source="Bio.pdf", page_or_slide="Page 44"),
                EvidenceItem(text="Stomata close to prevent water loss", source="Bio.pdf", page_or_slide="Page 44"),
            ],
            rubric=[
                RubricCriterion(criterion="Problem ID", description="Identifies heat effect", max_score=4, weight=0.33),
                RubricCriterion(criterion="Evidence Use", description="Cites RuBisCO", max_score=4, weight=0.33),
                RubricCriterion(criterion="Justification", description="Explains stomata closure", max_score=4, weight=0.34),
            ],
        )
        qa = run_heuristic_qa(challenge)
        self.assertEqual(qa.status, "pass")
        self.assertGreaterEqual(qa.score, 70)

    def test_patterns_taxonomy_and_selection(self):
        from app.ai.patterns import (
            TAXONOMY_CLUSTERS,
            CRITICAL_PATTERNS,
            get_all_clusters,
            get_patterns_for_cluster,
            select_patterns_for_generation,
            format_patterns_prompt_section,
        )
        # Verify 8 clusters
        clusters = get_all_clusters()
        self.assertGreaterEqual(len(clusters), 8)
        self.assertIn("Causal Reasoning", clusters)
        self.assertIn("Evidence & Data", clusters)

        # Verify pattern catalog
        self.assertGreaterEqual(len(CRITICAL_PATTERNS), 25)

        # Test pattern selection for 3 questions
        selected_3 = select_patterns_for_generation(
            cluster_name="All Clusters (Diverse Reasoning)",
            num_questions=3,
        )
        self.assertEqual(len(selected_3), 3)
        # Distinct patterns
        names = [p.name for p in selected_3]
        self.assertEqual(len(set(names)), 3)

        # Test prompt section formatting
        section = format_patterns_prompt_section(selected_3, tier="Tier 2: Ambiguous scenario")
        self.assertIn("COGNITIVE REASONING LEVEL: Tier 2: Ambiguous scenario", section)
        self.assertIn("TARGETED CRITICAL-THINKING PATTERNS", section)

    def test_challenge_set_schema(self):
        from app.ai.schemas import ChallengeSetSchema, ChallengeSchema
        cset = ChallengeSetSchema(
            title="Photosynthesis Inquiry Set",
            subject="Biology",
            grade="8",
            topic="Photosynthesis",
            overview_scenario="Investigating tomato yields in a controlled greenhouse.",
            challenges=[
                ChallengeSchema(
                    question_number=1,
                    title="Q1: Light Saturation",
                    challenge_type="evidence_analysis",
                    pattern="Evidence Evaluation",
                    pattern_cluster="Evidence & Data",
                    tier="Tier 1: Direct application",
                    skill_targeted="Evaluating data validity",
                    grade="8",
                    difficulty="medium",
                    learning_focus="Data evaluation",
                    scenario="Scenario text",
                    student_role="Advisor",
                    central_question="Which factor limits yield?",
                    evidence=[],
                    rubric=[],
                )
            ]
        )
        self.assertEqual(len(cset.challenges), 1)
        self.assertEqual(cset.challenges[0].pattern, "Evidence Evaluation")
        self.assertEqual(cset.challenges[0].question_number, 1)


if __name__ == "__main__":
    unittest.main()
