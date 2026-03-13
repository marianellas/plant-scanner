"""Step 2: Text API call — retrieve care tips for a named plant species.

Returns JSON: {"care_tips": [str, ...]}
"""

import json

import anthropic

MODEL = "claude-opus-4-6"

_PROMPT_TEMPLATE = (
    "You are a professional horticulturist. Provide practical care tips for {species}.\n"
    "Respond with ONLY valid JSON in exactly this format (no markdown, no extra text):\n"
    '{{"care_tips": ["<tip 1>", "<tip 2>", "<tip 3>", "<tip 4>", "<tip 5>"]}}'
)


def get_care_tips(species: str) -> dict:
    """Call the Claude text API to retrieve care tips for a plant species.

    Args:
        species: Scientific or common name of the plant.

    Returns:
        dict with key "care_tips" whose value is a list of strings.

    Raises:
        ValueError: if the response is not valid JSON or is missing "care_tips".
    """
    client = anthropic.Anthropic()
    prompt = _PROMPT_TEMPLATE.format(species=species)

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    text = next(
        (block.text for block in response.content if block.type == "text"), ""
    )

    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"API returned non-JSON response: {text!r}") from exc

    if "care_tips" not in result:
        raise ValueError(f"Response missing 'care_tips' key: {result}")

    return result
