import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Academic Plan Analyzer", layout="wide")

# Custom styling
st.markdown(
    """
    <style>
        body {
            background-color: #1e1e1e;
            color: white;
        }
        .css-1d391kg, .css-1v0mbdj {
            color: white !important;
        }
        .stApp {
            background-color: #1e1e1e;
        }
        .title {
            color: #4FC3F7;
            font-size: 2.5em;
            font-weight: bold;
        }
        .subheader {
            color: #81D4FA;
            font-size: 1.5em;
            margin-top: 2em;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown('<div class="title">🎓 Academic Plan Summary Explorer</div>', unsafe_allow_html=True)

# Sidebar file upload
st.sidebar.header("Upload Your Excel File")
uploaded_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, skiprows=2)

        if 'Academic Plan' not in df.columns or 'Academic Plan Description' not in df.columns:
            st.error("Missing required columns: 'Academic Plan' and/or 'Academic Plan Description'")
        else:
            # Sidebar filter
            st.sidebar.header("Filter by Academic Plan")
            unique_plans = df['Academic Plan'].dropna().unique()
            selected_plan = st.sidebar.selectbox("Choose an Academic Plan", ["All"] + sorted(unique_plans.tolist()))

            if selected_plan != "All":
                df = df[df['Academic Plan'] == selected_plan]

            # Display record count
            st.markdown('<div class="subheader">📊 Dataset Overview</div>', unsafe_allow_html=True)
            st.write(f"Showing **{len(df):,} records** for Academic Plan: `{selected_plan}`")

            # Show summary by Academic Plan Description
            st.markdown('<div class="subheader">🔍 Records by Academic Plan Description</div>', unsafe_allow_html=True)
            summary_df = (
                df['Academic Plan Description']
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Academic Plan Description", "Academic Plan Description": "Count"})
            )
            st.dataframe(summary_df, use_container_width=True)

            # Show raw preview
            st.markdown('<div class="subheader">📑 Data Preview</div>', unsafe_allow_html=True)
            st.dataframe(df.head(20), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("Upload an Excel file from the sidebar to begin.")
