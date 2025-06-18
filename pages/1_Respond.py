import streamlit as st
import json
import os
import csv
from datetime import datetime

# 🔧 Style
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
    .stButton button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #218838;
    }
    .question-card {
        background-color: rgba(0, 0, 0, 0.15);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 📁 Load available survey forms
form_dir = "forms"
form_files = [f for f in os.listdir(form_dir) if f.endswith(".json")]

if not form_files:
    st.warning("No survey forms found.")
    st.stop()

# 📋 Select a form
selected_form_file = st.selectbox("", form_files, label_visibility="collapsed")

# 📄 Load form data
with open(os.path.join(form_dir, selected_form_file), "r") as f:
    form = json.load(f)

# 📝 Show form title only
st.header(form["title"])

# 🧠 Session state
responses = st.session_state.get("responses", [None] * len(form["questions"]))
current_q = st.session_state.get("current_q", 0)

# ❓ Current question
question = form["questions"][current_q]
q_text = question["text"]
q_type = question["type"]

with st.container():
    st.markdown("<div class='question-card'>", unsafe_allow_html=True)
    st.subheader(f"Q{current_q + 1}: {q_text}")

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
    st.markdown("</div>", unsafe_allow_html=True)

# 🔘 Navigation
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
