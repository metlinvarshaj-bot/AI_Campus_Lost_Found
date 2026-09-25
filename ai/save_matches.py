from database.db import SessionLocal
from database.schema import Match

from ai.smart_matcher import find_smart_matches


def save_smart_matches(min_score=60.0):

    db = SessionLocal()

    try:

        matches = find_smart_matches(
            min_score=min_score
        )

        saved_count = 0

        for match in matches:

            existing_match = (
                db.query(Match)
                .filter(
                    Match.lost_item_id == match["lost_id"],
                    Match.found_item_id == match["found_id"]
                )
                .first()
            )

            if existing_match:

                existing_match.image_score = (
                    match["image_score"]
                )

                existing_match.text_score = (
                    match["text_score"]
                )

                existing_match.location_score = (
                    match["location_score"]
                )

                existing_match.time_score = (
                    match["time_score"]
                )

                existing_match.final_score = (
                    match["final_score"]
                )

                # Do not reset already completed workflows.
                if existing_match.status in (
                    "PENDING",
                    "REJECTED"
                ):
                    existing_match.status = "PENDING"

            else:

                new_match = Match(
                    lost_item_id=match["lost_id"],
                    found_item_id=match["found_id"],
                    image_score=match["image_score"],
                    text_score=match["text_score"],
                    location_score=match["location_score"],
                    time_score=match["time_score"],
                    final_score=match["final_score"],
                    status="PENDING"
                )

                db.add(new_match)

                saved_count += 1

        db.commit()

        print(
            f"Smart matching completed. "
            f"New matches saved: {saved_count}"
        )

        return matches

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()