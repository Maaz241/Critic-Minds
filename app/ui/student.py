"""
student.py
Student Challenge UI for Critic Minds.
Renders the published challenge scenario, evidence citations, response submission box,
and interactive rubric-based reasoning evaluation results.
"""
import streamlit as st
from app.ai.schemas import ChallengeSchema, EvaluationResult
from app.ai.providers import get_llm_provider, LLMProviderError
from app.ai.evaluation import evaluate_student_response
from data.sample_demo import SAMPLE_STRONG_RESPONSE, SAMPLE_WEAK_RESPONSE


def get_sample_responses_for_challenge(ch: ChallengeSchema):
    """Returns grounded exemplary and weak responses tailored to the active challenge."""
    title_lower = (ch.title or "").lower()
    scenario_lower = (ch.scenario or "").lower()
    if any(w in title_lower or w in scenario_lower for w in ["greenhouse", "photosynthesis", "elodea", "bubbles"]):
        return SAMPLE_STRONG_RESPONSE, SAMPLE_WEAK_RESPONSE

    # Tailored to custom domain (e.g. Periodic Table / Chemistry / Physics)
    citations_text = []
    for ev in ch.evidence[:2]:
        citations_text.append(f"{ev.source} ({ev.page_or_slide}) stating that '{ev.text[:130]}...'")
    evidence_citation_str = " and ".join(citations_text) if citations_text else "the curriculum evidence"

    strong = (
        f"Based on the empirical evidence in the curriculum, particularly {evidence_citation_str}, "
        f"we can determine that the observed pattern is governed by core scientific principles and systematic trends. "
        f"I considered the alternative hypothesis that this is merely a coincidence or anomalous measurement, "
        f"but that fails to account for the reproducible relationship demonstrated in the cited source. "
        f"Therefore, the evidence directly justifies this conclusion while accounting for the system's boundary conditions."
    )
    weak = (
        "I think the answer is simple because that's just how the elements and science behave. "
        "I don't need to look at specific numbers or pages because it's pretty obvious."
    )
    return strong, weak


