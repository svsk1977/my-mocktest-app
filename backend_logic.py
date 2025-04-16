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
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        keyfile_dict = dict(st.secrets["google_service_account"])
        keyfile_dict["private_key"] = keyfile_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, scope)
        client = gspread.authorize(creds)
        print("Successfully obtained Google Sheets client.")
        return client
    except Exception as e:
        print(f"Error getting Google Sheets client: {e}")
        return None

# ✅ Save score locally
def save_total_score(email, test_name, total_score):
    results_file = f"results_{test_name}_total.csv"
    file_exists = os.path.exists(results_file)
    with open(results_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['email', 'total_score', 'score_timestamp'])
        writer.writerow([email, total_score, get_current_time_ist()])
    print(f"Total score saved locally for {email}, {test_name}: {total_score}")

# ✅ Save per-question locally
def save_test_results(email, test_name, questions_df, responses, section_questions):
    results_file = f"attempts_{test_name}_{email}.csv"
    try:
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
        print(f"Per-question results saved locally for {email}, {test_name}.")
    except Exception as e:
        print(f"Error saving per-question results locally: {e}")

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
    try:
        client = get_gsheet_client()
        if client:
            sheet = client.open("mock_test_scores").worksheet("Total Scores")
            records = sheet.get_all_records()
            found_row_index = -1
            for i, row in enumerate(records):
                if str(row.get("student_id")) == str(student_id) and row.get("test_id") == test_id:
                    found_row_index = i + 2
                    break
            now = get_current_time_ist()
            row_data = [student_id, name, email, test_id, total_score, now]
            if found_row_index != -1:
                cell_list = sheet.range(f"A{found_row_index}:F{found_row_index}")
                for i, val in enumerate(row_data):
                    cell_list[i].value = val
                sheet.update_cells(cell_list)
                print(f"Total score updated in GSheet for student {student_id}, test {test_id}.")
            else:
                sheet.append_row(row_data)
                print(f"Total score appended to GSheet for student {student_id}, test {test_id}.")
        else:
            print("Google Sheets client not available, cannot save total score to GSheet.")
    except Exception as e:
        print(f"Error saving total score to Google Sheets: {e}")

# ✅ Save question-wise results to Google Sheet with timestamp
def save_attempts_to_gsheet(student_id, test_id, question_results, all_responses_with_time):
    try:
        client = get_gsheet_client()
        if client:
            sheet = client.open("mock_test_scores").worksheet("Question Attempts")
            print("Opened 'Question Attempts' sheet.")
            records = sheet.get_all_records()
            rows_to_delete = []
            for i, row in enumerate(records):
                if str(row.get("student_id")) == str(student_id) and row.get("test_id") == test_id:
                    rows_to_delete.append(i + 2)
            rows_to_delete.reverse()
            for row_num in rows_to_delete:
                try:
                    sheet.delete_rows(row_num)
                    print(f"Deleted row {row_num} for student {student_id}, test {test_id} in 'Question Attempts'.")
                except Exception as delete_e:
                    print(f"Error deleting row {row_num} in 'Question Attempts': {delete_e}")
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
                print(f"Appended {len(rows_to_append)} question attempts for student {student_id}, test {test_id}.")
            else:
                print(f"No new question attempts to append for student {student_id}, test {test_id}.")
            print("Finished saving question attempts to Google Sheets.")
        else:
            print("Google Sheets client not available, cannot save question attempts to GSheet.")
    except Exception as e:
        print(f"Error saving question attempts to Google Sheets: {e}")

# ✅ NEW: Save attempt user list (email, test, time)
def save_attempted_user(email, test_id):
    try:
        client = get_gsheet_client()
        if client:
            sheet = client.open("mock_test_scores").worksheet("Attempted Users")
            print("Opened 'Attempted Users' sheet.")
            now = get_current_time_ist()
            sheet.append_row([email, test_id, now])
            print(f"Appended user {email}, test {test_id} to 'Attempted Users'.")
        else:
            print("Google Sheets client not available, cannot save attempted user to GSheet.")
    except Exception as e:
        print(f"Error saving attempted user to Google Sheets: {e}")

# ✅ ✅ REPLACE: old local-only check
def check_attempted(email, test_id):
    try:
        client = get_gsheet_client()
        if client:
            sheet = client.open("mock_test_scores").worksheet("Attempted Users")
            print("Attempted Users sheet opened for checking.")
            records = sheet.get_all_records()
            for row in records:
                if row.get("email") == email and row.get("test_id") == test_id:
                    print(f"User {email} has attempted {test_id}.")
                    return True
            print(f"User {email} has not attempted {test_id}.")
            return False
        else:
            print("Google Sheets client not available, cannot check attempted user in GSheet.")
            return False
    except Exception as e:
        print(f"Error checking attempts in Google Sheets: {e}")
        return False

# ✅ Function to clear attempted status (for re-attempts)
def clear_attempted_user(email, test_id):
    try:
        client = get_gsheet_client()
        if client:
            sheet = client.open("mock_test_scores").worksheet("Attempted Users")
            print("Opened 'Attempted Users' sheet for clearing attempt.")
            records = sheet.get_all_records()
            rows_to_delete = []
            for i, row in enumerate(records):
                if row.get("email") == email and row.get("test_id") == test_id:
                    rows_to_delete.append(i + 2)
            rows_to_delete.reverse()
            for row_num in rows_to_delete:
                sheet.delete_rows(row_num)
                print(f"Cleared attempt for user {email}, test {test_id} from 'Attempted Users' (row {row_num}).")
            return True
        else:
            print("Google Sheets client not available, cannot clear attempted user in GSheet.")
            return False
    except Exception as e:
        print(f"Error clearing attempted user in Google Sheets: {e}")
        return False