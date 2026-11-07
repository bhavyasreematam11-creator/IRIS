"""Settings & Configuration view for IRIS (Dark Blue Theme)."""

import streamlit as st

from database.db import reset_db
from memory.hindsight_client import hindsight_manager
from utils.config import colors, settings


def render_settings():
    """Render application settings and connection configuration in Dark Blue theme."""
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <h2 style="margin: 0; color: #F8FAFC; font-size: 26px;">⚙️ System Settings & Integration Config</h2>
            <p style="margin: 4px 0 0 0; color: {colors.SECONDARY_TEXT}; font-size: 14px;">
                Manage persistent memory connectivity, configure LLM reasoning providers, and inspect database storage.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Section 1: Hindsight Configuration
    st.markdown(
        f"""
        <div class="iris-card">
            <h3 style="margin-top: 0; font-size: 18px; color: #F8FAFC;">🧠 Hindsight Persistent Memory Configuration</h3>
            <p style="font-size: 13px; color: {colors.SECONDARY_TEXT};">
                Configure your Hindsight daemon or cloud cluster endpoint. Changes can also be saved in your <code>.env</code> file.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        h_col1, h_col2 = st.columns(2)
        with h_col1:
            base_url = st.text_input("Hindsight Base URL", value=settings.HINDSIGHT_BASE_URL)
            bank_id = st.text_input("Hindsight Memory Bank ID", value=settings.HINDSIGHT_BANK_ID)
        with h_col2:
            api_key = st.text_input("Hindsight API Key (Optional for Local)", value=settings.HINDSIGHT_API_KEY, type="password")
            demo_mode_toggle = st.checkbox("Force Demo Mode (Use Isolated Local Store)", value=settings.HINDSIGHT_DEMO_MODE)

        test_conn_btn = st.button("🔌 Test Hindsight Connection", type="primary")

        if test_conn_btn:
            with st.spinner("Probing Hindsight connection..."):
                hindsight_manager.base_url = base_url.rstrip("/")
                hindsight_manager.api_key = api_key.strip()
                hindsight_manager.bank_id = bank_id.strip()
                hindsight_manager._client = None
                status = hindsight_manager.check_connection()

            if status.is_live:
                st.success(f"✓ Connected to Hindsight Server! API Version: {status.version} at {status.base_url}")
            else:
                st.warning(f"⚠️ {status.message}")
                if status.error_details:
                    st.caption(f"Technical detail: {status.error_details}")

    st.write("")

    # Section 2: LLM Provider Configuration
    st.markdown(
        f"""
        <div class="iris-card">
            <h3 style="margin-top: 0; font-size: 18px; color: #F8FAFC;">🤖 LLM Reasoning Provider</h3>
            <p style="font-size: 13px; color: {colors.SECONDARY_TEXT};">
                Select your generative model provider for deep synthesis of incident hypotheses. If unconfigured, IRIS uses deterministic local heuristics.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            provider = st.selectbox(
                "LLM Provider",
                ["openai", "gemini", "local"],
                index=["openai", "gemini", "local"].index(settings.LLM_PROVIDER if settings.LLM_PROVIDER in ["openai", "gemini", "local"] else "openai")
            )
            model_name = st.text_input("Model Name", value=settings.OPENAI_MODEL if provider == "openai" else settings.GEMINI_MODEL)
        with l_col2:
            if provider == "openai":
                llm_key = st.text_input("OpenAI API Key", value=settings.OPENAI_API_KEY, type="password")
                base_endpoint = st.text_input("API Base URL", value=settings.OPENAI_BASE_URL)
            elif provider == "gemini":
                llm_key = st.text_input("Gemini API Key", value=settings.GEMINI_API_KEY, type="password")
                base_endpoint = "https://generativelanguage.googleapis.com"
            else:
                st.info("Local SRE heuristic rule engine selected. No API key required.")

    st.write("")

    # Section 3: Database & Reset Management
    st.markdown(
        f"""
        <div class="iris-card">
            <h3 style="margin-top: 0; font-size: 18px; color: #F8FAFC;">🗄️ Database Management & Demo Seeding</h3>
            <p style="font-size: 13px; color: {colors.SECONDARY_TEXT};">
                Active SQLite database file: <code>{settings.DB_PATH}</code>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            if st.button("🔄 Reset Database & Re-seed Sample Records", use_container_width=True):
                reset_db(seed_samples=True)
                st.success("Database reset and re-seeded with 3 realistic sample incidents.")
                st.rerun()
        with d_col2:
            if st.button("🗑️ Clear All Records (Empty DB)", use_container_width=True):
                reset_db(seed_samples=False)
                st.warning("Database cleared of all records.")
                st.rerun()
