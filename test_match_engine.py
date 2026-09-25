from ai.match_engine import find_text_matches


matches = find_text_matches(min_score=60.0)


if not matches:
    print("No possible matches found.")

else:
    print("\nPossible Matches:\n")

    for match in matches:
        print(
            f"Lost ID: LF-{match['lost_id']:05d} | "
            f"Found ID: FI-{match['found_id']:05d} | "
            f"Text Score: {match['score']}%"
        )