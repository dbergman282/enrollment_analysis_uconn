import streamlit as st
import pandas as pd

st.title("Excel Summary: Academic Plan Description")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Skip first two rows
        df = pd.read_excel(uploaded_file, skiprows=2)

        # Display the dataframe shape
        st.write(f"Dataset contains {df.shape[0]:,} rows and {df.shape[1]:,} columns.")

        # Show the first few rows
        st.subheader("Preview of the Data")
        st.dataframe(df.head())

        # Check if the column exists
        if 'Academic Plan Description' in df.columns:
            st.subheader("Records per Academic Plan Description")
            counts = df['Academic Plan Description'].value_counts().reset_index()
            counts.columns = ['Academic Plan Description', 'Count']
            st.dataframe(counts)
        else:
            st.warning("Column 'Academic Plan Description' not found in the file.")

    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Please upload an Excel file to begin.")
