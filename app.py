import streamlit as st
import pandas as pd
import time
import datetime
import random
from streamlit_autorefresh import st_autorefresh
import json
import backend_logic  # Import the backend logic

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
            st.session_state["attempted"] = False
            st.rerun()
        else:
            st.error("Invalid Credentials")

# Countdown Timer
def countdown_timer(test_name, test_time):
    current_time = datetime.datetime.now()
    start_time = datetime.datetime.strptime(test_time, "%Y-%m-%d %H:%M:%S")
    if current_time >= start_time:
        st.success(f"{test_name} is now live! Click below to start your test.")
        if st.button("Start Test", key=f"start_test_{test_name}"):
            st.session_state["test_started"] = st.session_state["test_files"][test_name]
            st.session_state["current_section"] = 1
            st.session_state["current_question"] = 0
            st.session_state["start_time"] = time.time()
            st.session_state["responses"] = {}
            st.session_state["statuses"] = {}
            st.session_state["test_completed"] = False
            st.session_state["attempted"] = True
            st.rerun()
    else:
        remaining_time = start_time - current_time
        st.info(f"{test_name} will start in {remaining_time}")

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
        st.success("Test Completed! Your responses have been recorded.")
        return

    test_name = st.session_state.get("test_started")
    current_section = st.session_state["current_section"]
    question_index = st.session_state["current_question"]
    questions_df = st.session_state["questions_df"]
    section_questions = st.session_state[f"section_{current_section}_questions"]
    total_questions = len(section_questions)

    st_autorefresh(interval=1000, key="timer_refresh")
    section_time = 1 * 60
    remaining_time = section_time - (time.time() - st.session_state["start_time"])
    if remaining_time <= 0:
        next_section()
        return

    test_display_name = list(st.session_state["test_files"].keys())[list(st.session_state["test_files"].values()).index(test_name)]
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
    if f"shuffled_options_{question_id}" not in st.session_state:
        options = [section_questions.iloc[question_index]['option1'], section_questions.iloc[question_index]['option2'], section_questions.iloc[question_index]['option3'], section_questions.iloc[question_index]['option4']]
        random.shuffle(options)
        st.session_state[f"shuffled_options_{question_id}"] = options
    else:
        options = st.session_state[f"shuffled_options_{question_id}"]

    selected_answer = st.session_state["responses"].get(f"{current_section}_{question_id}", None)
    st.markdown("<style>div.stRadio > div {font-size: 20px !important; color: #444;}</style>", unsafe_allow_html=True)
    selected_answer = st.radio("Select Answer:", options, key=f"{current_section}_{question_id}", index=options.index(selected_answer) if selected_answer in options else None)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Previous") and question_index > 0:
            st.session_state["current_question"] -= 1
            st.rerun()
    with col2:
        if st.button("Save Answer"):
            st.session_state["responses"][f"{current_section}_{question_id}"] = selected_answer
            st.session_state["statuses"][f"{current_section}_{question_id}"] = "Answered"
            st.rerun()
    with col3:
        if st.button("Change Answer"):
            st.session_state["responses"][f"{current_section}_{question_id}"] = None
            st.session_state["statuses"][f"{current_section}_{question_id}"] = "Not Answered"
            st.rerun()
    with col4:
        if st.button("Save for Review"):
            st.session_state["responses"][f"{current_section}_{question_id}"] = selected_answer
            st.session_state["statuses"][f"{current_section}_{question_id}"] = "Review"
            st.rerun()
    with col5:
        if st.button("Next"):
            if question_index < len(section_questions) - 1:
                st.session_state["current_question"] += 1
                st.rerun()

    st.markdown("""
        <style>
        div.stButton > button:nth-child(2) {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
        div.stButton > button:nth-child(3) {
            background-color: #f44336;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
        div.stButton > button:nth-child(4) {
            background-color: #ff9800;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
        div.stButton > button:nth-child(5) {
            font-weight: bold;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

def calculate_and_store_results():
    questions_df = st.session_state["questions_df"]
    test_name = list(st.session_state["test_files"].keys())[list(st.session_state["test_files"].values()).index(st.session_state["test_started"])]
    section_questions = {}
    for section in range(1, 6):
        section_questions[section] = st.session_state[f"section_{section}_questions"]

    total_score = backend_logic.calculate_total_score(
        questions_df, st.session_state["responses"], section_questions
    )

    backend_logic.save_total_score(st.session_state["user"], test_name, total_score)
    backend_logic.save_test_results(
        st.session_state["user"], test_name, questions_df, st.session_state["responses"], section_questions
    )

    user_email = st.session_state["user"]
    students_df = load_students()
    student_row = students_df[students_df["email"] == user_email]
    if not student_row.empty:
        student_id = str(student_row.iloc[0]["student_id"])
        name = student_row.iloc[0]["name"]
        email = user_email
        test_id = test_name
        correct_answers = {row["question_id"]: row["answer"] for _, row in questions_df.iterrows()}
        user_answers = {}
        for section, section_data in section_questions.items():
            for _, row in section_data.iterrows():
                question_id = row["question_id"]
                user_answers[question_id] = st.session_state["responses"].get(f"{section}_{question_id}", None)

        total_score, question_results = backend_logic.calculate_score(user_answers, correct_answers)
        backend_logic.save_total_score_to_gsheet(student_id, name, email, test_id, total_score)
        backend_logic.save_attempts_to_gsheet(student_id, test_id, question_results)
        backend_logic.save_attempted_user(email, test_id)
        st.success("✅ Your result has been recorded in Google Sheets.")

if "logged_in" not in st.session_state:
    st.image("college_logo.png", width=150, use_container_width=False)
    st.markdown("<h4 style='text-align: center; color:blue; margin-top: -10px;'>Shri Vishnu College of Pharmacy (Autonomous), Bhimavaram</h4>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Welcome to GPAT 25 Mock Tests Portal</h1>", unsafe_allow_html=True)
    login()
elif "test_started" not in st.session_state:
    if st.session_state["attempted"] == True:
        st.write("You have already attempted the test.")
    else:
        tab1, tab2 = st.tabs(["Instructions", "Tests"])
        with tab1:
            instructions = load_instructions()
            st.write(instructions)
        with tab2:
            test_dates = {"Mock Test 1": "2025-03-10 14:00:00", "Mock Test 2": "2025-03-11 14:00:00"}
            st.session_state["test_files"] = {"Mock Test 1": "questions_test1.json", "Mock Test 2": "questions_test2.json"}
            for test_name, test_time in test_dates.items():
                if backend_logic.check_attempted(st.session_state["user"], test_name):
                    st.warning(f"You have already attempted {test_name}.")
                else:
                    countdown_timer(test_name, test_time)
else:
    if "questions_df" not in st.session_state:
        questions = load_questions_from_json(st.session_state["test_started"])
        st.session_state["questions_df"] = pd.DataFrame(questions)
        all_questions = st.session_state["questions_df"].sample(n=125)
        for section in range(1, 6):
            start_index = (section - 1) * 25
            end_index = start_index + 25
            st.session_state[f"section_{section}_questions"] = all_questions.iloc[start_index:end_index]
    start_test()
