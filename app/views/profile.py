"""User Profile view for IRIS: Profile details, role customization, and credentials management."""

import streamlit as st
from database.db import get_user_by_id, update_user_password, update_user_profile
from utils.config import colors
from utils.helpers import format_timestamp


def render_profile():
    """Render user profile details and settings."""
    user = st.session_state.get("user")
    if not user:
        st.warning("No active session found. Please sign in.")
        return

    # Refresh user from database to ensure up-to-date data
    fresh_user = get_user_by_id(user["id"])
    if fresh_user:
        user = fresh_user
        st.session_state["user"] = fresh_user

    # Header
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h2 style="margin: 0; color: #F8FAFC; font-size: 26px;">👤 User Profile & Preferences</h2>
            <p style="margin: 4px 0 0 0; color: {colors.SECONDARY_TEXT}; font-size: 14px;">
                Manage your responder credentials, on-call status, and incident response preferences.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Top User Identity Card
    st.markdown(
        f"""
        <div class="iris-card" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="background: linear-gradient(135deg, {colors.PRIMARY_BLUE} 0%, #1D4ED8 100%); width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 700; color: white; box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);">
                    {user['name'][:1].upper()}
                </div>
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <h3 style="margin: 0; font-size: 22px; color: #F8FAFC;">{user['name']}</h3>
                        <span class="status-pill status-pill-blue">{user['role']}</span>
                    </div>
                    <div style="font-size: 13px; color: {colors.SECONDARY_TEXT}; margin-top: 4px;">
                        <b>Email:</b> {user['email']} &nbsp;•&nbsp; <b>Dept:</b> {user.get('department', 'Reliability Engineering')}
                    </div>
                    <div style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-top: 2px;">
                        Member since: {format_timestamp(user.get('created_at'))}
                    </div>
                </div>
            </div>
            <div>
                <span style="background: #064E3B; color: #34D399; border: 1px solid #059669; padding: 6px 14px; border-radius: 9999px; font-size: 12px; font-weight: 600;">
                    🟢 Active On-Call Responder
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    p_col1, p_col2 = st.columns([3, 2])

    with p_col1:
        st.markdown(
            f"""
            <div class="iris-card">
                <h3 style="margin-top: 0; font-size: 18px; color: #F8FAFC;">Edit Responder Details</h3>
                <p style="font-size: 13px; color: {colors.SECONDARY_TEXT};">
                    Update how your identity appears across incident postmortems and memory audit logs.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("edit_profile_form"):
            new_name = st.text_input("Full Name", value=user["name"])
            new_role = st.selectbox(
                "Role",
                [
                    "Principal SRE",
                    "Site Reliability Engineer",
                    "DevOps Engineer",
                    "Incident Commander",
                    "Cloud Platform Architect",
                    "Security Operations Lead"
                ],
                index=[
                    "Principal SRE",
                    "Site Reliability Engineer",
                    "DevOps Engineer",
                    "Incident Commander",
                    "Cloud Platform Architect",
                    "Security Operations Lead"
                ].index(user["role"]) if user["role"] in [
                    "Principal SRE",
                    "Site Reliability Engineer",
                    "DevOps Engineer",
                    "Incident Commander",
                    "Cloud Platform Architect",
                    "Security Operations Lead"
                ] else 0
            )
            new_department = st.text_input("Department / Team", value=user.get("department", "Core Platform & Reliability"))
            new_bio = st.text_area(
                "SRE Specialization & Bio",
                value=user.get("bio", ""),
                placeholder="Describe your areas of expertise (e.g. Distributed DBs, Kubernetes Networking, Kafka, Ingress Security)...",
                height=100
            )

            save_profile = st.form_submit_button("Save Profile Changes", type="primary")

        if save_profile:
            if not new_name.strip():
                st.error("Name cannot be empty.")
            else:
                ok = update_user_profile(
                    user_id=user["id"],
                    name=new_name.strip(),
                    role=new_role,
                    department=new_department.strip(),
                    bio=new_bio.strip()
                )
                if ok:
                    st.success("Profile updated successfully!")
                    st.session_state["user"] = get_user_by_id(user["id"])
                    st.rerun()
                else:
                    st.error("Failed to update profile.")

    with p_col2:
        st.markdown(
            f"""
            <div class="iris-card">
                <h3 style="margin-top: 0; font-size: 18px; color: #F8FAFC;">Security & Password</h3>
                <p style="font-size: 13px; color: {colors.SECONDARY_TEXT};">
                    Update your account authentication credentials.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("change_password_form"):
            new_pwd = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_pwd = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
            pwd_submit = st.form_submit_button("Update Password", use_container_width=True)

        if pwd_submit:
            if not new_pwd.strip() or len(new_pwd.strip()) < 6:
                st.error("New password must be at least 6 characters.")
            elif new_pwd != confirm_pwd:
                st.error("Passwords do not match.")
            else:
                ok = update_user_password(user["id"], new_pwd.strip())
                if ok:
                    st.success("Password changed successfully!")
                else:
                    st.error("Failed to update password.")

        st.write("")
        st.markdown(
            f"""
            <div class="iris-card" style="border-color: #7F1D1D; background: #1A0F1A;">
                <h4 style="margin-top: 0; color: #F87171; font-size: 15px;">Session Actions</h4>
                <p style="font-size: 12px; color: {colors.SECONDARY_TEXT}; margin-bottom: 12px;">
                    Sign out of this active browser session on IRIS.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🚪 Sign Out of IRIS", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["is_authenticated"] = False
            st.session_state["current_page"] = "overview"
            st.rerun()
