from database.db import SessionLocal
from database.schema import (
    Match,
    LostItem,
    Handover,
    Verification,
)


db = SessionLocal()

try:

    matches = db.query(Match).all()

    updated = 0

    for match in matches:

        lost_item = (
            db.query(LostItem)
            .filter(
                LostItem.id == match.lost_item_id
            )
            .first()
        )

        handover = (
            db.query(Handover)
            .filter(
                Handover.match_id == match.id
            )
            .first()
        )

        verification = (
            db.query(Verification)
            .filter(
                Verification.match_id == match.id
            )
            .first()
        )

        old_status = match.status

        # ---------------------------------------------
        # Highest priority: completed handover
        # ---------------------------------------------
        if (
            handover
            and handover.status == "RETURNED"
        ):

            match.status = "RETURNED"

        # ---------------------------------------------
        # Approved ownership verification
        # ---------------------------------------------
        elif (
            verification
            and verification.status == "APPROVED"
        ):

            match.status = "VERIFIED"

        # ---------------------------------------------
        # Rejected verification
        # ---------------------------------------------
        elif (
            verification
            and verification.status == "REJECTED"
        ):

            match.status = "REJECTED"

        # ---------------------------------------------
        # Lost item already returned
        # ---------------------------------------------
        elif (
            lost_item
            and lost_item.status == "RETURNED"
        ):

            match.status = "RETURNED"

        # ---------------------------------------------
        # Otherwise pending
        # ---------------------------------------------
        else:

            match.status = "PENDING"

        if old_status != match.status:

            updated += 1

            print(
                f"Match {match.id}: "
                f"{old_status} → {match.status}"
            )

    db.commit()

    print(
        f"\n✅ Match status synchronization completed."
    )

    print(
        f"Updated records: {updated}"
    )

except Exception as e:

    db.rollback()

    print(
        f"❌ Status repair failed: {e}"
    )

finally:

    db.close()