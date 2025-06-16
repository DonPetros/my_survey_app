import streamlit as st
import json
import os

# Set the title at the top of the app
st.title("🛠️ Custom Survey Form Builder")

# Short description for the user
st.write("Define your own survey form by adding questions and choosing their type.")

# Ask the form creator how many questions they want to include
num_questions = st.number_input("How many questions?", min_value=1, max_value=20, step=1)

# We'll store all the defined questions in this list
questions = []

# Loop for each question based on how many the user chose
for i in range(int(num_questions)):
    st.markdown(f"### Question {i+1}")

    # Text input for the question text (e.g., "What is your name?")
    q_text = st.text_input(f"Enter question text for Q{i+1}:", key=f"text_{i}")
    
    # Select the question type from a dropdown
    q_type = st.selectbox(
        f"Select type for Q{i+1}:",
        options=["Text", "Scale (1–5)", "Multiple Choice"],
        key=f"type_{i}"
    )

    # Build a dictionary to hold the question data
    q_data = {
        "text": q_text,
        "type": q_type
    }

    # If the type is Multiple Choice, ask the creator to define the options
    if q_type == "Multiple Choice":
        options_text = st.text_input(
            f"Enter options for Q{i+1} (comma-separated, e.g. Red, Blue, Green):",
            key=f"options_{i}"
        )
        # Split the input into a list of options
        q_data["options"] = [opt.strip() for opt in options_text.split(",") if opt.strip()]

    # Add this question to the overall list
    questions.append(q_data)

# Ask for a title to name the form
form_title = st.text_input("Give your form a title:", value="My Survey")

# Save the form when the button is clicked
# Save the form when the button is clicked
if st.button("Save Survey Form"):
    # Store the full form as a dictionary
    form = {
        "title": form_title,
        "questions": questions
    }

    # Create a folder to store the form files (if it doesn't exist)
    os.makedirs("forms", exist_ok=True)

    # Format the filename based on the title
    filename = f"forms/{form_title.replace(' ', '_').lower()}.json"

    # Save the form data as a JSON file
    with open(filename, "w") as f:
        json.dump(form, f, indent=4)

    # Notify the user that it was saved
    st.success(f"✅ Survey form saved as `{filename}`")
