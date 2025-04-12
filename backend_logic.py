import os
import pandas as pd
import csv
import datetime
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def check_attempted(email, test_name):
    results_file = f"results_{test_name}_total.csv"
    if os.path.exists(results_file):
        df = pd.read_csv(results_file)
        return email in df['email'].values
    return False

def save_total_score(email, test_name, total_score):
    results_file = f"results_{test_name}_total.csv"
    file_exists = os.path.exists(results_file)
    with open(results_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['email', 'total_score', 'timestamp'])
        writer.writerow([email, total_score, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def save_test_results(email, test_name, questions_df, responses, section_questions):
    results_file = f"attempts_{test_name}_{email}.csv"
    with open(results_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['question_id', 'question', 'selected_option', 'correct_answer', 'score'])
        for section in section_questions:
            for index, row in section_questions[section].iterrows():
                question_id = row['question_id']
                question_text = row['question']
                correct_answer = row['answer']
                selected_option = responses.get(f"{section}_{question_id}", '')
                score = 0
                if selected_option == '':
                    score = 0
                elif selected_option == correct_answer:
                    score = 4
                else:
                    score = -1
                writer.writerow([question_id, question_text, selected_option, correct_answer, score])

def calculate_total_score(questions_df, responses, section_questions):
    total_score = 0
    for section in section_questions:
        for index, row in section_questions[section].iterrows():
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

def calculate_score(user_answers, correct_answers):
    total_score = 0
    question_results = []

    for qid, correct_ans in correct_answers.items():
        selected = user_answers.get(qid)

        if selected is None or selected == "":
            score = 0
        elif selected == correct_ans:
            score = 4
        else:
            score = -1

        total_score += score

        question_results.append({
            "question_id": qid,
            "selected_option": selected if selected else "",
            "correct_answer": correct_ans,
            "score": score
        })

    return total_score, question_results

def get_gsheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    keyfile_dict = dict(st.secrets["google_service_account"])
    keyfile_dict["private_key"] = keyfile_dict["private_key"].replace("\\n", "\n")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, scope)
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
