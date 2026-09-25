import io
import secrets
from datetime import datetime

import qrcode
import streamlit as st

from database.db import SessionLocal
from database.schema import (
    Handover,
    Match,
    LostItem,
    FoundItem,
    Reward,
)


def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def generate_qr_token():
    return secrets.token_urlsafe(16)


def show_handover():

    st.title("🔐 Secure Handover")

    user_id = st.session_state.get("user_id", 1)
    role = st.session_state.get("role")

    db = SessionLocal()

    try:

        if role == "admin":
            verified_matches = (
                db.query(Match, LostItem, FoundItem)
                .join(
                    LostItem,
                    Match.lost_item_id == LostItem.id
                )
                .join(
                    FoundItem,
                    Match.found_item_id == FoundItem.id
                )
                .filter(Match.status == "VERIFIED")
                .order_by(Match.final_score.desc())
                .all()
            )

        else:
            verified_matches = (
                db.query(Match, LostItem, FoundItem)
                .join(
                    LostItem,
                    Match.lost_item_id == LostItem.id
                )
                .join(
                    FoundItem,
                    Match.found_item_id == FoundItem.id
                )
                .filter(LostItem.user_id == user_id)
                .filter(Match.status == "VERIFIED")
                .order_by(Match.final_score.desc())
                .all()
            )

        if not verified_matches:
            st.info(
                "No approved matches are ready for handover."
            )
            return

        st.write(
            f"Approved matches ready for handover: "
            f"{len(verified_matches)}"
        )

        for match, lost, found in verified_matches:

            with st.container(border=True):

                st.subheader(
                    f"🔐 LF-{lost.id:05d} ↔ FI-{found.id:05d}"
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
                    f"**AI Match Score:** {match.final_score}%"
                )

                handover = (
                    db.query(Handover)
                    .filter(Handover.match_id == match.id)
                    .first()
                )

                # -----------------------------
                # Generate OTP + QR
                # -----------------------------
                if not handover:

                    if st.button(
                        "🔑 Generate OTP + QR",
                        key=f"generate_{match.id}",
                        use_container_width=True
                    ):

                        handover = Handover(
                            match_id=match.id,
                            otp_code=generate_otp(),
                            qr_token=generate_qr_token(),
                            status="READY",
                            handed_over_at=None
                        )

                        db.add(handover)
                        db.commit()

                        st.success(
                            "✅ OTP and QR generated successfully."
                        )

                        st.rerun()

                    continue

                # -----------------------------
                # Already Returned
                # -----------------------------
                if handover.status == "RETURNED":

                    st.success(
                        "🎉 This item has already been returned."
                    )

                    if handover.handed_over_at:
                        st.write(
                            f"Returned At: "
                            f"{handover.handed_over_at}"
                        )

                    continue

                # -----------------------------
                # READY
                # -----------------------------
                st.success(
                    "✅ Secure handover credentials already generated."
                )

                st.write(
                    f"**Handover Status:** {handover.status}"
                )

                # OTP display
                if role == "admin":
                    st.markdown("### 🔢 Handover OTP")
                    st.code(
                        handover.otp_code,
                        language="text"
                    )

                # QR
                qr_data = (
                    f"AI-CAMPUS-LF|"
                    f"MATCH-{match.id}|"
                    f"{handover.qr_token}"
                )

                qr_image = qrcode.make(qr_data)

                buffer = io.BytesIO()
                qr_image.save(buffer, format="PNG")
                buffer.seek(0)

                st.image(
                    buffer,
                    width=220,
                    caption="Secure Handover QR"
                )

                # -----------------------------
                # OTP INPUT
                # -----------------------------
                st.markdown("### 🔐 Verify Handover")

                otp_input = st.text_input(
                    "Enter 6-digit OTP",
                    max_chars=6,
                    key=f"otp_input_{match.id}",
                    placeholder="Enter OTP here"
                )

                # -----------------------------
                # VERIFY BUTTON
                # -----------------------------
                if st.button(
                    "✅ Verify OTP & Complete Handover",
                    key=f"verify_{match.id}",
                    use_container_width=True
                ):

                    if not otp_input.strip():

                        st.warning(
                            "Please enter the OTP."
                        )

                    elif otp_input.strip() != handover.otp_code:

                        st.error(
                            "❌ Invalid OTP."
                        )

                    else:

                        handover.status = "RETURNED"
                        handover.handed_over_at = datetime.utcnow()

                        match.status = "RETURNED"
                        lost.status = "RETURNED"
                        found.status = "RETURNED"

                        existing_reward = (
                            db.query(Reward)
                            .filter(
                                Reward.match_id == match.id
                            )
                            .first()
                        )

                        if not existing_reward:

                            reward = Reward(
                                user_id=found.user_id,
                                match_id=match.id,
                                points=25,
                                reason=(
                                    "Successfully returned "
                                    "a verified lost item"
                                ),
                                created_at=datetime.utcnow()
                            )

                            db.add(reward)

                        db.commit()

                        st.success(
                            "🎉 Handover completed successfully!"
                        )

                        st.success(
                            "📦 Item status updated to RETURNED."
                        )

                        st.success(
                            "🏆 Finder rewarded with 25 points!"
                        )

                        st.rerun()

    except Exception as e:

        db.rollback()

        st.error(
            f"Unable to process handover: {e}"
        )

    finally:
        db.close()