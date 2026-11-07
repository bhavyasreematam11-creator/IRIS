"""Incident Investigation Module view for IRIS (Dark Blue SaaS Theme)."""

import datetime
import streamlit as st

from app.incident_handler import incident_handler
from memory.hindsight_client import hindsight_manager
from utils.config import colors
from utils.helpers import get_memory_badge, get_severity_badge, get_status_badge, format_timestamp


def render_investigate():
    """Render the incident submission and AI investigation interface in Dark Blue theme."""
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <h2 style="margin: 0; color: #F8FAFC; font-size: 26px;">Investigate Technical Incident</h2>
            <p style="margin: 4px 0 0 0; color: {colors.SECONDARY_TEXT}; font-size: 14px;">
                Submit incident symptoms to trigger memory recall from Hindsight and receive structured AI troubleshooting guidance.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Pre-fill template loaders for live demonstration
    st.markdown(
        f"""
        <div style="padding: 14px 18px; background: {colors.NAVY_SURFACE}; border: 1px solid {colors.BORDER}; border-radius: 8px; margin-bottom: 20px;">
            <span style="font-size: 13px; font-weight: 600; color: #60A5FA;">⚡ Quick Demo Scenarios:</span>
            <span style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-left: 8px;">
                Load real recurring incident scenarios to evaluate Hindsight memory recall:
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    sc_col1, sc_col2, sc_col3 = st.columns(3)
    with sc_col1:
        if st.button("🔄 Scenario A: PostgreSQL Pool Exhaustion", use_container_width=True):
            st.session_state["inv_title"] = "Repeated Database Connection Pool Depletion in Auth Service"
            st.session_state["inv_category"] = "Database"
            st.session_state["inv_severity"] = "Critical"
            st.session_state["inv_system"] = "PostgreSQL Cluster (pgpool-01)"
            st.session_state["inv_desc"] = "Web client logins are failing with HTTP 500. Application logs indicate connection acquisition timeouts to the PostgreSQL replica cluster."
            st.session_state["inv_logs"] = "FATAL: remaining connection slots are reserved for non-replication superuser connections (SQLSTATE 53300)\norg.postgresql.util.PSQLException: Connection acquire timeout after 10000ms"
            st.rerun()

    with sc_col2:
        if st.button("💾 Scenario B: Redis Cache Out of Memory", use_container_width=True):
            st.session_state["inv_title"] = "Redis Cache Cluster Reached Max Memory with Write Failures"
            st.session_state["inv_category"] = "Infrastructure"
            st.session_state["inv_severity"] = "High"
            st.session_state["inv_system"] = "Redis Cluster (redis-session-prod)"
            st.session_state["inv_desc"] = "User session writes are failing cluster-wide. Redis reports 100% capacity utilization."
            st.session_state["inv_logs"] = "Redis::CommandError: OOM command not allowed when used memory > 'maxmemory'. Eviction policy volatile-lru failed to free memory."
            st.rerun()

    with sc_col3:
        if st.button("🔒 Scenario C: Ingress SSL Certificate Expiry", use_container_width=True):
            st.session_state["inv_title"] = "Public API Gateway TLS Certificate Handshake Errors"
            st.session_state["inv_category"] = "Security"
            st.session_state["inv_severity"] = "Critical"
            st.session_state["inv_system"] = "Kubernetes Ingress (nginx-ingress-prod)"
            st.session_state["inv_desc"] = "Browsers and mobile clients are reporting NET::ERR_CERT_DATE_INVALID when accessing public endpoints."
            st.session_state["inv_logs"] = "nginx: [warn] certificate for api.example.com has expired\ncurl: (60) SSL certificate problem: certificate has expired"
            st.rerun()

    st.write("")

    # Incident Submission Form
    with st.container():
        st.markdown(
            f"""
            <div class="iris-card">
                <h3 style="margin-top: 0; font-size: 18px; color: #F8FAFC;">Incident Parameters</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("incident_submission_form"):
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                title = st.text_input(
                    "Incident Title *",
                    value=st.session_state.get("inv_title", ""),
                    placeholder="e.g., PostgreSQL connection pool exhaustion during peak morning traffic"
                )
            with f_col2:
                category = st.selectbox(
                    "Category *",
                    ["Database", "Infrastructure", "Application", "Security", "Network", "Storage", "Third-Party API", "Other"],
                    index=["Database", "Infrastructure", "Application", "Security", "Network", "Storage", "Third-Party API", "Other"].index(
                        st.session_state.get("inv_category", "Database")
                    )
                )

            f_col3, f_col4, f_col5 = st.columns([1, 1, 1])
            with f_col3:
                severity = st.selectbox(
                    "Severity *",
                    ["Critical", "High", "Medium", "Low"],
                    index=["Critical", "High", "Medium", "Low"].index(
                        st.session_state.get("inv_severity", "Critical")
                    )
                )
            with f_col4:
                affected_system = st.text_input(
                    "Affected System *",
                    value=st.session_state.get("inv_system", ""),
                    placeholder="e.g., PostgreSQL Cluster (pgpool-01)"
                )
            with f_col5:
                timestamp_str = st.text_input(
                    "Timestamp (UTC)",
                    value=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    disabled=False
                )

            description = st.text_area(
                "Technical Description *",
                value=st.session_state.get("inv_desc", ""),
                placeholder="Explain the incident symptoms, user impact, affected endpoints, and observed anomalous behavior...",
                height=110
            )

            error_logs = st.text_area(
                "Error Messages / Stack Trace / Logs",
                value=st.session_state.get("inv_logs", ""),
                placeholder="Paste relevant terminal logs, exception stack traces, or SQL error messages here...",
                height=130
            )

            submit_btn = st.form_submit_button("🔍 Start Investigation & Recall Memory", type="primary", use_container_width=True)

    if submit_btn:
        valid, err_msg = incident_handler.validate_input(
            title=title,
            category=category,
            severity=severity,
            affected_system=affected_system,
            description=description
        )
        if not valid:
            st.error(f"Validation Error: {err_msg}")
        else:
            with st.spinner("Querying Hindsight persistent memory bank and analyzing incident..."):
                inc_id, report, recalled = incident_handler.process_new_incident(
                    title=title,
                    category=category,
                    severity=severity,
                    affected_system=affected_system,
                    description=description,
                    error_logs=error_logs
                )
                st.session_state["current_report"] = report
                st.session_state["current_recalled"] = recalled
                st.session_state["active_incident_id"] = inc_id
            st.success(f"Investigation initialized! Generated incident record **{inc_id}**.")
            st.rerun()

    # Display Active Investigation Results
    if "current_report" in st.session_state and st.session_state.get("current_report"):
        report = st.session_state["current_report"]
        recalled = st.session_state.get("current_recalled")
        inc_id = st.session_state.get("active_incident_id", report.incident_id)

        st.write("")
        st.divider()

        # Header for Investigation Report
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div>
                    <span style="font-size: 13px; font-weight: 700; color: #60A5FA;">ACTIVE INVESTIGATION</span>
                    <h2 style="margin: 2px 0 0 0; color: #F8FAFC; font-size: 24px;">Incident Investigation Report: {inc_id}</h2>
                </div>
                <div>
                    <span class="status-pill status-pill-blue">AI Provider: {report.ai_provider}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if report.setup_message:
            st.info(f"ℹ️ **System Notice:** {report.setup_message}")

        # Summary and Evidence Limitations Box
        st.markdown(
            f"""
            <div class="iris-banner-alert">
                <b style="color: #60A5FA;">Incident Overview:</b><br/>
                {report.incident_summary}
                <div style="margin-top: 10px; font-size: 12px; color: {colors.SECONDARY_TEXT}; border-top: 1px dashed #1E3A8A; padding-top: 6px;">
                    <b>Evidence Limitations & Confidence:</b> {report.evidence_limitations}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Section 1: Memory Precedents Retrieved from Hindsight
        st.markdown(
            f"""
            <div style="margin-top: 24px; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 20px; color: #F8FAFC;">
                    🧠 Relevant Previous Incidents from Persistent Memory
                </h3>
                <p style="margin: 4px 0 0 0; font-size: 13px; color: {colors.SECONDARY_TEXT};">
                    Knowledge retrieved via Hindsight semantic memory recall matching current failure signatures.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not report.relevant_previous_incidents:
            st.markdown(
                f"""
                <div class="iris-card" style="padding: 16px; color: {colors.SECONDARY_TEXT};">
                    No relevant historical precedents were found in the memory bank for these specific symptoms. This appears to be a novel failure pattern.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for idx, match in enumerate(report.relevant_previous_incidents, 1):
                badge_color = "#10B981" if match.similarity_score > 0.6 else "#3B82F6"
                sim_pct = int(match.similarity_score * 100)
                source_badge = '<span style="background: #172554; color: #60A5FA; border: 1px solid #2563EB; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">HINDSIGHT</span>' if match.source == "HINDSIGHT" else '<span style="background: #451A03; color: #FBBF24; border: 1px solid #B45309; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">DEMO MODE MEMORY</span>'
                
                st.markdown(
                    f"""
                    <div class="iris-card" style="border-left: 4px solid {badge_color}; margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                            <div>
                                <span style="font-size: 12px; font-weight: 700; color: #60A5FA;">{match.incident_id or match.memory_id}</span>
                                &nbsp;•&nbsp; {source_badge}
                                <h4 style="margin: 4px 0; font-size: 17px; color: #F8FAFC;">{match.title}</h4>
                                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT};">
                                    Affected System: <b>{match.affected_system}</b> &nbsp;|&nbsp; Category: <b>{match.category}</b>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="background: #064E3B; border: 1px solid #059669; color: #34D399; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 13px;">
                                    {sim_pct}% Relevance
                                </div>
                            </div>
                        </div>
                        
                        <div style="background: #0B132B; border: 1px solid #1E2D54; border-radius: 8px; padding: 12px 16px; margin: 10px 0;">
                            <div style="font-size: 13px; color: #60A5FA; font-weight: 600; margin-bottom: 4px;">
                                💡 Why this memory is relevant:
                            </div>
                            <div style="font-size: 13px; color: #E2E8F0;">
                                {match.relevance_explanation}
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 10px;">
                            <div style="background: #0B132B; border: 1px solid {colors.BORDER}; border-radius: 6px; padding: 10px 14px;">
                                <b style="font-size: 12px; color: #94A3B8; text-transform: uppercase;">Historical Root Cause:</b>
                                <div style="font-size: 13px; color: #F8FAFC; margin-top: 4px;">{match.root_cause}</div>
                            </div>
                            <div style="background: #0B132B; border: 1px solid {colors.BORDER}; border-radius: 6px; padding: 10px 14px;">
                                <b style="font-size: 12px; color: #34D399; text-transform: uppercase;">Verified Historical Resolution:</b>
                                <div style="font-size: 13px; color: #F8FAFC; margin-top: 4px;">{match.resolution}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Section 2: Potential Root Causes (AI Hypotheses)
        st.markdown(
            f"""
            <div style="margin-top: 24px; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 20px; color: #F8FAFC;">
                    🔍 Potential Root Causes (AI Hypotheses)
                </h3>
                <p style="margin: 4px 0 0 0; font-size: 13px; color: {colors.SECONDARY_TEXT};">
                    Hypothesized explanations based on telemetry signatures and historical correlation. These are hypotheses, not confirmed facts.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        for h in report.potential_root_causes:
            conf_badge = get_severity_badge(h.confidence)
            st.markdown(
                f"""
                <div class="iris-card" style="padding: 16px 20px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; font-size: 16px; color: #F8FAFC;">● {h.title}</h4>
                        <div>Confidence: {conf_badge}</div>
                    </div>
                    <div style="font-size: 13px; color: #E2E8F0; margin-top: 6px;">
                        <b>Rationale:</b> {h.rationale}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Section 3: Recommended Investigation Steps
        st.markdown(
            f"""
            <div style="margin-top: 24px; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 20px; color: #F8FAFC;">
                    📋 Recommended Troubleshooting & Diagnostic Steps
                </h3>
                <p style="margin: 4px 0 0 0; font-size: 13px; color: {colors.SECONDARY_TEXT};">
                    Prioritized sequence of operational commands to verify hypotheses and isolate root cause.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        for s in report.recommended_steps:
            st.markdown(
                f"""
                <div class="iris-card" style="padding: 16px 20px; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="background: {colors.PRIMARY_BLUE}; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700;">
                            {s.step_number}
                        </span>
                        <b style="font-size: 15px; color: #F8FAFC;">{s.title}</b>
                    </div>
                    <div style="margin-top: 10px;">
                        <pre style="margin: 0; font-size: 13px;"><code>{s.command_or_query}</code></pre>
                    </div>
                    <div style="margin-top: 8px; font-size: 12px; color: {colors.SECONDARY_TEXT};">
                        <b>Expected Outcome:</b> {s.expected_outcome}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Section 4: Suggested Resolution & Mitigation
        st.markdown(
            f"""
            <div style="margin-top: 24px; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 20px; color: #F8FAFC;">
                    🛠️ Suggested Resolution & Immediate Remediation
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="iris-card" style="border-left: 4px solid {colors.SUCCESS_GREEN};">
                <div style="font-size: 14px; color: #F8FAFC; line-height: 1.6;">
                    {report.suggested_resolution}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Section 5: Confirm Resolution & Retain in Hindsight
        st.write("")
        st.markdown(
            f"""
            <div class="iris-card" style="background: linear-gradient(135deg, #064E3B 0%, #111C3A 100%); border: 1px solid #059669; margin-top: 20px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <span style="font-size: 22px;">💾</span>
                    <div>
                        <h3 style="margin: 0; color: #34D399; font-size: 18px;">Retain Investigation Knowledge into Hindsight</h3>
                        <p style="margin: 2px 0 0 0; font-size: 13px; color: #A7F3D0;">
                            Lock in verified root causes, troubleshooting steps, and resolution. Future occurrences will immediately retrieve this intelligence.
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("retain_knowledge_form"):
            confirmed_rc = st.text_area(
                "Confirmed Root Cause *",
                value=report.potential_root_causes[0].title if report.potential_root_causes else "",
                help="The verified technical root cause discovered during this investigation."
            )
            confirmed_steps = st.text_area(
                "Troubleshooting Steps Executed *",
                value="\n".join([f"{s.step_number}. {s.title}: {s.command_or_query}" for s in report.recommended_steps]),
                help="The actual diagnostic procedure performed to isolate the failure."
            )
            confirmed_resolution = st.text_area(
                "Verified Resolution Applied *",
                value=report.suggested_resolution,
                help="The concrete mitigation and permanent architecture fix deployed."
            )

            retain_submit = st.form_submit_button("🧠 Confirm Resolution & Retain into Hindsight", type="primary", use_container_width=True)

        if retain_submit:
            if not confirmed_rc.strip() or not confirmed_resolution.strip():
                st.error("Please enter the confirmed root cause and verified resolution before retaining.")
            else:
                with st.spinner("Retaining structured knowledge into Hindsight persistent memory..."):
                    retain_res = incident_handler.resolve_and_retain(
                        incident_id=inc_id,
                        root_cause=confirmed_rc,
                        steps_taken=confirmed_steps,
                        resolution=confirmed_resolution
                    )
                st.success(f"✓ {retain_res.message} (Memory ID: {retain_res.memory_id})")
                st.balloons()
                st.session_state["current_report"] = None
                st.session_state["active_incident_id"] = None
                st.rerun()
