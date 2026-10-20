# Contributing to GPAT Mock Test Portal

First off, thank you for considering a contribution! 🎉 This project exists to
help pharmacy students prepare for GPAT under realistic exam conditions, and
every contribution — code, questions, docs, or bug reports — makes a real
difference for them.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Branch Naming Convention](#branch-naming-convention)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)
- [Adding Question Banks](#adding-question-banks)
- [Style Guide](#style-guide)
- [Reporting Bugs](#reporting-bugs)

## Ways to Contribute

- 🐛 **Report bugs** via [GitHub Issues](https://github.com/svsk1977/my-mocktest-app/issues)
- 💡 **Suggest features** — open an issue with the `enhancement` label
- 📝 **Improve documentation** — typos, clarifications, translations
- ❓ **Contribute question banks** — well-sourced, referenced MCQs
- 🔧 **Submit code** — bug fixes and features via pull requests

## Development Setup

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/<your-username>/my-mocktest-app.git
cd my-mocktest-app

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt -r requirements-dev.txt

# Run the app locally
streamlit run app.py

# Run the test suite + lint before committing
pytest
flake8 . --max-line-length=120
```

You do **not** need Google credentials for most contributions — the app runs
locally without a secrets file (Sheets logging is skipped gracefully).

## Branch Naming Convention

Create branches off `main` using this pattern:

```text
<type>/<short-description>

# Examples
feat/question-bank-editor
fix/timer-drift-on-refresh
docs/deployment-guide
test/section-scoring-edge-cases
```

## Commit Message Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<optional scope>): <short summary in present tense>

<optional body: what & why, not how>

<optional footer: "Closes #123">
```

| Type | Use for |
|---|---|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation only |
| `test` | Adding/fixing tests |
| `refactor` | Code changes that neither fix nor add features |
| `perf` | Performance improvements |
| `chore` | Tooling, CI, dependencies |
| `security` | Security hardening |

## Pull Request Process

1. Ensure `pytest` passes and `flake8` reports no new warnings.
2. Update `README.md` and `CHANGELOG.md` if your change affects users.
3. Fill in the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).
4. Link the issue your PR addresses (`Closes #12`).
5. One approval is required before merging; maintainers usually respond
   within a few days.

## Adding Question Banks

Question files are JSON arrays of objects with this exact schema:

```json
{
  "question_id": "126",
  "question": "The first physician of Unani system was ________",
  "option1": "Asclepedeus",
  "option2": "Hippocrates",
  "option3": "Hannemann",
  "option4": "Schmidt",
  "answer": "Asclepedeus"
}
```

**Requirements for accepted question contributions:**

- The `answer` string must exactly match one of the four options.
- Questions must be original or properly licensed — do not paste copyrighted
  question banks from commercial coaching material.
- Verify factual correctness with a standard reference
  (e.g., *Trease & Evans Pharmacognosy*, *KD Triangi MPharm* subject texts).
- Never include real student data in any file you commit.

## Style Guide

- Python code: [PEP 8](https://peps.python.org/pep-0008/), 120-char lines.
- Docstrings for public functions (`"""One-line summary."""` at minimum).
- Keep functions in `app.py` focused on UI; business logic belongs in
  `backend_logic.py` (that is what makes it unit-testable).

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and
include: environment, steps to reproduce, expected vs actual behavior, and
screenshots if relevant.

---

By participating in this project you agree to abide by the
[Code of Conduct](CODE_OF_CONDUCT.md). Thank you for helping students
succeed! 🎓
