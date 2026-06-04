# Mom's Cancer Health App

A Python/Kivy desktop app built to support a family member through bladder cancer treatment. Delivers scheduled, research-backed care prompts; logs daily sleep and mood ratings to SQLite; surfaces a weekly summary with 7-day averages and a logging-streak counter; and escalates low-mood entries to a designated caregiver via an email-to-SMS gateway.

## Features
- Configurable daily reminders loaded from `data/reminders.json` (graceful fallback if missing/invalid).
- Idempotent per-day reminder state — each reminder fires at most once per calendar day.
- Sleep & mood logging (1–10), persisted in SQLite with input validation.
- Weekly summary view: 7-day averages + logging-streak counter with milestone celebrations (7 / 30 / 100 days).
- Low-mood SMS alert sent over Gmail SMTP through a carrier email gateway (Verizon / AT&T / T-Mobile / Sprint).
- Secrets and contact info are loaded from environment variables — nothing personal is committed.

## Tech stack
Python 3.11 · Kivy · SQLite (`sqlite3`) · `smtplib` / `email.mime.text` · PyInstaller spec for packaging.

## Layout
```
mom-cancer-health-app/
├── HealthApp.py        # Kivy UI + app entry point
├── storage.py          # SQLite persistence: logs, streaks, weekly summary
├── reminders.py        # JSON-driven reminder schedule with safe fallback
├── data/               # reminders.json + generated health_app.db
├── assets/             # images & audio
├── tests/              # pytest suite for storage layer
├── HealthApp.spec      # PyInstaller build spec
└── .env.example        # template for required environment variables
```

## Setup

```bash
pip install kivy pytest
cp .env.example .env   # then fill in real values
```

Required environment variables (see `.env.example`):

| Variable | Purpose |
| --- | --- |
| `HEALTH_APP_EMAIL` | Gmail address used as the SMTP sender. |
| `HEALTH_APP_PASSWORD` | Gmail [App Password](https://myaccount.google.com/apppasswords). |
| `HEALTH_APP_CAREGIVER_PHONE` | 10-digit phone number to notify on low-mood entries. |

If any of these are unset, the app still runs normally — only the SMS alert is skipped, and the failure is surfaced in the UI.

## Run

```bash
python3 HealthApp.py
```

## Tests

```bash
pytest -q tests/
```

CI runs the same suite on every push and PR (`.github/workflows/ci.yml`).
