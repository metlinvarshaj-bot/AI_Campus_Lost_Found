from ai.smart_matcher import find_smart_matches


matches = find_smart_matches(
    min_score=60.0
)


if not matches:

    print(
        "No smart matches found."
    )

else:

    print(
        "\nSmart Possible Matches:\n"
    )

    for match in matches:

        print(
            f"Lost ID: LF-{match['lost_id']:05d} | "
            f"Found ID: FI-{match['found_id']:05d}"
        )

        print(
            f"Text Score: "
            f"{match['text_score']}%"
        )

        print(
            f"Location Score: "
            f"{match['location_score']}%"
        )

        print(
            f"Time Score: "
            f"{match['time_score']}%"
        )

        print(
            f"Image Score: "
            f"{match['image_score']}%"
        )

        print(
            f"Final Match Score: "
            f"{match['final_score']}%"
        )

        print(
            "-" * 50
        )