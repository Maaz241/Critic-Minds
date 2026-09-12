"""
app.py
Critic Minds — Main Streamlit Application Entry Point.
GenAI-powered EdTech platform that transforms textbook and lesson content into
evidence-grounded critical-thinking challenges and evaluates student reasoning.
"""
import sys
import importlib

# Ensure fresh reload of all app submodules on every execution
import app.config
import app.ai.schemas
import app.ai.patterns
import app.ai.providers
import app.ai.prompts
import app.ai.qa
import app.ai.generation
import app.ai.evaluation
import app.rag.embeddings
import app.rag.vectorstore
import app.rag.retrieval
import app.ingestion.pdf
import app.ingestion.unified
import app.ui.teacher
import app.ui.student
import app.ui.settings
import app.ui.styles

importlib.reload(app.config)
importlib.reload(app.ai.schemas)
importlib.reload(app.ai.patterns)
importlib.reload(app.ai.providers)
importlib.reload(app.ai.prompts)
importlib.reload(app.ai.qa)
importlib.reload(app.ai.generation)
importlib.reload(app.ai.evaluation)
importlib.reload(app.rag.embeddings)
importlib.reload(app.rag.vectorstore)
importlib.reload(app.rag.retrieval)
importlib.reload(app.ingestion.pdf)
importlib.reload(app.ingestion.unified)
importlib.reload(app.ui.teacher)
importlib.reload(app.ui.student)
importlib.reload(app.ui.settings)
importlib.reload(app.ui.styles)

import streamlit as st
from app.ui.styles import apply_custom_styles
from app.ui.teacher import render_teacher_studio
from app.ui.student import render_student_challenge
from app.ui.settings import render_ai_settings
from app.rag.vectorstore import VectorStore


def main():
    st.set_page_config(
        page_title="Critic Minds — Critical Thinking EdTech",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Apply modern custom stylesheet
    apply_custom_styles()

    # Initialize shared VectorStore in Streamlit session state
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = VectorStore()

    # Top Hero Banner
    st.markdown(
        """
        <div class="hero-banner">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <h1 class="hero-title">🧠 Critic Minds</h1>
                    <div class="hero-subtitle">From Textbook Knowledge to Critical Thinking</div>
                    <span class="hero-tagline">V1 Hackathon Edition • Grounded RAG Reasoning</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigation Tabs
    tabs = st.tabs([
        "🏠 Home",
        "👩‍🏫 Teacher Studio",
        "🧑‍🎓 Student Challenge",
        "⚙️ AI Settings",
    ])

    with tabs[0]:
        render_home_tab()

    with tabs[1]:
        render_teacher_studio(st.session_state.vectorstore)

    with tabs[2]:
        render_student_challenge()

    with tabs[3]:
        render_ai_settings()


def render_home_tab():
    """Renders the Home & Overview screen."""
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown(
            """
            ### Why Critic Minds?
            Traditional assessments overemphasize rote memorization and factual recall. Students can often repeat definitions without knowing how to evaluate competing claims, predict causal effects, or make evidence-grounded decisions.

            **Critic Minds bridges this gap:**
            1. **Ingests your actual teaching materials** (PDF, DOCX, TXT, PPTX).
            2. **Generates authentic inquiry challenges** (Evidence Analysis, What-If predictions, and Case Dilemmas).
            3. **Grounds every challenge in retrieved text** with traceable page & slide citations.
            4. **Empowers teachers** to review and adjust every detail before publishing.
            5. **Evaluates student thinking** against multi-dimensional rubrics—rewarding reasoned arguments rather than one fixed answer key.
            """
        )

        st.divider()
        st.markdown("#### 🚀 Quick Start Guide")
        st.markdown(
            """
            - **Step 1**: Head to **👩‍🏫 Teacher Studio** and click **'Load Biology Demo (1-Click)'** or upload your own document.
            - **Step 2**: Configure your grade, topic, and desired challenge type, then click **'Generate Critical Challenge'**.
            - **Step 3**: Review the AI generation & QA audit, make any edits, and click **'Approve & Publish to Student'**.
            - **Step 4**: Switch to **🧑‍🎓 Student Challenge**, inspect the evidence citations, and submit a reasoned response.
            - **Step 5**: Receive instant, transparent reasoning evaluation with strengths and improvement tips!
            """
        )

    with col_right:
        st.markdown(
            """
            <div class="cm-card" style="border-top: 4px solid #4338CA;">
                <h4 style="color:#1E1B4B; margin:0 0 12px 0;">⚡ End-to-End Loop</h4>
                <div style="font-family: 'JetBrains Mono', monospace; font-size:0.85rem; color:#475569; line-height:1.7;">
                    Upload Material (PDF/DOCX/PPTX)<br>
                    &nbsp;&nbsp;↓<br>
                    Unified Parsing & Metadata (Pages/Slides)<br>
                    &nbsp;&nbsp;↓<br>
                    In-Memory Vector RAG Retrieval<br>
                    &nbsp;&nbsp;↓<br>
                    Structured Challenge Generation (Gemini/Groq)<br>
                    &nbsp;&nbsp;↓<br>
                    AI Quality Assurance (QA) Audit<br>
                    &nbsp;&nbsp;↓<br>
                    Teacher Review, Customization & Approval<br>
                    &nbsp;&nbsp;↓<br>
                    Student Evidence Analysis & Response<br>
                    &nbsp;&nbsp;↓<br>
                    Rubric-Based Reasoning Evaluation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="cm-card" style="border-top: 4px solid #10B981;">
                <h4 style="color:#065F46; margin:0 0 8px 0;">🛡️ Core Differentiator</h4>
                <p style="color:#334155; font-size:0.92rem; line-height:1.5; margin:0;">
                    <b>Critic Minds evaluates how students think</b>, not merely whether their final answer matches an expected string. Alternative well-reasoned arguments are rewarded.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
