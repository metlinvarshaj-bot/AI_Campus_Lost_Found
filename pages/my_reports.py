import streamlit as st

from database.db import SessionLocal
from database.schema import LostItem, FoundItem


def show_my_reports():

    st.title("📋 My Reports")

    user_id = st.session_state.get("user_id", 1)

    db = SessionLocal()

    try:

        lost_items = (
            db.query(LostItem)
            .filter(LostItem.user_id == user_id)
            .order_by(LostItem.created_at.desc())
            .all()
        )

        found_items = (
            db.query(FoundItem)
            .filter(FoundItem.user_id == user_id)
            .order_by(FoundItem.created_at.desc())
            .all()
        )

        tab1, tab2 = st.tabs(
            ["📢 My Lost Items", "📦 My Found Items"]
        )

        # --------------------------------
        # LOST ITEMS
        # --------------------------------
        with tab1:

            if not lost_items:
                st.info("You have not reported any lost items yet.")

            else:

                st.subheader(
                    f"Lost Items: {len(lost_items)}"
                )

                for item in lost_items:

                    with st.container(border=True):

                        col1, col2 = st.columns(
                            [3, 1]
                        )

                        with col1:

                            st.markdown(
                                f"### 📢 {item.item_name}"
                            )

                            st.write(
                                f"**Category:** {item.category}"
                            )

                            if item.brand:
                                st.write(
                                    f"**Brand:** {item.brand}"
                                )

                            if item.color:
                                st.write(
                                    f"**Color:** {item.color}"
                                )

                            st.write(
                                f"**Location:** {item.location}"
                            )

                            st.write(
                                f"**Lost At:** "
                                f"{item.lost_at.strftime('%d-%m-%Y %I:%M %p')}"
                            )

                            if item.description:
                                st.write(
                                    f"**Description:** "
                                    f"{item.description}"
                                )

                        with col2:

                            st.metric(
                                "Case ID",
                                f"LF-{item.id:05d}"
                            )

                            if item.status == "LOST":
                                st.warning("Status: LOST")
                            elif item.status == "MATCHED":
                                st.info("Status: MATCHED")
                            elif item.status == "RETURNED":
                                st.success("Status: RETURNED")
                            else:
                                st.write(
                                    f"Status: {item.status}"
                                )

                            if item.image_path:
                                try:
                                    st.image(
                                        item.image_path,
                                        width=150
                                    )
                                except Exception:
                                    st.caption(
                                        "Image unavailable"
                                    )

        # --------------------------------
        # FOUND ITEMS
        # --------------------------------
        with tab2:

            if not found_items:
                st.info("You have not reported any found items yet.")

            else:

                st.subheader(
                    f"Found Items: {len(found_items)}"
                )

                for item in found_items:

                    with st.container(border=True):

                        col1, col2 = st.columns(
                            [3, 1]
                        )

                        with col1:

                            st.markdown(
                                f"### 📦 {item.item_name}"
                            )

                            st.write(
                                f"**Category:** {item.category}"
                            )

                            if item.brand:
                                st.write(
                                    f"**Brand:** {item.brand}"
                                )

                            if item.color:
                                st.write(
                                    f"**Color:** {item.color}"
                                )

                            st.write(
                                f"**Location:** {item.location}"
                            )

                            st.write(
                                f"**Found At:** "
                                f"{item.found_at.strftime('%d-%m-%Y %I:%M %p')}"
                            )

                            if item.description:
                                st.write(
                                    f"**Description:** "
                                    f"{item.description}"
                                )

                        with col2:

                            st.metric(
                                "Case ID",
                                f"FI-{item.id:05d}"
                            )

                            if item.status == "FOUND":
                                st.warning("Status: FOUND")
                            elif item.status == "MATCHED":
                                st.info("Status: MATCHED")
                            elif item.status == "RETURNED":
                                st.success("Status: RETURNED")
                            else:
                                st.write(
                                    f"Status: {item.status}"
                                )

                            if item.image_path:
                                try:
                                    st.image(
                                        item.image_path,
                                        width=150
                                    )
                                except Exception:
                                    st.caption(
                                        "Image unavailable"
                                    )

    except Exception as e:

        st.error(
            f"Unable to load your reports: {e}"
        )

    finally:

        db.close()