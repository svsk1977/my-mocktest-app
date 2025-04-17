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
    return datetime.datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

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

# ✅ Local-only calculation (not for GSheet saving during test)
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

# ✅ Save final results to Google Sheet at the end of the test
def save_final_results_to_gsheet(student_id, name, email, test_id, total_score, all_responses_with_time, correct_answers):
    try:
        client = get_gsheet_client()
        if client:
            # Save Total Score
            total_score_sheet = client.open("mock_test_scores").worksheet("Total Scores")
            now = get_current_time_ist()
            total_score_sheet.append_row([student_id, name, email, test_id, total_score, now])
            print(f"Total score saved to GSheet for {student_id}, {test_id}.")

            # Save Question-wise Scores
            question_scores_sheet = client.open("mock_test_scores").worksheet("Question Scores")
            rows_to_append = []
            for section, questions_data in all_responses_with_time.items():
                for q_key, response_data in questions_data.items():
                    question_id = q_key.split('_')[1]
                    correct_answer = correct_answers.get(question_id, "")
                    selected_answer = response_data.get("selected_answer", "")
                    score = 0
                    if selected_answer == correct_answer and selected_answer != "":
                        score = 4
                    elif selected_answer != "" and selected_answer != correct_answer:
                        score = -1

                    rows_to_append.append([
                        student_id,
                        test_id,
                        question_id,
                        score,
                        selected_answer,
                        correct_answer,
                        response_data.get("timestamp", "")
                    ])
            if rows_to_append:
                question_scores_sheet.append_rows(rows_to_append)
                print(f"Question-wise scores saved to GSheet for {student_id}, {test_id}.")
            else:
                print(f"No question-wise scores to save for {student_id}, {test_id}.")

        else:
            print("Google Sheets client not available, cannot save final results to GSheet.")
    except Exception as e:
        print(f"Error saving final results to Google Sheets: {e}")

def get_attempted_users_cache():
    if "attempted_users" not in st.session_state:
        client = get_gsheet_client()
        if client:
            sheet = client.open("mock_test_scores").worksheet("Attempted Users")
            records = sheet.get_all_records()
            st.session_state["attempted_users"] = {(row.get("email"), row.get("test_id")) for row in records if row.get("email") and row.get("test_id")}
        else:
            st.session_state["attempted_users"] = set()
    return st.session_state["attempted_users"]

def check_attempted(email, test_id):
    attempted_users = get_attempted_users_cache()
    return (email, test_id) in attempted_users

def save_attempted_user(email, test_id):
    try:
        client = get_gsheet_client()
        if client:
            sheet = client.open("mock_test_scores").worksheet("Attempted Users")
            now = get_current_time_ist()
            sheet.append_row([email, test_id, now])
            if "attempted_users" in st.session_state:
                st.session_state["attempted_users"].add((email, test_id)) # Update cache
            print(f"Appended user {email}, test {test_id} to 'Attempted Users'.")
        else:
            print("Google Sheets client not available, cannot save attempted user to GSheet.")
    except Exception as e:
        print(f"Error saving attempted user to Google Sheets: {e}")

def clear_attempted_user(email, test_id):
    try:
        client = get_gsheet_client()
        if client:
            sheet = client.open("mock_test_scores").worksheet("Attempted Users")
            records = sheet.get_all_records()
            rows_to_delete = []
            for i, row in enumerate(records):
                if row.get("email") == email and row.get("test_id") == test_id:
                    rows_to_delete.append(i + 2)
            rows_to_delete.reverse()
            for row_num in rows_to_delete:
                sheet.delete_rows(row_num)
                if "attempted_users" in st.session_state:
                    st.session_state["attempted_users"].discard((email, test_id)) # Update cache
                print(f"Cleared attempt for user {email}, test {test_id} from 'Attempted Users' (row {row_num}).")
            return True
        else:
            print("Google Sheets client not available, cannot clear attempted user in GSheet.")
            return False
    except Exception as e:
        print(f"Error clearing attempted user in Google Sheets: {e}")
        return False