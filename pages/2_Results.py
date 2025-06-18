import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

# Apply consistent visual styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #4e54c8, #8f94fb);
        color: white;
    }
    h1, h2, h3, p, label {
        transition: transform 0.2s ease-in-out;
    }
    h1:hover, h2:hover, h3:hover, p:hover, label:hover {
        transform: scale(1.05);
    }
    .stButton button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 5px;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Survey Summary & Visualisation")

response_dir = "responses"
csv_files = [f for f in os.listdir(response_dir) if f.endswith(".csv")]

if not csv_files:
    st.warning("No response files found.")
    st.stop()

selected_csv = st.selectbox("Select a form to view responses:", csv_files)
df = pd.read_csv(os.path.join(response_dir, selected_csv))

st.subheader(f"🗂 Showing {len(df)} responses from: `{selected_csv}`")

clean_columns = {col: col.replace(":", "").strip() for col in df.columns}
df = df.rename(columns=clean_columns)

for raw_col, clean_col in zip(clean_columns.keys(), clean_columns.values()):
    st.markdown(f"### {raw_col}")

    if df[clean_col].dtype == object:
        counts = df[clean_col].value_counts().reset_index()
        counts.columns = ["Category", "Count"]

        for _, row in counts.iterrows():
            st.write(f"**{int(row['Count'])}** people responded with: *{row['Category']}*")

        if len(counts) > 1:
            with st.expander("📊 View chart for this question"):
                chart = alt.Chart(counts).mark_bar().encode(
                    x=alt.X("Category", sort="-y"),
                    y="Count",
                    color=alt.Color("Category", legend=None)
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)

    elif pd.api.types.is_numeric_dtype(df[clean_col]):
        avg = df[clean_col].mean()
        st.write(f"Average rating: **{avg:.2f}**")

        with st.expander("📊 View distribution chart"):
            fig, ax = plt.subplots()
            sns.histplot(df[clean_col], bins=5, kde=True, ax=ax)
            ax.set_xlabel("Scale")
            ax.set_ylabel("Count")
            st.pyplot(fig)

    else:
        st.write("Unsupported data type.")
