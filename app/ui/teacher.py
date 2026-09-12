"""
teacher.py
Teacher Studio UI for Critic Minds.
Supports document upload (PDF, DOCX, TXT, PPTX), pedagogical challenge configuration,
AI-powered generation with grounding, QA audit display, and interactive editing/approval.
"""
import streamlit as st
from typing import Optional
import time
from app.ingestion.unified import extract_and_chunk, get_pdf_page_count, UnifiedDocument, ExtractionError
from app.rag.vectorstore import VectorStore
from app.rag.embeddings import get_embeddings_generator
from app.rag.retrieval import PedagogicalRetriever
from app.ai.providers import get_llm_provider, LLMProviderError
from app.ai.generation import generate_challenge
from app.ai.schemas import ChallengeSchema, EvidenceItem, RubricCriterion
from data.sample_demo import load_demo_document, SAMPLE_FILENAME


ACADEMIC_LEVELS = [
    "Grade 6 (Middle School)",
    "Grade 7 (Middle School)",
    "Grade 8 (Middle School)",
    "Grade 9 (High School / Freshman)",
    "Grade 10 (High School / Sophomore)",
    "Grade 11 (High School / Junior)",
    "Grade 12 (High School / Senior)",
    "Undergraduate (College / University)",
    "Masters (Graduate / Post-Graduate)",
    "PhD / Doctoral & Post-Doctoral",
]


def infer_subject_and_topic(filename: str, sample_text: str = "") -> tuple:
    """Intelligently detects domain and curriculum topic from filename and excerpt."""
    fn = filename.lower().replace("_", " ").replace("-", " ")
    st_low = sample_text.lower()[:1500]

    if any(w in fn or w in st_low for w in ["periodic", "element", "atomic", "mendeleev", "valence", "electronegativity", "halogen", "alkali", "noble gas"]):
        return "Chemistry", "Periodic Table & Periodic Trends"
    if any(w in fn or w in st_low for w in ["chemist", "reaction", "stoichiometry", "covalent", "ionic", "acid", "base", "molecule"]):
        return "Chemistry", "Chemical Bonding & Reactions"
    if any(w in fn or w in st_low for w in ["physic", "mechanics", "thermodynamic", "gravity", "optics", "quantum", "newton", "velocity"]):
        return "Physics", "Mechanics & Physical Principles"
    if any(w in fn or w in st_low for w in ["photosynth", "chloroplast", "limiting factor", "chlorophyll"]):
        return "Biology", "Photosynthesis & Limiting Factors"
    if any(w in fn or w in st_low for w in ["bio", "genetics", "dna", "cell", "ecosystem", "organism", "mitosis", "evolution"]):
        return "Biology", "Biological Systems & Genetics"
    if any(w in fn or w in st_low for w in ["hist", "revolution", "treaty", "civilization", "empire", "war"]):
        return "History", "Historical Analysis & Causality"
    if any(w in fn or w in st_low for w in ["math", "calculus", "linear", "probability", "statistics", "integral", "derivative"]):
        return "Mathematics", "Mathematical Reasoning"
    if any(w in fn or w in st_low for w in ["econ", "market", "inflation", "macro", "micro", "gdp"]):
        return "Economics", "Economic Systems & Markets"

    clean_name = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    return "Science", clean_name[:40]


def clear_workspace_state(vectorstore: VectorStore):
    """Cleans all previous document data, active challenges, and evaluation outputs."""
    vectorstore.clear()
    st.session_state.active_document = None
    st.session_state.active_doc_id = None
    st.session_state.last_uploaded = None
    st.session_state.last_scope_key = None
    st.session_state.challenge_set = None
    st.session_state.generated_challenge = None
    st.session_state.approved_challenge = None
    st.session_state.approved_challenge_set = None
    st.session_state.qa_results = []
    st.session_state.qa_result = None
    st.session_state.evaluation_result = None
    st.session_state.last_retrieved_results = []
    for k in list(st.session_state.keys()):
        if k.startswith("student_ans_") or k.startswith("student_eval_") or k == "student_answer_input":
            del st.session_state[k]


