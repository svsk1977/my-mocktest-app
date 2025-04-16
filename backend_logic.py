import os
import pandas as pd
import csv
import datetime
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone

# ... (get_current_time_ist, get_gsheet_client, calculate_score)

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

# ... (save_total_score, save_test_results)

def save_attempts_to_gsheet(student_id, test_id, question_results):
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Question Attempts")

    # Clear existing attempts
    records = sheet.get_all_records()
    rows_to_delete = []
    for i, row in enumerate(records):
        if str(row.get("student_id")) == str(student_id) and row.get("test_id") == test_id:
            rows_to_delete.append(i + 2)

    rows_to_delete.reverse()
    for row_num in rows_to_delete:
        sheet.delete_rows(row_num)

    # Append new attempts
    for result in question_results:
        print(f"Saving question: {result}") #added print statement
        sheet.append_row([
            student_id,
            test_id,
            result.get("question_id", ""),
            result.get("selected_option", ""),
            result.get("correct_answer", ""),
            result.get("score", 0)
        ])

def save_attempted_user(email, test_id):
    print(f"Saving attempted user: {email}, {test_id}") #added print statement
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Attempted Users")
    now = get_current_time_ist()
    sheet.append_row([email, test_id, now])

# ... (check_attempted)