"""
settings.py
AI Provider and Credentials Configuration UI for Critic Minds.
Supports Option A (Default integrated credentials) and Option B (User-provided API keys).
Ensures secrets are never exposed, logged, or permanently stored.
"""
import streamlit as st
from app.config import AppConfig
from app.ai.providers import get_llm_provider, LLMProviderError


def render_ai_settings():
    """Renders the AI provider and secrets configuration screen."""
    st.subheader("⚙️ AI Engine & Credentials Configuration")
    st.markdown(
        """
        Configure the language model used for **Challenge Generation**, **Quality Assurance**, 
        and **Student Reasoning Evaluation**.
        """
    )

    # Initialize session state for AI configuration if not present
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = AppConfig.default_provider()
    if "use_default_key" not in st.session_state:
        # If default key is present, default to using it; else user key
        st.session_state.use_default_key = AppConfig.is_default_available(st.session_state.ai_provider)
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        provider_options = ["Gemini", "Groq"]
        current_idx = 0 if st.session_state.ai_provider == "gemini" else 1
        chosen_provider = st.selectbox(
            "Select AI Provider",
            options=provider_options,
            index=current_idx,
            help="Gemini Flash provides high-speed multimodal reasoning. Groq provides ultra-low latency open models.",
        ).lower()
        st.session_state.ai_provider = chosen_provider

        has_default = AppConfig.is_default_available(chosen_provider)

        key_mode = st.radio(
            "API Key Source",
            options=["Critic Minds Default Configuration", "Use My Own API Key"],
            index=0 if (st.session_state.use_default_key and has_default) else 1,
            help="Choose whether to use pre-configured platform secrets or enter your own key for this session.",
        )
        st.session_state.use_default_key = (key_mode == "Critic Minds Default Configuration")

    with col2:
        if st.session_state.use_default_key:
            if has_default:
                st.success(f"✅ Integrated default {chosen_provider.capitalize()} API credentials are configured and ready.")
                st.caption("Default keys are securely loaded from application secrets and never exposed.")
            else:
                st.warning(
                    f"⚠️ No default API key found for {chosen_provider.capitalize()}. "
                    "Please select 'Use My Own API Key' below or configure `GEMINI_API_KEY`/`GROQ_API_KEY`."
                )
        else:
            user_key_input = st.text_input(
                f"Enter your {chosen_provider.capitalize()} API Key",
                value=st.session_state.user_api_key,
                type="password",
                placeholder="Paste API key here...",
                help="Your key is held strictly in session memory and never saved to disk or Git.",
            )
            st.session_state.user_api_key = user_key_input.strip()

            if st.session_state.user_api_key:
                st.info(f"🔑 Custom {chosen_provider.capitalize()} key configured for this session.")
            else:
                st.caption(f"Enter a valid {chosen_provider.capitalize()} key to enable AI features.")

    st.divider()

    # Connection Test Button
    test_col, status_col = st.columns([1, 2], gap="small")
    with test_col:
        test_clicked = st.button("🔌 Test AI Connection", use_container_width=True)

    with status_col:
        if test_clicked:
            with st.spinner("Testing connection with provider..."):
                try:
                    provider = get_llm_provider(
                        provider_name=st.session_state.ai_provider,
                        user_api_key=st.session_state.user_api_key,
                        use_default=st.session_state.use_default_key,
                    )
                    # Quick lightweight ping
                    result = provider.generate_text("Reply with the exact word 'READY'", temperature=0.0)
                    if "READY" in result.upper():
                        st.success(f"🎉 Successfully connected to {st.session_state.ai_provider.capitalize()}!")
                    else:
                        st.success(f"✅ Connected to {st.session_state.ai_provider.capitalize()}: {result[:40]}")
                except LLMProviderError as e:
                    st.error(f"❌ Connection failed: {e}")
                except Exception as ex:
                    st.error(f"❌ Connection error: {ex}")
