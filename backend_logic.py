# backend_logic.py
import os
import pandas as pd
import csv
import datetime
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone

# ✅ IST time
def get_current_time_ist():
    ist = timezone("Asia/Kolkata")
    return datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

# ✅ Google Sheets client
def get_gsheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    keyfile_dict = dict(st.secrets["google_service_account"])
    keyfile_dict["private_key"] = keyfile_dict["private_key"].replace("\\n", "\n")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, scope)
    return gspread.authorize(creds)

# ✅ Save score locally
def save_total_score(email, test_name, total_score):
    results_file = f"results_{test_name}_total.csv"
    file_exists = os.path.exists(results_file)
    with open(results_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['email', 'total_score', 'score_timestamp'])
        writer.writerow([email, total_score, get_current_time_ist()])

# ✅ Save per-question locally
def save_test_results(email, test_name, questions_df, responses, section_questions):
    results_file = f"attempts_{test_name}_{email}.csv"
    with open(results_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['question_id', 'question', 'selected_option', 'correct_answer', 'score', 'answer_timestamp'])
        for section in section_questions:
            for _, row in section_questions[section].iterrows():
                question_id = row['question_id']
                question_text = row['question']
                correct_answer = row['answer']
                selected_option = responses.get(f"{section}_{question_id}", '')
                timestamp = st.session_state.get(f"answer_timestamp_{section}_{question_id}", "")
                score = 0
                if selected_option == '':
                    score = 0
                elif selected_option == correct_answer:
                    score = 4
                else:
                    score = -1
                writer.writerow([question_id, question_text, selected_option, correct_answer, score, timestamp])

# ✅ Calculate final score + per-question result
def calculate_score(user_answers, correct_answers):
    total_score = 0
    question_results = []

    for qid, correct_ans in correct_answers.items():
        selected = user_answers.get(qid, "")
        score = 0
        if selected == "":
            score = 0
        elif selected == correct_ans:
            score = 4
        else:
            score = -1
        total_score += score

        question_results.append({
            "question_id": qid,
            "selected_option": selected,
            "correct_answer": correct_ans,
            "score": score,
        })

    return total_score, question_results

# ✅ Local-only calculation (not for GSheet)
def calculate_total_score(questions_df, responses, section_questions):
    total_score = 0
    for section in section_questions:
        for _, row in section_questions[section].iterrows():
            question_id = row['question_id']
            correct_answer = row['answer']
            selected_option = responses.get(f"{section}_{question_id}", '')
            if selected_option == '':
                score = 0
            elif selected_option == correct_answer:
                score = 4
            else:
                score = -1
            total_score += score
    return total_score

# ✅ Save total score to Google Sheet
def save_total_score_to_gsheet(student_id, name, email, test_id, total_score):
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Total Scores")

    records = sheet.get_all_records()
    found_row = -1
    for i, row in enumerate(records):
        if str(row.get("student_id")) == str(student_id) and row.get("test_id") == test_id:
            found_row = i + 2  # +2 because gspread rows are 1-indexed, and we skip header
            break

    now = get_current_time_ist()
    if found_row != -1:
        sheet.update_row([student_id, name, email, test_id, total_score, now], found_row)
    else:
        sheet.append_row([student_id, name, email, test_id, total_score, now])

# ✅ Save question-wise results to Google Sheet with timestamp
def save_attempts_to_gsheet(student_id, test_id, question_results, all_responses_with_time):
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Question Attempts")

    # Clear existing attempts for this student and test
    records = sheet.get_all_records()
    rows_to_delete = []
    for i, row in enumerate(records):
        if str(row.get("student_id")) == str(student_id) and row.get("test_id") == test_id:
            rows_to_delete.append(i + 2)  # +2 because gspread rows are 1-indexed, and we skip header

    rows_to_delete.reverse()  # Delete from bottom up
    for row_num in rows_to_delete:
        sheet.delete_rows(row_num)

    # Append new attempts with timestamp
    rows_to_append = []
    for section, questions in all_responses_with_time.items():
        for q_id, response_data in questions.items():
            result = next((r for r in question_results if r["question_id"] == q_id.split('_')[1]), None)
            if result:
                rows_to_append.append([
                    student_id,
                    test_id,
                    section,
                    q_id.split('_')[1],
                    response_data['selected_answer'],
                    result.get("correct_answer", ""),
                    result.get("score", 0),
                    response_data['timestamp']
                ])
    if rows_to_append:
        sheet.append_rows(rows_to_append)
    print("Question attempts saved successfully.")

# ✅ NEW: Save attempt user list (email, test, time)
def save_attempted_user(email, test_id):
    print(f"Saving attempted user: {email}, {test_id}")
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Attempted Users")
    now = get_current_time_ist()
    sheet.append_row([email, test_id, now])

# ✅ ✅ REPLACE: old local-only check
def check_attempted(email, test_id):
    try:
        print("Checking if user attempted test...")
        client = get_gsheet_client()
        print("Google Sheets client obtained.")
        sheet = client.open("mock_test_scores").worksheet("Attempted Users")
        print("Attempted Users sheet opened.")
        records = sheet.get_all_records()
        for row in records:
            if row.get("email") == email and row.get("test_id") == test_id:
                print(f"User {email} has attempted {test_id}.")
                return True
        print(f"User {email} has not attempted {test_id}.")
    except Exception as e:
        print(f"Error checking attempts: {e}")
        return False
    return False