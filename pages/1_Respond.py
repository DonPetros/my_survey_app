import streamlit as st
import json
import os
import csv
from datetime import datetime
from pathlib import Path

# 💄 Style for background and animation
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #141e30, #243b55);
        color: white;
    }
    h1, h2, h3, p, label,
    .stTextInput > label,
    .stSelectbox > label,
    .stSlider > label,
    .stNumberInput > label,
    .stRadio > label {
        transition: transform 0.2s ease-in-out;
    }
    h1:hover, h2:hover, h3:hover, p:hover, label:hover,
    .stTextInput > label:hover,
    .stSelectbox > label:hover,
    .stSlider > label:hover,
    .stNumberInput > label:hover,
    .stRadio > label:hover {
        transform: scale(1.05);
    }
    .stButton button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 5px;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #218838;
    }
    .question-box {
        background-color: rgba(0, 0, 0, 0.2);
        padding: 1.5em;
        border-radius: 1em;
        margin-top: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# 🧠 Title and form loader
st.title("📝 Fill Out a Survey Form")
st.markdown("Choose a form to complete and submit your answers below.")

form_dir = "forms"
form_files = [f for f in os.listdir(form_dir) if f.endswith(".json")]

if not form_files:
    st.warning("No survey forms found. Please create one first.")
    st.stop()

selected_form_file = st.selectbox("Choose a form to fill out:", form_files)

# 📦 Load selected form
with open(os.path.join(form_dir, selected_form_file), "r") as f:
    form = json.load(f)

st.header(f"Survey: {form['title']}")

# 🌱 Setup session state
responses = st.session_state.get("responses", [None] * len(form["questions"]))
current_q = st.session_state.get("current_q", 0)

# ✏️ Render question
question = form["questions"][current_q]
q_text = question["text"]
q_type = question["type"]

with st.container():
    st.markdown("<div class='question-box'>", unsafe_allow_html=True)
    st.subheader(f"Q{current_q + 1}: {q_text}")

    if q_type == "Text":
        answer = st.text_input("Your answer:", value=responses[current_q] or "")
    elif q_type == "Scale (1–5)":
        answer = st.slider("Rate from 1 to 5", 1, 5, value=responses[current_q] or 3)
    elif q_type == "Multiple Choice":
        options = question.get("options", [])
        index = options.index(responses[current_q]) if responses[current_q] in options else 0
        answer = st.radio("Choose one:", options, index=index)
    else:
        answer = "Unsupported question type"

    responses[current_q] = answer
    st.session_state["responses"] = responses
    st.markdown("</div>", unsafe_allow_html=True)

# 🔄 Navigation buttons
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if current_q > 0:
        if st.button("⬅️ Previous"):
            st.session_state["current_q"] = current_q - 1
            st.experimental_rerun()

with col2:
    if current_q < len(form["questions"]) - 1:
        if st.button("Next ➡️"):
            st.session_state["current_q"] = current_q + 1
            st.experimental_rerun()

with col3:
    if current_q == len(form["questions"]) - 1:
        with st.expander("🔍 Review your answers before submitting"):
            for i, q in enumerate(form["questions"]):
                st.markdown(f"**Q{i+1}: {q['text']}**")
                st.markdown(f"📝 _Your answer:_ `{responses[i]}`")

        if st.button("📩 Submit Responses"):
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
            st.experimental_rerun()
