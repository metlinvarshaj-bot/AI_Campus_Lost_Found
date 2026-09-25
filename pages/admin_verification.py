import streamlit as st

from database.db import SessionLocal
from database.schema import (
    Verification,
    Match,
    LostItem,
    FoundItem
)


def show_admin_verification():

    st.title("🛠️ Verification Review")

    db = SessionLocal()

    try:
        pending_records = (
            db.query(
                Verification,
                Match,
                LostItem,
                FoundItem
            )
            .join(
                Match,
                Verification.match_id == Match.id
            )
            .join(
                LostItem,
                Match.lost_item_id == LostItem.id
            )
            .join(
                FoundItem,
                Match.found_item_id == FoundItem.id
            )
            .filter(
                Verification.status == "PENDING"
            )
            .order_by(
                Match.final_score.desc()
            )
            .all()
        )

        if not pending_records:
            st.info(
                "No pending verification requests."
            )
            return

        st.write(
            f"Pending requests: {len(pending_records)}"
        )

        for verification, match, lost, found in pending_records:

            with st.container(border=True):

                st.subheader(
                    f"🎯 LF-{lost.id:05d} ↔ FI-{found.id:05d}"
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Final Match Score",
                        f"{match.final_score}%"
                    )

                with col2:
                    st.metric(
                        "Text Score",
                        f"{match.text_score}%"
                    )

                with col3:
                    st.metric(
                        "Location Score",
                        f"{match.location_score}%"
                    )

                st.write(
                    f"**Lost Item:** {lost.item_name}"
                )

                st.write(
                    f"**Found Item:** {found.item_name}"
                )

                st.write(
                    f"**Lost Location:** {lost.location}"
                )

                st.write(
                    f"**Found Location:** {found.location}"
                )

                st.write(
                    f"**Time Score:** {match.time_score}%"
                )

                st.markdown(
                    "### 🔐 Ownership Detail"
                )

                st.info(
                    verification.notes
                    if verification.notes
                    else "No ownership detail provided."
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Approve",
                        key=f"approve_{verification.id}",
                        use_container_width=True
                    ):

                        verification.status = "APPROVED"
                        match.status = "VERIFIED"
                        lost.status = "MATCHED"
                        found.status = "MATCHED"

                        db.commit()

                        st.success(
                            "Verification approved successfully."
                        )

                        st.rerun()

                with col2:

                    if st.button(
                        "❌ Reject",
                        key=f"reject_{verification.id}",
                        use_container_width=True
                    ):

                        verification.status = "REJECTED"
                        match.status = "REJECTED"

                        db.commit()

                        st.warning(
                            "Verification rejected."
                        )

                        st.rerun()

    except Exception as e:

        db.rollback()

        st.error(
            f"Unable to load verification requests: {e}"
        )

    finally:
        db.close()