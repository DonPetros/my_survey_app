import streamlit as st
import os
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import sqlite3
import hashlib

# =====================
# 🗃️ SQLite Setup for User Authentication
# =====================
conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)''')
conn.commit()

# Helper to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =====================
# 👤 Login/Sign-up System Setup
# =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

st.sidebar.title("🔑 Account")
auth_option = st.sidebar.radio("Select Option:", ["Login", "Sign Up"])

if not st.session_state.logged_in:
    if auth_option == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
            user = c.fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials.")

    elif auth_option == "Sign Up":
        new_username = st.sidebar.text_input("Choose a username")
        new_password = st.sidebar.text_input("Choose a password", type="password")
        if st.sidebar.button("Create Account"):
            c.execute("SELECT * FROM users WHERE username = ?", (new_username,))
            if c.fetchone():
                st.sidebar.error("Username already exists.")
            else:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, hash_password(new_password)))
                conn.commit()
                st.sidebar.success("Account created! You can now log in.")

# =====================
# 🚪 Sidebar Navigation
# =====================
st.sidebar.title("🧭 Navigation")
if st.session_state.logged_in:
    page = st.sidebar.radio("Go to:", ["📇 Create Form", "📝 Answer a Form", "📊 View Results", "🚪 Logout"])
else:
    page = st.sidebar.radio("Go to:", ["📝 Answer a Form"])

# ✅ Handle logout directly
if page == "🚪 Logout":
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("🔓 You have been logged out.")
    st.stop()

# 🔧 The rest of your app (Create Form, Answer, View Results) stays unchanged...
# You can copy and paste the rest of your logic below here

# For example:
if page == "📇 Create Form" and st.session_state.logged_in:
    st.title("🌌 Build a Survey Across the Cosmos")
    st.markdown("Add your own questions, choose the answer format, and save your custom survey form.")

    MAX_QUESTIONS = 50
    num_questions = st.number_input("How many questions would you like?", min_value=1, max_value=MAX_QUESTIONS, step=1)
    questions = []

    for i in range(int(num_questions)):
        st.markdown(f"### Question {i+1}")
        q_text = st.text_input(f"Enter question text for Q{i+1}:", key=f"text_{i}")
        q_type = st.selectbox(f"Select type for Q{i+1}:", ["Text", "Scale (1–5)", "Multiple Choice"], key=f"type_{i}")
        q_data = {"text": q_text, "type": q_type}
        if q_type == "Multiple Choice":
            options_text = st.text_input(f"Enter options for Q{i+1} (comma-separated, e.g. Yes, No, Maybe):", key=f"options_{i}")
            q_data["options"] = [opt.strip() for opt in options_text.split(",") if opt.strip()]
        questions.append(q_data)

    form_title = st.text_input("Give your form a title:", value="My Survey")
    if st.button("📂 Save Survey Form"):
        form = {"title": form_title, "questions": questions}
        os.makedirs("forms", exist_ok=True)
        filename = f"forms/{form_title.replace(' ', '_').lower()}.json"
        with open(filename, "w") as f:
            json.dump(form, f, indent=4)
        st.success(f"✅ Survey form saved as `{filename}`")

# =====================
# 🔧 Global Styling
# =====================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #141e30, #243b55);
        color: white;
    }
    h1, h2, h3, p, label {
        transition: transform 0.2s ease-in-out;
    }
    h1:hover, h2:hover, h3:hover, p:hover, label:hover {
        transform: scale(1.05);
    }
    .stButton button, .stDownloadButton button {
        background-color: #ff4b2b;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 8px;
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        background-color: #ff416c;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# =====================
# 📇 Create Form (Admin Only)
# =====================
if page == "📇 Create Form" and st.session_state.logged_in:
    st.title("🌌 Build a Survey Across the Cosmos")
    st.markdown("Add your own questions, choose the answer format, and save your custom survey form.")

    MAX_QUESTIONS = 50
    num_questions = st.number_input("How many questions would you like?", min_value=1, max_value=MAX_QUESTIONS, step=1)
    questions = []

    for i in range(int(num_questions)):
        st.markdown(f"### Question {i+1}")
        q_text = st.text_input(f"Enter question text for Q{i+1}:", key=f"text_{i}")
        q_type = st.selectbox(f"Select type for Q{i+1}:", ["Text", "Scale (1–5)", "Multiple Choice"], key=f"type_{i}")
        q_data = {"text": q_text, "type": q_type}
        if q_type == "Multiple Choice":
            options_text = st.text_input(f"Enter options for Q{i+1} (comma-separated, e.g. Yes, No, Maybe):", key=f"options_{i}")
            q_data["options"] = [opt.strip() for opt in options_text.split(",") if opt.strip()]
        questions.append(q_data)

    form_title = st.text_input("Give your form a title:", value="My Survey")
    if st.button("📂 Save Survey Form"):
        valid = True
        for idx, q in enumerate(questions):
            if not q["text"].strip():
                st.error(f"❗ Question {idx+1} is empty. Please enter a question.")
                valid = False
            if q["type"] == "Multiple Choice" and ("options" not in q or not q["options"]):
                st.error(f"❗ Question {idx+1} has no multiple-choice options.")
                valid = False
        if valid:
            form = {"title": form_title, "questions": questions}
            os.makedirs("forms", exist_ok=True)
            filename = f"forms/{form_title.replace(' ', '_').lower()}.json"
            with open(filename, "w") as f:
                json.dump(form, f, indent=4)
            st.success(f"✅ Survey form saved as `{filename}`")

# =====================
# 📝 Answer a Form (Public)
# =====================
elif page == "📝 Answer a Form":
    st.title("📝 Respond to a Survey")
    form_dir = "forms"
    os.makedirs(form_dir, exist_ok=True)
    form_files = [f for f in os.listdir(form_dir) if f.endswith(".json")]

    if not form_files:
        st.warning("No survey forms found.")
        st.stop()

    selected_form_file = st.selectbox("Select a form to answer:", form_files)
    with open(os.path.join(form_dir, selected_form_file), "r") as f:
        form = json.load(f)

    st.header(form["title"])
    responses = st.session_state.get("responses", [None] * len(form["questions"]))
    current_q = st.session_state.get("current_q", 0)

    question = form["questions"][current_q]
    q_text = question["text"]
    q_type = question["type"]

    st.markdown(f"### Q{current_q + 1}: {q_text}")
    if q_type == "Text":
        answer = st.text_input("Your answer:", value=responses[current_q] or "")
    elif q_type == "Scale (1–5)":
        answer = st.slider("Rate from 1 to 5", 1, 5, value=responses[current_q] or 3)
    elif q_type == "Multiple Choice":
        options = question.get("options", [])
        answer = st.radio("Choose one:", options, index=options.index(responses[current_q]) if responses[current_q] in options else 0)
    else:
        answer = "Unsupported question type"

    responses[current_q] = answer
    st.session_state["responses"] = responses

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if current_q > 0 and st.button("⬅️ Previous"):
            st.session_state["current_q"] = current_q - 1
            st.rerun()
    with col2:
        if current_q < len(form["questions"]) - 1 and st.button("Next ➡️"):
            st.session_state["current_q"] = current_q + 1
            st.rerun()
    with col3:
        if current_q == len(form["questions"]) - 1 and st.button("📩 Submit Responses"):
            if any(r is None or (isinstance(r, str) and not r.strip()) for r in responses):
                st.error("❗ Please answer all questions before submitting.")
            else:
                os.makedirs("responses", exist_ok=True)
                form_name = selected_form_file.replace(".json", "")
                csv_filename = f"responses/{form_name}.csv"
                row = {f"Q{i+1}: {q['text']}": responses[i] for i, q in enumerate(form["questions"])}
                write_header = not os.path.exists(csv_filename)
                with open(csv_filename, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=row.keys())
                    if write_header:
                        writer.writeheader()
                    writer.writerow(row)
                st.success("✅ Your responses have been submitted!")
                st.info(f"Saved to `{csv_filename}`")
                if "responses" in st.session_state:
                    del st.session_state["responses"]
                if "current_q" in st.session_state:
                    del st.session_state["current_q"]
                st.rerun()

# =====================
# 📊 View Results (Admin Only)
# =====================
elif page == "📊 View Results" and st.session_state.logged_in:
    st.title("📊 Survey Summary & Insights")
    response_dir = "responses"
    os.makedirs(response_dir, exist_ok=True)
    csv_files = [f for f in os.listdir(response_dir) if f.endswith(".csv")]

    if not csv_files:
        st.warning("No response files found.")
        st.stop()

    selected_csv = st.selectbox("Select a form to view responses:", csv_files)
    df = pd.read_csv(os.path.join(response_dir, selected_csv))
    st.markdown(f"### Showing **{len(df)}** responses from `{selected_csv}`")

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("📅 Download Full Results (CSV)", csv_buffer.getvalue(), file_name=selected_csv, mime="text/csv")

    clean_columns = {col: col.replace(":", "").strip() for col in df.columns}
    df = df.rename(columns=clean_columns)

    for raw_col, clean_col in zip(clean_columns.keys(), clean_columns.values()):
        st.markdown(f"### ✏️ {raw_col}")

        if df[clean_col].dtype == object:
            sort_order = st.radio(
                f"Sort responses for '{raw_col}':",
                ["Most popular", "Least popular", "Alphabetical"],
                key=f"sort_{clean_col}",
                horizontal=True
            )

            counts = df[clean_col].value_counts().reset_index()
            counts.columns = ["Category", "Count"]

            if sort_order == "Least popular":
                counts = counts.sort_values("Count")
            elif sort_order == "Alphabetical":
                counts = counts.sort_values("Category")

            top_n = counts.head(5)
            for _, row in top_n.iterrows():
                label = row['Category']
                percentage = (row['Count'] / len(df)) * 100
                if len(label) > 40:
                    label_display = label[:40] + "..."
                    st.write(f"💬 **{int(row['Count'])}** said: *{label_display}* (**{percentage:.1f}%**) ❕")
                    with st.expander("🔍 View full response"):
                        st.write(label)
                else:
                    st.write(f"💬 **{int(row['Count'])}** said: *{label}* (**{percentage:.1f}%**)")

            if len(counts) > 5:
                with st.expander("📖 See all responses"):
                    for _, row in counts.iterrows():
                        pct = (row['Count'] / len(df)) * 100
                        st.write(f"**{int(row['Count'])}** → {row['Category']} (**{pct:.1f}%**)")

            if len(counts) > 1:
                with st.expander("🥧 Show Pie Chart"):
                    fig, ax = plt.subplots()
                    ax.pie(counts['Count'], labels=counts['Category'], autopct='%1.1f%%', startangle=140, textprops={'color': 'white'})
                    ax.axis('equal')
                    fig.patch.set_facecolor('#243b55')
                    st.pyplot(fig)

        elif pd.api.types.is_numeric_dtype(df[clean_col]):
            avg = df[clean_col].mean()
            st.write(f"📈 Average rating: **{avg:.2f}**")

            with st.expander("📊 View histogram"):
                fig, ax = plt.subplots()
                sns.histplot(df[clean_col], bins=5, kde=True, ax=ax)
                ax.set_xlabel("Scale")
                ax.set_ylabel("Count")
                ax.set_facecolor("#f0f0f0")
                st.pyplot(fig)

            with st.expander("👥 View individual ratings"):
                for i, val in enumerate(df[clean_col]):
                    st.write(f"👤 Respondent {i+1}: **{val}**")
