"""Unit tests for the GPAT Mock Test Portal scoring engine.

These tests deliberately cover only the pure scoring functions in
``backend_logic`` so they run everywhere (CI included) without Google
credentials or a Streamlit runtime.
"""

import pandas as pd
import pytest

from backend_logic import calculate_score, calculate_total_score


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def correct_answers():
    return {
        "1": "Asclepedeus",
        "2": "Hippocrates",
        "3": "Hannemann",
        "4": "Schmidt",
    }


@pytest.fixture
def questions_df():
    return pd.DataFrame(
        [
            {"question_id": "1", "answer": "Asclepedeus"},
            {"question_id": "2", "answer": "Hippocrates"},
            {"question_id": "3", "answer": "Hannemann"},
            {"question_id": "4", "answer": "Schmidt"},
        ]
    )


def make_sections(questions_df):
    """Split the question bank into numbered sections like the app does."""
    return {1: questions_df.iloc[0:2], 2: questions_df.iloc[2:4]}


# ---------------------------------------------------------------------------
# calculate_score
# ---------------------------------------------------------------------------

class TestCalculateScore:
    def test_all_correct(self, correct_answers):
        answers = {qid: ans for qid, ans in correct_answers.items()}
        total, results = calculate_score(answers, correct_answers)
        assert total == 4 * len(correct_answers)
        assert len(results) == len(correct_answers)
        assert all(r["score"] == 4 for r in results)

    def test_all_wrong(self, correct_answers):
        answers = {qid: "definitely-wrong" for qid in correct_answers}
        total, results = calculate_score(answers, correct_answers)
        assert total == -len(correct_answers)
        assert all(r["score"] == -1 for r in results)

    def test_blank_scores_zero(self, correct_answers):
        answers = {qid: "" for qid in correct_answers}
        total, results = calculate_score(answers, correct_answers)
        assert total == 0
        assert all(r["score"] == 0 for r in results)

    def test_missing_answer_treated_as_blank(self, correct_answers):
        total, _ = calculate_score({}, correct_answers)
        assert total == 0

    def test_mixed_marks_follow_gpat_scheme(self, correct_answers):
        # 1 correct, 1 wrong, 1 blank, 1 skipped entirely
        answers = {"1": "Asclepedeus", "2": "Schmidt", "3": ""}
        total, results = calculate_score(answers, correct_answers)
        assert total == 4 - 1 + 0 + 0
        by_qid = {r["question_id"]: r for r in results}
        assert by_qid["1"]["score"] == 4
        assert by_qid["2"]["score"] == -1
        assert by_qid["3"]["score"] == 0
        assert by_qid["4"]["score"] == 0

    def test_result_records_carry_details(self, correct_answers):
        answers = {"1": "Asclepedeus", "2": "Schmidt"}
        _, results = calculate_score(answers, correct_answers)
        record = next(r for r in results if r["question_id"] == "2")
        assert record["selected_option"] == "Schmidt"
        assert record["correct_answer"] == "Hippocrates"
        assert record["score"] == -1

    def test_perfect_single_question(self, correct_answers):
        total, _ = calculate_score({"1": "Asclepedeus"}, correct_answers)
        assert total == 4


# ---------------------------------------------------------------------------
# calculate_total_score (section-aware variant used during a live test)
# ---------------------------------------------------------------------------

class TestCalculateTotalScore:
    def test_all_correct_across_sections(self, questions_df):
        sections = make_sections(questions_df)
        responses = {
            "1_1": "Asclepedeus",
            "1_2": "Hippocrates",
            "2_3": "Hannemann",
            "2_4": "Schmidt",
        }
        assert calculate_total_score(questions_df, responses, sections) == 16

    def test_negative_marking(self, questions_df):
        sections = make_sections(questions_df)
        responses = {
            "1_1": "wrong",
            "1_2": "wrong",
            "2_3": "wrong",
            "2_4": "wrong",
        }
        assert calculate_total_score(questions_df, responses, sections) == -4

    def test_skipped_questions_score_zero(self, questions_df):
        sections = make_sections(questions_df)
        assert calculate_total_score(questions_df, {}, sections) == 0

    def test_section_prefix_collision(self, questions_df):
        """Question ids live in per-section namespaces: 1_2 is section 1,
        question 2 — not section 2, question 1."""
        sections = make_sections(questions_df)
        responses = {"1_2": "Hippocrates"}  # correct only for section-1 q2
        assert calculate_total_score(questions_df, responses, sections) == 4

    def test_answer_without_save_not_counted(self, questions_df):
        """Unsaved answers are absent from responses, hence score 0."""
        sections = make_sections(questions_df)
        responses = {"1_1": "", "1_2": "Hippocrates"}
        assert calculate_total_score(questions_df, responses, sections) == 4


# ---------------------------------------------------------------------------
# Question-bank integrity (guards the JSON shipped in this repo)
# ---------------------------------------------------------------------------

class TestQuestionBanks:
    @pytest.mark.parametrize(
        "bank", ["questions_test1.json", "questions_test2.json"]
    )
    def test_bank_has_125_questions(self, bank):
        import json

        with open(bank, "r", encoding="utf-8") as f:
            questions = json.load(f)
        assert len(questions) == 125

    @pytest.mark.parametrize(
        "bank", ["questions_test1.json", "questions_test2.json"]
    )
    def test_every_answer_matches_an_option(self, bank):
        import json

        with open(bank, "r", encoding="utf-8") as f:
            questions = json.load(f)
        for q in questions:
            options = {
                q["option1"].strip(),
                q["option2"].strip(),
                q["option3"].strip(),
                q["option4"].strip(),
            }
            assert q["answer"].strip() in options, (
                f"{bank}: answer of question_id={q['question_id']} "
                f"does not match any option"
            )
