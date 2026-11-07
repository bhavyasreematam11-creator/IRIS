"""AI Memory Explorer view for IRIS: Visualizing Hindsight persistent knowledge (Dark Blue Theme)."""

import streamlit as st
import pandas as pd

from database.db import list_memory_audit, list_incidents
from memory.hindsight_client import hindsight_manager
from memory.recall import recall_memories
from utils.config import colors
from utils.helpers import format_timestamp


def render_memory_explorer():
    """Render the AI memory explorer interface in Dark Blue theme."""
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <h2 style="margin: 0; color: #F8FAFC; font-size: 26px;">🧠 AI Memory Explorer</h2>
            <p style="margin: 4px 0 0 0; color: {colors.SECONDARY_TEXT}; font-size: 14px;">
                Inspect Hindsight persistent agent memory banks, test multi-strategy semantic recall, and audit memory transactions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Connection Status Card
    status = hindsight_manager.check_connection()

    if status.is_live:
        banner_bg = "#064E3B"
        banner_border = "#059669"
        title_color = "#34D399"
        status_pill = '<span style="background: #10B981; color: white; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 12px;">● LIVE HINDSIGHT CONNECTED</span>'
    else:
        banner_bg = "#451A03"
        banner_border = "#B45309"
        title_color = "#FBBF24"
        status_pill = '<span style="background: #F59E0B; color: white; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 12px;">● DEMO MODE ACTIVE</span>'

    st.markdown(
        f"""
        <div style="background: {banner_bg}; border: 1px solid {banner_border}; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <h3 style="margin: 0; font-size: 18px; color: {title_color};">Memory Engine Status</h3>
                        {status_pill}
                    </div>
                    <p style="margin: 8px 0 0 0; font-size: 13px; color: #F8FAFC;">
                        {status.message}
                    </p>
                    {f'<div style="margin-top: 6px; font-size: 12px; color: #F87171;">Error detail: {status.error_details}</div>' if status.error_details else ''}
                </div>
                <div style="background: #0B132B; border: 1px solid #1E2D54; border-radius: 8px; padding: 10px 16px; font-size: 13px; color: #F8FAFC;">
                    <div><b>Base URL:</b> <code>{status.base_url}</code></div>
                    <div style="margin-top: 4px;"><b>Bank ID:</b> <code>{status.bank_id}</code></div>
                    {f'<div style="margin-top: 4px;"><b>API Version:</b> <code>{status.version}</code></div>' if status.version else ''}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Memory Statistics Row
    retained_incidents = list_incidents()
    retained_count = sum(1 for i in retained_incidents if i.get("retained_in_memory"))
    audit_logs = list_memory_audit(limit=100)
    recall_count = sum(1 for a in audit_logs if a["action"] == "RECALL")
    retain_count = sum(1 for a in audit_logs if a["action"] == "RETAIN")

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: {colors.PRIMARY_BLUE};">
                <div class="iris-metric-label">Retained Memories</div>
                <div class="iris-metric-value">{retained_count}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Active incident records</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col2:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: #8B5CF6;">
                <div class="iris-metric-label">Recall Queries</div>
                <div class="iris-metric-value">{recall_count}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Semantic search lookups</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col3:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: {colors.SUCCESS_GREEN};">
                <div class="iris-metric-label">Retain Operations</div>
                <div class="iris-metric-value">{retain_count}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Stored postmortems</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col4:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: {colors.WARNING_AMBER};">
                <div class="iris-metric-label">Storage Engine</div>
                <div class="iris-metric-value" style="font-size: 20px; padding-top: 6px;">{status.mode}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Isolated sandbox</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # Interactive Memory Search Interface
    st.markdown(
        f"""
        <div class="iris-card">
            <h3 style="margin-top: 0; font-size: 18px; color: #F8FAFC;">🔍 Test Memory Bank Retrieval (TEMPR Multi-Strategy Search)</h3>
            <p style="font-size: 13px; color: {colors.SECONDARY_TEXT}; margin-bottom: 14px;">
                Directly query Hindsight memory using natural language problem statements or error messages to observe multi-strategy semantic recall.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        s_col1, s_col2 = st.columns([4, 1])
        with s_col1:
            test_query = st.text_input(
                "Memory Query",
                placeholder="e.g., PostgreSQL connection pool exhaustion or database acquire timeout",
                label_visibility="collapsed"
            )
        with s_col2:
            search_exec = st.button("Query Memory Bank", type="primary", use_container_width=True)

    if search_exec and test_query.strip():
        with st.spinner("Executing semantic memory search..."):
            recall_res = recall_memories(query=test_query.strip(), limit=5)
            st.session_state["test_memory_results"] = recall_res

    if "test_memory_results" in st.session_state and st.session_state["test_memory_results"]:
        res = st.session_state["test_memory_results"]
        st.markdown(
            f"""
            <div style="margin: 16px 0 10px 0;">
                <span class="status-pill status-pill-blue">
                    Retrieved {len(res.matches)} matches from {res.mode} (Bank: {res.bank_id})
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not res.matches:
            st.info("No matching memories found for this query.")
        else:
            for match in res.matches:
                sim_pct = int(match.similarity_score * 100)
                st.markdown(
                    f"""
                    <div class="iris-card" style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <span style="font-size: 12px; font-weight: 700; color: #60A5FA;">{match.incident_id or match.memory_id}</span>
                                <h4 style="margin: 4px 0; font-size: 16px; color: #F8FAFC;">{match.title}</h4>
                                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT};">
                                    System: <b>{match.affected_system}</b> &nbsp;|&nbsp; Category: <b>{match.category}</b>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <span style="background: #064E3B; color: #34D399; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 12px; border: 1px solid #059669;">
                                    {sim_pct}% Match
                                </span>
                            </div>
                        </div>
                        <div style="margin-top: 10px; font-size: 13px; color: #F8FAFC; background: #0B132B; border: 1px solid #1E2D54; padding: 10px; border-radius: 6px;">
                            <b style="color: #60A5FA;">Why Retrieved:</b> {match.relevance_explanation}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.write("")

    # Tabs for Stored Knowledge & Audit Log
    tab1, tab2 = st.tabs(["📚 Retained Incident Records", "📜 Memory Audit Activity Log"])

    with tab1:
        st.markdown(
            f"""
            <div style="margin-bottom: 12px; font-size: 14px; color: {colors.SECONDARY_TEXT};">
                Review verified incident records preserved inside persistent agent memory.
            </div>
            """,
            unsafe_allow_html=True
        )

        all_incidents = list_incidents()
        retained_items = [i for i in all_incidents if i.get("retained_in_memory")]

        if not retained_items:
            st.info("No records have been retained into memory yet.")
        else:
            for item in retained_items:
                with st.expander(f"🧠 {item['id']} — {item['title']}", expanded=False):
                    st.markdown(f"**Affected System:** `{item['affected_system']}` | **Category:** `{item['category']}` | **Severity:** `{item['severity']}`")
                    st.markdown(f"**Confirmed Root Cause:**\n{item.get('root_cause', 'N/A')}")
                    st.markdown(f"**Diagnostic Procedure:**\n{item.get('steps_taken', 'N/A')}")
                    st.markdown(f"**Verified Resolution:**\n{item.get('resolution', 'N/A')}")

    with tab2:
        st.markdown(
            f"""
            <div style="margin-bottom: 12px; font-size: 14px; color: {colors.SECONDARY_TEXT};">
                Chronological audit record of every retain and recall operation executed by IRIS.
            </div>
            """,
            unsafe_allow_html=True
        )

        audits = list_memory_audit(limit=50)
        if not audits:
            st.info("No memory audit logs recorded yet.")
        else:
            df_audit = pd.DataFrame(audits)
            st.dataframe(
                df_audit[[
                    "id", "timestamp", "action", "mode", "incident_id", "content_summary", "success", "details"
                ]],
                use_container_width=True,
                hide_index=True
            )
