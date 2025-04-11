import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import datetime

def check_attempted(email, test_name):
    """
    Checks if a user has already attempted a test.

    Args:
        email (str): The user's email.
        test_name (str): The name of the test.

    Returns:
        bool: True if the user has attempted the test, False otherwise.
    """
    try:
        results_df = pd.read_csv(f"results_{test_name.replace(' ', '_')}_total.csv")
        return (results_df['email'] == email).any()
    except FileNotFoundError:
        return False  # If results file doesn't exist, assume no attempts yet


def save_total_score(email, test_name, total_score):
    """
    Saves the total score of a student for a specific test.

    Args:
        email (str): The student's email.
        test_name (str): The name of the test.
        total_score (int): The total score obtained.
    """
    filename = f"results_{test_name.replace(' ', '_')}_total.csv"
    try:
        results_df = pd.read_csv(filename)
    except FileNotFoundError:
        results_df = pd.DataFrame(columns=['email', 'test_name', 'total_score'])

    new_row = pd.DataFrame([{'email': email, 'test_name': test_name, 'total_score': total_score}])
    results_df = pd.concat([results_df, new_row], ignore_index=True)
    results_df.to_csv(filename, index=False)


def save_test_results(user, test_name, questions_df, responses, section_questions):
    """
    Saves the detailed test results (attempt for each question) for each student
    to a separate CSV file.

    Args:
        user (str): The user's email.
        test_name (str): The name of the test.
        questions_df (pd.DataFrame): DataFrame containing all questions.
        responses (dict): Dictionary of student responses.
        section_questions (dict): Dictionary containing section questions.
    """
    detailed_results = []

    for section, section_data in section_questions.items():
        for _, row in section_data.iterrows():
            question_id = row['question_id']
            correct_answer = row['answer']
            student_answer = responses.get(f"{section}_{question_id}", None)

            if student_answer is None:
                score = 0
            elif student_answer == correct_answer:
                score = 4
            else:
                score = -1

            detailed_results.append({
                "email": user,
                "test_name": test_name,
                "section": section,
                "question_id": question_id,
                "question": row['question'],
                "correct_answer": correct_answer,
                "student_answer": student_answer,
                "score": score
            })

    detailed_results_df = pd.DataFrame(detailed_results)
    filename = f"attempts_{test_name.replace(' ', '_')}_{user.replace('@', '_').replace('.', '_')}.csv"
    detailed_results_df.to_csv(filename, index=False)


def calculate_total_score(questions_df, responses, section_questions):
    """
    Calculates the total score for a student.

    Args:
        questions_df (pd.DataFrame): DataFrame containing all questions.
        responses (dict): Dictionary of student responses.
        section_questions (dict): Dictionary containing section questions.

    Returns:
        int: The total score.
    """
    total_score = 0
    for section, section_data in section_questions.items():
        for _, row in section_data.iterrows():
            question_id = row['question_id']
            correct_answer = row['answer']
            student_answer = responses.get(f"{section}_{question_id}", None)

            if student_answer is None:
                score = 0
            elif student_answer == correct_answer:
                score = 4
            else:
                score = -1
            total_score += score
    return total_score
def get_gsheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["google_service_account"], scope)
    client = gspread.authorize(creds)
    return client

def save_total_score_to_gsheet(student_id, name, email, test_id, total_score):
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Total Scores")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([student_id, name, email, test_id, total_score, now])

def save_attempts_to_gsheet(student_id, test_id, question_results):
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Question Attempts")
    for result in question_results:
        sheet.append_row([
            student_id,
            test_id,
            result.get("question_id", ""),
            result.get("selected_option", ""),
            result.get("correct_answer", ""),
            result.get("score", 0)
        ])