import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# Apply consistent visual styling
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
    </style>
""", unsafe_allow_html=True)

st.title("💎 Survey Summary & Insights")

response_dir = "responses"
csv_files = [f for f in os.listdir(response_dir) if f.endswith(".csv")]

if not csv_files:
    st.warning("No response files found.")
    st.stop()

selected_csv = st.selectbox("Select a form to view responses:", csv_files)
df = pd.read_csv(os.path.join(response_dir, selected_csv))

st.subheader(f"📋 Showing {len(df)} responses from: `{selected_csv}`")

# Download results button
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)
st.download_button("📥 Download Full Results (CSV)", csv_buffer.getvalue(), file_name=selected_csv, mime="text/csv")

# Clean column names
clean_columns = {col: col.replace(":", "").strip() for col in df.columns}
df = df.rename(columns=clean_columns)

for raw_col, clean_col in zip(clean_columns.keys(), clean_columns.values()):
    st.markdown(f"### ✏️ {raw_col}")

    if df[clean_col].dtype == object:
        sort_order = st.radio(
            f"Sort responses for '{raw_col}':",
            ["Most popular", "Least popular", "Alphabetical"],
            key=f"sort_{clean_col}",
            horizontal=True
        )

        counts = df[clean_col].value_counts().reset_index()
        counts.columns = ["Category", "Count"]

        if sort_order == "Least popular":
            counts = counts.sort_values("Count")
        elif sort_order == "Alphabetical":
            counts = counts.sort_values("Category")

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

        if len(counts) > 5:
            with st.expander("📖 See all responses"):
                for _, row in counts.iterrows():
                    pct = (row['Count'] / len(df)) * 100
                    st.write(f"**{int(row['Count'])}** → {row['Category']} (**{pct:.1f}%**)")

        if len(counts) > 1:
            with st.expander("🥧 Show Pie Chart"):
                fig, ax = plt.subplots()
                ax.pie(counts['Count'], labels=counts['Category'], autopct='%1.1f%%', startangle=140, textprops={'color': 'white'})
                ax.axis('equal')
                fig.patch.set_facecolor('#243b55')
                st.pyplot(fig)

    elif pd.api.types.is_numeric_dtype(df[clean_col]):
        avg = df[clean_col].mean()
        st.write(f"📈 Average rating: **{avg:.2f}**")

        with st.expander("📊 View histogram"):
            fig, ax = plt.subplots()
            sns.histplot(df[clean_col], bins=5, kde=True, ax=ax)
            ax.set_xlabel("Scale")
            ax.set_ylabel("Count")
            ax.set_facecolor("#f0f0f0")
            st.pyplot(fig)

        with st.expander("👥 View individual ratings"):
            for i, val in enumerate(df[clean_col]):
                st.write(f"👤 Respondent {i+1}: **{val}**")

    else:
        st.info("Unsupported data type for this column.")
