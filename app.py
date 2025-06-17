import streamlit as st
import json
import os

MAX_QUESTIONS = 50  # Limit the number of questions to avoid clutter

# Custom background and button style
st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1557682250-33bd709cbe85?auto=format&fit=crop&w=1950&q=80');
        background-size: cover;
        background-attachment: fixed;
    }

    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        padding: 0.5em 2em;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        font-size: 16px;
        transition: 0.3s ease;
    }

    div.stButton > button:first-child:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }

    .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header and description
st.markdown("## 📋 Build a Survey")
st.caption("Add your own questions, choose the answer format, and save your custom survey form.")
st.markdown("---")

# Ask the form creator how many questions they want to include
num_questions = st.number_input("🔢 How many questions would you like?", min_value=1, max_value=MAX_QUESTIONS, step=1)

# We'll store all the defined questions in this list
questions = []

# Loop for each question
for i in range(int(num_questions)):
    st.markdown(f"### ✏️ Question {i+1}")
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
            f"Enter options for Q{i+1} (comma-separated):",
            key=f"options_{i}"
        )
        q_data["options"] = [opt.strip() for opt in options_text.split(",") if opt.strip()]

    questions.append(q_data)

# Ask for a title
form_title = st.text_input("📝 Give your form a title:", value="My Survey")

# Save the form
if st.button("💾 Save Survey Form"):
    form = {
        "title": form_title,
        "questions": questions
    }

    os.makedirs("forms", exist_ok=True)
    filename = f"forms/{form_title.replace(' ', '_').lower()}.json"

    with open(filename, "w") as f:
        json.dump(form, f, indent=4)

    st.success(f"✅ Survey form saved as `{filename}`")
