"""
styles.py
Custom styling and aesthetic design system for Critic Minds.
Enhances Streamlit with modern typography, polished cards, glassmorphic badges, and responsive containers.
"""
import streamlit as st


def apply_custom_styles():
    """Injects high-quality CSS for an exceptional visual experience."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

        /* Global Typography */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
            border-radius: 16px;
            padding: 36px 32px;
            color: #FFFFFF;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.25);
        }
        .hero-title {
            font-size: 2.3rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0 0 8px 0;
            color: #FFFFFF;
        }
        .hero-subtitle {
            font-size: 1.15rem;
            font-weight: 500;
            color: #C7D2FE;
            margin: 0 0 14px 0;
        }
        .hero-tagline {
            display: inline-block;
            background: rgba(255, 255, 255, 0.15);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #EEF2FF;
            backdrop-filter: blur(8px);
        }

        /* Card Container */
        .cm-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 22px 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02), 0 1px 2px rgba(0, 0, 0, 0.03);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .cm-card:hover {
            border-color: #CBD5E1;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
        }

        /* Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-right: 8px;
            margin-bottom: 6px;
        }
        .badge-indigo {
            background: #EEF2FF;
            color: #4338CA;
            border: 1px solid #C7D2FE;
        }
        .badge-emerald {
            background: #ECFDF5;
            color: #047857;
            border: 1px solid #A7F3D0;
        }
        .badge-amber {
            background: #FFFBEB;
            color: #B45309;
            border: 1px solid #FDE68A;
        }
        .badge-purple {
            background: #FAF5FF;
            color: #7E22CE;
            border: 1px solid #E9D5FF;
        }

        /* Evidence Card */
        .evidence-card {
            background: #F8FAFC;
            border-left: 4px solid #6366F1;
            border-radius: 4px 8px 8px 4px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }
        .evidence-citation {
            font-size: 0.78rem;
            font-weight: 700;
            color: #4F46E5;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 4px;
        }
        .evidence-text {
            font-size: 0.92rem;
            color: #334155;
            line-height: 1.5;
        }

        /* Rubric Criteria Row */
        .rubric-row {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 10px;
        }
        .rubric-title {
            font-weight: 700;
            color: #1E293B;
            font-size: 0.95rem;
        }
        .rubric-desc {
            color: #64748B;
            font-size: 0.85rem;
            margin-top: 2px;
        }

        /* Score Display */
        .score-circle {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
        }
        .score-num {
            font-size: 2.8rem;
            font-weight: 800;
            line-height: 1;
        }
        .score-max {
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 600;
        }
        .score-label {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 700;
            margin-top: 6px;
        }

        /* Prompt Injection / QA Note */
        .qa-pass-banner {
            background: #F0FDF4;
            border: 1px solid #BBF7D0;
            color: #166534;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.88rem;
            font-weight: 500;
            margin-bottom: 16px;
        }

        /* Role Pill */
        .role-pill {
            background: #EFF6FF;
            color: #1D4ED8;
            border: 1px solid #BFDBFE;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
