"""Overview Dashboard view for IRIS (Dark Blue SaaS Theme)."""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.db import get_analytics_summary, list_incidents, list_memory_audit
from memory.hindsight_client import hindsight_manager
from utils.config import colors
from utils.helpers import get_memory_badge, get_severity_badge, get_status_badge, format_timestamp


def render_overview():
    """Render the main overview dashboard in Dark Blue SaaS theme."""
    # Welcoming Header
    st.markdown(
        f"""
        <div class="iris-banner-primary">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <h1 style="margin: 0; font-size: 28px; color: #F8FAFC !important;">Good morning! Welcome to IRIS.</h1>
                    <p style="margin: 6px 0 0 0; font-size: 15px; color: {colors.SECONDARY_TEXT};">
                        Your intelligent partner for incident investigation and knowledge retention.
                    </p>
                </div>
                <div>
                    <span class="status-pill status-pill-blue">
                        Tagline: Turning Past Incidents into Future Intelligence
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Fetch stats
    stats = get_analytics_summary()
    status = hindsight_manager.check_connection()

    # Metric Cards Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: {colors.PRIMARY_BLUE};">
                <div class="iris-metric-label">Total Incidents</div>
                <div class="iris-metric-value">{stats['total_incidents']}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Tracked in SQLite</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: {colors.SUCCESS_GREEN};">
                <div class="iris-metric-label">Resolved Incidents</div>
                <div class="iris-metric-value">{stats['resolved_incidents']}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">With verified postmortems</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: {colors.WARNING_AMBER};">
                <div class="iris-metric-label">Recurring Systems</div>
                <div class="iris-metric-value">{stats['recurring_incident_groups']}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Repeated alerts recorded</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: #8B5CF6;">
                <div class="iris-metric-label">Knowledge Memories</div>
                <div class="iris-metric-value">{stats['retained_memories']}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Preserved in Hindsight</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # Quick Action Bar
    q_col1, q_col2 = st.columns([3, 1])
    with q_col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 12px; padding: 14px 18px; background: {colors.NAVY_SURFACE}; border: 1px solid {colors.BORDER}; border-radius: 8px;">
                <span style="font-size: 20px;">⚡</span>
                <span style="font-size: 14px; color: {colors.TEXT}; font-weight: 500;">
                    Encountered an active production issue? Trigger an AI-assisted investigation with persistent memory recall.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with q_col2:
        if st.button("🔍 Investigate New Incident", type="primary", use_container_width=True):
            st.session_state["current_page"] = "investigate"
            st.rerun()

    st.write("")

    # Main Grid: Recent Incidents & Severity Distribution
    grid_left, grid_right = st.columns([3, 2])

    with grid_left:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 18px; color: #F8FAFC !important;">Recent Incidents</h3>
                <span style="font-size: 12px; color: {colors.SECONDARY_TEXT};">Displaying latest entries</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        recent_incidents = list_incidents(limit=5)
        if not recent_incidents:
            st.info("No incidents recorded yet. Click 'Investigate New Incident' to create your first record.")
        else:
            for inc in recent_incidents:
                sample_tag = ' <span style="font-size: 11px; background: #1E293B; color: #94A3B8; padding: 2px 6px; border-radius: 4px; font-weight: 600;">SAMPLE</span>' if inc.get("is_sample") else '<span style="font-size: 11px; background: #172554; color: #60A5FA; padding: 2px 6px; border-radius: 4px; font-weight: 600;">LIVE</span>'
                st.markdown(
                    f"""
                    <div class="iris-card" style="padding: 16px 20px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <span style="font-size: 12px; font-weight: 700; color: {colors.PRIMARY_BLUE}; letter-spacing: 0.05em;">{inc['id']}</span>{sample_tag}
                                <h4 style="margin: 4px 0 6px 0; font-size: 16px; color: #F8FAFC !important;">{inc['title']}</h4>
                                <div style="font-size: 13px; color: {colors.SECONDARY_TEXT}; margin-bottom: 8px;">
                                    <b>System:</b> {inc['affected_system']} &nbsp;•&nbsp; <b>Category:</b> {inc['category']} &nbsp;•&nbsp; {format_timestamp(inc['created_at'])}
                                </div>
                            </div>
                            <div style="text-align: right; display: flex; flex-direction: column; gap: 6px; align-items: flex-end;">
                                {get_severity_badge(inc['severity'])}
                                {get_status_badge(inc['status'])}
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 8px; border-top: 1px solid #1E2D54;">
                            <div>
                                {get_memory_badge(bool(inc.get('retained_in_memory')))}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with grid_right:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 18px; color: #F8FAFC !important;">Incident Severity Breakdown</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        sev_data = stats["severity_dist"]
        if sev_data:
            df_sev = pd.DataFrame([
                {"Severity": k, "Count": v} for k, v in sev_data.items()
            ])
            color_map = {
                "Critical": "#EF4444",
                "High": "#F59E0B",
                "Medium": "#3B82F6",
                "Low": "#10B981"
            }
            fig = px.pie(
                df_sev,
                values="Count",
                names="Severity",
                hole=0.65,
                color="Severity",
                color_discrete_map=color_map
            )
            fig.update_layout(
                showlegend=True,
                margin=dict(t=10, b=10, l=10, r=10),
                height=240,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color="#94A3B8"))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No severity distribution data available.")

        # Recent Memory Activity Feed
        st.markdown(
            f"""
            <div style="margin-top: 20px; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 18px; color: #F8FAFC !important;">Recent Memory Activity</h3>
                <span style="font-size: 12px; color: {colors.SECONDARY_TEXT};">Retain and recall audit trail</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        audits = list_memory_audit(limit=4)
        if not audits:
            st.markdown(
                f"""
                <div class="iris-card" style="padding: 14px; font-size: 13px; color: {colors.SECONDARY_TEXT};">
                    No persistent memory activity recorded yet. Run an investigation or retain an incident to see memory actions.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for a in audits:
                action_color = colors.PRIMARY_BLUE if a["action"] == "RECALL" else colors.SUCCESS_GREEN
                action_icon = "🔍" if a["action"] == "RECALL" else "💾"
                st.markdown(
                    f"""
                    <div style="display: flex; gap: 12px; align-items: flex-start; padding: 12px 14px; background: {colors.NAVY_SURFACE}; border: 1px solid {colors.BORDER}; border-radius: 8px; margin-bottom: 8px;">
                        <span style="font-size: 16px;">{action_icon}</span>
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 600; font-size: 13px; color: {action_color};">{a['action']} • {a['mode']}</span>
                                <span style="font-size: 11px; color: {colors.SECONDARY_TEXT};">{format_timestamp(a['timestamp'])}</span>
                            </div>
                            <div style="font-size: 12px; color: {colors.TEXT}; margin-top: 3px;">
                                {a.get('content_summary', a.get('query', 'Memory transaction'))}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
