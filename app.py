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

            # Sidebar multiselect
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

            # Sort function for Admit Term
            def admit_term_sort_key(term):
                if pd.isna(term): return (9999, 3)
                parts = term.split()
                if len(parts) != 2: return (9999, 3)
                season_order = {"Spring": 1, "Summer": 2, "Fall": 3}
                season, year = parts[0], parts[1]
                return (int(year), season_order.get(season, 4))

            # Main Pivot Table
            if 'Admit Term' in filtered_df.columns:
                with st.expander("📅 Record Count by Admit Term and Academic Plan Description"):
                    filtered_df['Admit Term Sort Key'] = filtered_df['Admit Term'].apply(admit_term_sort_key)
                    filtered_df = filtered_df.sort_values('Admit Term Sort Key')
                    pivot_df = pd.pivot_table(
                        filtered_df,
                        index='Admit Term',
                        columns='Academic Plan Description',
                        aggfunc='size',
                        fill_value=0
                    )
                    pivot_df = pivot_df.loc[sorted(pivot_df.index, key=admit_term_sort_key)]
                    st.dataframe(pivot_df, use_container_width=True)
            else:
                st.warning("⚠️ Column 'Admit Term' not found in the data.")

            # Map Visa Type to Student Type
            filtered_df['Student Type'] = filtered_df['Visa Type'].apply(
                lambda x: 'International' if str(x).strip().upper() == 'F1' else 'Domestic'
            )

            # Student Type Summary
            with st.expander("🌍 Student Type Summary by Academic Plan"):
                student_type_summary = pd.pivot_table(
                    filtered_df,
                    index='Student Type',
                    columns='Academic Plan Description',
                    aggfunc='size',
                    fill_value=0
                )
                st.dataframe(student_type_summary, use_container_width=True)

            # International Students Pivot
            with st.expander("🌍 International Students by Admit Term and Academic Plan"):
                intl_df = filtered_df[filtered_df['Student Type'] == 'International']
                if not intl_df.empty:
                    intl_df = intl_df.copy()
                    intl_df['Admit Term Sort Key'] = intl_df['Admit Term'].apply(admit_term_sort_key)
                    intl_df = intl_df.sort_values('Admit Term Sort Key')
                    intl_pivot = pd.pivot_table(
                        intl_df,
                        index='Admit Term',
                        columns='Academic Plan Description',
                        aggfunc='size',
                        fill_value=0
                    )
                    intl_pivot = intl_pivot.loc[sorted(intl_pivot.index, key=admit_term_sort_key)]
                    st.dataframe(intl_pivot, use_container_width=True)
                else:
                    st.info("No international students found in the selected data.")

            # Domestic Students Pivot
            with st.expander("🏠 Domestic Students by Admit Term and Academic Plan"):
                dom_df = filtered_df[filtered_df['Student Type'] == 'Domestic']
                if not dom_df.empty:
                    dom_df = dom_df.copy()
                    dom_df['Admit Term Sort Key'] = dom_df['Admit Term'].apply(admit_term_sort_key)
                    dom_df = dom_df.sort_values('Admit Term Sort Key')
                    dom_pivot = pd.pivot_table(
                        dom_df,
                        index='Admit Term',
                        columns='Academic Plan Description',
                        aggfunc='size',
                        fill_value=0
                    )
                    dom_pivot = dom_pivot.loc[sorted(dom_pivot.index, key=admit_term_sort_key)]
                    st.dataframe(dom_pivot, use_container_width=True)
                else:
                    st.info("No domestic students found in the selected data.")

            # Campus Summary by Academic Plan
            with st.expander("🏫 Campus Summary by Academic Plan"):
                if 'Campus' in filtered_df.columns:
                    campus_df = filtered_df.copy()
                    campus_pivot = pd.pivot_table(
                        campus_df,
                        index='Campus',
                        columns='Academic Plan Description',
                        aggfunc='size',
                        fill_value=0
                    )
                    st.dataframe(campus_pivot, use_container_width=True)
                else:
                    st.info("Column 'Campus' not found in the selected data.")

            # 🔄 Custom Pivot Table Builder
            with st.expander("🛠️ Build Your Own Pivot Table"):
                st.markdown("Use the dropdowns below to choose your row and column variables.")

                available_columns = filtered_df.columns.tolist()

                row_choice = st.selectbox("Select row variable:", available_columns, index=available_columns.index("Admit Term") if "Admit Term" in available_columns else 0)
                col_choice = st.selectbox("Select column variable:", available_columns, index=available_columns.index("Academic Plan Description") if "Academic Plan Description" in available_columns else 1)

                if row_choice and col_choice:
                    # --- Count Pivot Table ---
                    st.markdown("### 🔢 Count of Records")
                    pivot_count = pd.pivot_table(
                        filtered_df,
                        index=row_choice,
                        columns=col_choice,
                        aggfunc='size',
                        fill_value=0
                    )

                    if row_choice == "Admit Term":
                        pivot_count = pivot_count.loc[sorted(pivot_count.index, key=admit_term_sort_key)]

                    st.dataframe(pivot_count, use_container_width=True)

                    # --- Sum of Enrolled Credits Pivot Table ---
                    if 'Enrolled Credits' in filtered_df.columns:
                        st.markdown("### 🎓 Sum of Enrolled Credits")
                        pivot_credits = pd.pivot_table(
                            filtered_df,
                            index=row_choice,
                            columns=col_choice,
                            values='Enrolled Credits',
                            aggfunc='sum',
                            fill_value=0
                        )

                        if row_choice == "Admit Term":
                            pivot_credits = pivot_credits.loc[sorted(pivot_credits.index, key=admit_term_sort_key)]

                        st.dataframe(pivot_credits, use_container_width=True)
                    else:
                        st.warning("⚠️ Column 'Enrolled Credits' not found in the data.")

            # 💰 Revenue Estimator by Cost Per Credit and Future Potential
            with st.expander("💰 Estimated Revenue by Academic Plan"):
                st.markdown("Enter cost per credit and required credits for each academic plan. Revenue is calculated as `Enrolled Credits × Cost per Credit`. Future revenue is based on remaining credits times cost.")

                # Predefined defaults
                fallback_cost = 1200
                fallback_required_credits = 33

                default_costs = {
                    "Busn Analytics and Proj Man MS": 1200,
                    "Fin and Entrprise Risk Mgmt MS": 1500,
                    "Financial Technology MS": 1500,
                    "Accounting MS": 1125,
                    "Human Resource Management MS": 1200,
                    "Social Resp and Imp MS": 1200,
                    "Supply Chain Management MS": 1200
                }

                default_required_credits = {
                    "Busn Analytics and Proj Man MS": 37,
                    "Fin and Entrprise Risk Mgmt MS": 36,
                    "Financial Technology MS": 36,
                    "Accounting MS": 30,
                    "Human Resource Management MS": 33,
                    "Social Resp and Imp MS": 30,
                    "Supply Chain Management MS": 30
                }

                available_plans = sorted(filtered_df['Academic Plan Description'].dropna().unique())
                cost_inputs = {}
                credits_required_inputs = {}

                st.markdown("#### 💵 Cost per Credit & 🎓 Credits Required (Editable)")
                for plan in available_plans:
                    default_cost = default_costs.get(plan, fallback_cost)
                    default_required = default_required_credits.get(plan, fallback_required_credits)

                    col1, col2 = st.columns(2)
                    with col1:
                        cost_inputs[plan] = st.number_input(
                            f"{plan} – Cost per Credit", min_value=0, max_value=5000,
                            value=default_cost, step=25, key=f"cost_{plan}"
                        )
                    with col2:
                        credits_required_inputs[plan] = st.number_input(
                            f"{plan} – Total Credits Required", min_value=0, max_value=100,
                            value=default_required, step=1, key=f"credits_required_{plan}"
                        )

                # Calculate revenue and future revenue
                filtered_df['Cost Per Credit'] = filtered_df['Academic Plan Description'].map(cost_inputs)
                filtered_df['Credits Required'] = filtered_df['Academic Plan Description'].map(credits_required_inputs)

                # Enrolled revenue
                filtered_df['Revenue'] = filtered_df['Enrolled Credits'] * filtered_df['Cost Per Credit']

                # Future revenue
                if 'STFACT_TOT_CUMULATIVE' in filtered_df.columns:
                    filtered_df['Credits Remaining'] = (
                        filtered_df['Credits Required'] - filtered_df['STFACT_TOT_CUMULATIVE']
                    ).clip(lower=0)

                    filtered_df['Future Revenue'] = (
                        filtered_df['Credits Remaining'] * filtered_df['Cost Per Credit']
                    )
                else:
                    st.warning("⚠️ Column 'STFACT_TOT_CUMULATIVE' not found. Future revenue cannot be calculated.")
                    filtered_df['Future Revenue'] = 0

                # Row dropdown
                row_fields = [col for col in filtered_df.columns if col != 'Academic Plan Description']
                row_choice = st.selectbox("Select row variable for revenue tables:", row_fields, index=row_fields.index("Admit Term") if "Admit Term" in row_fields else 0)

                # Enrolled Revenue Table
                st.markdown("### 📈 Estimated Revenue Table (Current Enrolled Credits × Cost)")
                revenue_pivot = pd.pivot_table(
                    filtered_df,
                    index=row_choice,
                    columns='Academic Plan Description',
                    values='Revenue',
                    aggfunc='sum',
                    fill_value=0
                )
                if row_choice == "Admit Term":
                    revenue_pivot = revenue_pivot.loc[sorted(revenue_pivot.index, key=admit_term_sort_key)]
                st.dataframe(revenue_pivot.applymap(lambda x: f"${x:,.0f}"), use_container_width=True)

                # Future Revenue Table
                st.markdown("### 🧮 Future Revenue Table (Remaining Credits × Cost)")
                future_pivot = pd.pivot_table(
                    filtered_df,
                    index=row_choice,
                    columns='Academic Plan Description',
                    values='Future Revenue',
                    aggfunc='sum',
                    fill_value=0
                )
                if row_choice == "Admit Term":
                    future_pivot = future_pivot.loc[sorted(future_pivot.index, key=admit_term_sort_key)]
                st.dataframe(future_pivot.applymap(lambda x: f"${x:,.0f}"), use_container_width=True)

                # Flat table
                st.markdown("### 📄 Total Future Revenue by Group (Flat Table)")
                flat_group = st.selectbox("Group future revenue by:", row_fields, index=row_fields.index("Admit Term") if "Admit Term" in row_fields else 0, key="flat_future_group")

                flat_table = (
                    filtered_df
                    .groupby(flat_group)
                    .agg(Total_Future_Revenue=('Future Revenue', 'sum'))
                    .reset_index()
                    .sort_values(by=flat_group)
                )
                flat_table['Total_Future_Revenue'] = flat_table['Total_Future_Revenue'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(flat_table, use_container_width=True)



    
    except Exception as e:
        st.error(f"❌ Error reading the file: {e}")
else:
    st.info("⬅️ Please upload an Excel file from the sidebar to get started.")
