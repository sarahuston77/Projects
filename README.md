# Sara Huston — Project Portfolio

Selected projects in health-tech, optimization, and simulation. Each section mirrors a resume bullet: impact first, stack second, details last.

---

## 🏥 Mom's Cancer Health App
**Stack:** Python, Kivy, SQLite, SMTP

Desktop health companion built for a family member undergoing treatment for bladder cancer. Daily use correlated with a **sustained 10 bpm reduction in blood pressure**.

- **Engineered** a Kivy GUI with SQLite-backed sleep/mood logging, JSON-configured reminder scheduling, and SMTP-to-SMS low-mood alerts routed through carrier email gateways (Verizon, AT&T, T-Mobile, Sprint).
- **Designed** a 7-day Unicode-sparkline trend view (`▁▂▃▄▅▆▇█`) over the logged values so a caregiver can read a week of vitals at a glance.
- **Hardened** the alert path: secrets loaded from environment, send failures surfaced to the user instead of silently swallowed, so false reassurance can't reach the patient.

<details>
<summary><strong>Run it locally</strong></summary>

```bash
cd mom-cancer-health-app
pip install -r requirements.txt
cp .env.example .env       # set HEALTH_APP_EMAIL + HEALTH_APP_PASSWORD (Gmail App Password)
set -a; source .env; set +a
python3 HealthApp.py
```

`HEALTH_APP_PASSWORD` must be a Gmail [App Password](https://myaccount.google.com/apppasswords) (2-Step Verification required). If either var is missing, the app shows `"message to Sara FAILED. Call her directly."` on the next low-mood log instead of failing silently.
</details>

---

## 🏃 Fitness Tracker (Android)
**Stack:** Java, Android SDK, Firebase Auth, Firebase Realtime Database, Google Maps

Native Android fitness app with email/password login, GPS-traced exercise sessions, a personal exercise log, and a profile screen — backed end-to-end by Firebase.

- **Implemented** Firebase Authentication and a Realtime Database schema for per-user exercise history, with offline-tolerant reads/writes.
- **Integrated** Google Maps + `ACCESS_FINE_LOCATION` to plot live run routes, gated behind a runtime-permissions flow.
- **Structured** the UI as a single-activity, multi-fragment architecture (Home / Map / Log / Profile) over a shared `BaseActivity`.

---

## 📊 Supply Chain & Production Planning Optimizer
**Stack:** MMXPRS, FICO Xpress, Mosel

A **1,000+ line mixed-integer optimization model** for a mock tomato producer, balancing purchasing, production, storage, and sales across 4 SKUs under capacity and inventory constraints.

- **Lifted modeled profit by 22%** over the baseline plan by jointly optimizing buy/make/store/sell decisions instead of treating them as independent steps.
- **Modeled** capacity ceilings, storage limits, and demand windows as linear constraints; produced a multi-period decision schedule the operator can execute directly.

---

## License

Portfolio / educational use.
