"""
test_e2e_flow.py
End-to-end integration test verifying the complete happy path:
Load demo document -> Vector RAG retrieval -> Structured Generation -> QA Audit -> Student Evaluation.
"""
import unittest
import numpy as np
from app.rag.vectorstore import VectorStore
from app.rag.retrieval import PedagogicalRetriever
from app.ai.providers import BaseLLMProvider
from app.ai.generation import generate_challenge
from app.ai.evaluation import evaluate_student_response
from data.sample_demo import load_demo_document, SAMPLE_STRONG_RESPONSE, SAMPLE_WEAK_RESPONSE


class MockEducationalProvider(BaseLLMProvider):
    """Mock LLM Provider returning valid, deterministic JSON for CI testing."""

    def generate_text(self, prompt: str, temperature: float = 0.3, response_format_json: bool = False) -> str:
        if "Critic Minds Master Evaluator" in prompt:
            # Check if student response is strong or weak
            student_section = prompt.split("STUDENT'S SUBMITTED RESPONSE:")[-1] if "STUDENT'S SUBMITTED RESPONSE:" in prompt else prompt
            if "doubled the rate" in student_section:
                return """{
                    "total_score": 15,
                    "max_score": 16,
                    "criteria": [
                        {"criterion": "Evidence Selection", "score": 4, "max_score": 4, "feedback": "Superb citation of Page 43 bubble rates."},
                        {"criterion": "Reasoning & Alternatives", "score": 4, "max_score": 4, "feedback": "Accurately noted CO2 plateau and RuBisCO sensitivity."},
                        {"criterion": "Justified Conclusion", "score": 4, "max_score": 4, "feedback": "Well defended recommendation."},
                        {"criterion": "Problem Context", "score": 3, "max_score": 4, "feedback": "Thorough grasp of greenhouse factors."}
                    ],
                    "strengths": ["Clear citation of quantitative bubble rates", "Addresses counter-arguments"],
                    "improvements": ["Could elaborate on night-time greenhouse ventilation"],
                    "overall_feedback": "Exemplary critical thinking with nuanced causal justification."
                }"""
            else:
                return """{
                    "total_score": 6,
                    "max_score": 16,
                    "criteria": [
                        {"criterion": "Evidence Selection", "score": 1, "max_score": 4, "feedback": "No specific evidence or page numbers cited."},
                        {"criterion": "Reasoning & Alternatives", "score": 2, "max_score": 4, "feedback": "Assumes more light always helps; ignored limiting factor plateau."},
                        {"criterion": "Justified Conclusion", "score": 2, "max_score": 4, "feedback": "Unsupported conclusion."},
                        {"criterion": "Problem Context", "score": 1, "max_score": 4, "feedback": "Oversimplifies photosynthesis to generic recall."}
                    ],
                    "strengths": ["Understands plants require light"],
                    "improvements": ["Cite specific evidence from the text", "Examine what happens when light is no longer limiting"],
                    "overall_feedback": "Response is based on simple recall rather than analyzing the evidence."
                }"""

        elif "Critic Minds Quality Auditor" in prompt:
            return """{
                "status": "pass",
                "score": 95,
                "issues": [],
                "regenerate": false
            }"""

        elif "Number of Questions to Generate:" in prompt:
            # Multi-question generation response
            return """{
                "title": "Comprehensive Photosynthesis Inquiry Set",
                "subject": "Biology",
                "grade": "8",
                "topic": "Photosynthesis",
                "overview_scenario": "Commercial greenhouse growers in Ontario are testing light, CO2, and temperature controls to optimize harvest.",
                "challenges": [
                    {
                        "question_number": 1,
                        "title": "Part 1: Evidence Evaluation of Bubble Rates",
                        "challenge_type": "evidence_analysis",
                        "pattern": "Evidence Evaluation",
                        "pattern_cluster": "Evidence & Data",
                        "tier": "Tier 1: Direct application",
                        "skill_targeted": "Distinguishing strong vs weak evidence",
                        "grade": "8",
                        "difficulty": "medium",
                        "estimated_time_minutes": 10,
                        "learning_focus": "Interpreting bubble production plateaus",
                        "scenario": "Growers compare bubble rates from light intensity vs CO2 enrichment.",
                        "student_role": "Science Consultant",
                        "central_question": "Which piece of evidence most strongly indicates that CO2 has reached its saturation threshold?",
                        "evidence": [
                            {
                                "text": "At elevated CO2 (0.10%), bubble count increased from 48 to 82 bubbles/min before plateauing.",
                                "source": "Biology_Grade8_Photosynthesis_Chapter4.pdf",
                                "page_or_slide": "Page 43"
                            }
                        ],
                        "task_instructions": ["Examine data", "Evaluate strongest evidence"],
                        "response_requirements": ["Cite page 43"],
                        "hints": ["Look for where rate flattens"],
                        "extension_question": "What other variable could be limiting?",
                        "possible_interpretations": ["CO2 is saturated", "Light is saturated"],
                        "rubric": [
                            {"criterion": "Evidence Selection", "description": "Accurate citations", "max_score": 4, "weight": 0.5},
                            {"criterion": "Reasoning", "description": "Logical inference", "max_score": 4, "weight": 0.5}
                        ]
                    },
                    {
                        "question_number": 2,
                        "title": "Part 2: What-If Heat Stress Perturbation",
                        "challenge_type": "what_if",
                        "pattern": "Cause vs. Correlation",
                        "pattern_cluster": "Causal Reasoning",
                        "tier": "Tier 1: Direct application",
                        "skill_targeted": "Avoiding post-hoc reasoning and causal mechanisms",
                        "grade": "8",
                        "difficulty": "medium",
                        "estimated_time_minutes": 10,
                        "learning_focus": "Enzymatic denaturation vs stomatal response",
                        "scenario": "Greenhouse heating fails, raising midday temperature to 41C.",
                        "student_role": "Horticultural Advisor",
                        "central_question": "Did the temperature increase directly cause the yield collapse, or was it stomatal closure and water deficit? Explain the causal chain.",
                        "evidence": [
                            {
                                "text": "Above 38C, RuBisCO enzymes denature and stomata close, halving glucose synthesis.",
                                "source": "Biology_Grade8_Photosynthesis_Chapter4.pdf",
                                "page_or_slide": "Page 44"
                            }
                        ],
                        "task_instructions": ["Trace physiological steps", "Disentangle temperature vs water"],
                        "response_requirements": ["Explain enzyme denaturation"],
                        "hints": ["Consider RuBisCO kinetics"],
                        "extension_question": "How does nocturnal respiration change at 40C?",
                        "possible_interpretations": ["Direct enzyme damage", "Indirect CO2 starvation"],
                        "rubric": [
                            {"criterion": "Causal Mechanism", "description": "Explains denaturation", "max_score": 4, "weight": 0.5},
                            {"criterion": "Justified Conclusion", "description": "Grounded synthesis", "max_score": 4, "weight": 0.5}
                        ]
                    }
                ]
            }"""

        else:
            # Single Challenge Generation Prompt
            return """{
                "title": "The Greenhouse Limiting Factor Conundrum",
                "challenge_type": "evidence_analysis",
                "grade": "8",
                "difficulty": "medium",
                "estimated_time_minutes": 15,
                "learning_focus": "Evaluating empirical evidence regarding photosynthetic limiting factors",
                "scenario": "Commercial greenhouse growers in Ontario increased lighting hours but noticed no increase in tomato yield. They have budget for either heating ventilation or CO2 canisters.",
                "student_role": "Horticultural Science Consultant",
                "central_question": "Based on the evidence, which resource should the growers invest in to optimize yield?",
                "evidence": [
                    {
                        "text": "At elevated CO2 (0.10%), bubble count increased from 48 to 82 bubbles/min before plateauing.",
                        "source": "Biology_Grade8_Photosynthesis_Chapter4.pdf",
                        "page_or_slide": "Page 43"
                    },
                    {
                        "text": "Above 38C, RuBisCO enzymes denature and stomata close, halving glucose synthesis.",
                        "source": "Biology_Grade8_Photosynthesis_Chapter4.pdf",
                        "page_or_slide": "Page 44"
                    }
                ],
                "task_instructions": [
                    "Evaluate the bubble production data for light vs CO2",
                    "Determine which factor is currently limiting yield",
                    "Defend your recommendation against the alternative"
                ],
                "response_requirements": [
                    "Cite at least 2 pieces of evidence with page numbers",
                    "Address the alternative option"
                ],
                "hints": ["Look at what happens to the rate after 0.10% CO2"],
                "extension_question": "How would stomatal closure impact water loss vs carbon intake?",
                "possible_interpretations": ["CO2 enrichment is optimal", "Temperature regulation is primary"],
                "rubric": [
                    {"criterion": "Evidence Selection", "description": "Accurately integrates data", "max_score": 4, "weight": 0.25},
                    {"criterion": "Reasoning & Alternatives", "description": "Addresses trade-offs", "max_score": 4, "weight": 0.25},
                    {"criterion": "Justified Conclusion", "description": "Coherent synthesis", "max_score": 4, "weight": 0.25},
                    {"criterion": "Problem Context", "description": "Understands limiting factors", "max_score": 4, "weight": 0.25}
                ]
            }"""



