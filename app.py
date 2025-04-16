# app.py
import streamlit as st
import pandas as pd
import time
import datetime
import random
from streamlit_autorefresh import st_autorefresh
import json
import backend_logic

# Load Questions from JSON (for a specific test)
def load_questions_from_json(test_file):
    try:
        with open(test_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"{test_file} not found!")
        return None

# Load Students from CSV
def load_students():
    try:
        return pd.read_csv("students.csv")
    except FileNotFoundError:
        st.error("students.csv not found!")
        return None

# Load Instructions from Text File
def load_instructions():
    try:
        with open("instructions.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Instructions not found."

# Color Coding
status_colors = {"Not Answered": "🔴", "Answered": "🟢", "Review": "🟡"}

# Login Function (Email from CSV)
def login():
    st.subheader("Login to Mock Test Portal")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        students_df = load_students()
        if students_df is not None and email in students_df['email'].values and password == "Test@123":
            st.session_state["user"] = email
            st.session_state["logged_in"] = True
            st.session_state["attempted"] = backend_logic.check_attempted(email, st.session_state.get("current_test_id", "")) # Check on login
            st.session_state["all_responses_with_time"] = {}
            st.rerun()
        else:
            st.error("Invalid Credentials")

# Countdown Timer
def countdown_timer(test_id, test_time):
    current_time = datetime.datetime.now()
    start_time = datetime.datetime.strptime(test_time, "%Y-%m-%d %H:%M:%S")
    if current_time >= start_time:
        st.success(f"{test_id} is now live! Click below to start your test.")
        if st.button("Start Test", key=f"start_test_{test_id}"):
            st.session_state["test_started"] = st.session_state["test_files"][test_id]
            st.session_state["current_section"] = 1
            st.session_state["current_question"] = 0
            st.session_state["start_time"] = time.time()
            st.session_state["responses"] = {}
            st.session_state["statuses"] = {}
            st.session_state["test_completed"] = False
            st.session_state["attempted"] = True
            st.session_state["all_responses_with_time"] = {}
            backend_logic.save_attempted_user(st.session_state["user"], test_id) # Save on starting
            st.rerun()
    else:
        remaining_time = start_time - current_time
        st.info(f"{test_id} will start in {remaining_time}")

# Move to Next Section
def next_section():
    if st.session_state["current_section"] < 5:
        st.session_state["current_section"] += 1
        st.session_state["current_question"] = 0
        st.session_state["start_time"] = time.time()
        st.rerun()
    else:
        st.session_state["test_completed"] = True
        st.rerun()

# Test Interface
def start_test():
    if st.session_state.get("test_completed"):
        calculate_and_store_results()