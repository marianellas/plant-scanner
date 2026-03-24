"""Step 2: Text API calls — general care tips, targeted plant help, and toxicity.

get_care_tips  → {"care_tips": [str, ...]}
get_plant_help → {"diagnosis": str, "advice": [str, ...]}
get_toxicity   → {"toxic": bool, "details": str, "targets": [str, ...]}
"""

import json

import anthropic

MODEL = "claude-opus-4-6"

_PROMPT_TEMPLATE = (
    "You are a professional horticulturist. "
    "Provide practical care tips for {species}.\n"
    "Respond with ONLY valid JSON in exactly this format "
    "(no markdown, no extra text):\n"
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


_HELP_PROMPT_TEMPLATE = (
    "You are a professional horticulturist. "
    "A user has a {species} and is experiencing the following issue: {issue}\n"
    "Diagnose the likely cause and give specific, actionable advice to fix it.\n"
    "Respond with ONLY valid JSON in exactly this format "
    "(no markdown, no extra text):\n"
    '{{"diagnosis": "<one sentence cause>", '
    '"advice": ["<step 1>", "<step 2>", "<step 3>"]}}'
)


def get_plant_help(species: str, issue: str) -> dict:
    """Call the Claude text API for targeted help with a specific plant problem.

    Args:
        species: Scientific or common name of the plant.
        issue: User's description of the problem (e.g. "leaves are turning yellow").

    Returns:
        dict with keys "diagnosis" (str) and "advice" (list of str).

    Raises:
        ValueError: if the response is not valid JSON or is missing required keys.
    """
    client = anthropic.Anthropic()
    prompt = _HELP_PROMPT_TEMPLATE.format(species=species, issue=issue)

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

    if "diagnosis" not in result or "advice" not in result:
        raise ValueError(f"Response missing required keys: {result}")

    return result


_TOXIC_PROMPT_TEMPLATE = (
    "You are a veterinarian and pediatric safety expert. "
    "Is {species} toxic to {targets}?\n"
    "Respond with ONLY valid JSON in exactly this format "
    "(no markdown, no extra text):\n"
    '{{"toxic": <true|false>, "details": "<one sentence summary>", '
    '"targets": [<list of who it is toxic to from: {targets}>]}}'
)

TOXIC_CHOICES = ["cats", "dogs", "kids", "all"]


def get_toxicity(species: str, target: str) -> dict:
    """Call the Claude text API to check if a plant is toxic to cats, dogs, or kids.

    Args:
        species: Scientific or common name of the plant.
        target: One of "cats", "dogs", "kids", or "all".

    Returns:
        dict with keys "toxic" (bool), "details" (str), and "targets" (list of str).

    Raises:
        ValueError: if the response is not valid JSON or is missing required keys.
    """
    targets = "cats, dogs, and children" if target == "all" else target
    client = anthropic.Anthropic()
    prompt = _TOXIC_PROMPT_TEMPLATE.format(species=species, targets=targets)

    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    text = next(
        (block.text for block in response.content if block.type == "text"), ""
    )

    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"API returned non-JSON response: {text!r}") from exc

    if "toxic" not in result or "details" not in result:
        raise ValueError(f"Response missing required keys: {result}")

    return result