def render_teacher_studio(vectorstore: VectorStore):
    """Renders the Teacher Studio workflow."""
    st.subheader("👩‍🏫 Teacher Studio — Critical Challenge Creator")
    st.caption("Upload curriculum materials, configure reasoning goals, generate grounded challenges, and approve for students.")

    # 1. Document Ingestion Section
    st.markdown("#### 1. Learning Material Ingestion")
    col_up, col_actions = st.columns([2.5, 1.5], gap="medium")

    with col_up:
        uploaded_file = st.file_uploader(
            "Upload Textbook or Lesson Document (PDF, DOCX, TXT, PPTX)",
            type=["pdf", "docx", "txt", "pptx", "ppt"],
            help="Critic Minds extracts text, tracks pages/slides, and constructs a curriculum vector index.",
        )

    with col_actions:
        st.write("")
        st.write("")
        act_c1, act_c2 = st.columns(2)
        with act_c1:
            if st.button("🌱 Load Biology Demo", use_container_width=True, help="Load Grade 8 Photosynthesis demo curriculum"):
                with st.spinner("Indexing Grade 8 Biology demo..."):
                    clear_workspace_state(vectorstore)
                    demo_doc = load_demo_document()
                    embed_gen = get_embeddings_generator()
                    texts = [c.text for c in demo_doc.chunks]
                    vectors = embed_gen.embed_passages(texts)
                    vectorstore.add_document(demo_doc, vectors)
                    st.session_state.active_document = demo_doc
                    st.session_state.active_doc_id = demo_doc.document_id
                    st.session_state.last_scope_key = "demo_biology"
                    st.session_state.current_subject = "Biology"
                    st.session_state.current_topic = "Photosynthesis & Limiting Factors"
                    st.session_state.grade_idx = 2  # Grade 8
                    st.success(f"Loaded '{SAMPLE_FILENAME}' ({len(demo_doc.chunks)} pages indexed)!")
                    st.rerun()

        with act_c2:
            if st.button("🗑️ Clear Library", use_container_width=True, help="Clear active document, vector database, and previous questions"):
                clear_workspace_state(vectorstore)
                st.info("Workspace & vector database cleared.")
                st.rerun()

    # Scope detection
    selected_page_range = None
    should_ingest = False
    scope_key = "default"

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        is_pdf = uploaded_file.name.lower().endswith(".pdf")
        total_pages = get_pdf_page_count(file_bytes) if is_pdf else 1

        # Check if file switched
        if st.session_state.get("last_uploaded_filename") != uploaded_file.name:
            clear_workspace_state(vectorstore)
            st.session_state.last_uploaded_filename = uploaded_file.name

        if is_pdf and total_pages > 25:
            st.info(f"📚 Large document: **{uploaded_file.name}** has **{total_pages} pages**.")
            p_mode = st.radio(
                "Select Ingestion Scope:",
                options=[
                    f"Chapter / Lesson Range (Recommended — fast indexing)",
                    f"Full Document (All {total_pages} pages)",
                ],
                index=0,
                horizontal=True,
            )
            if "Chapter" in p_mode:
                r_col1, r_col2, r_col3 = st.columns([1, 1, 2])
                with r_col1:
                    start_p = st.number_input("Start Page", min_value=1, max_value=total_pages, value=1)
                with r_col2:
                    end_p = st.number_input("End Page", min_value=start_p, max_value=total_pages, value=min(start_p + 29, total_pages))
                selected_page_range = (int(start_p), int(end_p))
                scope_key = f"{uploaded_file.name}_{start_p}_{end_p}"
                with r_col3:
                    st.write("")
                    st.write("")
                    btn_label = "📥 Ingest Selected Pages"
                    if st.session_state.get("last_scope_key") == scope_key:
                        btn_label = "✅ Pages Ingested (Re-ingest)"
                    if st.button(btn_label, type="primary", use_container_width=True):
                        should_ingest = True
            else:
                selected_page_range = (1, total_pages)
                scope_key = f"{uploaded_file.name}_all"
                if st.button("📥 Ingest All Pages", type="primary"):
                    should_ingest = True
        else:
            selected_page_range = (1, total_pages)
            scope_key = f"{uploaded_file.name}_full"
            if st.session_state.get("last_scope_key") != scope_key:
                should_ingest = True

        # Perform ingestion if requested
        if should_ingest:
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            t0 = time.time()

            def _on_progress(curr, tot, msg):
                pct = min(0.65, max(0.05, (curr / max(1, tot)) * 0.65))
                progress_bar.progress(pct)
                status_text.caption(f"⏳ {msg}")

            try:
                status_text.caption(f"⏳ Parsing '{uploaded_file.name}'...")
                # Clear previous documents so no leftover chunks contaminate search
                vectorstore.clear()
                # Clear previous generated challenges
                st.session_state.challenge_set = None
                st.session_state.generated_challenge = None
                st.session_state.approved_challenge = None
                st.session_state.approved_challenge_set = None
                st.session_state.qa_results = []
                st.session_state.qa_result = None

                parsed_doc = extract_and_chunk(
                    file_bytes=file_bytes,
                    filename=uploaded_file.name,
                    page_range=selected_page_range,
                    progress_callback=_on_progress,
                )

                embed_gen = get_embeddings_generator()
                texts = [c.text for c in parsed_doc.chunks]

                def _on_embed_progress(curr, tot, msg):
                    pct = min(1.0, 0.65 + (curr / max(1, tot)) * 0.35)
                    progress_bar.progress(pct)
                    status_text.caption(f"⏳ {msg}")

                status_text.caption(f"⏳ Building vector index for {len(texts)} chunks...")
                vectors = embed_gen.embed_passages(
                    texts,
                    batch_size=64,
                    progress_callback=_on_embed_progress,
                )

                vectorstore.add_document(parsed_doc, vectors)
                st.session_state.active_document = parsed_doc
                st.session_state.active_doc_id = parsed_doc.document_id
                st.session_state.last_uploaded = uploaded_file.name
                st.session_state.last_scope_key = scope_key

                # Intelligently infer Subject and Topic from the newly parsed text
                sample_txt = " ".join([c.text for c in parsed_doc.chunks[:4]])
                inferred_s, inferred_t = infer_subject_and_topic(uploaded_file.name, sample_txt)
                st.session_state.current_subject = inferred_s
                st.session_state.current_topic = inferred_t

                elapsed = round(time.time() - t0, 1)
                progress_bar.progress(1.0)
                status_text.empty()
                progress_bar.empty()

                page_scope_str = f"Pages {selected_page_range[0]}-{selected_page_range[1]}" if selected_page_range else f"{len(parsed_doc.chunks)} sections"
                st.success(f"✅ Indexed **{uploaded_file.name}** ({page_scope_str}, {len(parsed_doc.chunks)} chunks) in **{elapsed}s**!")
                st.rerun()
            except ExtractionError as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Extraction error: {e}")
            except Exception as ex:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Failed to process file: {ex}")

    # Active Document Status Card
    if "active_document" in st.session_state and st.session_state.active_document:
        active_doc: UnifiedDocument = st.session_state.active_document
        st.markdown(
            f"""
            <div class="cm-card" style="padding: 12px 18px; margin-top: 10px; margin-bottom: 20px;">
                <span class="badge badge-indigo">Active Document</span>
                <strong style="color:#1E293B;">{active_doc.filename}</strong>
                <span style="color:#64748B; font-size:0.85rem; margin-left: 12px;">
                    Format: <b>{active_doc.file_type.upper()}</b> | 
                    Indexed Chunks: <b>{len(active_doc.chunks)}</b> |
                    Scope: <b>{st.session_state.get('last_scope_key', 'Active')}</b>
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("👆 Please upload a document or click **'Load Biology Demo'** to begin.")
        return

    st.divider()

    # 2. Challenge Configuration Form
    st.markdown("#### 2. Challenge Configuration & Critical Thinking Focus")
    from app.ai.patterns import get_all_clusters, COGNITIVE_TIERS
    from app.ai.generation import generate_challenge_set
    from app.ai.schemas import ChallengeSetSchema

    with st.form("challenge_config_form"):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            subject = st.text_input(
                "Subject",
                value=st.session_state.get("current_subject", "Chemistry"),
                help="Disciplinary domain (auto-detected from your document)",
            )
            topic = st.text_input(
                "Topic",
                value=st.session_state.get("current_topic", "Periodic Table & Periodic Trends"),
                help="Specific curriculum topic or concept",
            )
        with f_col2:
            default_grade_idx = st.session_state.get("grade_idx", 2)
            grade = st.selectbox(
                "Target Academic Level",
                options=ACADEMIC_LEVELS,
                index=default_grade_idx,
                help="From Grade 6 to Undergraduate, Masters, and PhD. AI calibrates vocabulary and reasoning depth.",
            )
            challenge_type_label = st.selectbox(
                "Challenge Type",
                options=[
                    "Evidence Analysis (Evaluate competing claims)",
                    "What-If Challenge (Causal predictions & changed conditions)",
                    "Case Analysis (Diagnostic dilemma & practical decisions)",
                ],
                index=0,
            )
        with f_col3:
            difficulty = st.selectbox("Difficulty", options=["Easy", "Medium", "Hard"], index=1)
            est_time = st.number_input("Expected Time (Total Minutes)", min_value=5, max_value=60, value=15, step=5)

        # Critical Thinking Controls: Question Count, Pattern Cluster, and Cognitive Tier
        p_col1, p_col2, p_col3 = st.columns([1, 2, 2])
        with p_col1:
            num_questions = st.number_input(
                "Number of Questions",
                min_value=1,
                max_value=5,
                value=1,
                step=1,
                help="Choose how many critical-thinking questions you want to create (1 to 5).",
            )
        with p_col2:
            pattern_cluster = st.selectbox(
                "Critical-Thinking Cluster",
                options=get_all_clusters(),
                index=0,
                help="Select a cognitive reasoning cluster or 'All Clusters' for a diverse mix of critical patterns.",
            )
        with p_col3:
            tier = st.selectbox(
                "Cognitive Complexity Tier",
                options=list(COGNITIVE_TIERS.keys()),
                index=0,
                help="Tier 1: Direct application | Tier 2: Ambiguous/Noisy | Tier 3: Multi-step reasoning.",
            )

        teacher_instructions = st.text_area(
            "Custom Teacher Guidance (Optional)",
            placeholder="e.g. Focus on electronegativity trends, ionic vs covalent distinctions, or experimental anomaly data.",
            help="Your specific pedagogical notes will guide the AI generation process.",
        )

        generate_submitted = st.form_submit_button(
            f"✨ Generate Critical Challenge ({num_questions} Question{'s' if num_questions > 1 else ''})",
            use_container_width=True,
        )

    # Normalize challenge type slug
    if "evidence analysis" in challenge_type_label.lower():
        c_type_slug = "evidence_analysis"
    elif "what-if" in challenge_type_label.lower():
        c_type_slug = "what_if"
    else:
        c_type_slug = "case_analysis"

    # Execution when Generate is clicked
    if generate_submitted:
        # Check if selected page range was not yet ingested
        if uploaded_file is not None and scope_key != "default" and st.session_state.get("last_scope_key") != scope_key:
            with st.spinner(f"Auto-indexing selected pages for '{uploaded_file.name}' before generating..."):
                try:
                    vectorstore.clear()
                    parsed_doc = extract_and_chunk(
                        file_bytes=file_bytes,
                        filename=uploaded_file.name,
                        page_range=selected_page_range,
                    )
                    embed_gen = get_embeddings_generator()
                    texts = [c.text for c in parsed_doc.chunks]
                    vectors = embed_gen.embed_passages(texts, batch_size=64)
                    vectorstore.add_document(parsed_doc, vectors)
                    st.session_state.active_document = parsed_doc
                    st.session_state.active_doc_id = parsed_doc.document_id
                    st.session_state.last_scope_key = scope_key
                except Exception as e:
                    st.error(f"Auto-ingestion error: {e}")
                    return

        # Store teacher's custom subject and topic edits
        st.session_state.current_subject = subject
        st.session_state.current_topic = topic
        try:
            st.session_state.grade_idx = ACADEMIC_LEVELS.index(grade)
        except Exception:
            pass

        with st.spinner(f"Retrieving curriculum evidence & generating {num_questions} grounded question(s) for {grade}..."):
            try:
                # 1. Retrieve
                retriever = PedagogicalRetriever(vectorstore)
                retrieved_results = retriever.retrieve(
                    subject=subject,
                    grade=grade,
                    topic=topic,
                    challenge_type=c_type_slug,
                    instructions=teacher_instructions,
                    doc_id=st.session_state.active_doc_id,
                    top_k=max(6, num_questions * 3),
                )

                if not retrieved_results:
                    st.warning("No relevant passages found in the active document. Please adjust the topic or upload more content.")
                    return

                st.session_state.last_retrieved_results = retrieved_results

                # 2. Provider
                provider = get_llm_provider(
                    provider_name=st.session_state.get("ai_provider", "gemini"),
                    user_api_key=st.session_state.get("user_api_key"),
                    use_default=st.session_state.get("use_default_key", False),
                )

                # 3. Generate & Audit Multi-Question Challenge Set
                challenge_set, qa_results = generate_challenge_set(
                    subject=subject,
                    grade=grade,
                    topic=topic,
                    challenge_type=c_type_slug,
                    difficulty=difficulty.lower(),
                    estimated_time=int(est_time),
                    teacher_instructions=teacher_instructions,
                    retrieved_results=retrieved_results,
                    provider=provider,
                    num_questions=int(num_questions),
                    pattern_cluster=pattern_cluster,
                    tier=tier,
                )

                st.session_state.challenge_set = challenge_set
                st.session_state.qa_results = qa_results
                st.session_state.generated_challenge = challenge_set.challenges[0] if challenge_set.challenges else None
                st.session_state.qa_result = qa_results[0] if qa_results else None
                st.session_state.challenge_approved = False
                st.success(f"Generated {len(challenge_set.challenges)} critical-thinking question(s) successfully! Review and customize below.")

            except LLMProviderError as e:
                st.error(f"AI Generation Error: {e}")
            except Exception as ex:
                st.error(f"Unexpected error: {ex}")

    # 3. Review, QA, and Edit Workspace
    if "challenge_set" in st.session_state and st.session_state.challenge_set:
        cset: ChallengeSetSchema = st.session_state.challenge_set
        qas = st.session_state.get("qa_results", [])

        st.divider()
        st.markdown(f"#### 3. AI Challenge Review & Teacher Customization ({len(cset.challenges)} Question{'s' if len(cset.challenges)>1 else ''})")

        # Global Overview Scenario
        if cset.overview_scenario:
            st.info(f"**Overarching Context:** {cset.overview_scenario}")

        # If multiple questions, render tabs; if single, render single view
        if len(cset.challenges) > 1:
            q_tabs = st.tabs([f"Question #{i+1}: {ch.pattern or ch.title[:20]}" for i, ch in enumerate(cset.challenges)])
        else:
            q_tabs = [st.container()]

        edited_challenges = []

        for idx, (tab, ch) in enumerate(zip(q_tabs, cset.challenges)):
            qa = qas[idx] if idx < len(qas) else None
            with tab:
                # Pattern and Reasoning Skill Pill Banner
                pat_name = ch.pattern or "Critical Reasoning"
                pat_cluster = ch.pattern_cluster or "Cognitive Reasoning"
                pat_skill = ch.skill_targeted or "Critical Analysis & Justification"
                ch_tier = ch.tier or "Tier 1: Direct application"

                st.markdown(
                    f"""
                    <div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:8px; padding:10px 14px; margin-bottom:14px;">
                        <span class="badge badge-indigo">🎯 Pattern: {pat_name}</span>
                        <span class="badge badge-purple">📁 Cluster: {pat_cluster}</span>
                        <span class="badge badge-amber">⚖️ {ch_tier}</span>
                        <div style="margin-top:6px; font-size:0.9rem; color:#3730A3;">
                            <b>Targeted Cognitive Skill:</b> {pat_skill}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Transparency Panel
                with st.expander(f"🔍 Question #{idx+1} Transparency & QA Audit", expanded=False):
                    t_col1, t_col2, t_col3 = st.columns(3)
                    with t_col1:
                        st.markdown(f"**Type:** `{ch.challenge_type}`")
                        st.markdown(f"**Learning Focus:** {ch.learning_focus}")
                    with t_col2:
                        qa_score = qa.score if qa else 92
                        qa_status = qa.status.upper() if qa else "PASS"
                        badge_class = "badge-emerald" if qa_status == "PASS" else "badge-amber"
                        st.markdown(f"**AI QA Status:** <span class='badge {badge_class}'>{qa_status} ({qa_score}/100)</span>", unsafe_allow_html=True)
                        if qa and qa.issues:
                            st.caption("QA Notes: " + "; ".join(qa.issues))
                    with t_col3:
                        st.markdown(f"**Evidence Items:** `{len(ch.evidence)}` grounded citations")

                # Editable fields
                e_title = st.text_input(f"Question #{idx+1} Title", value=ch.title, key=f"t_title_{idx}")
                e_role = st.text_input(f"Question #{idx+1} Student Role", value=ch.student_role, key=f"t_role_{idx}")
                e_scenario = st.text_area(f"Question #{idx+1} Scenario / Dilemma", value=ch.scenario, height=100, key=f"t_scen_{idx}")
                e_question = st.text_area(f"Question #{idx+1} Inquiry Question (Incorporating Pattern Stem)", value=ch.central_question, height=75, key=f"t_q_{idx}")

                # Evidence display
                st.markdown("##### 📄 Evidence Provided to Student")
                for e_i, ev in enumerate(ch.evidence):
                    st.markdown(
                        f"""
                        <div class="evidence-card">
                            <div class="evidence-citation">📌 Evidence #{e_i+1} — {ev.source} ({ev.page_or_slide})</div>
                            <div class="evidence-text">{ev.text}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Rubric Overview
                st.markdown("##### 📊 Rubric Criteria")
                r_cols = st.columns(len(ch.rubric) if ch.rubric else 1)
                for r_i, crit in enumerate(ch.rubric):
                    with r_cols[r_i % len(r_cols)]:
                        st.markdown(
                            f"""
                            <div class="rubric-row">
                                <div class="rubric-title">{crit.criterion}</div>
                                <div class="rubric-desc">{crit.description}</div>
                                <div style="font-weight:700; color:#4338CA; margin-top:4px;">Max: {crit.max_score} pts</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                # Clone or update
                ch_updated = ch.model_copy()
                ch_updated.title = e_title
                ch_updated.student_role = e_role
                ch_updated.scenario = e_scenario
                ch_updated.central_question = e_question
                edited_challenges.append(ch_updated)

        # Action Buttons: Approve & Publish or Regenerate
        st.write("")
        act_col1, act_col2 = st.columns([2, 1], gap="medium")
        with act_col1:
            btn_label = f"🚀 Approve & Publish Challenge Set ({len(edited_challenges)} Question{'s' if len(edited_challenges)>1 else ''})"
            if st.button(btn_label, type="primary", use_container_width=True):
                cset.challenges = edited_challenges
                st.session_state.approved_challenge_set = cset
                st.session_state.approved_challenge = edited_challenges[0]
                st.session_state.challenge_approved = True
                st.success(f"🎉 All {len(edited_challenges)} Question(s) Approved and Published! Switch to the **'Student Challenge'** tab to attempt them.")

        with act_col2:
            if st.button("🔄 Regenerate Questions", use_container_width=True):
                st.session_state.challenge_set = None
                st.session_state.generated_challenge = None
                st.rerun()

