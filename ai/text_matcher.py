from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def calculate_text_similarity(
    lost_text: str,
    found_text: str
) -> float:

    lost_text = (lost_text or "").strip()
    found_text = (found_text or "").strip()

    if not lost_text or not found_text:
        return 0.0

    model = get_model()

    embeddings = model.encode(
        [lost_text, found_text],
        normalize_embeddings=True
    )

    score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    score = max(0.0, min(1.0, float(score)))

    return round(score * 100, 2)