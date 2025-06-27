import streamlit as st
import os
import json
from pathlib import Path

# Add custom styling for background, text, hover effects and buttons
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #141e30, #243b55);  /* Dark blue gradient background */
        colour: white;
    }
    h1, h3, p, label, .stTextInput > label, .stSelectbox > label, .stSlider > label, .stNumberInput > label {
        transition: transform 0.2s ease-in-out;
        display: inline-block;
    }
    /* Slight zoom effect when hovering over text */
    h1:hover, h3:hover, p:hover, label:hover, .stTextInput > label:hover, .stSelectbox > label:hover, .stSlider > label:hover, .stNumberInput > label:hover {
        transform: scale(1.04);
    }
    /* Style for the green buttons */
    .stButton button {
        background-colour: #28a745;
        colour: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 6px;
        transition: background-colour 0.3s ease, transform 0.2s ease;
        font-weight: 600;
    }
    .stButton button:hover {
        background-colour: #218838;
        transform: scale(1.03);
    }
    /* Light background box for each question block */
    .question-block {
        background-colour: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Set a maximum limit for number of questions
MAX_QUESTIONS = 50

# Page title
st.title("🌌 Build a Survey Across the Cosmos")

# Quick intro
st.markdown("Add your own questions, choose the answer format, and save your custom survey form.")

# Ask user how many questions they want to add
num_questions = st.number_input("How many questions would you like?", min_value=1, max_value=MAX_QUESTIONS, step=1)

# List to hold all question data
questions = []

# Create input fields for each question
for i in range(int(num_questions)):
    
    # Start a new block for each question
    st.markdown(f"<div class='question-block'>", unsafe_allow_html=True)
    st.markdown(f"### Question {i+1}")

    # Input for the question itself
    q_text = st.text_input(f"Enter question text for Q{i+1}:", key=f"text_{i}")

    # Choose type of question (e.g. text answer, scale, multiple choice)
    q_type = st.selectbox(
        f"Select type for Q{i+1}:",
        options=["Text", "Scale (1–5)", "Multiple Choice"],
        key=f"type_{i}"
    )

    # Start creating the question dictionary
    q_data = {
        "text": q_text,
        "type": q_type
    }

    # If user chose "Multiple Choice", ask for answer options
    if q_type == "Multiple Choice":
        options_text = st.text_input(
            f"Enter options for Q{i+1} (comma-separated, e.g. Red, Blue, Green):",
            key=f"options_{i}"
        )
        # Convert input string into a list of options, removing empty spaces
        q_data["options"] = [opt.strip() for opt in options_text.split(",") if opt.strip()]

    # Add the finished question to the list
    questions.append(q_data)
    st.markdown("</div>", unsafe_allow_html=True)

# Ask user to name the survey
form_title = st.text_input("Give your form a title:", value="My Survey")

# Save button – when clicked, save the survey as a .json file
if st.button("📂 Save Survey Form"):
    # Create a dictionary with form title and all questions
    form = {
        "title": form_title,
        "questions": questions
    }

    # Make sure the folder exists for saving
    os.makedirs("forms", exist_ok=True)
    # Create a filename using the title (lowercase, spaces replaced with underscores)
    filename = f"forms/{form_title.replace(' ', '_').lower()}.json"

    # Save the form as a JSON file
    with open(filename, "w") as f:
        json.dump(form, f, indent=4)

    # Let the user know it was saved successfully
    st.success(f"✅ Survey form saved as `{filename}`")
