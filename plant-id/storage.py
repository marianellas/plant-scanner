"""Read/write plant identification results to plants_log.json."""

import json
import os
from datetime import datetime, timezone

LOG_FILE = os.path.join(os.path.dirname(__file__), "plants_log.json")


def load_log() -> list[dict]:
    """Return the full log as a list of dicts (empty list if file missing)."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def append_entry(
    image_path: str,
    identification: dict,
    care: dict,
    help_result: dict | None = None,
    toxic_result: dict | None = None,
) -> dict:
    """Append a new entry to the log and return it."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "image_path": image_path,
        "species": identification["species"],
        "common_name": identification.get("common_name", "unknown"),
        "confidence": identification["confidence"],
        "care_tips": care["care_tips"],
    }
    if help_result:
        entry["plant_help"] = {
            "diagnosis": help_result["diagnosis"],
            "advice": help_result["advice"],
        }
    if toxic_result:
        entry["toxicity"] = toxic_result
    log = load_log()
    log.append(entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    return entry
