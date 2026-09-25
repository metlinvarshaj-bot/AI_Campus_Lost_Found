import os
import importlib
import inspect
import hashlib

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import func

from database.db import engine, Base, SessionLocal
from database import schema


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Campus Lost & Found",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """
    Automatically create all database tables.

    This is important for Streamlit Cloud because the cloud
    environment may start with a fresh SQLite database.
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        st.error(f"Database initialization failed: {exc}")
        st.stop()


initialize_database()


# ============================================================
# REQUIRED DIRECTORIES
# ============================================================

def create_required_directories():
    folders = [
        "assets",
        "uploads",
        "uploads/lost",
        "uploads/found",
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)


create_required_directories()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main content spacing */
    .main {
        padding-top: 1rem;
    }

    /* Hide Streamlit's automatic pages navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.20);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
    }

    /* Footer */
    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION_STATE = {
    "logged_in": False,
    "role": None,
    "user_id": None,
    "user_name": None,
    "page": "dashboard",
    "current_page": "dashboard",
}


for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db_session():
    return SessionLocal()


# ============================================================
# ADMIN AUTO-CREATE
# ============================================================

def ensure_admin_account():
    """
    Create or synchronize the admin account from Streamlit Secrets.

    Required Streamlit Secrets:

    [admin]
    email = "admin@campus.com"
    password = "YOUR_ADMIN_PASSWORD"
    """

    try:
        admin_email = str(
            st.secrets["admin"]["email"]
        ).strip().lower()

        admin_password = str(
            st.secrets["admin"]["password"]
        )

    except Exception:
        # Secrets are not configured.
        return

    if not admin_email or not admin_password:
        return

    password_hash = hashlib.sha256(
        admin_password.encode("utf-8")
    ).hexdigest()

    db = get_db_session()

    try:

        admin_user = (
            db.query(schema.User)
            .filter(
                schema.User.email == admin_email
            )
            .first()
        )

        # ----------------------------------------------------
        # CREATE ADMIN IF MISSING
        # ----------------------------------------------------

        if admin_user is None:

            admin_user = schema.User(
                name="Campus Admin",
                email=admin_email,
                password_hash=password_hash,
                role="admin",
                reward_points=0,
                is_active=True,
            )

            db.add(admin_user)
            db.commit()

        # ----------------------------------------------------
        # SYNCHRONIZE EXISTING ADMIN
        # ----------------------------------------------------

        else:

            changed = False

            if admin_user.role != "admin":
                admin_user.role = "admin"
                changed = True

            if not admin_user.is_active:
                admin_user.is_active = True
                changed = True

            if admin_user.password_hash != password_hash:
                admin_user.password_hash = password_hash
                changed = True

            if changed:
                db.commit()

    except Exception:
        db.rollback()

    finally:
        db.close()


ensure_admin_account()


# ============================================================
# PAGE NAVIGATION
# ============================================================

def set_page(page_name):
    st.session_state["page"] = page_name
    st.session_state["current_page"] = page_name


# ============================================================
# DASHBOARD COUNTS
# ============================================================

