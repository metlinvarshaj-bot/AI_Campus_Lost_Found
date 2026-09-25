from datetime import datetime

import streamlit as st

from database.db import SessionLocal
from database.schema import Match, LostItem, FoundItem, Verification


def show_verification():

    st.title("🔐 Ownership Verification")

    user_id = st.session_state.get("user_id", 1)

    db = SessionLocal()

    try:
        pending_matches = (
            db.query(Match, LostItem, FoundItem)
            .join(
                LostItem,
                Match.lost_item_id == LostItem.id
            )
            .join(
                FoundItem,
                Match.found_item_id == FoundItem.id
            )
            .filter(
                LostItem.user_id == user_id
            )
            .filter(
                Match.status == "PENDING"
            )
            .order_by(
                Match.final_score.desc()
            )
            .all()
        )

        if not pending_matches:
            st.info(
                "No possible matches are waiting for verification."
            )
            return

        st.write(
            "Review the possible match and submit a private "
            "ownership detail for admin verification."
        )

        for match, lost, found in pending_matches:

            with st.container(border=True):

                st.subheader(
                    f"🎯 LF-{lost.id:05d} ↔ FI-{found.id:05d}"
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Final Score",
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
                    "**Enter a private identifying detail that "
                    "can help the admin verify ownership.**"
                )

                st.caption(
                    "Example: a unique scratch, sticker, mark, "
                    "or other detail you can identify."
                )

                verification_note = st.text_area(
                    "Ownership Detail",
                    key=f"verify_{match.id}",
                    placeholder=(
                        "Example: Small scratch near the USB connector"
                    )
                )

                if st.button(
                    "📤 Submit for Verification",
                    key=f"submit_{match.id}",
                    use_container_width=True
                ):

                    if not verification_note.strip():
                        st.warning(
                            "Please enter an ownership detail."
                        )
                        continue

                    existing = (
                        db.query(Verification)
                        .filter(
                            Verification.match_id == match.id
                        )
                        .first()
                    )

                    if existing:
                        existing.notes = verification_note.strip()
                        existing.status = "PENDING"
                        existing.verified_at = None

                    else:
                        verification = Verification(
                            match_id=match.id,
                            status="PENDING",
                            notes=verification_note.strip(),
                            verified_at=None,
                            created_at=datetime.utcnow()
                        )

                        db.add(verification)

                    db.commit()

                    st.success(
                        "✅ Verification request submitted "
                        "successfully."
                    )

    except Exception as e:

        db.rollback()

        st.error(
            f"Unable to submit verification: {e}"
        )

    finally:
        db.close()