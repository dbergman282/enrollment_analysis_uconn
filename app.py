import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Academic Plan Summary", layout="wide")

# Title
st.title("🎓 Academic Plan Summary Explorer")

# Sidebar
st.sidebar.header("📁 Upload Your Excel File")
uploaded_file = st.sidebar.file_uploader("Choose an Excel file (.xlsx)", type=["xlsx"])

# Predefined default programs
default_programs = [
    "Busn Analytics and Proj Man MS",
    "Fin and Entrprise Risk Mgmt MS",
    "Financial Technology MS",
    "Accounting MS",
    "Human Resource Management MS",
    "Social Resp and Imp MS",
    "Supply Chain Management MS"
]

# Load and cache Excel data
@st.cache_data(show_spinner=False)
def load_data(file):
    return pd.read_excel(file, skiprows=2)

if uploaded_file:
    try:
        df = load_data(uploaded_file)

        # Validate required column
        if 'Academic Plan Description' not in df.columns:
            st.error("❌ Column 'Academic Plan Description' not found in the uploaded file.")
        else:
            # Get all plan descriptions
            all_plans = sorted(df['Academic Plan Description'].dropna().unique())

            # Sidebar multiselect with custom CSS to reduce height
            st.sidebar.markdown("### 🎯 Filter by Program")
            st.markdown("""
                <style>
                    .stMultiSelect [data-baseweb="tag"] {
                        margin: 1px;
                        padding-top: 3px;
                        padding-bottom: 3px;
                    }
                </style>
            """, unsafe_allow_html=True)

            selected_plans = st.sidebar.multiselect(
                "Select Academic Plan Descriptions:",
                options=all_plans,
                default=[p for p in default_programs if p in all_plans],
            )

            # Filter data
            filtered_df = df[df['Academic Plan Description'].isin(selected_plans)]

            # Show summary
            st.subheader("📊 Record Counts by Academic Plan Description")
            summary_df = (
                filtered_df['Academic Plan Description']
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Academic Plan Description", "Academic Plan Description": "Count"})
            )

            st.dataframe(summary_df, use_container_width=True)

            # Pivot table: Rows = Admit Term, Columns = Academic Plan Description, Values = Count
            if 'Admit Term' in filtered_df.columns:
                st.subheader("📅 Record Count by Admit Term and Academic Plan Description")
                pivot_df = pd.pivot_table(
                    filtered_df,
                    index='Admit Term',
                    columns='Academic Plan Description',
                    aggfunc='size',
                    fill_value=0
                )
                st.dataframe(pivot_df, use_container_width=True)
            else:
                st.warning("⚠️ Column 'Admit Term' not found in the data.")

            # Pivot table: Rows = Admit Term, Columns = Academic Plan Description, Values = Count
            if 'Admit Term' in filtered_df.columns:
                st.subheader("📅 Record Count by Admit Term and Academic Plan Description")

                # Create a custom sort key for Admit Term
                def admit_term_sort_key(term):
                    if pd.isna(term): return (9999, 3)  # Put NaNs at the bottom
                    parts = term.split()
                    if len(parts) != 2: return (9999, 3)  # Unrecognized format
                    season_order = {"Spring": 1, "Summer": 2, "Fall": 3}
                    season, year = parts[0], parts[1]
                    return (int(year), season_order.get(season, 4))

                # Clean and sort Admit Term values
                filtered_df['Admit Term Sort Key'] = filtered_df['Admit Term'].apply(admit_term_sort_key)
                filtered_df = filtered_df.sort_values('Admit Term Sort Key')

                # Create pivot table
                pivot_df = pd.pivot_table(
                    filtered_df,
                    index='Admit Term',
                    columns='Academic Plan Description',
                    aggfunc='size',
                    fill_value=0
                )

                # Reorder index using sort key
                pivot_df = pivot_df.loc[sorted(pivot_df.index, key=admit_term_sort_key)]

                st.dataframe(pivot_df, use_container_width=True)
            else:
                st.warning("⚠️ Column 'Admit Term' not found in the data.")


    except Exception as e:
        st.error(f"❌ Error reading the file: {e}")
else:
    st.info("⬅️ Please upload an Excel file from the sidebar to get started.")