def get_dashboard_counts(user_id=None, role=None):

    db = get_db_session()

    try:

        # ----------------------------------------------------
        # STUDENT COUNTS
        # ----------------------------------------------------

        if role == "student" and user_id is not None:

            lost_count = (
                db.query(schema.LostItem)
                .filter(
                    schema.LostItem.user_id == user_id
                )
                .count()
            )

            found_count = (
                db.query(schema.FoundItem)
                .filter(
                    schema.FoundItem.user_id == user_id
                )
                .count()
            )

            matched_count = (
                db.query(schema.Match)
                .join(
                    schema.LostItem,
                    schema.Match.lost_item_id
                    == schema.LostItem.id
                )
                .filter(
                    schema.LostItem.user_id == user_id
                )
                .count()
            )

            returned_count = (
                db.query(schema.LostItem)
                .filter(
                    schema.LostItem.user_id == user_id,
                    schema.LostItem.status == "RETURNED",
                )
                .count()
            )

            user = (
                db.query(schema.User)
                .filter(
                    schema.User.id == user_id
                )
                .first()
            )

            reward_points = (
                user.reward_points
                if user
                else 0
            )

            return {
                "lost": lost_count,
                "found": found_count,
                "matches": matched_count,
                "returned": returned_count,
                "reward_points": reward_points,
            }

        # ----------------------------------------------------
        # ADMIN / OVERALL COUNTS
        # ----------------------------------------------------

        lost_count = (
            db.query(schema.LostItem).count()
        )

        found_count = (
            db.query(schema.FoundItem).count()
        )

        match_count = (
            db.query(schema.Match).count()
        )

        returned_count = (
            db.query(schema.LostItem)
            .filter(
                schema.LostItem.status == "RETURNED"
            )
            .count()
        )

        pending_verifications = (
            db.query(schema.Verification)
            .filter(
                schema.Verification.status == "PENDING"
            )
            .count()
        )

        reward_transactions = (
            db.query(schema.Reward).count()
        )

        total_reward_points = (
            db.query(
                func.coalesce(
                    func.sum(schema.Reward.points),
                    0,
                )
            ).scalar()
            or 0
        )

        return {
            "lost": lost_count,
            "found": found_count,
            "matches": match_count,
            "returned": returned_count,
            "pending_verifications": pending_verifications,
            "reward_transactions": reward_transactions,
            "reward_points": total_reward_points,
        }

    finally:
        db.close()


# ============================================================
# STUDENT DASHBOARD
# ============================================================

