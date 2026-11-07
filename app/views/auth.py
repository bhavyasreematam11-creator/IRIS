"""Authentication View: Login and Signup for IRIS in Dark Blue SaaS Theme."""

import streamlit as st
from database.db import authenticate_user, create_user
from utils.config import colors


def render_auth_page():
    """Render the Sign In and Sign Up portal."""
    st.markdown(
        f"""
        <div style="max-width: 480px; margin: 40px auto 20px auto; text-align: center;">
            <div style="background: {colors.PRIMARY_BLUE}; color: white; width: 48px; height: 48px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 800; box-shadow: 0 0 20px rgba(59, 130, 246, 0.4); margin-bottom: 12px;">
                ⚡
            </div>
            <h1 style="margin: 0; font-size: 32px; color: #F8FAFC; letter-spacing: -0.03em;">IRIS</h1>
            <p style="margin: 4px 0 0 0; font-size: 14px; color: {colors.SECONDARY_TEXT};">
                Intelligent Incident Response System • Persistent SRE Memory
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_l, col_center, col_r = st.columns([1, 2, 1])

    with col_center:
        auth_tab1, auth_tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])

        with auth_tab1:
            st.markdown(
                f"""
                <div class="iris-card" style="margin-top: 10px;">
                    <h3 style="margin-top: 0; font-size: 18px; color: #F8FAFC;">Welcome Back</h3>
                    <p style="font-size: 13px; color: {colors.SECONDARY_TEXT}; margin-bottom: 16px;">
                        Authenticate to access incident investigations and Hindsight memory banks.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("signin_form"):
                email = st.text_input("Work Email", placeholder="e.g. bhavya@iris.ai")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                login_submit = st.form_submit_button("Sign In to IRIS", type="primary", use_container_width=True)

            if login_submit:
                if not email.strip() or not password.strip():
                    st.error("Please provide both email and password.")
                else:
                    user = authenticate_user(email.strip(), password.strip())
                    if user:
                        st.session_state["user"] = user
                        st.session_state["is_authenticated"] = True
                        st.session_state["current_page"] = "overview"
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please verify your email and password.")

            st.write("")
            st.markdown(
                f"""
                <div style="text-align: center; margin: 10px 0; font-size: 12px; color: {colors.SECONDARY_TEXT};">
                    ── OR ONE-CLICK DEMO LOGIN ──
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("⚡ Quick Demo Login (as Bhavya Sharma - Principal SRE)", use_container_width=True):
                user = authenticate_user("bhavya@iris.ai", "password123")
                if user:
                    st.session_state["user"] = user
                    st.session_state["is_authenticated"] = True
                    st.session_state["current_page"] = "overview"
                    st.rerun()

        with auth_tab2:
            st.markdown(
                f"""
                <div class="iris-card" style="margin-top: 10px;">
                    <h3 style="margin-top: 0; font-size: 18px; color: #F8FAFC;">Create Responder Account</h3>
                    <p style="font-size: 13px; color: {colors.SECONDARY_TEXT}; margin-bottom: 16px;">
                        Join your team's SRE incident response workspace.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("signup_form"):
                name = st.text_input("Full Name *", placeholder="e.g. Jane Doe")
                reg_email = st.text_input("Work Email *", placeholder="e.g. jane@company.com")
                reg_password = st.text_input("Password *", type="password", placeholder="At least 6 characters")
                role = st.selectbox(
                    "Primary Role *",
                    [
                        "Principal SRE",
                        "Site Reliability Engineer",
                        "DevOps Engineer",
                        "Incident Commander",
                        "Cloud Platform Architect",
                        "Security Operations Lead"
                    ]
                )
                department = st.selectbox(
                    "Department *",
                    [
                        "Core Platform & Reliability",
                        "Infrastructure Engineering",
                        "Security & Compliance",
                        "Cloud & Distributed Systems",
                        "Product Engineering"
                    ]
                )
                signup_submit = st.form_submit_button("Create Account & Access IRIS", type="primary", use_container_width=True)

            if signup_submit:
                if not name.strip() or not reg_email.strip() or not reg_password.strip():
                    st.error("Please fill in all required fields.")
                elif len(reg_password.strip()) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success, msg, new_user = create_user(
                        name=name.strip(),
                        email=reg_email.strip(),
                        password=reg_password.strip(),
                        role=role,
                        department=department
                    )
                    if success and new_user:
                        st.session_state["user"] = new_user
                        st.session_state["is_authenticated"] = True
                        st.session_state["current_page"] = "overview"
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error(msg)
