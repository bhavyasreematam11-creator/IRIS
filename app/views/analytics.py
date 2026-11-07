"""Analytics Dashboard view for IRIS: Incident trends, memory impact, and resolution metrics (Dark Blue Theme)."""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.db import get_analytics_summary, list_incidents, list_memory_audit
from utils.config import colors


def render_analytics():
    """Render the Analytics Dashboard with Plotly Dark Blue visualizations."""
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <h2 style="margin: 0; color: #F8FAFC; font-size: 26px;">📊 Operational Analytics & Memory Impact</h2>
            <p style="margin: 4px 0 0 0; color: {colors.SECONDARY_TEXT}; font-size: 14px;">
                Quantitative metrics on incident trends, failure categories, recurring systems, and Hindsight memory effectiveness.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    stats = get_analytics_summary()
    incidents = list_incidents()
    audits = list_memory_audit(limit=200)

    # Top KPI metric cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: {colors.PRIMARY_BLUE};">
                <div class="iris-metric-label">Total Incidents</div>
                <div class="iris-metric-value">{stats['total_incidents']}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Persisted in database</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k2:
        resolution_rate = int((stats['resolved_incidents'] / max(stats['total_incidents'], 1)) * 100)
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: {colors.SUCCESS_GREEN};">
                <div class="iris-metric-label">Resolution Rate</div>
                <div class="iris-metric-value">{resolution_rate}%</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">{stats['resolved_incidents']} of {stats['total_incidents']} resolved</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k3:
        retention_rate = int((stats['retained_memories'] / max(stats['total_incidents'], 1)) * 100)
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: #8B5CF6;">
                <div class="iris-metric-label">Memory Retention</div>
                <div class="iris-metric-value">{retention_rate}%</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Preserved in Hindsight</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f"""
            <div class="iris-metric-card" style="border-top-color: {colors.WARNING_AMBER};">
                <div class="iris-metric-label">Recurring Clusters</div>
                <div class="iris-metric-value">{stats['recurring_incident_groups']}</div>
                <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">Repeated system issues</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # Visualizations Row 1: Severity Distribution & Category Breakdown
    g1, g2 = st.columns(2)

    with g1:
        st.markdown(
            f"""
            <div class="iris-card">
                <h4 style="margin: 0 0 10px 0; color: #F8FAFC; font-size: 16px;">Severity Distribution</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        sev_counts = stats["severity_dist"]
        if sev_counts:
            df_sev = pd.DataFrame([{"Severity": k, "Count": v} for k, v in sev_counts.items()])
            color_map = {
                "Critical": "#EF4444",
                "High": "#F59E0B",
                "Medium": "#3B82F6",
                "Low": "#10B981"
            }
            fig1 = px.pie(
                df_sev,
                values="Count",
                names="Severity",
                hole=0.6,
                color="Severity",
                color_discrete_map=color_map
            )
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                legend=dict(font=dict(color="#94A3B8"))
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No severity data available.")

    with g2:
        st.markdown(
            f"""
            <div class="iris-card">
                <h4 style="margin: 0 0 10px 0; color: #F8FAFC; font-size: 16px;">Incidents by Category</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        cat_counts = stats["category_dist"]
        if cat_counts:
            df_cat = pd.DataFrame([{"Category": k, "Count": v} for k, v in cat_counts.items()])
            fig2 = px.bar(
                df_cat,
                x="Category",
                y="Count",
                text="Count",
                color_discrete_sequence=[colors.PRIMARY_BLUE]
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                xaxis=dict(title="", showgrid=False, tickfont=dict(color="#94A3B8")),
                yaxis=dict(title="Incidents", showgrid=True, gridcolor="#1E2D54", tickfont=dict(color="#94A3B8"), titlefont=dict(color="#94A3B8"))
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No category data available.")

    st.write("")

    # Visualizations Row 2: Memory Retrieval Activity & Recurring Systems
    g3, g4 = st.columns(2)

    with g3:
        st.markdown(
            f"""
            <div class="iris-card">
                <h4 style="margin: 0 0 10px 0; color: #F8FAFC; font-size: 16px;">Memory Activity (Retain vs. Recall)</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        if audits:
            df_audits = pd.DataFrame(audits)
            action_counts = df_audits["action"].value_counts().reset_index()
            action_counts.columns = ["Action", "Count"]
            fig3 = px.bar(
                action_counts,
                x="Action",
                y="Count",
                color="Action",
                color_discrete_map={"RECALL": colors.PRIMARY_BLUE, "RETAIN": colors.SUCCESS_GREEN},
                text="Count"
            )
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                xaxis=dict(title="", tickfont=dict(color="#94A3B8")),
                yaxis=dict(title="Operations", showgrid=True, gridcolor="#1E2D54", tickfont=dict(color="#94A3B8"), titlefont=dict(color="#94A3B8")),
                showlegend=False
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No memory audit activity recorded yet.")

    with g4:
        st.markdown(
            f"""
            <div class="iris-card">
                <h4 style="margin: 0 0 10px 0; color: #F8FAFC; font-size: 16px;">Recurring Systems Analysis</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        if incidents:
            df_inc = pd.DataFrame(incidents)
            sys_counts = df_inc["affected_system"].value_counts().head(6).reset_index()
            sys_counts.columns = ["System", "Incidents"]
            fig4 = px.bar(
                sys_counts,
                x="Incidents",
                y="System",
                orientation="h",
                text="Incidents",
                color_discrete_sequence=["#38BDF8"]
            )
            fig4.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                yaxis=dict(autorange="reversed", title="", tickfont=dict(color="#94A3B8")),
                xaxis=dict(showgrid=True, gridcolor="#1E2D54", tickfont=dict(color="#94A3B8"))
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No system incident data recorded.")
