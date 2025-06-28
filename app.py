import streamlit as st
import os
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# =====================
# 👤 Login System Setup (Admin only)
# =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "letmein"

if not st.session_state.logged_in:
    st.sidebar.title("🔑 Admin Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()

# =====================
# 🚪 Sidebar Navigation
# =====================
st.sidebar.title("🧭 Navigation")
if st.session_state.logged_in:
    page = st.sidebar.radio("Go to:", ["🏗️ Create Form", "📝 Answer a Form", "📊 View Results", "🚪 Logout"])
else:
    page = st.sidebar.radio("Go to:", ["📝 Answer a Form"])

# =====================
# 🏗️ Create Form (Admin Only)
# =====================
if page == "🏗️ Create Form" and st.session_state.logged_in:
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
            options_text = st.text_input(f"Enter options for Q{i+1} (comma-separated):", key=f"options_{i}")
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
# 📝 Answer a Form (Public)
# =====================
elif page == "📝 Answer a Form":
    st.title("📝 Respond to a Survey")
    form_dir = "forms"
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
            del st.session_state["responses"]
            del st.session_state["current_q"]
            st.rerun()

# =====================
# 📊 View Results (Admin Only)
# =====================
elif page == "📊 View Results" and st.session_state.logged_in:
    st.title("📊 Survey Summary & Insights")
    response_dir = "responses"
    csv_files = [f for f in os.listdir(response_dir) if f.endswith(".csv")]

    if not csv_files:
        st.warning("No response files found.")
        st.stop()

    selected_csv = st.selectbox("Select a form to view responses:", csv_files)
    df = pd.read_csv(os.path.join(response_dir, selected_csv))
    st.markdown(f"### Showing **{len(df)}** responses from `{selected_csv}`")

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("📥 Download Full Results (CSV)", csv_buffer.getvalue(), file_name=selected_csv, mime="text/csv")

    clean_columns = {col: col.replace(":", "").strip() for col in df.columns}
    df = df.rename(columns=clean_columns)

    for raw_col, clean_col in zip(clean_columns.keys(), clean_columns.values()):
        st.markdown(f"### ✏️ {raw_col}")
        if df[clean_col].dtype == object:
            counts = df[clean_col].value_counts().reset_index()
            counts.columns = ["Category", "Count"]
            with st.expander("🥧 Show Pie Chart"):
                fig, ax = plt.subplots()
                ax.pie(counts['Count'], labels=counts['Category'], autopct='%1.1f%%', startangle=140)
                ax.axis('equal')
                st.pyplot(fig)
        elif pd.api.types.is_numeric_dtype(df[clean_col]):
            avg = df[clean_col].mean()
            st.write(f"📈 Average rating: **{avg:.2f}**")
            with st.expander("📊 View histogram"):
                fig, ax = plt.subplots()
                sns.histplot(df[clean_col], bins=5, kde=True, ax=ax)
                st.pyplot(fig)

# =====================
# 🚪 Logout
# =====================
elif page == "🚪 Logout":
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()
