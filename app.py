import os
import importlib
import inspect

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import func

# ============================================================
# DATABASE IMPORTS
# ============================================================

from database.db import engine, Base, SessionLocal
from database import schema


# ============================================================
# DATABASE INITIALIZATION
# IMPORTANT FOR STREAMLIT CLOUD
# ============================================================

def initialize_database():
    """
    Create all SQLAlchemy tables when the application starts.

    This is especially important on Streamlit Cloud because the
    local SQLite database file may not already exist there.
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        st.error(f"Database initialization failed: {exc}")
        st.stop()


initialize_database()


# ============================================================
# CREATE REQUIRED DIRECTORIES
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
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Campus Lost & Found",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROFESSIONAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */
    .main {
        padding-top: 1rem;
    }

    /* App title */
    .app-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        font-size: 1rem;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }

    /* Metric cards */
    .metric-card {
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        background: rgba(128, 128, 128, 0.06);
        min-height: 120px;
    }

    .metric-title {
        font-size: 0.9rem;
        opacity: 0.75;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
    }

    /* Section cards */
    .info-card {
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid rgba(128, 128, 128, 0.22);
        margin-bottom: 1rem;
        background: rgba(128, 128, 128, 0.04);
    }

    /* Status boxes */
    .success-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #2e8b57;
        background: rgba(46, 139, 87, 0.10);
    }

    .warning-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #d69e2e;
        background: rgba(214, 158, 46, 0.10);
    }

    .error-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #c53030;
        background: rgba(197, 48, 48, 0.10);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.20);
    }

    /* Hide footer */
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

default_session_state = {
    "logged_in": False,
    "role": None,
    "user_id": None,
    "user_name": None,
    "page": "dashboard",
    "current_page": "dashboard",
}


for key, value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# DATABASE SESSION HELPER
# ============================================================

def get_db_session():
    return SessionLocal()


# ============================================================
# NAVIGATION HELPER
# ============================================================

def set_page(page_name):
    st.session_state["page"] = page_name
    st.session_state["current_page"] = page_name


# ============================================================
# DATABASE COUNTS
# ============================================================

def get_dashboard_counts(user_id=None, role=None):
    db = get_db_session()

    try:
        if role == "student" and user_id is not None:
            lost_count = (
                db.query(schema.LostItem)
                .filter(schema.LostItem.user_id == user_id)
                .count()
            )

            found_count = (
                db.query(schema.FoundItem)
                .filter(schema.FoundItem.user_id == user_id)
                .count()
            )

            matched_count = (
                db.query(schema.Match)
                .join(
                    schema.LostItem,
                    schema.Match.lost_item_id == schema.LostItem.id
                )
                .filter(schema.LostItem.user_id == user_id)
                .count()
            )

            returned_count = (
                db.query(schema.LostItem)
                .filter(
                    schema.LostItem.user_id == user_id,
                    schema.LostItem.status == "RETURNED"
                )
                .count()
            )

            user = (
                db.query(schema.User)
                .filter(schema.User.id == user_id)
                .first()
            )

            reward_points = user.reward_points if user else 0

            return {
                "lost": lost_count,
                "found": found_count,
                "matches": matched_count,
                "returned": returned_count,
                "reward_points": reward_points,
            }

        # Admin / overall counts
        lost_count = db.query(schema.LostItem).count()
        found_count = db.query(schema.FoundItem).count()
        match_count = db.query(schema.Match).count()

        returned_count = (
            db.query(schema.LostItem)
            .filter(schema.LostItem.status == "RETURNED")
            .count()
        )

        pending_verifications = (
            db.query(schema.Verification)
            .filter(schema.Verification.status == "PENDING")
            .count()
        )

        reward_transactions = db.query(schema.Reward).count()

        total_reward_points = (
            db.query(func.coalesce(func.sum(schema.Reward.points), 0))
            .scalar()
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
# DASHBOARD METRIC CARD
# ============================================================

def show_metric(title, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

def student_dashboard():
    st.markdown(
        '<div class="app-title">🔐 AI Campus Lost & Found</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="app-subtitle">
            Welcome back, <b>{st.session_state.get("user_name", "Student")}</b>.
            Find, verify and securely recover lost belongings.
        </div>
        """,
        unsafe_allow_html=True,
    )

    counts = get_dashboard_counts(
        user_id=st.session_state.get("user_id"),
        role="student",
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        show_metric("My Lost Items", counts["lost"])

    with col2:
        show_metric("My Found Items", counts["found"])

    with col3:
        show_metric("Possible Matches", counts["matches"])

    with col4:
        show_metric("Returned Items", counts["returned"])

    with col5:
        show_metric("Reward Points", counts["reward_points"])

    st.markdown("### How the system works")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="info-card">
                <h4>📦 1. Report</h4>
                <p>
                Report your lost or found item with description,
                location, time and optional photo.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="info-card">
                <h4>🤖 2. AI Match</h4>
                <p>
                AI compares text, location, time and images
                to identify possible matching items.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="info-card">
                <h4>🔐 3. Secure Return</h4>
                <p>
                Verify ownership and complete the final
                handover using OTP and QR verification.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Quick Actions")

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        if st.button("📱 Report Lost Item", use_container_width=True):
            set_page("lost_item")
            st.rerun()

    with q2:
        if st.button("📦 Report Found Item", use_container_width=True):
            set_page("found_item")
            st.rerun()

    with q3:
        if st.button("🤖 Possible Matches", use_container_width=True):
            set_page("possible_matches")
            st.rerun()

    with q4:
        if st.button("🎁 My Rewards", use_container_width=True):
            set_page("rewards")
            st.rerun()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def admin_dashboard():
    st.markdown(
        '<div class="app-title">🛡️ Campus Lost & Found Admin</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="app-subtitle">
            Monitor verification, handover and AI matching activity.
        </div>
        """,
        unsafe_allow_html=True,
    )

    counts = get_dashboard_counts(role="admin")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        show_metric("Total Lost", counts["lost"])

    with col2:
        show_metric("Total Found", counts["found"])

    with col3:
        show_metric("AI Matches", counts["matches"])

    with col4:
        show_metric("Returned", counts["returned"])

    col5, col6, col7 = st.columns(3)

    with col5:
        show_metric(
            "Pending Verification",
            counts["pending_verifications"],
        )

    with col6:
        show_metric(
            "Reward Transactions",
            counts["reward_transactions"],
        )

    with col7:
        show_metric(
            "Reward Points",
            counts["reward_points"],
        )

    st.markdown("### System Overview")

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

    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PAGE MODULE RUNNER
# ============================================================

def run_page_module(module_name, function_candidates):
    """
    Safely execute the requested page module.

    Different page files may use different function names.
    We therefore try known names first and then inspect the module
    for a suitable callable.
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

    # Try exact known function names
    for function_name in function_candidates:
        function = getattr(module, function_name, None)

        if callable(function):
            try:
                function()
            except TypeError:
                function()
            return

    # Fallback: find a page-like function defined in the module
    candidates = []

    for name, obj in inspect.getmembers(module, inspect.isfunction):
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
            candidates.append((name, obj))

    if candidates:
        try:
            candidates[0][1]()
            return
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

        st.markdown(
            "## 🔐 AI Campus Lost & Found"
        )

        if st.session_state.get("logged_in"):

            st.markdown(
                f"""
                <div class="info-card">
                    <b>{st.session_state.get("user_name", "User")}</b><br>
                    <small>
                        Role: {st.session_state.get("role", "student").title()}
                    </small>
                </div>
                """,
                unsafe_allow_html=True,
            )

            role = st.session_state.get("role")

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

            labels = list(navigation.keys())
            values = list(navigation.values())

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

            selected_page = navigation[selected_label]

            if selected_page != current_page:
                set_page(selected_page)
                st.rerun()

            st.divider()

            if st.button(
                "🚪 Logout",
                use_container_width=True,
            ):
                st.session_state["logged_in"] = False
                st.session_state["role"] = None
                st.session_state["user_id"] = None
                st.session_state["user_name"] = None
                set_page("dashboard")
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

    # Not logged in
    if not st.session_state.get("logged_in", False):

        run_login_page()

        return

    # Logged in
    render_sidebar()

    current_page = st.session_state.get(
        "page",
        "dashboard",
    )

    # --------------------------------------------------------
    # Student / Admin dashboard
    # --------------------------------------------------------

    if current_page == "dashboard":

        if st.session_state.get("role") == "admin":
            admin_dashboard()
        else:
            student_dashboard()

    # --------------------------------------------------------
    # Student pages
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Handover
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Admin pages
    # --------------------------------------------------------

    elif current_page == "admin_verification":

        if st.session_state.get("role") != "admin":

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

    elif current_page == "admin_analytics":

        if st.session_state.get("role") != "admin":

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

    # --------------------------------------------------------
    # Unknown page
    # --------------------------------------------------------

    else:

        st.warning(
            "Unknown page selected. Returning to dashboard."
        )

        set_page("dashboard")
        st.rerun()


# ============================================================
# APP ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()