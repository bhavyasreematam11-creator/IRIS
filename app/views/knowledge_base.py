"""Knowledge Base view for IRIS: Curated postmortems, verified runbooks, and architectural patterns (Dark Blue Theme)."""

import streamlit as st

from database.db import list_incidents
from utils.config import colors
from utils.helpers import format_timestamp


def render_knowledge_base():
    """Render the Knowledge Base and Runbooks portal in Dark Blue theme."""
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <h2 style="margin: 0; color: #F8FAFC; font-size: 26px;">📚 Knowledge Base & Runbooks</h2>
            <p style="margin: 4px 0 0 0; color: {colors.SECONDARY_TEXT}; font-size: 14px;">
                Verified technical postmortems, standard operating procedures, and incident prevention patterns retained in memory.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    incidents = list_incidents()
    resolved_incidents = [i for i in incidents if i.get("status") == "Resolved" and i.get("resolution")]

    kb_col1, kb_col2 = st.columns([3, 1])
    with kb_col1:
        search_kb = st.text_input("🔍 Search Knowledge Base", placeholder="Filter runbooks by system, failure mode, or technology...")
    with kb_col2:
        cat_select = st.selectbox(
            "Domain Filter",
            ["All Domains", "Database", "Infrastructure", "Security", "Application", "Network"]
        )

    filtered = resolved_incidents
    if cat_select != "All Domains":
        filtered = [i for i in filtered if i.get("category") == cat_select]
    if search_kb.strip():
        q = search_kb.strip().lower()
        filtered = [
            i for i in filtered
            if q in i["title"].lower() or q in i["affected_system"].lower() or q in i.get("root_cause", "").lower()
        ]

    st.markdown(
        f"""
        <div style="margin: 14px 0 16px 0; font-size: 13px; color: {colors.SECONDARY_TEXT};">
            Showing {len(filtered)} verified runbooks & postmortems
        </div>
        """,
        unsafe_allow_html=True
    )

    if not filtered:
        st.info("No matching knowledge base articles found.")
        return

    for item in filtered:
        with st.expander(f"📖 [{item['category']}] {item['title']} — {item['affected_system']}", expanded=False):
            st.markdown(
                f"""
                <div style="background: #0F1D40; border: 1px solid #1E3A8A; border-radius: 8px; padding: 14px; margin-bottom: 14px;">
                    <b style="color: #60A5FA; font-size: 14px;">Executive Incident Summary:</b>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #F8FAFC;">{item['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Root Cause Analysis:**\n{item.get('root_cause', 'N/A')}")
                if item.get("steps_taken"):
                    st.markdown(f"**Diagnostic Runbook Steps:**\n{item.get('steps_taken')}")
            with col_b:
                st.markdown(f"**Permanent Remediation & Architectural Fix:**\n{item.get('resolution', 'N/A')}")
                st.markdown(f"**Affected Component:** `{item['affected_system']}`")
                st.markdown(f"**Recorded In Memory:** `{'Yes (Hindsight/Demo)' if item.get('retained_in_memory') else 'No'}`")

            # Download postmortem as markdown
            postmortem_md = f"""# Postmortem: {item['title']}
- Incident ID: {item['id']}
- Category: {item['category']}
- Affected System: {item['affected_system']}
- Created: {format_timestamp(item['created_at'])}

## Incident Summary
{item['description']}

## Error Signatures
{item.get('error_logs', 'None recorded')}

## Root Cause
{item.get('root_cause', 'N/A')}

## Diagnostic Procedure
{item.get('steps_taken', 'N/A')}

## Permanent Resolution
{item.get('resolution', 'N/A')}
"""
            st.download_button(
                label=f"📥 Download Runbook Markdown ({item['id']})",
                data=postmortem_md,
                file_name=f"postmortem_{item['id']}.md",
                mime="text/markdown",
                key=f"dl_{item['id']}"
            )
