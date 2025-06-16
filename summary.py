import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.title("📊 Survey Summary & Visualisation")

# List available response CSVs
response_dir = "responses"
csv_files = [f for f in os.listdir(response_dir) if f.endswith(".csv")]

# Stop if no responses exist
if not csv_files:
    st.warning("No response files found.")
    st.stop()

# Let the user pick a CSV file to analyse
selected_csv = st.selectbox("Select a form to view responses:", csv_files)

# Load the CSV into a pandas DataFrame
df = pd.read_csv(os.path.join(response_dir, selected_csv))

st.subheader(f"🗂 Showing {len(df)} responses from: `{selected_csv}`")

# Clean column names to avoid Altair errors (remove colons)
clean_columns = {col: col.replace(":", "").strip() for col in df.columns}
df = df.rename(columns=clean_columns)

# Loop through each question (column) to display summaries
for raw_col, clean_col in zip(clean_columns.keys(), clean_columns.values()):
    st.markdown(f"### {raw_col}")  # Display the original question text

    # If it's text with lots of unique values, just show some examples
    if df[clean_col].dtype == object:
        unique_values = df[clean_col].nunique()

        if unique_values <= 10:
            counts = df[clean_col].value_counts()
            st.bar_chart(counts)
        else:
            st.write("Sample responses:")
            st.write(df[clean_col].sample(min(5, len(df))).tolist())

    # If it's numeric (like a scale), show average and histogram
    elif pd.api.types.is_numeric_dtype(df[clean_col]):
        st.write(f"Average: {df[clean_col].mean():.2f}")
        fig, ax = plt.subplots()
        df[clean_col].plot(kind='hist', bins=5, ax=ax, rwidth=0.8)
        ax.set_xlabel("Scale")
        ax.set_ylabel("Count")
        st.pyplot(fig)

    else:
        st.write("Unsupported data type.")
