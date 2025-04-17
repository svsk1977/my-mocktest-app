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
        if not st.session_state.get("results_saved", False): # Check if results are already saved
            calculate_and_store_results()
            st.session_state["results_saved"] = True # Set the flag
            st.success("✅ Test Completed! Thanks for attempting.")
        else:
            st.success("✅ Test Completed! Your results have already been recorded.")
        return

    test_id = st.session_state.get("test_started")
    current_section = st.session_state["current_section"]
    question_index = st.session_state["current_question"]
    questions_df = st.session_state["questions_df"]
    section_questions = st.session_state[f"section_{current_section}_questions"]
    total_questions = len(section_questions)

    if not st.session_state.get("test_completed"):
        st_autorefresh(interval=1000, key="timer_refresh")
        section_time = 1 * 60
        remaining_time = section_time - (time.time() - st.session_state["start_time"])
        if remaining_time <= 0:
            next_section()
            return

    test_display_name = list(st.session_state["test_files"].keys())[list(st.session_state["test_files"].values()).index(test_id)]
    st.markdown(f"<h2 style='text-align:center; color:blue; font-size:50px;'>{test_display_name} - Section {current_section}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center; color:red; font-size:40px;'>⏳ Time Left: {int(remaining_time // 60)} min {int(remaining_time % 60)} sec</h3>", unsafe_allow_html=True)

    st.sidebar.title("Navigation Panel")
    nav_cols = st.sidebar.columns(4)
    for i in range(total_questions):
        q_id = section_questions.iloc[i]['question_id']
        status = st.session_state["statuses"].get(f"{current_section}_{q_id}", "Not Answered")
        btn_label = f"{status_colors.get(status, '🔴')} Q{i + 1}"
        if nav_cols[i % 4].button(btn_label, key=f"nav_{q_id}"):
            st.session_state["current_question"] = i
            st.rerun()

    question = section_questions.iloc[question_index]['question']
    st.markdown(f"<h1 style='color:#1E8449; font-size:35px;'>{question}</h1>", unsafe_allow_html=True)

    question_id = section_questions.iloc[question_index]['question_id']
    current_q_key = f"{current_section}_{question_id}"
    if f"shuffled_options_{question_id}" not in st.session_state:
        options = [section_questions.iloc[question_index]['option1'], section_questions.iloc[question_index]['option2'], section_questions.iloc[question_index]['option3'], section_questions.iloc[question_index]['option4']]
        random.shuffle(options)
        st.session_state[f"shuffled_options_{question_id}"] = options
    else:
        options = st.session_state[f"shuffled_options_{question_id}"]

    selected_answer = st.session_state["responses"].get(current_q_key, None)
    st.markdown("<style>div.stRadio > div {font-size: 20px !important; color: #444;}</style>", unsafe_allow_html=True)
    selected_answer = st.radio("Select Answer:", options, key=current_q_key, index=options.index(selected_answer) if selected_answer in options else None)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Previous") and question_index > 0:
            st.session_state["current_question"] -= 1
            st.rerun()
    with col2:
        if st.button("Save Answer"):
            st.session_state["responses"][current_q_key] = selected_answer
            st.session_state["statuses"][current_q_key] = "Answered"
            st.session_state["all_responses_with_time"].setdefault(current_section, {})[current_q_key] = {
                "selected_answer": selected_answer,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state[f"answer_timestamp_{current_section}_{question_id}"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
    with col3:
        if st.button("Change Answer"):
            st.session_state["responses"][current_q_key] = None
            st.session_state["statuses"][current_q_key] = "Not Answered"
            st.session_state["all_responses_with_time"].setdefault(current_section, {})[current_q_key] = {
                "selected_answer": None,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%