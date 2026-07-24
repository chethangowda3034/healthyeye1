# HealthyEye — Setup Guide

A minimal full-stack prototype: upload a photo of a medicine strip/syrup label,
and get a plain-language card explaining what it's for, when to take it, what
to avoid, and (where relevant) a common home remedy alternative.

## Project structure

```
healthyeye/
├── backend/
│   ├── main.py          → FastAPI app, routes, Claude vision call
│   ├── database.py       → SQLAlchemy models + SQLite setup
│   ├── seed_data.py       → Curated medicine database (~20 starter entries)
│   └── requirements.txt
└── frontend/
    └── index.html         → Single-page upload interface (no build step needed)
```

## 1. Backend setup

You'll need a free Anthropic API key: https://console.anthropic.com/
(New accounts get a small amount of free credit — enough for a lot of testing.)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="your-key-here"   # Windows: set ANTHROPIC_API_KEY=your-key-here

uvicorn main:app --reload
```

This starts the API at `http://localhost:8000`. On first run it auto-creates
`healthyeye.db` (SQLite file) and seeds it with the starter medicine list.

Check it worked: open `http://localhost:8000/medicines` in your browser —
you should see a JSON list of ~20 medicines.

## 2. Frontend setup

No build step — it's a single static HTML file.

```bash
cd frontend
python3 -m http.server 5500
```

Then open `http://localhost:5500` in your browser.

(Or just double-click `index.html` — but running it through a local server
avoids some browsers blocking the camera/file APIs on `file://` URLs.)

## 3. Try it

1. Open the frontend in your browser (works on your phone too, if it's on
   the same wifi network as your laptop — use your laptop's local IP instead
   of `localhost`, e.g. `http://192.168.1.5:5500`, and update `API_BASE` in
   `index.html` to match).
2. Upload a photo of a medicine strip's backside (or take one now).
3. Watch it read the label and return a plain-language card.

## What to expand next (in priority order for an investor demo)

1. **Grow the medicine database** — currently ~20 entries in `seed_data.py`.
   Expanding to the ~150 most common Indian OTC medicines will make live
   demos much more reliably impressive. This is genuinely the highest-value
   thing to spend time on before showing investors.
2. **Confidence/accuracy testing** — photograph 15-20 real strips you have
   at home and see how often the label OCR + match actually succeeds.
   Fix the failure patterns you find before the demo.
3. **Mobile camera capture** — already wired up (`capture="environment"`
   attribute), test it on an actual phone.
4. **User accounts / history** — not needed for an investor demo, but a
   natural next feature once you have real users.

## Before this goes anywhere near real users

- Every entry in `seed_data.py` should be checked against an authoritative
  source (CDSCO, package insert, or a pharmacist/doctor you trust) — wrong
  medical information here is a genuine safety risk, not just a bug.
- Add clearer, harder-to-miss disclaimers that this is not a diagnosis.
- Consider what happens with prescription-only drugs vs OTC — you may want
  to flag prescription medicines differently (e.g. "this requires a doctor's
  prescription — here's general info, but don't self-medicate").
- Talk to an actual pharmacist or doctor before pitching this as
  medically authoritative, even in early conversations with investors —
  it strengthens your pitch and reduces real risk.

## Cost note

Right now everything is free: SQLite (free), FastAPI (free), the only
recurring cost is per-request Anthropic API usage during testing, which is
covered by free credits for a good while at demo-level usage. No hosting
cost until you deploy somewhere.
