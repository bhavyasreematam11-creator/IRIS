"""UI, formatting, and general helper utilities for IRIS (Dark Blue SaaS Theme)."""

import datetime
import uuid
import streamlit as st
from utils.config import colors


def generate_incident_id() -> str:
    """Generate a clean, professional incident ID, e.g., INC-2026-A1B2."""
    year = datetime.datetime.now().year
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"INC-{year}-{short_uuid}"


def format_timestamp(dt: datetime.datetime | str | None) -> str:
    """Format timestamps cleanly for UI display."""
    if not dt:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    if isinstance(dt, str):
        try:
            parsed = datetime.datetime.fromisoformat(dt.replace("Z", "+00:00"))
            return parsed.strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            return dt
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def get_severity_badge(severity: str) -> str:
    """Return an HTML badge styled for the severity level in dark blue theme."""
    sev = (severity or "Medium").upper()
    style_map = {
        "LOW": ("#082F49", "#38BDF8", "#0284C7", "● Low"),
        "MEDIUM": ("#451A03", "#FBBF24", "#B45309", "▲ Medium"),
        "HIGH": ("#431407", "#FB923C", "#C2410C", "▲ High"),
        "CRITICAL": ("#450A0A", "#F87171", "#DC2626", "🚨 Critical"),
    }
    bg, fg, border, label = style_map.get(sev, ("#1E293B", "#94A3B8", "#334155", sev.title()))
    return f'<span style="background-color: {bg}; color: {fg}; font-weight: 600; padding: 3px 10px; border-radius: 9999px; font-size: 12px; display: inline-block; border: 1px solid {border};">{label}</span>'


def get_status_badge(status: str) -> str:
    """Return an HTML badge styled for the incident status in dark blue theme."""
    st_val = (status or "Open").upper()
    style_map = {
        "INVESTIGATING": ("#172554", "#60A5FA", "#2563EB", "🔍 Investigating"),
        "OPEN": ("#451A03", "#FBBF24", "#B45309", "⏳ Open"),
        "RESOLVED": ("#064E3B", "#34D399", "#059669", "✓ Resolved"),
        "CLOSED": ("#1E293B", "#94A3B8", "#334155", "Closed"),
    }
    bg, fg, border, label = style_map.get(st_val, ("#172554", "#60A5FA", "#2563EB", st_val.title()))
    return f'<span style="background-color: {bg}; color: {fg}; font-weight: 600; padding: 3px 10px; border-radius: 9999px; font-size: 12px; display: inline-block; border: 1px solid {border};">{label}</span>'


def get_memory_badge(is_retained: bool) -> str:
    """Return an HTML badge indicating whether an incident is preserved in Hindsight."""
    if is_retained:
        return '<span style="background-color: #064E3B; color: #34D399; font-weight: 600; padding: 3px 10px; border-radius: 9999px; font-size: 12px; display: inline-block; border: 1px solid #059669;">🧠 Retained in Hindsight</span>'
    return '<span style="background-color: #1E293B; color: #94A3B8; font-weight: 500; padding: 3px 10px; border-radius: 9999px; font-size: 12px; display: inline-block; border: 1px solid #334155;">⚪ Not Retained</span>'


