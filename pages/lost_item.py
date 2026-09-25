import os
from datetime import datetime

import streamlit as st

from database.db import SessionLocal
from database.schema import LostItem
from ai.save_matches import save_smart_matches


def show_lost_item_form():

    st.title("📢 Report Lost Item")

    st.write(
        "Enter the details of the item you lost."
    )

    with st.form("lost_item_form"):

        item_name = st.text_input(
            "Item Name *",
            placeholder="Example: Laptop Charger"
        )

        category = st.selectbox(
            "Category *",
            [
                "ID Card",
                "Mobile",
                "Laptop",
                "Charger",
                "Wallet",
                "Books",
                "Bag",
                "Keys",
                "Bottle",
                "Other"
            ]
        )

        brand = st.text_input(
            "Brand",
            placeholder="Example: HP"
        )

        color = st.text_input(
            "Color",
            placeholder="Example: Black"
        )

        description = st.text_area(
            "Description *",
            placeholder=(
                "Describe the item, scratches, stickers, "
                "unique marks..."
            )
        )

        location = st.text_input(
            "Lost Location *",
            placeholder="Example: Library - First Floor"
        )

        lost_date = st.date_input(
            "Lost Date"
        )

        lost_time = st.time_input(
            "Lost Time"
        )

        photo = st.file_uploader(
            "Upload Item Photo",
            type=["jpg", "jpeg", "png"]
        )

        submitted = st.form_submit_button(
            "📤 Submit Lost Item",
            use_container_width=True
        )

    if submitted:

        if not item_name.strip():
            st.error("Please enter the item name.")
            return

        if not description.strip():
            st.error("Please enter a description.")
            return

        if not location.strip():
            st.error("Please enter the lost location.")
            return

        user_id = st.session_state.get(
            "user_id"
        )

        if not user_id:
            st.error(
                "User session not found. Please login again."
            )
            return

        image_path = None

        # ---------------------------------------------
        # Save uploaded image
        # ---------------------------------------------
        if photo is not None:

            upload_folder = os.path.join(
                "uploads",
                "lost"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            safe_name = (
                f"{user_id}_{timestamp}_{photo.name}"
            )

            image_path = os.path.join(
                upload_folder,
                safe_name
            )

            with open(
                image_path,
                "wb"
            ) as file:

                file.write(
                    photo.getbuffer()
                )

        lost_datetime = datetime.combine(
            lost_date,
            lost_time
        )

        db = SessionLocal()

        try:

            new_item = LostItem(
                user_id=user_id,
                item_name=item_name.strip(),
                category=category,
                brand=brand.strip(),
                color=color.strip(),
                description=description.strip(),
                location=location.strip(),
                lost_at=lost_datetime,
                image_path=image_path,
                status="LOST"
            )

            db.add(new_item)

            db.commit()

            db.refresh(new_item)

            # -----------------------------------------
            # AUTOMATIC AI MATCHING
            # -----------------------------------------
            save_smart_matches(
                min_score=60.0
            )

            st.success(
                f"✅ Lost item reported successfully! "
                f"Case ID: LF-{new_item.id:05d}"
            )

            st.info(
                "🤖 AI matching completed automatically."
            )

        except Exception as e:

            db.rollback()

            st.error(
                f"Unable to save the lost item: {e}"
            )

        finally:

            db.close()