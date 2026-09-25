import streamlit as st

from database.db import SessionLocal
from database.schema import (
    FoundItem,
    LostItem,
    Match,
    Reward,
)

from pages.login import show_login
from pages.lost_item import show_lost_item_form
from pages.found_item import show_found_item_form
from pages.my_reports import show_my_reports
from pages.possible_matches import show_possible_matches
from pages.verification import show_verification
from pages.admin_verification import show_admin_verification
from pages.handover import show_handover
from pages.rewards import show_rewards
from pages.admin_analytics import show_admin_analytics


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="AI Campus Lost & Found",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# PROFESSIONAL UI STYLING
# ==========================================================
st.markdown(
    """
    <style>

    /* Main page */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Titles */
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .subtitle {
        font-size: 18px;
        color: #666666;
        margin-bottom: 25px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid #e5e7eb;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background: white;
    }

    /* Cards */
    .custom-card {
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background: white;
        margin-bottom: 15px;
    }

    /* Status boxes */
    .status-success {
        padding: 12px 16px;
        border-radius: 10px;
        background-color: #e8f7ee;
        border: 1px solid #b7e4c7;
        margin-bottom: 10px;
    }

    .status-warning {
        padding: 12px 16px;
        border-radius: 10px;
        background-color: #fff8e1;
        border: 1px solid #ffe082;
        margin-bottom: 10px;
    }

    .status-danger {
        padding: 12px 16px;
        border-radius: 10px;
        background-color: #fdecea;
        border: 1px solid #f5c2c0;
        margin-bottom: 10px;
    }

    /* Form styling */
    div[data-testid="stForm"] {
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        padding: 20px;
    }

    /* Hide unnecessary decoration */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# SESSION STATE
# ==========================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "role" not in st.session_state:
    st.session_state["role"] = None

if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"


# ==========================================================
# LOGIN CHECK
# ==========================================================
if not st.session_state["logged_in"]:
    show_login()
    st.stop()


# ==========================================================
# DATABASE COUNTS
# ==========================================================
db = SessionLocal()

try:

    current_user_id = st.session_state["user_id"]
    current_role = st.session_state["role"]

    if current_role == "student":

        # ----------------------------------------------
        # Student lost count
        # ----------------------------------------------
        my_lost_count = (
            db.query(LostItem)
            .filter(
                LostItem.user_id == current_user_id
            )
            .count()
        )

        # ----------------------------------------------
        # Student found count
        # ----------------------------------------------
        my_found_count = (
            db.query(FoundItem)
            .filter(
                FoundItem.user_id == current_user_id
            )
            .count()
        )

        # ----------------------------------------------
        # Possible matches
        # ----------------------------------------------
        possible_match_count = (
            db.query(Match)
            .join(
                LostItem,
                Match.lost_item_id == LostItem.id
            )
            .filter(
                LostItem.user_id == current_user_id
            )
            .filter(
                Match.status.in_(
                    ["PENDING", "VERIFIED"]
                )
            )
            .count()
        )

        # ----------------------------------------------
        # Reward points
        # ----------------------------------------------
        reward_rows = (
            db.query(Reward.points)
            .filter(
                Reward.user_id == current_user_id
            )
            .all()
        )

        total_reward_points = sum(
            row[0] for row in reward_rows
        )

    else:

        # ----------------------------------------------
        # Admin statistics
        # ----------------------------------------------
        total_lost_count = (
            db.query(LostItem).count()
        )

        total_found_count = (
            db.query(FoundItem).count()
        )

        total_match_count = (
            db.query(Match).count()
        )

        returned_count = (
            db.query(LostItem)
            .filter(
                LostItem.status == "RETURNED"
            )
            .count()
        )

finally:
    db.close()


# ==========================================================
# SIDEBAR HEADER
# ==========================================================
st.sidebar.title("🎓 Campus Lost & Found")

st.sidebar.write(
    f"Welcome, {st.session_state['user_name']}"
)

st.sidebar.write(
    f"Role: {st.session_state['role'].title()}"
)

st.sidebar.divider()


# ==========================================================
# STUDENT NAVIGATION
# ==========================================================
if st.session_state["role"] == "student":

    if st.sidebar.button(
        "🏠 Dashboard",
        use_container_width=True
    ):
        st.session_state["page"] = "dashboard"
        st.rerun()

    if st.sidebar.button(
        "📢 Report Lost Item",
        use_container_width=True
    ):
        st.session_state["page"] = "lost_item"
        st.rerun()

    if st.sidebar.button(
        "📦 Report Found Item",
        use_container_width=True
    ):
        st.session_state["page"] = "found_item"
        st.rerun()

    if st.sidebar.button(
        "📋 My Reports",
        use_container_width=True
    ):
        st.session_state["page"] = "my_reports"
        st.rerun()

    if st.sidebar.button(
        "🔍 Possible Matches",
        use_container_width=True
    ):
        st.session_state["page"] = "possible_matches"
        st.rerun()

    if st.sidebar.button(
        "🔐 Verification",
        use_container_width=True
    ):
        st.session_state["page"] = "verification"
        st.rerun()

    if st.sidebar.button(
        "🔑 Secure Handover",
        use_container_width=True
    ):
        st.session_state["page"] = "handover"
        st.rerun()

    if st.sidebar.button(
        "🏆 My Rewards",
        use_container_width=True
    ):
        st.session_state["page"] = "rewards"
        st.rerun()


# ==========================================================
# ADMIN NAVIGATION
# ==========================================================
elif st.session_state["role"] == "admin":

    if st.sidebar.button(
        "🏠 Admin Dashboard",
        use_container_width=True
    ):
        st.session_state["page"] = "dashboard"
        st.rerun()

    if st.sidebar.button(
        "🛡️ Verification Review",
        use_container_width=True
    ):
        st.session_state["page"] = "admin_verification"
        st.rerun()

    if st.sidebar.button(
        "🔑 Secure Handover",
        use_container_width=True
    ):
        st.session_state["page"] = "handover"
        st.rerun()

    if st.sidebar.button(
        "📊 Analytics",
        use_container_width=True
    ):
        st.session_state["page"] = "admin_analytics"
        st.rerun()


# ==========================================================
# LOGOUT
# ==========================================================
if st.sidebar.button(
    "Logout",
    use_container_width=True
):

    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["user_name"] = None
    st.session_state["user_id"] = None
    st.session_state["page"] = "dashboard"

    st.rerun()


# ==========================================================
# STUDENT SECTION
# ==========================================================
if st.session_state["role"] == "student":

    # ------------------------------------------------------
    # STUDENT DASHBOARD
    # ------------------------------------------------------
    if st.session_state["page"] == "dashboard":

        st.markdown(
            '<div class="main-title">🎓 Student Dashboard</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">'
            'Smart campus lost & found management system'
            '</div>',
            unsafe_allow_html=True
        )

        st.success(
            f"Welcome {st.session_state['user_name']}!"
        )

        # ----------------------------------------------
        # Dashboard metrics
        # ----------------------------------------------
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📢 My Lost Items",
                my_lost_count
            )

        with col2:
            st.metric(
                "📦 My Found Items",
                my_found_count
            )

        with col3:
            st.metric(
                "🔍 Possible Matches",
                possible_match_count
            )

        with col4:
            st.metric(
                "🏆 Reward Points",
                total_reward_points
            )

        st.divider()

        st.subheader("⚡ Quick Actions")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "📢 Report Lost Item",
                use_container_width=True
            ):
                st.session_state["page"] = "lost_item"
                st.rerun()

        with col2:

            if st.button(
                "📦 Report Found Item",
                use_container_width=True
            ):
                st.session_state["page"] = "found_item"
                st.rerun()


    # ------------------------------------------------------
    # LOST ITEM
    # ------------------------------------------------------
    elif st.session_state["page"] == "lost_item":

        show_lost_item_form()


    # ------------------------------------------------------
    # FOUND ITEM
    # ------------------------------------------------------
    elif st.session_state["page"] == "found_item":

        show_found_item_form()


    # ------------------------------------------------------
    # MY REPORTS
    # ------------------------------------------------------
    elif st.session_state["page"] == "my_reports":

        show_my_reports()


    # ------------------------------------------------------
    # POSSIBLE MATCHES
    # ------------------------------------------------------
    elif st.session_state["page"] == "possible_matches":

        show_possible_matches()


    # ------------------------------------------------------
    # VERIFICATION
    # ------------------------------------------------------
    elif st.session_state["page"] == "verification":

        show_verification()


    # ------------------------------------------------------
    # HANDOVER
    # ------------------------------------------------------
    elif st.session_state["page"] == "handover":

        show_handover()


    # ------------------------------------------------------
    # REWARDS
    # ------------------------------------------------------
    elif st.session_state["page"] == "rewards":

        show_rewards()


# ==========================================================
# ADMIN SECTION
# ==========================================================
elif st.session_state["role"] == "admin":

    # ------------------------------------------------------
    # ADMIN DASHBOARD
    # ------------------------------------------------------
    if st.session_state["page"] == "dashboard":

        st.markdown(
            '<div class="main-title">🛠️ Admin Dashboard</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">'
            'Campus-wide lost & found monitoring'
            '</div>',
            unsafe_allow_html=True
        )

        st.success(
            f"Welcome {st.session_state['user_name']}!"
        )

        # ----------------------------------------------
        # Admin metrics
        # ----------------------------------------------
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📢 Total Lost",
                total_lost_count
            )

        with col2:
            st.metric(
                "📦 Total Found",
                total_found_count
            )

        with col3:
            st.metric(
                "🔍 Total Matches",
                total_match_count
            )

        with col4:
            st.metric(
                "✅ Returned",
                returned_count
            )

        st.divider()

        st.subheader("🛠️ Admin Functions")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🛡️ Open Verification Review",
                use_container_width=True
            ):
                st.session_state["page"] = "admin_verification"
                st.rerun()

        with col2:

            if st.button(
                "📊 Open Analytics",
                use_container_width=True
            ):
                st.session_state["page"] = "admin_analytics"
                st.rerun()


    # ------------------------------------------------------
    # ADMIN VERIFICATION
    # ------------------------------------------------------
    elif st.session_state["page"] == "admin_verification":

        show_admin_verification()


    # ------------------------------------------------------
    # ADMIN HANDOVER
    # ------------------------------------------------------
    elif st.session_state["page"] == "handover":

        show_handover()


    # ------------------------------------------------------
    # ADMIN ANALYTICS
    # ------------------------------------------------------
    elif st.session_state["page"] == "admin_analytics":

        show_admin_analytics()