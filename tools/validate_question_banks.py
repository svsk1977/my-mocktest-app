#!/usr/bin/env python3
"""Validate the JSON question banks shipped with the GPAT Mock Test Portal.

Checks per question bank file:
  * valid JSON, top-level list
  * required keys present (question_id, question, option1..4, answer)
  * answer matches one of the four options
  * question_id uniqueness
  * minimum bank size (125 questions per full mock test)

Exit code is non-zero if any check fails, so this script is wired into CI
(``python tools/validate_question_banks.py``).
"""

import json
import sys
from pathlib import Path

REQUIRED_KEYS = ("question_id", "question", "option1", "option2", "option3", "option4", "answer")
MIN_QUESTIONS = 125
BANK_GLOB = "questions_test*.json"


def validate_bank(path: Path) -> list:
    errors = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            questions = json.load(fh)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON ({exc})"]

    if not isinstance(questions, list):
        return [f"{path}: top-level value must be a JSON array"]

    if len(questions) < MIN_QUESTIONS:
        errors.append(
            f"{path}: only {len(questions)} questions, expected at least {MIN_QUESTIONS}"
        )

    seen_ids = set()
    for idx, q in enumerate(questions):
        label = f"{path}[{idx}] question_id={q.get('question_id', '?')}"

        for key in REQUIRED_KEYS:
            if key not in q or not str(q[key]).strip():
                errors.append(f"{label}: missing or empty key '{key}'")

        if "question_id" in q:
            if q["question_id"] in seen_ids:
                errors.append(f"{label}: duplicate question_id")
            seen_ids.add(q["question_id"])

        if all(k in q for k in ("answer", "option1", "option2", "option3", "option4")):
            options = {str(q[f"option{i}"]).strip() for i in range(1, 5)}
            if str(q["answer"]).strip() not in options:
                errors.append(f"{label}: answer does not match any option")

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    banks = sorted(repo_root.glob(BANK_GLOB))
    if not banks:
        print(f"FAIL: no question bank files matching {BANK_GLOB}")
        return 1

    all_errors = []
    for bank in banks:
        all_errors.extend(validate_bank(bank))
        if not [e for e in all_errors if e.startswith(str(bank))]:
            count = len(json.loads(bank.read_text(encoding="utf-8")))
            print(f"OK: {bank.name} ({count} questions)")

    if all_errors:
        print("\nFAILURES:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("\nAll question banks are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
