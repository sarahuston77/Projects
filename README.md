# Sara Huston — Project Portfolio

Selected projects spanning health-tech, operations research, and mobile development. Each project ships end-to-end: design, implementation, and measurable impact.

---

## 🏥 Mom's Cancer Health App
**Stack:** Python · Kivy · SQLite · SMTP (email-to-SMS gateway)

Designed and shipped a cross-platform desktop app to support a family member through bladder cancer treatment. Delivers research-backed care prompts on a configurable schedule, persists daily sleep and mood logs to SQLite, and auto-escalates low-mood entries to a caregiver via SMS over a carrier email gateway. A weekly summary view surfaces 7-day sleep/mood averages and a logging-streak counter — data the patient brings to oncology follow-ups. Contributed to a sustained **10 bpm drop in resting blood pressure**.

**Highlights:** event-driven Kivy UI with dynamic layout · parameterized JSON reminder schedule with graceful fallback · idempotent per-day reminder state machine · environment-based secret management (no committed credentials).

### Setup — SMS alerts on low mood
When a mood rating below 6 is logged, the app sends an SMS to a designated contact via an email-to-SMS gateway. Two environment variables are required:

| Variable | Purpose |
| --- | --- |
| `HEALTH_APP_EMAIL` | Gmail address used as the SMTP sender. |
| `HEALTH_APP_PASSWORD` | Gmail [App Password](https://myaccount.google.com/apppasswords) (not the account password). |

Copy `mom-cancer-health-app/.env.example` to `.env` and fill in real values, or export them in your shell:

```bash
export HEALTH_APP_EMAIL="your.address@gmail.com"
export HEALTH_APP_PASSWORD="your-16-char-app-password"
python3 mom-cancer-health-app/HealthApp.py
```

If the variables are unset, mood logging still works — only the SMS alert is skipped, and the UI surfaces the failure.

---

## 📊 Supply-Chain & Production Planning Optimizer
**Stack:** FICO Xpress · Mosel · MMXPRS · Mixed-Integer Programming

Authored a **1,000+ line mixed-integer optimization model** for a multi-product manufacturer, jointly optimizing purchasing, production, inventory, and sales across four SKUs under capacity, storage, and demand constraints. Solver-driven decisions improved modeled **profit by 22%** versus the baseline plan.

**Highlights:** multi-period planning horizon · binary setup decisions · sensitivity analysis on input cost shocks.

---

## 📱 Sports Simulation Running App
**Stack:** Android (Java) · Gradle · Firebase

Native Android application that simulates and tracks running workouts, backed by Firebase for auth and real-time data sync across devices. Built with a modular Gradle project structure and standard Android architecture components.

---

## License

Portfolio / educational use.

