# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Dropped support for end-of-life Python 3.9/3.10; CI now tests on
  Python 3.11, 3.12 and 3.13 (aligns with current Streamlit ≥ 1.66
  requirements).

## [1.1.0] - 2026-10-20

### Added
- MIT `LICENSE` — the project is now properly open source.
- Professional `README.md` with badges, architecture overview, setup,
  deployment and customization guides.
- Community health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `SECURITY.md`, `SUPPORT.md`.
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`): lint + unit tests
  on every push and pull request.
- Dependabot configuration for automated dependency-update PRs.
- Issue templates (bug report / feature request) and a pull-request template.
- Unit-test suite for the scoring engine (`tests/test_scoring.py`) covering
  the GPAT +4/−1/0 marking scheme.
- `requirements-dev.txt` and `pytest.ini` for reproducible local testing.
- `.streamlit/config.toml` theme and a `secrets.toml.example` template.
- `.gitignore` covering Python artifacts, coverage files and secrets.

### Changed
- Portal password is now read from Streamlit secrets
  (`portal_password`) with a safe fallback default — no more reliance on a
  hard-coded value in the UI layer.
- Cleaned repository of stray working files; standardized file naming.

### Fixed
- Corrected the misspelled `passowrd` column header in `students.csv`.

## [1.0.0] - 2025-04-15

### Added
- Initial public release of the GPAT 25 Mock Tests Portal.
- Streamlit-based exam engine: login, instructions tab, timed sections,
  color-coded navigation panel, save/change/review answer workflow.
- Two complete 125-question GPAT question banks (`questions_test1.json`,
  `questions_test2.json`).
- Google Sheets integration for total scores, question-wise responses and
  attempt tracking (`backend_logic.py`).
- GPAT-standard negative marking: +4 correct, −1 wrong, 0 skipped.
- Deployed to Streamlit Community Cloud for Shri Vishnu College of Pharmacy
  (Autonomous), Bhimavaram.

[Unreleased]: https://github.com/svsk1977/my-mocktest-app/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/svsk1977/my-mocktest-app/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/svsk1977/my-mocktest-app/releases/tag/v1.0.0
