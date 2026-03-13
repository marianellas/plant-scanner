#!/usr/bin/env python3
"""plant_id — identify a plant from a photo and get care tips.

Usage:
    python plant_id.py <image_path>
    python plant_id.py path/to/photo.jpg
"""

import argparse
import base64
import imghdr
import json
import sys

import care
import identifier
import storage

_MEDIA_TYPES = {
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
}


def _detect_media_type(path: str) -> str:
    kind = imghdr.what(path)
    if kind not in _MEDIA_TYPES:
        return "image/jpeg"
    return _MEDIA_TYPES[kind]


def run(image_path: str) -> None:
    try:
        with open(image_path, "rb") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    image_b64 = base64.standard_b64encode(raw).decode("utf-8")
    media_type = _detect_media_type(image_path)

    print("Identifying plant…")
    try:
        id_result = identifier.identify_plant(image_b64, media_type)
    except ValueError as exc:
        print(f"Identification failed: {exc}", file=sys.stderr)
        sys.exit(1)

    species = id_result["species"]
    common_name = id_result.get("common_name", "unknown")
    confidence = id_result["confidence"]
    print(f"  Species    : {species}")
    print(f"  Common name: {common_name}")
    print(f"  Confidence : {confidence:.0%}")

    print("\nFetching care tips…")
    try:
        care_result = care.get_care_tips(species)
    except ValueError as exc:
        print(f"Care tips failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print("  Care tips:")
    for i, tip in enumerate(care_result["care_tips"], 1):
        print(f"    {i}. {tip}")

    entry = storage.append_entry(image_path, id_result, care_result)
    print(f"\nSaved to {storage.LOG_FILE}")
    print(json.dumps(entry, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Identify a plant from a photo and get care tips."
    )
    parser.add_argument("image", help="Path to the plant photo (JPEG/PNG/GIF/WebP)")
    args = parser.parse_args()
    run(args.image)


if __name__ == "__main__":
    main()
