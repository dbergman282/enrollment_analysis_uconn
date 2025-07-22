import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Academic Plan Summary", layout="wide")

# Custom dark theme styling
st.markdown("""
    <style>
        /* Set dark background for whole app */
        .stApp {
            background-color: #121212;
            color: #E0E0E0;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #1e1e1e;
        }

        /* Headers */
        .title {
            color: #4FC3F7;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 0.5em;
        }
        .subheader {
            color: #81D4FA;
            font-size: 1.5em;
            margin-top: 2em;
            margin-bottom: 1em;
        }

        /* Multiselect background + text */
        div[data-baseweb="select"] {
            background-color: #2a2a2a;
            color: #E0E0E0;
        }
        div[data-baseweb="select"] * {
            color: #E0E0E0 !important;
        }

        /* Fix white border on focus */
        .css-13cymwt-control, .css-t3ipsp-control {
            background-color: #2a2a2a !important;
            border-color: #444 !important;
        }

        /* DataFrame */
        div[data-testid="stDataFrame"] {
            background-color: #1e1e1e;
        }

        /* Remove top white bar padding */
        header, .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title">🎓 Academic Plan Summary Explorer</div>', unsafe_allow_html=True)

# Sidebar upload
st.sidebar.header("📁 Upload Excel File")
uploaded_file = st.sidebar.file_uploader("Upload .xlsx", type=["xlsx"])

if uploaded_file:
    try:
        # Read data skipping first 2 rows
        df = pd.read_excel(uploaded_file, skiprows=2)

        if 'Academic Plan' not in df.columns or 'Academic Plan Description' not in df.columns:
            st.error("❌ Missing required columns: 'Academic Plan' and/or 'Academic Plan Description'")
        else:
            # Sidebar filter
            st.sidebar.header("🎯 Filter by Academic Plan")
            all_plans = sorted(df['Academic Plan'].dropna().unique())
            selected_plans = st.sidebar.multiselect("Select Academic Plan(s)", options=all_plans, default=all_plans)

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

            # Style DataFrame to match dark theme
            styled_df = summary_df.style.set_properties(**{
                'background-color': '#1e1e1e',
                'color': '#E0E0E0',
                'border-color': '#333333'
            })

            st.dataframe(styled_df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("⬅️ Upload an Excel file using the sidebar to begin.")
