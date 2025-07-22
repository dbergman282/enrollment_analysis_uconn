import streamlit as st
import pandas as pd

# Set dark mode explicitly in config
st.set_page_config(page_title="Academic Plan Summary", layout="wide")

# Apply consistent dark styling
st.markdown("""
    <style>
        /* App background */
        .stApp {
            background-color: #121212;
            color: #E0E0E0;
        }

        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #1e1e1e;
        }

        /* Headers */
        .title {
            color: #4FC3F7;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 1em;
        }
        .subheader {
            color: #81D4FA;
            font-size: 1.5em;
            margin-top: 1.5em;
        }

        /* DataFrame scroll bar */
        div[data-testid="stDataFrame"] > div {
            background-color: #1e1e1e;
        }

        /* Table text */
        .css-1v0ambj, .css-1d391kg, .css-1v0mbdj {
            color: #E0E0E0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title">🎓 Academic Plan Summary Explorer</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Upload Your Excel File")
uploaded_file = st.sidebar.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Read data, skip first two rows
        df = pd.read_excel(uploaded_file, skiprows=2)

        if 'Academic Plan' not in df.columns or 'Academic Plan Description' not in df.columns:
            st.error("❌ The uploaded file must contain 'Academic Plan' and 'Academic Plan Description' columns.")
        else:
            # Sidebar multiselect
            all_plans = sorted(df['Academic Plan'].dropna().unique())
            selected_plans = st.sidebar.multiselect("Filter by Academic Plan(s)", options=all_plans, default=all_plans)

            # Filter data
            filtered_df = df[df['Academic Plan'].isin(selected_plans)]

            # Summary
            st.markdown('<div class="subheader">📊 Records by Academic Plan Description</div>', unsafe_allow_html=True)
            summary_df = (
                filtered_df['Academic Plan Description']
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Academic Plan Description", "Academic Plan Description": "Count"})
            )

            # Style summary table
            styled = summary_df.style.set_properties(**{
                'background-color': '#1e1e1e',
                'color': '#E0E0E0',
                'border-color': '#333333'
            })

            st.dataframe(styled, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("📂 Upload an Excel file using the sidebar to begin.")
