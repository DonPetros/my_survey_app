import streamlit as st
import os
import json
from pathlib import Path

# Apply custom background and hover zoom effects
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #4e54c8, #8f94fb);
        color: white;
    }
    h1, h3, p, label, .stTextInput > label, .stSelectbox > label, .stSlider > label, .stNumberInput > label {
        transition: transform 0.2s ease-in-out;
    }
    h1:hover, h3:hover, p:hover, label:hover, .stTextInput > label:hover, .stSelectbox > label:hover, .stSlider > label:hover, .stNumberInput > label:hover {
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

MAX_QUESTIONS = 50

st.title("Build a Survey")
st.markdown("Add your own questions, choose the answer format, and save your custom survey form.")

num_questions = st.number_input("How many questions would you like?", min_value=1, max_value=MAX_QUESTIONS, step=1)

questions = []

for i in range(int(num_questions)):
    st.markdown(f"### Question {i+1}")

    q_text = st.text_input(f"Enter question text for Q{i+1}:", key=f"text_{i}")

    q_type = st.selectbox(
        f"Select type for Q{i+1}:",
        options=["Text", "Scale (1–5)", "Multiple Choice"],
        key=f"type_{i}"
    )

    q_data = {
        "text": q_text,
        "type": q_type
    }

    if q_type == "Multiple Choice":
        options_text = st.text_input(
            f"Enter options for Q{i+1} (comma-separated, e.g. Red, Blue, Green):",
            key=f"options_{i}"
        )
        q_data["options"] = [opt.strip() for opt in options_text.split(",") if opt.strip()]

    questions.append(q_data)

form_title = st.text_input("Give your form a title:", value="My Survey")

if st.button("📂 Save Survey Form"):
    form = {
        "title": form_title,
        "questions": questions
    }

    os.makedirs("forms", exist_ok=True)
    filename = f"forms/{form_title.replace(' ', '_').lower()}.json"

    with open(filename, "w") as f:
        json.dump(form, f, indent=4)

    st.success(f"✅ Survey form saved as `{filename}`")
