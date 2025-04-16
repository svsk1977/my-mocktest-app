import os
import pandas as pd
import csv
import datetime
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone

# ... (get_current_time_ist, get_gsheet_client, save_total_score, save_test_results, calculate_score, calculate_total_score are the same)

def save_total_score_to_gsheet(student_id, name, email, test_id, total_score):
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Total Scores")

    records = sheet.get_all_records()
    found_row = -1
    for i, row in enumerate(records):
        if str(row.get("student_id")) == str(student_id) and row.get("test_id") == test_id:
            found_row = i + 2 # +2 because gspread rows are 1-indexed, and we skip header
            break

    now = get_current_time_ist()
    if found_row != -1:
        sheet.update_row([student_id, name, email, test_id, total_score, now], found_row)
    else:
        sheet.append_row([student_id, name, email, test_id, total_score, now])

def save_attempts_to_gsheet(student_id, test_id, question_results):
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Question Attempts")

    # Clear existing attempts for this student and test
    records = sheet.get_all_records()
    rows_to_delete = []
    for i, row in enumerate(records):
        if str(row.get("student_id")) == str(student_id) and row.get("test_id") == test_id:
            rows_to_delete.append(i + 2)  # +2 because gspread rows are 1-indexed, and we skip header

    rows_to_delete.reverse() # Delete from bottom up
    for row_num in rows_to_delete:
        sheet.delete_rows(row_num)

    # Append new attempts
    for result in question_results:
        sheet.append_row([
            student_id,
            test_id,
            result.get("question_id", ""),
            result.get("selected_option", ""),
            result.get("correct_answer", ""),
            result.get("score", 0)
        ])

def save_attempted_user(email, test_id):
    client = get_gsheet_client()
    sheet = client.open("mock_test_scores").worksheet("Attempted Users")
    now = get_current_time_ist()
    sheet.append_row([email, test_id, now])

def check_attempted(email, test_id):
    try:
        client = get_gsheet_client()
        sheet = client.open("mock_test_scores").worksheet("Attempted Users")
        records = sheet.get_all_records()
        for row in records:
            if row.get("email") == email and row.get("test_id") == test_id:
                return True
    except:
        return False
    return False