import streamlit as st

from database.db import SessionLocal
from database.schema import Reward


def show_rewards():

    st.title("🏆 My Rewards")

    user_id = st.session_state.get("user_id", 1)

    db = SessionLocal()

    try:

        rewards = (
            db.query(Reward)
            .filter(Reward.user_id == user_id)
            .order_by(Reward.created_at.desc())
            .all()
        )

        total_points = sum(
            reward.points for reward in rewards
        )

        st.metric(
            "🏆 Total Reward Points",
            total_points
        )

        if not rewards:
            st.info(
                "You have not earned any reward points yet."
            )
            return

        st.subheader(
            f"Reward History ({len(rewards)})"
        )

        for reward in rewards:

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(
                        f"**{reward.reason}**"
                    )

                    if reward.match_id:
                        st.caption(
                            f"Match ID: {reward.match_id}"
                        )

                    st.caption(
                        f"Date: "
                        f"{reward.created_at.strftime('%d-%m-%Y %I:%M %p')}"
                    )

                with col2:
                    st.metric(
                        "Points",
                        f"+{reward.points}"
                    )

    except Exception as e:

        st.error(
            f"Unable to load rewards: {e}"
        )

    finally:
        db.close()