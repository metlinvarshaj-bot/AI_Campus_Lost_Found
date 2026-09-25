from datetime import datetime

from database.db import SessionLocal
from database.schema import LostItem, FoundItem

from ai.text_matcher import calculate_text_similarity
from ai.image_matcher import calculate_image_similarity


def calculate_location_score(
    lost_location: str,
    found_location: str
) -> float:

    lost_location = (lost_location or "").strip().lower()
    found_location = (found_location or "").strip().lower()

    if not lost_location or not found_location:
        return 0.0

    if lost_location == found_location:
        return 100.0

    lost_words = set(lost_location.split())
    found_words = set(found_location.split())

    common_words = lost_words.intersection(found_words)

    if common_words:
        return 70.0

    return 0.0


def calculate_time_score(
    lost_time: datetime,
    found_time: datetime
) -> float:

    if not lost_time or not found_time:
        return 0.0

    difference_minutes = abs(
        (lost_time - found_time).total_seconds()
    ) / 60

    if difference_minutes <= 30:
        return 100.0

    if difference_minutes <= 60:
        return 80.0

    if difference_minutes <= 180:
        return 50.0

    if difference_minutes <= 360:
        return 25.0

    return 0.0


def calculate_final_score(
    text_score: float,
    location_score: float,
    time_score: float,
    image_score: float | None = None
) -> float:

    # Both images are available
    if image_score is not None:

        final_score = (
            (text_score * 0.50)
            + (location_score * 0.20)
            + (time_score * 0.15)
            + (image_score * 0.15)
        )

    # Image not available
    else:

        final_score = (
            (text_score * 0.60)
            + (location_score * 0.25)
            + (time_score * 0.15)
        )

    return round(final_score, 2)


def find_smart_matches(min_score: float = 60.0):

    db = SessionLocal()

    try:

        lost_items = db.query(LostItem).all()
        found_items = db.query(FoundItem).all()

        matches = []

        for lost in lost_items:

            for found in found_items:

                # -----------------------------------------
                # TEXT DATA
                # -----------------------------------------
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

                text_score = calculate_text_similarity(
                    lost_text,
                    found_text
                )

                # -----------------------------------------
                # LOCATION
                # -----------------------------------------
                location_score = calculate_location_score(
                    lost.location,
                    found.location
                )

                # -----------------------------------------
                # TIME
                # -----------------------------------------
                time_score = calculate_time_score(
                    lost.lost_at,
                    found.found_at
                )

                # -----------------------------------------
                # IMAGE
                # -----------------------------------------
                image_score = None

                if (
                    lost.image_path
                    and found.image_path
                    and lost.image_path.strip()
                    and found.image_path.strip()
                ):

                    image_score = calculate_image_similarity(
                        lost.image_path,
                        found.image_path
                    )

                # -----------------------------------------
                # FINAL SCORE
                # -----------------------------------------
                final_score = calculate_final_score(
                    text_score=text_score,
                    location_score=location_score,
                    time_score=time_score,
                    image_score=image_score
                )

                # -----------------------------------------
                # SAVE CANDIDATE
                # -----------------------------------------
                if final_score >= min_score:

                    matches.append({
                        "lost_id": lost.id,
                        "found_id": found.id,
                        "text_score": text_score,
                        "location_score": location_score,
                        "time_score": time_score,
                        "image_score": (
                            image_score
                            if image_score is not None
                            else 0.0
                        ),
                        "final_score": final_score
                    })

        matches.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return matches

    finally:

        db.close()