class TestEndToEndFlow(unittest.TestCase):

    def setUp(self):
        self.store = VectorStore()
        self.doc = load_demo_document()
        # Seed pseudo embeddings for the 3 demo pages
        dim = 384
        vectors = np.zeros((len(self.doc.chunks), dim), dtype=np.float32)
        for i in range(len(self.doc.chunks)):
            vectors[i, i % dim] = 1.0
        self.store.add_document(self.doc, vectors)
        self.provider = MockEducationalProvider()

    def test_full_pipeline(self):
        # 1. Retrieval
        retriever = PedagogicalRetriever(self.store)
        retrieved = retriever.retrieve(
            subject="Biology",
            grade="8",
            topic="Photosynthesis",
            challenge_type="evidence_analysis",
            doc_id=self.doc.document_id,
            top_k=2,
        )
        self.assertGreaterEqual(len(retrieved), 2)
        for r in retrieved:
            self.assertTrue("Page" in r.chunk.citation)

        # 2. Challenge Generation
        challenge, qa = generate_challenge(
            subject="Biology",
            grade="8",
            topic="Photosynthesis",
            challenge_type="evidence_analysis",
            difficulty="medium",
            estimated_time=15,
            teacher_instructions="Focus on Ontario greenhouse data",
            retrieved_results=retrieved,
            provider=self.provider,
        )
        self.assertEqual(challenge.title, "The Greenhouse Limiting Factor Conundrum")
        self.assertEqual(qa.status, "pass")
        self.assertGreaterEqual(qa.score, 90)
        self.assertGreaterEqual(len(challenge.evidence), 2)
        self.assertIn("Page 43", challenge.evidence[0].page_or_slide)

        # 3. Student Evaluation: Strong response
        strong_eval = evaluate_student_response(
            challenge=challenge,
            student_response=SAMPLE_STRONG_RESPONSE,
            provider=self.provider,
        )
        self.assertGreaterEqual(strong_eval.total_score, 14)
        self.assertTrue(len(strong_eval.strengths) > 0)

        # 4. Student Evaluation: Weak response
        weak_eval = evaluate_student_response(
            challenge=challenge,
            student_response=SAMPLE_WEAK_RESPONSE,
            provider=self.provider,
        )
        self.assertLess(weak_eval.total_score, 10)
        self.assertGreater(strong_eval.total_score, weak_eval.total_score)
        self.assertTrue(len(weak_eval.improvements) > 0)

    def test_multi_question_pipeline(self):
        from app.ai.generation import generate_challenge_set
        from app.ai.schemas import ChallengeSetSchema

        retriever = PedagogicalRetriever(self.store)
        retrieved = retriever.retrieve(
            subject="Biology",
            grade="8",
            topic="Photosynthesis",
            challenge_type="evidence_analysis",
            doc_id=self.doc.document_id,
            top_k=4,
        )

        cset, qas = generate_challenge_set(
            subject="Biology",
            grade="8",
            topic="Photosynthesis",
            challenge_type="evidence_analysis",
            difficulty="medium",
            estimated_time=20,
            teacher_instructions="Focus on empirical bubble rates",
            retrieved_results=retrieved,
            provider=self.provider,
            num_questions=2,
            pattern_cluster="All Clusters (Diverse Reasoning)",
            tier="Tier 1: Direct application",
        )

        self.assertIsInstance(cset, ChallengeSetSchema)
        self.assertEqual(len(cset.challenges), 2)
        self.assertEqual(len(qas), 2)
        self.assertEqual(cset.challenges[0].question_number, 1)
        self.assertEqual(cset.challenges[1].question_number, 2)
        self.assertTrue(bool(cset.challenges[0].pattern))
        self.assertTrue(bool(cset.challenges[1].pattern))
        self.assertEqual(qas[0].status, "pass")
        self.assertEqual(qas[1].status, "pass")


if __name__ == "__main__":
    unittest.main()
