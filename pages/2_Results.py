import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# ========== 🎨 Custom Styling ==========
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
    .stButton button, .stDownloadButton button {
        background-color: #ff4b2b;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 8px;
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        background-color: #ff416c;
        transform: scale(1.05);
    }
    /* Make selectbox and headers feel more integrated */
    .css-1cpxqw2 { margin-bottom: -1rem; }
    </style>
""", unsafe_allow_html=True)

# ========== 🧠 App Title ==========
st.title("🧬 Explore Survey Insights")

# ========== 📂 Load Available CSV Files from "responses" Folder ==========
response_dir = "responses"
csv_files = [f for f in os.listdir(response_dir) if f.endswith(".csv")]

# If no files are found, show a warning and exit
if not csv_files:
    st.warning("No response files found.")
    st.stop()

# ========== 📑 Select a CSV File to View ==========
selected_csv = st.selectbox("Choose a survey response file:", csv_files)

# ========== 📊 Load CSV into DataFrame ==========
df = pd.read_csv(os.path.join(response_dir, selected_csv))

# ========== 👁️ Show File Summary and Download Option ==========
st.markdown(f"### Showing **{len(df)}** responses from `{selected_csv}`")

# Add download button for the current CSV file
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)
st.download_button("📥 Download Full Results (CSV)", csv_buffer.getvalue(), file_name=selected_csv, mime="text/csv")

# ========== 🧼 Clean Column Names (Remove colons, extra whitespace) ==========
clean_columns = {col: col.replace(":", "").strip() for col in df.columns}
df = df.rename(columns=clean_columns)

# ========== 🔍 Loop Through Questions (Columns) ==========
for raw_col, clean_col in zip(clean_columns.keys(), clean_columns.values()):
    st.markdown(f"### ✏️ {raw_col}")

    # ========== 📚 Handle Text-Based Responses ==========
    if df[clean_col].dtype == object:
        sort_order = st.radio(
            f"Sort responses for '{raw_col}':",
            ["Most popular", "Least popular", "Alphabetical"],
            key=f"sort_{clean_col}",
            horizontal=True
        )

        counts = df[clean_col].value_counts().reset_index()
        counts.columns = ["Category", "Count"]

        # Apply sorting option
        if sort_order == "Least popular":
            counts = counts.sort_values("Count")
        elif sort_order == "Alphabetical":
            counts = counts.sort_values("Category")

        # Show top 5 responses
        top_n = counts.head(5)
        for _, row in top_n.iterrows():
            label = row['Category']
            percentage = (row['Count'] / len(df)) * 100
            if len(label) > 40:
                label_display = label[:40] + "..."
                st.write(f"💬 **{int(row['Count'])}** said: *{label_display}* (**{percentage:.1f}%**) ❕")
                with st.expander("🔍 View full response"):
                    st.write(label)
            else:
                st.write(f"💬 **{int(row['Count'])}** said: *{label}* (**{percentage:.1f}%**)")

        # Optional: See all responses
        if len(counts) > 5:
            with st.expander("📖 See all responses"):
                for _, row in counts.iterrows():
                    pct = (row['Count'] / len(df)) * 100
                    st.write(f"**{int(row['Count'])}** → {row['Category']} (**{pct:.1f}%**)")

        # Optional: Pie chart visualisation
        if len(counts) > 1:
            with st.expander("🥧 Show Pie Chart"):
                fig, ax = plt.subplots()
                ax.pie(counts['Count'], labels=counts['Category'], autopct='%1.1f%%', startangle=140, textprops={'color': 'white'})
                ax.axis('equal')
                fig.patch.set_facecolor('#243b55')
                st.pyplot(fig)

    # ========== 📈 Handle Numeric/Scale Responses ==========
    elif pd.api.types.is_numeric_dtype(df[clean_col]):
        avg = df[clean_col].mean()
        st.write(f"📈 Average rating: **{avg:.2f}**")

        # Show histogram of responses
        with st.expander("📊 View histogram"):
            fig, ax = plt.subplots()
            sns.histplot(df[clean_col], bins=5, kde=True, ax=ax)
            ax.set_xlabel("Scale")
            ax.set_ylabel("Count")
            ax.set_facecolor("#f0f0f0")
            st.pyplot(fig)

        # Show individual responses
        with st.expander("👥 View individual ratings"):
            for i, val in enumerate(df[clean_col]):
                st.write(f"👤 Respondent {i+1}: **{val}**")

    # ========== 🤷‍♂️ Unsupported Data Type ==========
    else:
        st.info("Unsupported data type for this column.")
