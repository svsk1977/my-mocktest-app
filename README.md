# GPAT Mock Test Portal 🎓

[![CI](https://github.com/svsk1977/my-mocktest-app/actions/workflows/ci.yml/badge.svg)](https://github.com/svsk1977/my-mocktest-app/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B)](https://streamlit.io/)
[![Made with Love](https://img.shields.io/badge/made%20with-%E2%9D%A4-for%20students-ff69b4)](https://github.com/svsk1977/my-mocktest-app)

> A free, open-source online examination portal that recreates the real GPAT
> (Graduate Pharmacy Aptitude Test) experience — timed sections, a live
> question navigator, review flags and instant scoring — so pharmacy students
> can practice under genuine exam conditions.

---

## Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Screens Walkthrough](#screens-walkthrough)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Deployment (Streamlit Cloud)](#deployment-streamlit-cloud)
- [Customizing Your Tests](#customizing-your-tests)
- [Scoring Model](#scoring-model)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## About the Project

The **GPAT Mock Test Portal** was built for students of Shri Vishnu College of
Pharmacy (Autonomous), Bhimavaram, to prepare for GPAT and similar
pharmacy-entrance examinations. Most free mock-test sites either show
untimed question lists or hide their question banks behind ads and sign-up
walls. This project flips that: it is fully open source, ships with **250+
real GPAT-style questions** (two full 125-question mock tests), and faithfully
reproduces the mechanics of a computer-based test — section timers, question
status colors, mandatory answer saving, and negative marking.

Every result is recorded automatically to a Google Sheet (total score plus a
question-by-question breakdown), so faculty can review performance analytics
without any server administration. The whole system deploys for free on
Streamlit Community Cloud.

## Features

| Feature | Description |
|---|---|
| 🔐 **Secure login** | Students authenticate with their registered email; the roster and the shared test password are configurable. |
| ⏱️ **Timed examination** | Each of the 5 sections carries its own countdown (3 minutes in the sample config); the test auto-advances when time expires — exactly like the real GPAT CBT. |
| 🗺️ **Navigation panel** | A live sidebar grid shows the status of every question and lets students jump to any question instantly. |
| 🚦 **Color-coded status** | 🟢 Answered · 🔴 Not Answered · 🟡 Saved for Review · ⚪ Not Visited. |
| 💾 **Mandatory save workflow** | Answers count only after clicking **Save Answer** — training students to avoid the classic "selected but never saved" mistake. |
| 📦 **Randomized question sets** | Each attempt draws 125 questions from the bank and shuffles answer options, so no two attempts are identical. |
| ➖ **Negative marking** | GPAT scoring: **+4** for correct, **−1** for wrong, **0** for skipped. |
| 📊 **Automatic result recording** | Total scores and per-question responses (with timestamps) are appended to Google Sheets for faculty review. |
| ♻️ **Re-test support** | Admins can clear a student's attempt to allow a fresh try. |

## Screens Walkthrough

1. **Login** — the college-branded welcome screen with email + password sign-in.
2. **Instructions & Tests tabs** — mandatory exam rules on one tab, live test
   cards with start countdowns on the other.
3. **Test interface** — question area (center) with the section timer and the
   color-coded navigation panel (sidebar).
4. **Completion** — results are finalized, saved to Google Sheets, and a
   confirmation message is displayed.

## Tech Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/) (pure Python, no HTML/JS needed)
- **Backend logic**: Python 3.9+ with `pandas`
- **Data storage**:
  - Question banks — JSON files (`questions_test1.json`, `questions_test2.json`)
  - Student roster — CSV (`students.csv`)
  - Results & attempt tracking — Google Sheets via [`gspread`](https://github.com/burnash/gspread) + a service account
- **Timer refresh**: `streamlit-autorefresh` for the 1-second countdown tick
- **CI**: GitHub Actions (lint + unit tests on every push/PR)
- **Hosting**: Streamlit Community Cloud (free tier)

## Project Structure

```text
my-mocktest-app/
├── app.py                     # Streamlit UI: login, test engine, navigation
├── backend_logic.py           # Scoring engine + Google Sheets integration
├── questions_test1.json       # Mock Test 1 question bank (125 questions)
├── questions_test2.json       # Mock Test 2 question bank (125 questions)
├── students.csv               # Student roster (dummy data in this repo)
├── instructions.txt           # Exam instructions shown in the portal
├── college_logo.png           # College branding
├── requirements.txt           # Runtime dependencies
├── requirements-dev.txt       # Development/test dependencies
├── .streamlit/
│   ├── config.toml            # UI theme
│   └── secrets.toml.example   # Template for secrets (never commit real ones)
├── tests/
│   └── test_scoring.py        # Unit tests for the scoring engine
└── .github/
    ├── workflows/ci.yml       # Lint + test pipeline
    ├── dependabot.yml         # Automated dependency updates
    ├── ISSUE_TEMPLATE/        # Bug report & feature request forms
    └── PULL_REQUEST_TEMPLATE.md
```

## Getting Started

### Prerequisites

- Python 3.9 or newer
- A Google account (only needed if you want the Google Sheets result logging)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/svsk1977/my-mocktest-app.git
cd my-mocktest-app

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the portal
streamlit run app.py
```

The portal opens at `http://localhost:8501`. Log in with any email from
`students.csv` (dummy data included by default, e.g. `student1@email.com`)
and the portal password.

### Configuration

Secrets are managed through Streamlit's secrets system. Copy the template
and fill in your values:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

```toml
# .streamlit/secrets.toml
portal_password = "YourStrongPassword"

[google_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "mocktest@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

Create a Google Sheet named `mock_test_scores` with three worksheets —
`Total Scores`, `Question Scores`, and `Attempted Users` — and share it with
the service account's `client_email` (Editor access).

> **Note:** if no secrets file is present, the app still runs for local
> practice — the portal falls back to the default password and simply skips
> the Google Sheets logging.

## Deployment (Streamlit Cloud)

1. Fork this repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect the fork.
3. Set the main file path to `app.py`.
4. In **Advanced settings → Secrets**, paste the contents of your
   `secrets.toml`.
5. Deploy — every push to `main` automatically redeploys the app.

## Customizing Your Tests

- **Add a test**: drop a new `questions_testN.json` file (list of objects with
  `question`, `option1`–`option4`, `answer`, `question_id`) and register it in
  the `test_files` / `test_dates` dictionaries in `app.py`.
- **Change section timing**: adjust `section_time = 3 * 60` in `app.py`.
- **Register students**: append rows to `students.csv`
  (`student_id,name,email`).
- **Edit exam rules**: edit `instructions.txt`.

## Scoring Model

The scoring engine (unit-tested in `tests/test_scoring.py`) implements the
official GPAT marking scheme:

| Outcome | Marks |
|---|---|
| Correct answer | **+4** |
| Wrong answer | **−1** |
| Unattempted | **0** |

## Roadmap

- [ ] Admin dashboard with per-question analytics
- [ ] Topic-wise performance breakdown
- [ ] Question bank editor UI
- [ ] Per-student unique passwords (hashed)
- [ ] Support for more exams (NIPER, PG CET)
- [ ] Multi-language UI

## Contributing

Contributions are what make the open-source community such an amazing place
to learn, inspire, and create. Any contributions you make are **greatly
appreciated** — see the [Contributing Guide](CONTRIBUTING.md) for details on
branch naming, commit conventions, and the PR workflow.

## Security

Found a vulnerability? Please follow the responsible-disclosure process in
[SECURITY.md](SECURITY.md) — do **not** open a public issue.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more
information.

## Acknowledgements

- [Streamlit](https://streamlit.io/) — the fastest way to build data apps
- [gspread](https://github.com/burnash/gspread) — Google Sheets for humans
- Shri Vishnu College of Pharmacy (Autonomous), Bhimavaram — for the
  inspiration and the question banks
- Every student who stress-tested a mock test under the countdown clock ⏳

---

<p align="center">Made with ❤️ for pharmacy students ·
<a href="https://github.com/svsk1977">svsk1977</a></p>
