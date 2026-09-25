from database.db import SessionLocal
from database.schema import LostItem, FoundItem

from ai.text_matcher import calculate_text_similarity


def find_text_matches(min_score=60.0):
    """
    Compare every lost item with every found item
    using AI text similarity.

    Returns:
        List of possible matches.
    """

    db = SessionLocal()

    try:
        lost_items = db.query(LostItem).all()
        found_items = db.query(FoundItem).all()

        matches = []

        for lost in lost_items:
            for found in found_items:

                lost_text = (
                    f"{lost.item_name}. "
                    f"{lost.category}. "
                    f"{lost.brand or ''}. "
                    f"{lost.color or ''}. "
                    f"{lost.description or ''}"
                )

                found_text = (
                    f"{found.item_name}. "
                    f"{found.category}. "
                    f"{found.brand or ''}. "
                    f"{found.color or ''}. "
                    f"{found.description or ''}"
                )

                score = calculate_text_similarity(
                    lost_text,
                    found_text
                )

                if score >= min_score:
                    matches.append({
                        "lost_id": lost.id,
                        "found_id": found.id,
                        "score": score
                    })

        matches.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return matches

    finally:
        db.close()