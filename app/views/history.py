"""Incident History view for IRIS (Dark Blue SaaS Theme)."""

import streamlit as st

from database.db import get_incident, list_incidents
from memory.retain import retain_incident
from utils.config import colors
from utils.helpers import get_memory_badge, get_severity_badge, get_status_badge, format_timestamp


def render_history():
    """Render the incident history and postmortem management page in Dark Blue theme."""
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <h2 style="margin: 0; color: #F8FAFC; font-size: 26px;">Incident History & Audit Log</h2>
            <p style="margin: 4px 0 0 0; color: {colors.SECONDARY_TEXT}; font-size: 14px;">
                Complete persistent record of previous technical incidents, root causes, and resolutions stored in SQLite.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Search & Filter Controls Card
    with st.container():
        f_col1, f_col2, f_col3, f_col4 = st.columns([3, 1, 1, 1])
        with f_col1:
            search_query = st.text_input("🔍 Search Incidents", placeholder="Search by ID, title, affected system, or keywords...")
        with f_col2:
            cat_filter = st.selectbox(
                "Category",
                ["All", "Database", "Infrastructure", "Application", "Security", "Network", "Storage", "Third-Party API", "Other"]
            )
        with f_col3:
            sev_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
        with f_col4:
            status_filter = st.selectbox("Status", ["All", "Resolved", "Investigating", "Open"])

        include_samples = st.checkbox("Include Sample Demo Records", value=True)

    # Fetch incidents from SQLite
    incidents = list_incidents(
        category=cat_filter,
        severity=sev_filter,
        status=status_filter,
        search_query=search_query,
        include_samples=include_samples
    )

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 16px 0 12px 0;">
            <span style="font-size: 14px; font-weight: 600; color: #F8FAFC;">
                Showing {len(incidents)} incidents
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not incidents:
        st.markdown(
            f"""
            <div class="iris-card" style="text-align: center; padding: 40px 20px; color: {colors.SECONDARY_TEXT};">
                <p style="font-size: 18px; font-weight: 600; margin: 0 0 8px 0; color: #F8FAFC;">No matching incidents found</p>
                <p style="font-size: 14px; margin: 0;">Try adjusting your search terms or filter criteria.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    for inc in incidents:
        sample_label = '<span style="font-size: 11px; background: #1E293B; color: #94A3B8; padding: 2px 6px; border-radius: 4px; font-weight: 600; margin-left: 6px;">SAMPLE</span>' if inc.get("is_sample") else '<span style="font-size: 11px; background: #172554; color: #60A5FA; padding: 2px 6px; border-radius: 4px; font-weight: 600; margin-left: 6px;">LIVE INCIDENT</span>'

        with st.expander(f"{inc['id']} — {inc['title']}", expanded=False):
            # Top row inside expander
            t_col1, t_col2 = st.columns([3, 1])
            with t_col1:
                st.markdown(
                    f"""
                    <div>
                        <span style="font-size: 14px; font-weight: 700; color: #60A5FA;">{inc['id']}</span>
                        {sample_label}
                        <h3 style="margin: 4px 0 8px 0; color: #F8FAFC;">{inc['title']}</h3>
                        <div style="font-size: 13px; color: {colors.SECONDARY_TEXT};">
                            <b>Affected System:</b> {inc['affected_system']} &nbsp;|&nbsp; 
                            <b>Category:</b> {inc['category']} &nbsp;|&nbsp; 
                            <b>Reported:</b> {format_timestamp(inc['created_at'])}
                            {f"&nbsp;|&nbsp; <b>Resolved:</b> {format_timestamp(inc['resolved_at'])}" if inc.get('resolved_at') else ""}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with t_col2:
                st.markdown(
                    f"""
                    <div style="text-align: right; display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">
                        {get_severity_badge(inc['severity'])}
                        {get_status_badge(inc['status'])}
                        {get_memory_badge(bool(inc.get('retained_in_memory')))}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.write("")

            # Description & Error Logs
            st.markdown(f"**Technical Description:**\n{inc['description']}")
            if inc.get("error_logs"):
                st.markdown("**Error Logs & Stack Trace:**")
                st.code(inc["error_logs"], language="bash")

            # Postmortem Findings
            if inc.get("root_cause") or inc.get("resolution"):
                st.markdown("---")
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    st.markdown(f"**Confirmed Root Cause:**\n{inc.get('root_cause', 'Pending confirmation')}")
                    if inc.get("steps_taken"):
                        st.markdown(f"**Diagnostic Steps Executed:**\n{inc.get('steps_taken')}")
                with p_col2:
                    st.markdown(f"**Verified Resolution:**\n{inc.get('resolution', 'Pending resolution')}")

            # Option to retain in memory if not yet retained
            if not inc.get("retained_in_memory") and inc.get("resolution"):
                st.write("")
                if st.button(f"🧠 Retain {inc['id']} in Hindsight Memory", key=f"btn_retain_{inc['id']}"):
                    with st.spinner("Retaining into Hindsight..."):
                        res = retain_incident(
                            incident_id=inc["id"],
                            title=inc["title"],
                            category=inc["category"],
                            severity=inc["severity"],
                            affected_system=inc["affected_system"],
                            description=inc["description"],
                            error_logs=inc.get("error_logs", ""),
                            root_cause=inc.get("root_cause", ""),
                            steps_taken=inc.get("steps_taken", ""),
                            resolution=inc.get("resolution", ""),
                            timestamp=inc["created_at"]
                        )
                    st.success(f"Successfully retained in {res.mode}! Memory ID: {res.memory_id}")
                    st.rerun()
