import streamlit as st
import os
import json
from pathlib import Path

# Apply custom background, refined zoom effects, and override grey inputs
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #141e30, #243b55);
        color: white;
    }
    h1, h3, p, label, .stTextInput > label, .stSelectbox > label, .stSlider > label, .stNumberInput > label {
        transition: transform 0.2s ease-in-out;
        display: inline-block;
    }
    h1:hover, h3:hover, p:hover, label:hover, .stTextInput > label:hover, .stSelectbox > label:hover, .stSlider > label:hover, .stNumberInput > label:hover {
        transform: scale(1.04);
    }
    .stButton button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 6px;
        transition: background-color 0.3s ease, transform 0.2s ease;
        font-weight: 600;
    }
    .stButton button:hover {
        background-color: #218838;
        transform: scale(1.03);
    }
    .question-block {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    /* Remove default grey input backgrounds */
    section[data-testid="stTextInput"] input,
    section[data-testid="stNumberInput"] input,
    section[data-testid="stSelectbox"] div[role="combobox"] {
        background-color: transparent !important;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 6px;
        padding: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

MAX_QUESTIONS = 50

# App title
st.title("🛠️ Build a Survey")
st.markdown("Add your own questions, choose the answer format, and save your custom survey form.")

# Choose number of questions
num_questions = st.number_input("How many questions would you like?", min_value=1, max_value=MAX_QUESTIONS, step=1)

questions = []

# Loop to create question blocks
for i in range(int(num_questions)):
    st.markdown(f"<div class='question-block'>", unsafe_allow_html=True)
    st.markdown(f"### Question {i+1}")

    # Input question text
    q_text = st.text_input(f"Enter question text for Q{i+1}:", key=f"text_{i}")

    # Choose question type
    q_type = st.selectbox(
        f"Select type for Q{i+1}:",
        options=["Text", "Scale (1–5)", "Multiple Choice"],
        key=f"type_{i}"
    )

    q_data = {
        "text": q_text,
        "type": q_type
    }

    # Handle multiple choice input
    if q_type == "Multiple Choice":
        options_text = st.text_input(
            f"Enter options for Q{i+1} (comma-separated, e.g. Red, Blue, Green):",
            key=f"options_{i}"
        )
        q_data["options"] = [opt.strip() for opt in options_text.split(",") if opt.strip()]

    questions.append(q_data)
    st.markdown("</div>", unsafe_allow_html=True)

# Form title input
form_title = st.text_input("Give your form a title:", value="My Survey")

# Save form
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
