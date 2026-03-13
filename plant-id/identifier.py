"""Step 1: Vision API call — identify a plant species from a photo.

Returns JSON: {"species": str, "common_name": str, "confidence": float}
"""

import json

import anthropic

MODEL = "claude-opus-4-6"

_PROMPT = (
    "You are a professional botanist. Examine the plant in this image and identify it, "
    "also commonly known as its popular name (e.g. Epipremnum aureum -> Golden Pothos).\n"
    "Respond with ONLY valid JSON in exactly this format (no markdown, no extra text):\n"
    '{"species": "<scientific name>", "common_name": "<common name>", "confidence": <float 0.0-1.0>}'
)


def identify_plant(image_b64: str, media_type: str) -> dict:
    """Call Claude vision API with a base64-encoded image.

    Args:
        image_b64: Base64-encoded image data (no data-URI prefix).
        media_type: MIME type, e.g. "image/jpeg" or "image/png".

    Returns:
        dict with keys "species" (str), "common_name" (str), and "confidence" (float).

    Raises:
        ValueError: if the response is not valid JSON or is missing required keys.
    """
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": _PROMPT},
                ],
            }
        ],
    )

    text = next(
        (block.text for block in response.content if block.type == "text"), ""
    )

    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"API returned non-JSON response: {text!r}") from exc

    if "species" not in result:
        raise ValueError(f"Response missing 'species' key: {result}")

    if "confidence" not in result:
        result["confidence"] = 0.0

    return result
