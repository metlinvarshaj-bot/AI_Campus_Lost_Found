import streamlit as st

from database.db import SessionLocal
from database.schema import Match, LostItem, FoundItem


def show_possible_matches():

    st.title("🔍 Possible Matches")

    user_id = st.session_state.get(
        "user_id",
        1
    )

    db = SessionLocal()

    try:

        matches = (
            db.query(
                Match,
                LostItem,
                FoundItem
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
                LostItem.user_id == user_id
            )
            .filter(
                Match.status.in_(
                    ["PENDING", "VERIFIED"]
                )
            )
            .order_by(
                Match.final_score.desc()
            )
            .all()
        )

        if not matches:

            st.info(
                "No possible matches found "
                "for your lost items yet."
            )

            return

        st.write(
            f"Found {len(matches)} possible match(es)."
        )

        for match, lost, found in matches:

            with st.container(border=True):

                st.subheader(
                    f"🎯 Match: "
                    f"LF-{lost.id:05d} "
                    f"↔ "
                    f"FI-{found.id:05d}"
                )

                # -----------------------------------------
                # SCORE CARDS
                # -----------------------------------------
                col1, col2, col3, col4 = st.columns(4)

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

                with col4:
                    st.metric(
                        "Image Score",
                        f"{match.image_score}%"
                    )

                st.write(
                    f"**Time Score:** "
                    f"{match.time_score}%"
                )

                st.divider()

                # -----------------------------------------
                # LOST ITEM
                # -----------------------------------------
                st.markdown(
                    "### 📢 Lost Item"
                )

                st.write(
                    f"**Item:** {lost.item_name}"
                )

                st.write(
                    f"**Category:** {lost.category}"
                )

                if lost.brand:
                    st.write(
                        f"**Brand:** {lost.brand}"
                    )

                if lost.color:
                    st.write(
                        f"**Color:** {lost.color}"
                    )

                st.write(
                    f"**Location:** {lost.location}"
                )

                if lost.description:
                    st.write(
                        f"**Description:** "
                        f"{lost.description}"
                    )

                # -----------------------------------------
                # FOUND ITEM
                # -----------------------------------------
                st.markdown(
                    "### 📦 Found Item"
                )

                st.write(
                    f"**Item:** {found.item_name}"
                )

                st.write(
                    f"**Category:** {found.category}"
                )

                if found.brand:
                    st.write(
                        f"**Brand:** {found.brand}"
                    )

                if found.color:
                    st.write(
                        f"**Color:** {found.color}"
                    )

                st.write(
                    f"**Location:** {found.location}"
                )

                if found.description:
                    st.write(
                        f"**Description:** "
                        f"{found.description}"
                    )

                # -----------------------------------------
                # IMAGE PREVIEW
                # -----------------------------------------
                if (
                    lost.image_path
                    and found.image_path
                ):

                    col1, col2 = st.columns(2)

                    with col1:

                        st.caption(
                            "Lost Item Photo"
                        )

                        try:
                            st.image(
                                lost.image_path,
                                width=250
                            )
                        except Exception:
                            st.caption(
                                "Lost image unavailable"
                            )

                    with col2:

                        st.caption(
                            "Found Item Photo"
                        )

                        try:
                            st.image(
                                found.image_path,
                                width=250
                            )
                        except Exception:
                            st.caption(
                                "Found image unavailable"
                            )

                # -----------------------------------------
                # MATCH LEVEL
                # -----------------------------------------
                if match.final_score >= 85:

                    st.success(
                        "🟢 Strong possible match"
                    )

                elif match.final_score >= 60:

                    st.warning(
                        "🟡 Possible match - "
                        "verification required"
                    )

                else:

                    st.info(
                        "🔵 Low-confidence match"
                    )

                st.caption(
                    "AI scores indicate candidate similarity "
                    "only. Ownership must be verified before "
                    "handover."
                )

    except Exception as e:

        st.error(
            f"Unable to load possible matches: {e}"
        )

    finally:

        db.close()