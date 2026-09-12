"""
patterns.py
Unified Critical-Thinking Questioning Patterns & Cognitive Taxonomy for Critic Minds.

Consolidates:
1. Core Critical-Thinking Patterns (Assumption Identification, Evidence Evaluation, Cause vs Correlation, etc.)
2. Assessment-Item / Question Patterns (Real-life Cases, Problem Scenarios, Dilemmas, What-If, Predictions, etc.)
3. Cognitive Complexity Tiers (Tier 1: Direct, Tier 2: Ambiguous, Tier 3: Multi-step)
4. Extended Dimensions (Definitional Reasoning, Criteria Setting, Stakeholder Mapping, Trade-offs, Systems, etc.)
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class CriticalPattern:
    id: str
    name: str
    cluster: str
    skill_targeted: str
    typical_stem: str
    description: str


# 8 Unified Clusters
TAXONOMY_CLUSTERS: Dict[str, str] = {
    "All Clusters (Diverse Reasoning)": "Distribute diverse, complementary critical-thinking patterns across questions.",
    "Assumption & Framing": "Detecting hidden premises, conceptual boundaries, clarifying terms, and surfacing underlying values.",
    "Evidence & Data": "Distinguishing strong vs. weak evidence, evaluating sources, interpreting quantitative data, calibrated inference.",
    "Causal Reasoning": "Differentiating cause vs correlation, uncovering causal mechanisms, counterfactuals, and path dependence.",
    "Perspective & Ethics": "Recognizing subjectivity and bias, stakeholder power mapping, ethical frameworks, and fairness dilemmas.",
    "Argumentation": "Steelmanning counterarguments, spotting logical fallacies, dialectical synthesis across conflicting sources.",
    "Systems & Futures": "Holistic second-order effects, feedback loops, tipping points, hypothetical disruptions (what-if), and predictions.",
    "Decision & Action": "Setting evaluation criteria, analyzing trade-offs, deciding under deep uncertainty, feasibility, and adaptive monitoring.",
    "Metacognition & Transfer": "Transferring principles to novel scenarios, self-evaluating reasoning limits, model critique, and interdisciplinary synthesis.",
}

# Complete catalog of critical thinking patterns
CRITICAL_PATTERNS: List[CriticalPattern] = [
    # 1. Assumption & Framing
    CriticalPattern(
        id="assumption_id",
        name="Assumption Identification",
        cluster="Assumption & Framing",
        skill_targeted="Detecting hidden premises and unstated assertions",
        typical_stem="What underlying assumption is being made here? Why might it be flawed or incomplete?",
        description="Encourages learners to uncover unstated presuppositions that an argument relies upon."
    ),
    CriticalPattern(
        id="clarification_def",
        name="Clarification & Definitional Reasoning",
        cluster="Assumption & Framing",
        skill_targeted="Clarifying conceptual boundaries and term consistency",
        typical_stem="What exactly is meant by this concept in this context? Is the term being applied consistently?",
        description="Challenges ambiguous or shifting definitions that lead to flawed inferences."
    ),
    CriticalPattern(
        id="problem_framing",
        name="Problem Framing & Reframing",
        cluster="Assumption & Framing",
        skill_targeted="Questioning premise boundaries and asking the right question",
        typical_stem="Is this the right problem to solve? What hidden constraints are built into how this situation is framed?",
        description="Asks students to look beyond the given framing and consider alternative definitions of the core dilemma."
    ),
    CriticalPattern(
        id="values_clarification",
        name="Values Clarification",
        cluster="Assumption & Framing",
        skill_targeted="Surfacing conflicting foundational priorities",
        typical_stem="Which fundamental values are in tension here (e.g., efficiency, equity, sustainability, freedom)?",
        description="Highlights that many disagreements stem from conflicting fundamental values rather than just facts."
    ),

    # 2. Evidence & Data
    CriticalPattern(
        id="evidence_eval",
        name="Evidence Evaluation",
        cluster="Evidence & Data",
        skill_targeted="Distinguishing strong vs. weak empirical evidence",
        typical_stem="Which piece of evidence most strongly supports or contradicts the claim? How reliable and relevant is it?",
        description="Prompts students to interrogate source quality, sample size, relevance, and methodological rigor."
    ),
    CriticalPattern(
        id="inference_incomplete",
        name="Inference from Incomplete Data",
        cluster="Evidence & Data",
        skill_targeted="Calibrated inference and avoiding overreach",
        typical_stem="What can you reliably infer from this limited data? What remains uncertain and requires further investigation?",
        description="Teaches intellectual humility and calibrated reasoning under data gaps."
    ),
    CriticalPattern(
        id="quantitative_literacy",
        name="Data & Quantitative Literacy",
        cluster="Evidence & Data",
        skill_targeted="Interpreting rates, graphs, baselines, and statistics",
        typical_stem="What does the quantitative data indicate about rates or baselines? Could the visual graph be misleading?",
        description="Engages students in mathematical and empirical data analysis from charts and tables."
    ),
    CriticalPattern(
        id="source_credibility",
        name="Source & Expertise Evaluation",
        cluster="Evidence & Data",
        skill_targeted="Evaluating authority, incentives, and potential conflicts of interest",
        typical_stem="Who produced this evidence? What expertise and potential incentives or biases might influence their report?",
        description="Guides students to evaluate source origins and structural incentives."
    ),

    # 3. Causal Reasoning
    CriticalPattern(
        id="cause_vs_correlation",
        name="Cause vs. Correlation",
        cluster="Causal Reasoning",
        skill_targeted="Avoiding post-hoc reasoning and spotting confounding variables",
        typical_stem="Did factor X cause event Y, or is this merely a correlation? What alternative explanations exist?",
        description="Helps students disentangle concurrent occurrences from true causal relationships."
    ),
    CriticalPattern(
        id="causal_mechanism",
        name="Causal Mechanism Explanation",
        cluster="Causal Reasoning",
        skill_targeted="Tracing step-by-step physical or biological mechanisms",
        typical_stem="What is the precise step-by-step mechanism by which intervention X leads to outcome Y?",
        description="Requires explaining the intermediate physiological, ecological, or physical steps."
    ),
    CriticalPattern(
        id="counterfactual_reasoning",
        name="Counterfactual Reasoning",
        cluster="Causal Reasoning",
        skill_targeted="Testing necessity and sufficiency through hypothetical subtraction",
        typical_stem="What would have occurred if factor X had not taken place? Was X necessary, sufficient, or contributory?",
        description="Isolates the unique causal contribution of individual factors."
    ),
    CriticalPattern(
        id="path_dependence",
        name="Historical & Path-Dependence Analysis",
        cluster="Causal Reasoning",
        skill_targeted="Understanding legacy effects and lock-in",
        typical_stem="How did historical events or past decisions create this current constraint? What lock-in exists?",
        description="Examines how past conditions shape present possibilities and constraints."
    ),

    # 4. Perspective & Ethics
    CriticalPattern(
        id="perspective_bias",
        name="Perspective-Taking & Bias Detection",
        cluster="Perspective & Ethics",
        skill_targeted="Recognizing subjectivity, cognitive bias, and diverse viewpoints",
        typical_stem="How would different stakeholders perceive this situation? What cognitive bias might influence their view?",
        description="Cultivates cognitive empathy and recognition of confirmation bias and self-interest."
    ),
    CriticalPattern(
        id="ethical_dilemma",
        name="Ethical and Social Dilemmas",
        cluster="Perspective & Ethics",
        skill_targeted="Weighing social benefits vs ecological/moral costs",
        typical_stem="How should social needs be balanced against ecological impact or ethical imperatives in this decision?",
        description="Forces explicit evaluation of competing moral duties and stakeholder welfare."
    ),
    CriticalPattern(
        id="stakeholder_mapping",
        name="Stakeholder Mapping & Power Analysis",
        cluster="Perspective & Ethics",
        skill_targeted="Identifying who benefits, who bears costs, and who is excluded",
        typical_stem="Who gains the primary benefit, who absorbs the externalized costs, and who lacks a voice in this decision?",
        description="Reveals distributional asymmetry and power dynamics."
    ),
    CriticalPattern(
        id="intergenerational_justice",
        name="Intergenerational Justice",
        cluster="Perspective & Ethics",
        skill_targeted="Long-term ethical responsibility toward future cohorts",
        typical_stem="What obligations do present decision-makers owe to future generations who cannot participate today?",
        description="Extends the temporal boundary of ethics across decades."
    ),

    # 5. Argumentation
    CriticalPattern(
        id="counterargument_steelmanning",
        name="Counterargument Construction",
        cluster="Argumentation",
        skill_targeted="Steelmanning opposing views and testing resilience",
        typical_stem="What is the most formidable counterargument to this claim? Does the primary hypothesis survive it?",
        description="Trains students to build the strongest possible opposing case rather than knocking down straw men."
    ),
    CriticalPattern(
        id="fallacy_spotting",
        name="Logical Fallacy Spotting",
        cluster="Argumentation",
        skill_targeted="Metacognition regarding reasoning errors and invalid deductions",
        typical_stem="Identify the reasoning flaw or fallacy in this claim. How can the argument be repaired into a valid deduction?",
        description="Diagnoses false dichotomies, slippery slopes, circular arguments, and hasty generalizations."
    ),
    CriticalPattern(
        id="synthesis_conflicting",
        name="Synthesis Across Sources",
        cluster="Argumentation",
        skill_targeted="Dialectical, integrative synthesis of conflicting evidence",
        typical_stem="The two sources provide conflicting observations. Synthesize an integrative position that accounts for both.",
        description="Replaces superficial either/or thinking with nuanced dialectical integration."
    ),
    CriticalPattern(
        id="conflict_resolution",
        name="Conflict Resolution & Negotiation",
        cluster="Argumentation",
        skill_targeted="Finding integrative, interest-based compromises",
        typical_stem="What negotiated compromise or creative policy could satisfy the core interests of both competing sides?",
        description="Focuses on practical problem-solving between adversarial stances."
    ),

    # 6. Systems & Futures
    CriticalPattern(
        id="systems_unintended",
        name="Systems Thinking & Unintended Consequences",
        cluster="Systems & Futures",
        skill_targeted="Holistic reasoning and anticipating ripple effects",
        typical_stem="If this intervention is deployed, what second-order or unintended cascading effects might follow in the system?",
        description="Discourages linear thinking by tracing network feedback across ecological or economic networks."
    ),
    CriticalPattern(
        id="feedback_tipping",
        name="Feedback Loops & Tipping Points",
        cluster="Systems & Futures",
        skill_targeted="Identifying reinforcing loops, balancing loops, and thresholds",
        typical_stem="Is this system governed by a reinforcing or balancing feedback loop? Where might a dangerous tipping point lie?",
        description="Analyzes non-linear dynamics and self-amplifying cascades."
    ),
    CriticalPattern(
        id="what_if_disruption",
        name="What-If Hypothetical Disruptions",
        cluster="Systems & Futures",
        skill_targeted="Exploring system perturbations and resilience",
        typical_stem="What if variable X changes dramatically (e.g. key species removed, temperature spikes)? How will the system adapt?",
        description="Standard what-if scenario exploration testing system boundaries."
    ),
    CriticalPattern(
        id="prediction_exercises",
        name="Prediction Exercises",
        cluster="Systems & Futures",
        skill_targeted="Projecting future states using ecological and physical laws",
        typical_stem="Based on current trends and scientific laws, predict the state of this system in 1 year vs 10 years. Justify.",
        description="Demands grounded forward projections backed by scientific principles."
    ),

    # 7. Decision & Action
    CriticalPattern(
        id="criteria_setting",
        name="Criteria Setting & Evaluation Standards",
        cluster="Decision & Action",
        skill_targeted="Establishing transparent, weighted decision rubrics",
        typical_stem="What objective criteria should be used to evaluate these solutions? How should those criteria be weighted?",
        description="Moves students from gut feelings to structured multi-criteria decision analysis."
    ),
    CriticalPattern(
        id="tradeoff_analysis",
        name="Trade-off & Equity Analysis",
        cluster="Decision & Action",
        skill_targeted="Weighing unavoidable costs against tangible benefits",
        typical_stem="What unavoidable trade-offs are created by this choice? Which trade-off is most defensible and why?",
        description="Forces recognition that no complex solution is cost-free."
    ),
    CriticalPattern(
        id="decision_uncertainty",
        name="Decision-Making Under Deep Uncertainty",
        cluster="Decision & Action",
        skill_targeted="Choosing robust, precautionary, or no-regret strategies",
        typical_stem="Given that the future conditions cannot be predicted with certainty, what is the most robust, no-regret action?",
        description="Cultivates resilience and the precautionary principle when risk cannot be eliminated."
    ),
    CriticalPattern(
        id="monitoring_adaptive",
        name="Monitoring & Adaptive Management",
        cluster="Decision & Action",
        skill_targeted="Designing observation, intervention, and iterative feedback loops",
        typical_stem="What key indicators should be monitored after intervention? How will we know if we need to adjust the plan?",
        description="Emphasizes that scientific and civic management is iterative rather than one-and-done."
    ),

    # 8. Metacognition & Transfer
    CriticalPattern(
        id="scenario_transfer",
        name="Scenario-Based Application & Transfer",
        cluster="Metacognition & Transfer",
        skill_targeted="Transferring abstract principles to novel, unfamiliar contexts",
        typical_stem="Apply this scientific principle to a completely new situation. Where does the analogy fit, and where does it break down?",
        description="Deepens conceptual mastery by testing cross-domain transfer."
    ),
    CriticalPattern(
        id="metacognitive_calibration",
        name="Metacognitive Calibration",
        cluster="Metacognition & Transfer",
        skill_targeted="Assessing confidence, limits of knowledge, and self-bias",
        typical_stem="How confident are you in this conclusion? What specific new evidence or observation would prove you wrong?",
        description="Builds falsifiability and calibration into the student's thinking process."
    ),
    CriticalPattern(
        id="model_analogy_critique",
        name="Model & Analogy Critique",
        cluster="Metacognition & Transfer",
        skill_targeted="Recognizing the boundaries and simplifications of scientific models",
        typical_stem="In what ways is this model or analogy accurate, and where does it oversimplify or distort reality?",
        description="Teaches that models are useful approximations with distinct structural limits."
    ),
    CriticalPattern(
        id="interdisciplinary_integration",
        name="Interdisciplinary Integration",
        cluster="Metacognition & Transfer",
        skill_targeted="Combining biological, social, economic, and technological dimensions",
        typical_stem="How do the biological, economic, and sociological factors interact here to prevent a simplistic technical fix?",
        description="Integrates scientific facts with broader human systems."
    ),
]


COGNITIVE_TIERS = {
    "Tier 1: Direct application": "Clear scenario focusing on a single core critical-thinking concept with explicit variables.",
    "Tier 2: Ambiguous scenario": "Requires disambiguation, distinguishing signal from noisy/incomplete evidence, and handling uncertainty.",
    "Tier 3: Multi-step reasoning": "Combines 2 or more critical-thinking patterns (e.g. Cause vs Correlation + Trade-off Analysis + Unintended Consequences).",
}


def get_all_clusters() -> List[str]:
    """Returns list of cluster names."""
    return list(TAXONOMY_CLUSTERS.keys())


def get_patterns_for_cluster(cluster_name: str) -> List[CriticalPattern]:
    """Returns patterns belonging to a cluster (or all if diverse)."""
    if "All Clusters" in cluster_name:
        return CRITICAL_PATTERNS
    return [p for p in CRITICAL_PATTERNS if p.cluster.lower() == cluster_name.lower()]


def select_patterns_for_generation(
    cluster_name: str,
    num_questions: int,
    specific_pattern_name: Optional[str] = None
) -> List[CriticalPattern]:
    """
    Selects a coherent sequence of critical thinking patterns based on the requested count and cluster.
    """
    if specific_pattern_name:
        for p in CRITICAL_PATTERNS:
            if p.name.lower() == specific_pattern_name.lower():
                return [p] * num_questions

    pool = get_patterns_for_cluster(cluster_name)
    if not pool:
        pool = CRITICAL_PATTERNS

    # If diverse mix across clusters:
    if "All Clusters" in cluster_name:
        # Pick high-impact complementary progression:
        # Q1: Evidence / Assumption
        # Q2: Causal / What-If
        # Q3: Trade-off / Decision
        # Q4: Systems / Unintended
        # Q5: Metacognition / Synthesis
        priority_ids = [
            "evidence_eval",
            "cause_vs_correlation",
            "tradeoff_analysis",
            "systems_unintended",
            "counterargument_steelmanning",
        ]
        selected = []
        for pid in priority_ids[:num_questions]:
            match = next((p for p in CRITICAL_PATTERNS if p.id == pid), None)
            if match:
                selected.append(match)
        # Fill if needed
        while len(selected) < num_questions:
            selected.append(pool[len(selected) % len(pool)])
        return selected

    # Within a specific cluster, select up to num_questions distinct patterns
    return pool[:num_questions] if len(pool) >= num_questions else (pool * num_questions)[:num_questions]


def format_patterns_prompt_section(patterns: List[CriticalPattern], tier: str) -> str:
    """Formats pattern guidance text for injection into the LLM system prompt."""
    tier_desc = COGNITIVE_TIERS.get(tier, COGNITIVE_TIERS["Tier 1: Direct application"])
    lines = [
        f"COGNITIVE REASONING LEVEL: {tier}",
        f"Guideline: {tier_desc}",
        "",
        f"TARGETED CRITICAL-THINKING PATTERNS ({len(patterns)} Question{'s' if len(patterns)>1 else ''}):"
    ]
    for idx, p in enumerate(patterns, 1):
        lines.append(f"Question #{idx}:")
        lines.append(f"  - Pattern: {p.name} (Cluster: {p.cluster})")
        lines.append(f"  - Target Skill: {p.skill_targeted}")
        lines.append(f"  - Typical Inquiry Stem: \"{p.typical_stem}\"")
        lines.append(f"  - Pedagogy Note: {p.description}")
        lines.append("")
    return "\n".join(lines)
