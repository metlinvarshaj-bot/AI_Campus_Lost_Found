from ai.text_matcher import calculate_text_similarity


lost_description = (
    "Black HP laptop charger with "
    "a small scratch near the connector."
)

found_description = (
    "Black HP charger with a scratch "
    "near the connector."
)


score = calculate_text_similarity(
    lost_description,
    found_description
)


print(f"Text Similarity Score: {score}%")