def inject_custom_css():
    """Inject premium Dark Blue enterprise SaaS CSS."""
    custom_css = f"""
    <style>
    /* Dark Blue Page Canvas */
    .stApp {{
        background-color: {colors.BACKGROUND};
        color: {colors.TEXT};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    
    /* Main container padding */
    .main .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: #070D1E;
        border-right: 1px solid {colors.BORDER};
    }}
    
    [data-testid="stSidebar"] .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }}

    [data-testid="stSidebar"] * {{
        color: {colors.TEXT};
    }}
    
    /* Header typography */
    h1, h2, h3, h4, h5, h6 {{
        color: #F8FAFC !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}

    p, span, label, div {{
        color: inherit;
    }}
    
    /* Dark Blue Card Component */
    .iris-card {{
        background: {colors.NAVY_SURFACE};
        border: 1px solid {colors.NAVY_BORDER};
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 1.25rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
        color: {colors.TEXT};
    }}
    
    .iris-card:hover {{
        border-color: {colors.PRIMARY_BLUE};
        box-shadow: 0 6px 12px -1px rgba(37, 99, 235, 0.2);
    }}
    
    /* Stat Metric Box */
    .iris-metric-card {{
        background: {colors.NAVY_SURFACE};
        border: 1px solid {colors.NAVY_BORDER};
        border-radius: 12px;
        padding: 20px;
        text-align: left;
        box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.3);
        border-top: 3px solid {colors.PRIMARY_BLUE};
    }}
    
    .iris-metric-value {{
        font-size: 32px;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
        margin-top: 4px;
    }}
    
    .iris-metric-label {{
        font-size: 13px;
        font-weight: 600;
        color: {colors.SECONDARY_TEXT};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* Banner Callouts */
    .iris-banner-primary {{
        background: linear-gradient(135deg, #0F1D40 0%, #111C3A 100%);
        border: 1px solid #1E3A8A;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    }}
    
    .iris-banner-alert {{
        background-color: #0F1E3D;
        border-left: 4px solid {colors.PRIMARY_BLUE};
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        border-top: 1px solid #1E2D54;
        border-right: 1px solid #1E2D54;
        border-bottom: 1px solid #1E2D54;
    }}
    
    /* Buttons */
    div.stButton > button:first-child {{
        background-color: {colors.PRIMARY_BLUE};
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
    }}
    
    div.stButton > button:first-child:hover {{
        background-color: #2563EB;
        color: #FFFFFF;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.5);
    }}
    
    div.stButton > button[kind="secondary"] {{
        background-color: #111C3A;
        color: #F8FAFC;
        border: 1px solid {colors.BORDER};
    }}
    
    /* Dark Blue Form Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {{
        border-radius: 8px !important;
        border-color: {colors.BORDER} !important;
        background-color: #0A1128 !important;
        color: #F8FAFC !important;
    }}
    
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {colors.PRIMARY_BLUE} !important;
        box-shadow: 0 0 0 1px {colors.PRIMARY_BLUE} !important;
    }}

    /* Radio buttons in sidebar */
    [data-testid="stSidebar"] .stRadio label {{
        color: #E2E8F0 !important;
    }}

    /* Selectbox dropdown menu */
    [data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"] {{
        background-color: #0B132B !important;
        border: 1px solid {colors.BORDER} !important;
    }}
    li[role="option"] {{
        color: #F8FAFC !important;
        background-color: #0B132B !important;
    }}
    li[role="option"]:hover, li[aria-selected="true"] {{
        background-color: #1E293B !important;
        color: {colors.PRIMARY_BLUE} !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid {colors.BORDER};
        padding-bottom: 4px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px 6px 0 0;
        padding: 10px 18px;
        font-weight: 600;
        color: {colors.SECONDARY_TEXT};
        background-color: transparent;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: #60A5FA !important;
        border-bottom: 2px solid {colors.PRIMARY_BLUE} !important;
        background-color: #0F1E3D !important;
    }}
    
    /* Code and Terminal Blocks */
    pre, code {{
        background-color: #070B16 !important;
        color: #E2E8F0 !important;
        border-radius: 8px !important;
        border: 1px solid #1E2D54 !important;
    }}
    
    /* Streamlit Expander */
    .streamlit-expanderHeader {{
        font-weight: 600;
        color: #F8FAFC !important;
        background-color: #111C3A !important;
        border-radius: 8px;
        border: 1px solid {colors.BORDER} !important;
    }}

    .streamlit-expanderContent {{
        background-color: #0E1730;
        border-left: 1px solid {colors.BORDER};
        border-right: 1px solid {colors.BORDER};
        border-bottom: 1px solid {colors.BORDER};
        border-radius: 0 0 8px 8px;
        padding: 16px;
    }}

    /* Dataframe tables */
    [data-testid="stDataFrame"] {{
        border: 1px solid {colors.BORDER};
        border-radius: 8px;
    }}
    
    /* Status pills */
    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }}
    
    .status-pill-green {{
        background-color: #064E3B;
        color: #34D399;
        border: 1px solid #059669;
    }}
    
    .status-pill-blue {{
        background-color: #172554;
        color: #60A5FA;
        border: 1px solid #2563EB;
    }}
    
    .status-pill-amber {{
        background-color: #451A03;
        color: #FBBF24;
        border: 1px solid #B45309;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
