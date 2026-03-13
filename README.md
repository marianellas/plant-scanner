# plant-scanner 🌿

I love plants! This CLI tool identifies plants from photos using the Anthropic Claude vision API. Point it at any photo and it returns the scientific name, common name, confidence score, and care tips — all saved to a local log.

---

## How it works

1. **Identify** — sends your photo to Claude (vision call) and gets back the species, common name, and confidence
2. **Care tips** — sends the species name to Claude (text call) and gets back practical care tips
3. **Log** — appends both results to `plants_log.json` for future reference

---

## Setup

**1. Install the dependency**

```bash
pip install anthropic
```

**2. Set your API key**

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Usage

```bash
python plant_id.py <path-to-image> [--plant-help "describe your issue"]
```

### Identify a single photo

```bash
python plant_id.py plant_pics/plant_pic.jpg
```

### Identify a photo using a full path

```bash
python plant_id.py /Users/yourname/Desktop/mystery_plant.png
```

### Sample output

```
Identifying plant…
  Species    : Epipremnum aureum
  Common name: Golden Pothos
  Confidence : 96%

Fetching care tips…
  Care tips:
    1. Water when the top inch of soil feels dry
    2. Thrives in bright indirect light but tolerates low light
    3. Feed with a balanced liquid fertilizer monthly in spring and summer
    4. Keep away from cold drafts and temperatures below 50°F (10°C)
    5. Wipe leaves occasionally to remove dust and improve light absorption

Saved to /path/to/plant-id/plants_log.json
```

---

### Get help with a specific plant problem

Use `--plant-help` to describe what's wrong. Claude will diagnose the likely cause and give targeted, actionable advice.

```bash
python plant_id.py plant_pics/plant_pic.jpg --plant-help "leaves are turning yellow and drooping"
```

```bash
python plant_id.py plant_pics/plant_pic.jpg --plant-help "brown crispy edges on leaves"
```

```bash
python plant_id.py plant_pics/plant_pic.jpg --plant-help "not growing and soil stays wet for weeks"
```

### Sample output with `--plant-help`

```
Identifying plant…
  Species    : Epipremnum aureum
  Common name: Golden Pothos
  Confidence : 96%

Fetching care tips…
  Care tips:
    1. Water when the top inch of soil feels dry
    ...

Diagnosing issue: 'leaves are turning yellow and drooping'…
  Diagnosis: Overwatering is causing root rot and oxygen deprivation in the roots.
  Advice:
    1. Let the soil dry out completely before watering again
    2. Remove the plant from its pot and inspect roots — trim any black or mushy ones
    3. Repot in fresh, well-draining soil and ensure the pot has drainage holes

Saved to /path/to/plant-id/plants_log.json
{
  "timestamp": "2026-03-13T18:42:01.123456+00:00",
  "image_path": "plant_pics/plant_pic.jpg",
  "species": "Epipremnum aureum",
  "common_name": "Golden Pothos",
  "confidence": 0.96,
  "care_tips": [...],
  "plant_help": {
    "diagnosis": "Overwatering is causing root rot and oxygen deprivation in the roots.",
    "advice": [
      "Let the soil dry out completely before watering again",
      "Remove the plant from its pot and inspect roots — trim any black or mushy ones",
      "Repot in fresh, well-draining soil and ensure the pot has drainage holes"
    ]
  }
}
```

---

## Project structure

```
plant-scanner/
├── README.md
└── plant-id/
    ├── plant_id.py       # CLI entrypoint — run this
    ├── identifier.py     # Step 1: vision API call → species + common name + confidence
    ├── care.py           # Step 2: text API call → care tips
    ├── storage.py        # Reads and writes plants_log.json
    ├── plants_log.json   # Auto-created on first run
    ├── plant_pics/       # Put your plant photos here
    └── tests/
        ├── test_identifier.py
        └── test_care.py
```

---

## Running the tests

```bash
cd plant-id
python -m pytest tests/ -v
```

---

## Supported image formats

JPEG, PNG, GIF, WebP
