import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Academic Plan Summary", layout="wide")

# Title
st.title("🎓 Academic Plan Summary Explorer")

# Sidebar
st.sidebar.header("📁 Upload Your Excel File")
uploaded_file = st.sidebar.file_uploader("Choose an Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Read Excel skipping the first 2 rows
        df = pd.read_excel(uploaded_file, skiprows=2)

        # Check necessary columns
        if 'Academic Plan' not in df.columns or 'Academic Plan Description' not in df.columns:
            st.error("❌ Missing required columns: 'Academic Plan' and/or 'Academic Plan Description'")
        else:
            # Filter options
            all_plans = sorted(df['Academic Plan'].dropna().unique())
            selected_plans = st.sidebar.multiselect("Filter by Academic Plan(s)", options=all_plans, default=all_plans)

            # Apply filter
            filtered_df = df[df['Academic Plan'].isin(selected_plans)]

            # Show summary
            st.subheader("📊 Record Counts by Academic Plan Description")
            summary_df = (
                filtered_df['Academic Plan Description']
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Academic Plan Description", "Academic Plan Description": "Count"})
            )

            st.dataframe(summary_df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error reading the file: {e}")
else:
    st.info("⬅️ Please upload an Excel file from the sidebar to get started.")