def student_dashboard():

    user_name = st.session_state.get(
        "user_name",
        "Student",
    )

    st.title("🔐 AI Campus Lost & Found")

    st.caption(
        f"Welcome back, {user_name}. "
        "Find, verify and securely recover lost belongings."
    )

    counts = get_dashboard_counts(
        user_id=st.session_state.get("user_id"),
        role="student",
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "My Lost Items",
            counts["lost"],
        )

    with col2:
        st.metric(
            "My Found Items",
            counts["found"],
        )

    with col3:
        st.metric(
            "Possible Matches",
            counts["matches"],
        )

    with col4:
        st.metric(
            "Returned Items",
            counts["returned"],
        )

    with col5:
        st.metric(
            "Reward Points",
            counts["reward_points"],
        )

    st.divider()

    # --------------------------------------------------------
    # HOW SYSTEM WORKS
    # --------------------------------------------------------

    st.subheader("How the system works")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("📦 1. Report")
        st.write(
            "Report your lost or found item with "
            "description, location, time and optional photo."
        )

    with c2:
        st.subheader("🤖 2. AI Match")
        st.write(
            "AI compares text, location, time and images "
            "to identify possible matching items."
        )

    with c3:
        st.subheader("🔐 3. Secure Return")
        st.write(
            "Verify ownership and complete the final "
            "handover using OTP and QR verification."
        )

    st.divider()

    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------

    st.subheader("Quick Actions")

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        if st.button(
            "📱 Report Lost Item",
            use_container_width=True,
        ):
            set_page("lost_item")
            st.rerun()

    with q2:
        if st.button(
            "📦 Report Found Item",
            use_container_width=True,
        ):
            set_page("found_item")
            st.rerun()

    with q3:
        if st.button(
            "🤖 Possible Matches",
            use_container_width=True,
        ):
            set_page("possible_matches")
            st.rerun()

    with q4:
        if st.button(
            "🎁 My Rewards",
            use_container_width=True,
        ):
            set_page("rewards")
            st.rerun()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def admin_dashboard():

    st.title("🛡️ Campus Lost & Found Admin")

    st.caption(
        "Monitor verification, handover and AI matching activity."
    )

    counts = get_dashboard_counts(
        role="admin"
    )

    # --------------------------------------------------------
    # FIRST ROW
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Lost",
            counts["lost"],
        )

    with col2:
        st.metric(
            "Total Found",
            counts["found"],
        )

    with col3:
        st.metric(
            "AI Matches",
            counts["matches"],
        )

    with col4:
        st.metric(
            "Returned",
            counts["returned"],
        )

    # --------------------------------------------------------
    # SECOND ROW
    # --------------------------------------------------------

    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric(
            "Pending Verification",
            counts["pending_verifications"],
        )

    with col6:
        st.metric(
            "Reward Transactions",
            counts["reward_transactions"],
        )

    with col7:
        st.metric(
            "Reward Points",
            counts["reward_points"],
        )

    st.divider()

    # --------------------------------------------------------
    # OVERVIEW CHART
    # --------------------------------------------------------

    st.subheader("System Overview")

    overview_df = pd.DataFrame(
        {
            "Metric": [
                "Lost Items",
                "Found Items",
                "AI Matches",
                "Returned Items",
                "Pending Verification",
            ],
            "Count": [
                counts["lost"],
                counts["found"],
                counts["matches"],
                counts["returned"],
                counts["pending_verifications"],
            ],
        }
    )

    fig = px.bar(
        overview_df,
        x="Metric",
        y="Count",
        title="Campus Lost & Found Overview",
        text="Count",
    )

    fig.update_layout(
        xaxis_title="",
        yaxis_title="Count",
        showlegend=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# PAGE MODULE RUNNER
# ============================================================

def run_page_module(
    module_name,
    function_candidates,
):
    """
    Dynamically load page modules.

    This keeps the existing pages/*.py architecture intact.
    """

    try:

        module = importlib.import_module(
            f"pages.{module_name}"
        )

    except Exception as exc:

        st.error(
            f"Unable to load pages/{module_name}.py\n\n{exc}"
        )

        return

    # --------------------------------------------------------
    # TRY KNOWN FUNCTION NAMES
    # --------------------------------------------------------

    for function_name in function_candidates:

        function = getattr(
            module,
            function_name,
            None,
        )

        if callable(function):

            try:
                function()
            except Exception as exc:
                st.error(
                    f"Error in {module_name}.py: {exc}"
                )

            return

    # --------------------------------------------------------
    # FALLBACK DISCOVERY
    # --------------------------------------------------------

    candidates = []

    for name, obj in inspect.getmembers(
        module,
        inspect.isfunction,
    ):

        if obj.__module__ != module.__name__:
            continue

        lowered = name.lower()

        if any(
            keyword in lowered
            for keyword in [
                "page",
                "render",
                "show",
                "main",
                "dashboard",
            ]
        ):

            candidates.append(
                (name, obj)
            )

    if candidates:

        try:

            candidates[0][1]()

        except Exception as exc:

            st.error(
                f"Error while running {module_name}.py: {exc}"
            )

        return

    st.warning(
        f"No page function found in pages/{module_name}.py"
    )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def render_sidebar():

    with st.sidebar:

        st.title("🔐 AI Campus Lost & Found")

        # ----------------------------------------------------
        # LOGGED-IN USER
        # ----------------------------------------------------

        if st.session_state.get("logged_in"):

            user_name = st.session_state.get(
                "user_name",
                "User",
            )

            role = st.session_state.get(
                "role",
                "student",
            )

            st.subheader(f"👤 {user_name}")
            st.caption(f"Role: {role.title()}")

            st.divider()

            # ------------------------------------------------
            # STUDENT NAVIGATION
            # ------------------------------------------------

            if role == "student":

                navigation = {
                    "🏠 Dashboard": "dashboard",
                    "📱 Report Lost": "lost_item",
                    "📦 Report Found": "found_item",
                    "📋 My Reports": "my_reports",
                    "🤖 Possible Matches": "possible_matches",
                    "✅ Verification": "verification",
                    "🔐 Secure Handover": "handover",
                    "🎁 My Rewards": "rewards",
                }

            # ------------------------------------------------
            # ADMIN NAVIGATION
            # ------------------------------------------------

            else:

                navigation = {
                    "🏠 Dashboard": "dashboard",
                    "✅ Verification Review": "admin_verification",
                    "🔐 Secure Handover": "handover",
                    "📊 Analytics": "admin_analytics",
                }

            current_page = st.session_state.get(
                "page",
                "dashboard",
            )

            labels = list(
                navigation.keys()
            )

            values = list(
                navigation.values()
            )

            current_index = (
                values.index(current_page)
                if current_page in values
                else 0
            )

            selected_label = st.radio(
                "Navigation",
                labels,
                index=current_index,
            )

            selected_page = navigation[
                selected_label
            ]

            if selected_page != current_page:

                set_page(
                    selected_page
                )

                st.rerun()

            st.divider()

            # ------------------------------------------------
            # LOGOUT
            # ------------------------------------------------

            if st.button(
                "🚪 Logout",
                use_container_width=True,
            ):

                st.session_state["logged_in"] = False
                st.session_state["role"] = None
                st.session_state["user_id"] = None
                st.session_state["user_name"] = None
                st.session_state["page"] = "dashboard"
                st.session_state["current_page"] = "dashboard"

                st.rerun()

        else:

            st.info(
                "Please login or create a student account to continue."
            )


# ============================================================
# LOGIN PAGE
# ============================================================

def run_login_page():

    run_page_module(
        "login",
        [
            "login_page",
            "show_login_page",
            "show_login",
            "render_login",
            "render_login_page",
            "main",
        ],
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    # --------------------------------------------------------
    # USER NOT LOGGED IN
    # --------------------------------------------------------

    if not st.session_state.get(
        "logged_in",
        False,
    ):

        run_login_page()
        return

    # --------------------------------------------------------
    # USER LOGGED IN
    # --------------------------------------------------------

    render_sidebar()

    current_page = st.session_state.get(
        "page",
        "dashboard",
    )

    # ========================================================
    # DASHBOARD
    # ========================================================

    if current_page == "dashboard":

        if (
            st.session_state.get("role")
            == "admin"
        ):
            admin_dashboard()

        else:
            student_dashboard()

    # ========================================================
    # STUDENT PAGES
    # ========================================================

    elif current_page == "lost_item":

        run_page_module(
            "lost_item",
            [
                "lost_item_page",
                "show_lost_item",
                "show_lost_item_page",
                "render_lost_item",
                "render_lost_item_page",
                "main",
            ],
        )

    elif current_page == "found_item":

        run_page_module(
            "found_item",
            [
                "found_item_page",
                "show_found_item",
                "show_found_item_page",
                "render_found_item",
                "render_found_item_page",
                "main",
            ],
        )

    elif current_page == "my_reports":

        run_page_module(
            "my_reports",
            [
                "my_reports_page",
                "show_my_reports",
                "render_my_reports",
                "main",
            ],
        )

    elif current_page == "possible_matches":

        run_page_module(
            "possible_matches",
            [
                "possible_matches_page",
                "show_possible_matches",
                "render_possible_matches",
                "main",
            ],
        )

    elif current_page == "verification":

        run_page_module(
            "verification",
            [
                "verification_page",
                "show_verification",
                "render_verification",
                "main",
            ],
        )

    elif current_page == "rewards":

        run_page_module(
            "rewards",
            [
                "rewards_page",
                "show_rewards",
                "render_rewards",
                "main",
            ],
        )

    # ========================================================
    # SECURE HANDOVER
    # ========================================================

    elif current_page == "handover":

        run_page_module(
            "handover",
            [
                "handover_page",
                "show_handover",
                "render_handover",
                "main",
            ],
        )

    # ========================================================
    # ADMIN VERIFICATION
    # ========================================================

    elif current_page == "admin_verification":

        if (
            st.session_state.get("role")
            != "admin"
        ):

            st.error(
                "Admin access required."
            )

            set_page("dashboard")
            st.stop()

        run_page_module(
            "admin_verification",
            [
                "admin_verification_page",
                "show_admin_verification",
                "render_admin_verification",
                "main",
            ],
        )

    # ========================================================
    # ADMIN ANALYTICS
    # ========================================================

    elif current_page == "admin_analytics":

        if (
            st.session_state.get("role")
            != "admin"
        ):

            st.error(
                "Admin access required."
            )

            set_page("dashboard")
            st.stop()

        run_page_module(
            "admin_analytics",
            [
                "admin_analytics_page",
                "show_admin_analytics",
                "render_admin_analytics",
                "main",
            ],
        )

    # ========================================================
    # UNKNOWN PAGE
    # ========================================================

    else:

        st.warning(
            "Unknown page selected. Returning to dashboard."
        )

        set_page("dashboard")
        st.rerun()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()