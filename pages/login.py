import hashlib

import streamlit as st

from database.db import SessionLocal
from database.schema import User


def hash_password(password: str) -> str:
    """
    Convert a password into a SHA-256 hash.
    """
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def show_login():

    st.title("🔐 AI Campus Lost & Found")

    login_tab, register_tab = st.tabs(
        ["🔑 Login", "📝 Create Account"]
    )

    # ======================================================
    # LOGIN
    # ======================================================
    with login_tab:

        st.subheader("Login")

        role = st.selectbox(
            "Login as",
            ["Student", "Admin"],
            key="login_role"
        )

        email = st.text_input(
            "Email",
            key="login_email"
        ).strip().lower()

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if not email or not password:
                st.warning(
                    "Please enter email and password."
                )

            else:

                db = SessionLocal()

                try:

                    user = (
                        db.query(User)
                        .filter(User.email == email)
                        .first()
                    )

                    if not user:

                        st.error(
                            "Account not found. "
                            "Please create an account first."
                        )

                    elif not user.is_active:

                        st.error(
                            "This account is inactive."
                        )

                    elif user.password_hash != hash_password(password):

                        st.error(
                            "Invalid email or password."
                        )

                    elif user.role != role.lower():

                        st.error(
                            "Selected role does not match "
                            "this account."
                        )

                    else:

                        st.session_state["logged_in"] = True
                        st.session_state["role"] = user.role
                        st.session_state["user_name"] = user.name
                        st.session_state["user_id"] = user.id
                        st.session_state["page"] = "dashboard"

                        st.success(
                            "Login successful!"
                        )

                        st.rerun()

                except Exception as e:

                    st.error(
                        f"Login error: {e}"
                    )

                finally:

                    db.close()

    # ======================================================
    # REGISTRATION
    # ======================================================
    with register_tab:

        st.subheader("Create Student Account")

        name = st.text_input(
            "Full Name",
            key="register_name"
        )

        email = st.text_input(
            "Email",
            key="register_email"
        ).strip().lower()

        password = st.text_input(
            "Create App Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm_password"
        )

        st.caption(
            "Use a password created for this app. "
            "Do not enter your Gmail or college email password."
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not name.strip():
                st.warning(
                    "Please enter your name."
                )

            elif not email:
                st.warning(
                    "Please enter your email."
                )

            elif len(password) < 6:
                st.warning(
                    "Password must contain at least 6 characters."
                )

            elif password != confirm_password:
                st.error(
                    "Passwords do not match."
                )

            else:

                db = SessionLocal()

                try:

                    existing_user = (
                        db.query(User)
                        .filter(User.email == email)
                        .first()
                    )

                    if existing_user:

                        st.error(
                            "An account with this email "
                            "already exists."
                        )

                    else:

                        new_user = User(
                            name=name.strip(),
                            email=email,
                            password_hash=hash_password(password),
                            role="student",
                            reward_points=0,
                            is_active=True
                        )

                        db.add(new_user)
                        db.commit()
                        db.refresh(new_user)

                        st.success(
                            "✅ Account created successfully! "
                            "You can now login."
                        )

                except Exception as e:

                    db.rollback()

                    st.error(
                        f"Registration error: {e}"
                    )

                finally:

                    db.close()