from ai.save_matches import save_smart_matches


matches = save_smart_matches(min_score=60.0)


print("\nSaved Match Results:\n")

if not matches:
    print("No possible matches found.")

else:
    for match in matches:
        print(
            f"Lost ID: LF-{match['lost_id']:05d} | "
            f"Found ID: FI-{match['found_id']:05d} | "
            f"Final Score: {match['final_score']}%"
        )