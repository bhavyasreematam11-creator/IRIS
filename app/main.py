"""IRIS: Intelligent Incident Response System - Main Application Entrypoint (Dark Blue Theme & Auth)."""

import sys
from pathlib import Path

# Ensure root project directory is in python search path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from database.db import authenticate_user, init_db
from memory.hindsight_client import hindsight_manager
from utils.config import colors, settings
from utils.helpers import inject_custom_css

# Page Configuration
st.set_page_config(
    page_title="IRIS — Intelligent Incident Response System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database & Seed Defaults
init_db(seed_samples=True)

# Inject Dark Blue Enterprise SaaS Theme CSS
inject_custom_css()

# Session State Initialization
if "is_authenticated" not in st.session_state:
    # Default to unauthenticated unless previously signed in
    st.session_state["is_authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "overview"

# --- AUTHENTICATION GATE ---
if not st.session_state.get("is_authenticated") or not st.session_state.get("user"):
    from app.views.auth import render_auth_page
    render_auth_page()
    st.stop()

# Current Logged-In User
current_user = st.session_state["user"]

# --- SIDEBAR BRANDING & NAVIGATION ---
with st.sidebar:
    # IRIS Logo & Title
    st.markdown(
        f"""
        <div style="padding-bottom: 16px; border-bottom: 1px solid {colors.BORDER}; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: {colors.PRIMARY_BLUE}; color: white; width: 38px; height: 38px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);">
                    ⚡
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 22px; font-weight: 800; color: #F8FAFC !important; letter-spacing: -0.03em;">IRIS</h2>
                    <span style="font-size: 11px; font-weight: 600; color: {colors.PRIMARY_BLUE}; text-transform: uppercase; letter-spacing: 0.05em;">Incident Response</span>
                </div>
            </div>
            <p style="margin: 8px 0 0 0; font-size: 12px; color: {colors.SECONDARY_TEXT}; line-height: 1.4;">
                Turning Past Incidents into Future Intelligence.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Navigation menu
    nav_options = [
        ("overview", "🏠 Overview"),
        ("investigate", "🔍 Investigate Incident"),
        ("history", "📋 Incident History"),
        ("memory_explorer", "🧠 AI Memory Explorer"),
        ("knowledge_base", "📚 Knowledge Base"),
        ("analytics", "📊 Analytics"),
        ("profile", "👤 User Profile"),
        ("settings", "⚙️ Settings"),
    ]

    # Map labels to page keys
    label_to_key = {label: key for key, label in nav_options}
    key_to_label = {key: label for key, label in nav_options}

    current_label = key_to_label.get(st.session_state["current_page"], "🏠 Overview")

    selected_label = st.radio(
        "Navigation",
        options=[label for _, label in nav_options],
        index=[label for _, label in nav_options].index(current_label),
        label_visibility="collapsed"
    )

    # Update current page if radio selection changed
    if label_to_key[selected_label] != st.session_state["current_page"]:
        st.session_state["current_page"] = label_to_key[selected_label]
        st.rerun()

    # Sidebar Bottom Footer Spacer
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    
    # Hindsight status check
    conn_status = hindsight_manager.check_connection()
    if conn_status.is_live:
        status_html = f"""
        <div style="background: #064E3B; border: 1px solid #059669; border-radius: 8px; padding: 10px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="color: #34D399; font-size: 14px;">●</span>
                <span style="font-size: 12px; font-weight: 700; color: #34D399;">Hindsight Connected</span>
            </div>
            <div style="font-size: 11px; color: #A7F3D0; margin-top: 2px;">Bank: <code>{conn_status.bank_id}</code></div>
        </div>
        """
    else:
        status_html = f"""
        <div style="background: #451A03; border: 1px solid #B45309; border-radius: 8px; padding: 10px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="color: #FBBF24; font-size: 14px;">●</span>
                <span style="font-size: 12px; font-weight: 700; color: #FBBF24;">Demo Memory Active</span>
            </div>
            <div style="font-size: 11px; color: #FDE68A; margin-top: 2px;">Local fallback store</div>
        </div>
        """

    st.markdown(status_html, unsafe_allow_html=True)

    # User Profile & Sign Out
    st.markdown(
        f"""
        <div style="padding-top: 12px; border-top: 1px solid {colors.BORDER};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: {colors.PRIMARY_BLUE}; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; color: white;">
                        {current_user['name'][:1].upper()}
                    </div>
                    <div>
                        <div style="font-size: 13px; font-weight: 600; color: #F8FAFC;">{current_user['name']}</div>
                        <div style="font-size: 11px; color: {colors.SECONDARY_TEXT};">{current_user.get('role', 'SRE')}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    if st.button("🚪 Sign Out", key="sidebar_signout", use_container_width=True):
        st.session_state["user"] = None
        st.session_state["is_authenticated"] = False
        st.session_state["current_page"] = "overview"
        st.rerun()

    st.markdown(
        f"""
        <div style="margin-top: 8px; font-size: 11px; color: {colors.SECONDARY_TEXT}; text-align: center;">
            IRIS {settings.APP_VERSION} • Dark Blue SaaS
        </div>
        """,
        unsafe_allow_html=True
    )

# --- MAIN CONTENT AREA ROUTER ---
current_page = st.session_state["current_page"]

if current_page == "overview":
    from app.views.overview import render_overview
    render_overview()
elif current_page == "investigate":
    from app.views.investigate import render_investigate
    render_investigate()
elif current_page == "history":
    from app.views.history import render_history
    render_history()
elif current_page == "memory_explorer":
    from app.views.memory_explorer import render_memory_explorer
    render_memory_explorer()
elif current_page == "knowledge_base":
    from app.views.knowledge_base import render_knowledge_base
    render_knowledge_base()
elif current_page == "analytics":
    from app.views.analytics import render_analytics
    render_analytics()
elif current_page == "profile":
    from app.views.profile import render_profile
    render_profile()
elif current_page == "settings":
    from app.views.settings import render_settings
    render_settings()
else:
    from app.views.overview import render_overview
    render_overview()
