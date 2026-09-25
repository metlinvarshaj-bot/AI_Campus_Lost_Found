import streamlit as st

from database.db import SessionLocal
from database.schema import (
    LostItem,
    FoundItem,
    Match,
    Verification,
    Reward,
)


def show_admin_analytics():

    st.title("📊 Admin Analytics")

    db = SessionLocal()

    try:

        # ==================================================
        # MAIN COUNTS
        # ==================================================

        total_lost = (
            db.query(LostItem).count()
        )

        total_found = (
            db.query(FoundItem).count()
        )

        total_matches = (
            db.query(Match).count()
        )

        returned_items = (
            db.query(LostItem)
            .filter(
                LostItem.status == "RETURNED"
            )
            .count()
        )

        pending_verification = (
            db.query(Verification)
            .filter(
                Verification.status == "PENDING"
            )
            .count()
        )

        total_rewards = (
            db.query(Reward).count()
        )

        total_reward_points = (
            sum(
                reward.points
                for reward in db.query(Reward).all()
            )
        )

        # ==================================================
        # TOP METRICS
        # ==================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📢 Total Lost",
                total_lost
            )

        with col2:
            st.metric(
                "📦 Total Found",
                total_found
            )

        with col3:
            st.metric(
                "🔍 Total Matches",
                total_matches
            )

        with col4:
            st.metric(
                "✅ Returned",
                returned_items
            )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "🛡️ Pending Verification",
                pending_verification
            )

        with col2:
            st.metric(
                "🏆 Reward Transactions",
                total_rewards
            )

        with col3:
            st.metric(
                "🎁 Total Reward Points",
                total_reward_points
            )

        st.divider()

        # ==================================================
        # LOST ITEM STATUS
        # ==================================================

        st.subheader("📢 Lost Item Status")

        lost_status_data = {}

        for status in [
            "LOST",
            "MATCHED",
            "RETURNED"
        ]:

            count = (
                db.query(LostItem)
                .filter(
                    LostItem.status == status
                )
                .count()
            )

            lost_status_data[status] = count

        st.bar_chart(
            lost_status_data
        )

        # ==================================================
        # FOUND ITEM STATUS
        # ==================================================

        st.subheader("📦 Found Item Status")

        found_status_data = {}

        for status in [
            "FOUND",
            "MATCHED",
            "RETURNED"
        ]:

            count = (
                db.query(FoundItem)
                .filter(
                    FoundItem.status == status
                )
                .count()
            )

            found_status_data[status] = count

        st.bar_chart(
            found_status_data
        )

        # ==================================================
        # MATCH STATUS
        # ==================================================

        st.subheader("🔍 Match Status")

        match_status_data = {}

        for status in [
            "PENDING",
            "VERIFIED",
            "RETURNED",
            "REJECTED"
        ]:

            count = (
                db.query(Match)
                .filter(
                    Match.status == status
                )
                .count()
            )

            match_status_data[status] = count

        st.bar_chart(
            match_status_data
        )

        # ==================================================
        # RECENT MATCHES
        # ==================================================

        st.subheader("🎯 Recent AI Matches")

        recent_matches = (
            db.query(Match)
            .order_by(
                Match.final_score.desc()
            )
            .limit(10)
            .all()
        )

        if not recent_matches:

            st.info(
                "No AI matches available yet."
            )

        else:

            for match in recent_matches:

                with st.container(
                    border=True
                ):

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.write(
                            f"**Match ID:** {match.id}"
                        )

                    with col2:
                        st.write(
                            f"**Final:** "
                            f"{match.final_score}%"
                        )

                    with col3:
                        st.write(
                            f"**Image:** "
                            f"{match.image_score}%"
                        )

                    with col4:
                        st.write(
                            f"**Status:** "
                            f"{match.status}"
                        )

    except Exception as e:

        st.error(
            f"Unable to load analytics: {e}"
        )

    finally:

        db.close()