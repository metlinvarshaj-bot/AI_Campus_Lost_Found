from database.db import SessionLocal
from database.schema import LostItem, FoundItem

from ai.image_matcher import calculate_image_similarity


db = SessionLocal()

try:
    lost_item = (
        db.query(LostItem)
        .filter(LostItem.image_path.isnot(None))
        .first()
    )

    found_item = (
        db.query(FoundItem)
        .filter(FoundItem.image_path.isnot(None))
        .first()
    )

    if not lost_item:
        print("No lost item image found in the database.")

    elif not found_item:
        print("No found item image found in the database.")

    else:
        print("Lost Image:")
        print(lost_item.image_path)

        print("\nFound Image:")
        print(found_item.image_path)

        score = calculate_image_similarity(
            lost_item.image_path,
            found_item.image_path
        )

        print(
            f"\nImage Similarity Score: {score}%"
        )

finally:
    db.close()