def render_student_challenge():
    """Renders the Student Challenge and Evaluation experience."""
    st.subheader("🧑‍🎓 Student Challenge — Reasoning Arena")
    st.caption("Review the situation and curriculum evidence, construct your argument, and receive rubric-based reasoning feedback.")

    # Check if a challenge set or challenge has been published
    cset = st.session_state.get("approved_challenge_set")
    single_ch = st.session_state.get("approved_challenge")

    if not cset and not single_ch:
        st.info("ℹ️ No challenge has been published yet. Please ask the teacher to publish a challenge in the **Teacher Studio**.")
        return

    challenges = cset.challenges if (cset and cset.challenges) else [single_ch]

    # Question selector if multiple questions exist
    if len(challenges) > 1:
        st.markdown(f"##### 🎯 Challenge Set: **{cset.title if cset else 'Critical Inquiry Set'}** ({len(challenges)} Questions)")
        q_options = list(range(len(challenges)))
        active_q_idx = st.radio(
            "Select Question:",
            options=q_options,
            format_func=lambda i: f"Question #{i+1}: {challenges[i].pattern or challenges[i].title[:22]}",
            horizontal=True,
            key="student_active_q_idx",
        )
    else:
        active_q_idx = 0

    ch: ChallengeSchema = challenges[active_q_idx]

    # 1. Challenge Header & Role
    pat_label = f"• Pattern: {ch.pattern}" if ch.pattern else ""
    tier_label = f"• {ch.tier}" if ch.tier else ""
    st.markdown(
        f"""
        <div class="cm-card">
            <span class="role-pill">🎯 Your Assigned Role: {ch.student_role or 'Student Analyst'}</span>
            <h2 style="margin: 0 0 10px 0; color: #1E293B;">{ch.title}</h2>
            <div style="margin-bottom: 12px;">
                <span class="badge badge-indigo">Academic Level: {ch.grade}</span>
                <span class="badge badge-purple">{ch.challenge_type.replace('_', ' ').title()}</span>
                <span class="badge badge-amber">{ch.difficulty.capitalize()}</span>
                <span class="badge badge-emerald">⏱️ ~{ch.estimated_time_minutes} min</span>
            </div>
            {f'<div style="margin-bottom: 10px; color:#4338CA; font-weight:600; font-size:0.9rem;">🧠 Focus: {ch.skill_targeted} {pat_label} {tier_label}</div>' if ch.skill_targeted or ch.pattern else ''}
            <p style="font-size: 1.05rem; color: #334155; line-height: 1.6; margin-bottom: 0;">
                {ch.scenario}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Central Question & Tasks
    st.markdown(
        f"""
        <div class="cm-card" style="border-left: 5px solid #4338CA; background: #F8FAFC;">
            <h4 style="color: #1E1B4B; margin: 0 0 8px 0;">❓ Central Inquiry Question</h4>
            <div style="font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 12px;">
                {ch.central_question}
            </div>
            <div style="font-size: 0.9rem; color: #475569;">
                <b>Task Instructions:</b>
                <ul style="margin-top: 4px; margin-bottom: 4px; padding-left: 20px;">
                    {''.join(f'<li>{t}</li>' for t in ch.task_instructions)}
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Evidence Cards with Citations
    st.markdown("#### 📄 Supporting Curriculum Evidence")
    st.caption("Cite these specific evidence statements to substantiate your reasoning.")
    for idx, ev in enumerate(ch.evidence):
        citation = f"{ev.source} — {ev.page_or_slide}" if ev.source else "Curriculum Source"
        st.markdown(
            f"""
            <div class="evidence-card">
                <div class="evidence-citation">Item #{idx+1}: {citation}</div>
                <div class="evidence-text">{ev.text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Hints Accordion
    if ch.hints:
        with st.expander("💡 Need a Hint? Socratic Guiding Questions"):
            for h in ch.hints:
                st.markdown(f"• *{h}*")

    st.divider()

    # 4. Student Response Submission Form
    st.markdown(f"#### ✍️ Your Reasoning & Argumentation (Question #{active_q_idx+1})")
    st.caption("Explain your conclusion using the evidence. Mention any alternative explanations you considered and why you accepted or rejected them.")

    # Storage key for per-question responses (directly bound to text_area key)
    ans_widget_key = f"student_ans_area_{active_q_idx}"
    eval_key = f"student_eval_{active_q_idx}"

    if ans_widget_key not in st.session_state:
        st.session_state[ans_widget_key] = ""

    strong_resp, weak_resp = get_sample_responses_for_challenge(ch)

    # Demo Fill Buttons for rapid test/presentation
    b_col1, b_col2, _ = st.columns([1, 1, 2])
    with b_col1:
        if st.button("📝 Fill Strong Response", key=f"fill_strong_{active_q_idx}", use_container_width=True, help="Load an exemplary evidence-supported response"):
            st.session_state[ans_widget_key] = strong_resp
            st.rerun()
    with b_col2:
        if st.button("⚠️ Fill Weak Response", key=f"fill_weak_{active_q_idx}", use_container_width=True, help="Load an unsupported recall-only response"):
            st.session_state[ans_widget_key] = weak_resp
            st.rerun()

    student_response = st.text_area(
        "Write your reasoned response below:",
        height=180,
        placeholder="Structure your answer with evidence, evaluate alternative views, and justify your recommendation...",
        key=ans_widget_key,
    )


    submit_col, _ = st.columns([1, 2])
    with submit_col:
        evaluate_clicked = st.button("📤 Submit for Reasoning Evaluation", type="primary", key=f"eval_btn_{active_q_idx}", use_container_width=True)

    if evaluate_clicked:
        if not student_response or len(student_response.strip()) < 15:
            st.warning("Please write a complete reasoning response before submitting.")
            return

        with st.spinner("Analyzing student reasoning, evidence usage, and justification depth..."):
            try:
                provider = get_llm_provider(
                    provider_name=st.session_state.get("ai_provider", "gemini"),
                    user_api_key=st.session_state.get("user_api_key"),
                    use_default=st.session_state.get("use_default_key", False),
                )
                eval_result = evaluate_student_response(
                    challenge=ch,
                    student_response=student_response,
                    provider=provider,
                )
                st.session_state[eval_key] = eval_result
                st.session_state.evaluation_result = eval_result
                st.success("Reasoning evaluation complete!")

            except LLMProviderError as e:
                st.error(f"Evaluation Error: {e}")
            except Exception as ex:
                st.error(f"Unexpected evaluation error: {ex}")

    # 5. Display Evaluation Results for the active question
    active_eval = st.session_state.get(eval_key) or st.session_state.get("evaluation_result")
    if active_eval:
        ev_res: EvaluationResult = active_eval

        st.divider()
        st.markdown("### 🎓 Reasoning Feedback & Assessment")

        percentage = round((ev_res.total_score / max(1, ev_res.max_score)) * 100)

        # Score & Summary Header
        sc_col1, sc_col2 = st.columns([1, 2], gap="medium")
        with sc_col1:
            st.markdown(
                f"""
                <div class="score-circle">
                    <div class="score-num">{ev_res.total_score}</div>
                    <div class="score-max">/ {ev_res.max_score} Total Points ({percentage}%)</div>
                    <div class="score-label">Reasoning Quality</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sc_col2:
            st.markdown(
                f"""
                <div class="cm-card" style="height: 100%;">
                    <h4 style="margin:0 0 8px 0; color:#1E293B;">Teacher Appraisal</h4>
                    <p style="color:#475569; font-size:0.95rem; line-height:1.5;">
                        {ev_res.overall_feedback}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Strengths and Improvements
        f_col1, f_col2 = st.columns(2, gap="medium")
        with f_col1:
            st.markdown(
                f"""
                <div class="cm-card" style="border-top: 4px solid #10B981;">
                    <h5 style="color:#065F46; margin:0 0 8px 0;">🌟 Key Reasoning Strengths</h5>
                    <ul style="padding-left: 20px; color:#334155; font-size:0.9rem;">
                        {''.join(f'<li>{s}</li>' for s in ev_res.strengths)}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with f_col2:
            st.markdown(
                f"""
                <div class="cm-card" style="border-top: 4px solid #F59E0B;">
                    <h5 style="color:#92400E; margin:0 0 8px 0;">🎯 Opportunities for Deeper Inquiry</h5>
                    <ul style="padding-left: 20px; color:#334155; font-size:0.9rem;">
                        {''.join(f'<li>{imp}</li>' for imp in ev_res.improvements)}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Criterion Breakdown
        st.markdown("#### 📋 Detailed Rubric Dimension Breakdown")
        for crit in ev_res.criteria:
            crit_pct = round((crit.score / max(1, crit.max_score)) * 100)
            color_badge = "badge-emerald" if crit_pct >= 75 else "badge-amber" if crit_pct >= 50 else "badge-indigo"
            st.markdown(
                f"""
                <div class="rubric-row">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="rubric-title">{crit.criterion}</span>
                        <span class="badge {color_badge}">{crit.score} / {crit.max_score} pts</span>
                    </div>
                    <div class="rubric-desc" style="margin-top: 6px; color:#334155;">
                        {crit.feedback}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
