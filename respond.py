import streamlit as st
import json
import os
from datetime import datetime

st.title("📝 Fill Out a Survey Form")

# Look for all available form JSON files
form_dir = "forms"
form_files = [f for f in os.listdir(form_dir) if f.endswith(".json")]

if not form_files:
    st.warning("No survey forms found. Please create one first.")
    st.stop()

# Let user choose which form to fill
selected_form_file = st.selectbox("Choose a form to fill out:", form_files)

# Load the selected form
with open(os.path.join(form_dir, selected_form_file), "r") as f:
    form = json.load(f)

st.header(f"Survey: {form['title']}")

# Store the user’s answers here
responses = []

# Go through each question and render the appropriate input
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

# Save responses when submitted
import csv  # add this to your imports at the top

# When the user submits their answers
if st.button("Submit Responses"):
    os.makedirs("responses", exist_ok=True)

    form_name = selected_form_file.replace(".json", "")
    csv_filename = f"responses/{form_name}.csv"

    # Build a row of answers (flat format)
    row = {f"Q{i+1}: {r['question']}": r["answer"] for i, r in enumerate(responses)}

    # Check if the file exists — if not, write headers first
    write_header = not os.path.exists(csv_filename)

    with open(csv_filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())

        if write_header:
            writer.writeheader()

        writer.writerow(row)

    st.success("✅ Your responses have been submitted!")
    st.info(f"Saved to `{csv_filename}`")
