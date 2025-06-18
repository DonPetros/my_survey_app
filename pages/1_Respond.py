import streamlit as st
import json
import os
import csv
from datetime import datetime
from pathlib import Path

# Apply custom background and hover zoom effects
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #4e54c8, #8f94fb);
        color: white;
    }
    h1, h2, h3, p, label, .stTextInput > label, .stSelectbox > label, .stSlider > label, .stNumberInput > label, .stRadio > label {
        transition: transform 0.2s ease-in-out;
    }
    h1:hover, h2:hover, h3:hover, p:hover, label:hover, .stTextInput > label:hover, .stSelectbox > label:hover, .stSlider > label:hover, .stNumberInput > label:hover, .stRadio > label:hover {
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
    </style>
""", unsafe_allow_html=True)

st.title("Fill Out a Survey Form")
st.markdown("Choose a form to complete and submit your answers below.")

form_dir = "forms"
form_files = [f for f in os.listdir(form_dir) if f.endswith(".json")]

if not form_files:
    st.warning("No survey forms found. Please create one first.")
    st.stop()

selected_form_file = st.selectbox("Choose a form to fill out:", form_files)

with open(os.path.join(form_dir, selected_form_file), "r") as f:
    form = json.load(f)

st.header(f"Survey: {form['title']}")

responses = []

for i, question in enumerate(form["questions"]):
    q_text = question["text"]
    q_type = question["type"]

    st.subheader(f"Q{i+1}: {q_text}")

    if q_type == "Text":
        answer = st.text_input("Your answer:", key=f"q{i}")
    elif q_type == "Scale (1–5)":
        answer = st.slider("Rate from 1 to 5", 1, 5, key=f"q{i}")
    elif q_type == "Multiple Choice":
        options = question.get("options", [])
        answer = st.radio("Choose one:", options, key=f"q{i}")
    else:
        answer = "Unsupported question type"

    responses.append({
        "question": q_text,
        "answer": answer
    })

if st.button("📩 Submit Responses"):
    os.makedirs("responses", exist_ok=True)

    form_name = selected_form_file.replace(".json", "")
    csv_filename = f"responses/{form_name}.csv"

    row = {f"Q{i+1}: {r['question']}": r["answer"] for i, r in enumerate(responses)}
    write_header = not os.path.exists(csv_filename)

    with open(csv_filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())

        if write_header:
            writer.writeheader()

        writer.writerow(row)

    st.success("✅ Your responses have been submitted!")
    st.info(f"Saved to `{csv_filename}`")
