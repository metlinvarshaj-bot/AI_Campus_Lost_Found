from functools import lru_cache

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


MODEL_NAME = "openai/clip-vit-base-patch32"


@lru_cache(maxsize=1)
def load_clip_model():
    """
    Load CLIP processor and model only once.
    """

    processor = CLIPProcessor.from_pretrained(
        MODEL_NAME
    )

    model = CLIPModel.from_pretrained(
        MODEL_NAME
    )

    model.eval()

    return processor, model


def get_image_embedding(image_path: str):
    """
    Convert an image into a normalized CLIP embedding.
    """

    processor, model = load_clip_model()

    image = Image.open(image_path).convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():

        # Get visual features from CLIP vision encoder
        vision_outputs = model.vision_model(
            **inputs
        )

        # Extract pooled image representation
        image_embeds = vision_outputs.pooler_output

        # Apply CLIP visual projection
        image_embeds = model.visual_projection(
            image_embeds
        )

        # Normalize the embedding
        image_embeds = image_embeds / image_embeds.norm(
            dim=-1,
            keepdim=True
        )

    return image_embeds


def calculate_image_similarity(
    lost_image_path: str,
    found_image_path: str
) -> float:
    """
    Compare two images using CLIP.

    Returns:
        Similarity score from 0 to 100.
    """

    if not lost_image_path or not found_image_path:
        return 0.0

    try:

        lost_embedding = get_image_embedding(
            lost_image_path
        )

        found_embedding = get_image_embedding(
            found_image_path
        )

        # Cosine similarity because embeddings are normalized
        similarity = torch.sum(
            lost_embedding * found_embedding
        ).item()

        # Convert [-1, 1] to [0, 100]
        score = (
            (similarity + 1.0)
            / 2.0
        ) * 100.0

        score = max(
            0.0,
            min(100.0, score)
        )

        return round(score, 2)

    except Exception as e:

        print(
            f"Image matching error: {e}"
        )

        return 0.0