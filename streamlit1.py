import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Page setup
st.set_page_config(page_title="💿 Data sweeper", layout="wide")
st.title("💿 Data sweeper")
st.markdown("Transform your CSV or Excel files with built-in data cleaning and visualization features!")

# File uploader
uploaded_files = st.file_uploader("Upload one or more files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

# If files are uploaded
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_ext = os.path.splitext(uploaded_file.name)[-1].lower()

        # Read file based on extension
        try:
            if file_ext == ".csv":
                df = pd.read_csv(uploaded_file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(uploaded_file)
            else:
                st.error(f"Unsupported file format: {file_ext}")
                continue
        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {e}")
            continue

        # File info
        st.write(f"**File Name:** {uploaded_file.name}")
        st.write(f"**File Size:** {uploaded_file.size / 1024:.2f} KB")

        # Preview data
        st.write("🔎 Preview (Top Rows)")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🛠 Data Cleaning Options")
        if st.checkbox(f"Enable cleaning for {uploaded_file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {uploaded_file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("Duplicates removed successfully.")

            with col2:
                if st.button(f"Fill Missing Values in {uploaded_file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("Missing numeric values filled with column averages.")

            # Column selection
            st.subheader("🎯 Select Columns to Keep")
            if not df.empty and len(df.columns) > 0:
                selected_columns = st.multiselect(
                    f"Choose Columns for {uploaded_file.name}",
                    options=df.columns.tolist(),
                    default=df.columns.tolist()
                )
                df = df[selected_columns]
            else:
                st.warning("No columns available to select.")

            # Visualization
            st.subheader("📊 Visualize Numeric Columns")
            if st.checkbox(f"Show Bar Chart for {uploaded_file.name}"):
                numeric_data = df.select_dtypes(include="number")
                if not numeric_data.empty:
                    st.bar_chart(numeric_data.iloc[:, :2])
                else:
                    st.info("No numeric columns available to plot.")

            # File conversion
            st.subheader("🔄 Convert File Format")
            convert_to = st.radio(f"Convert {uploaded_file.name} to:", ["CSV", "Excel"], key=uploaded_file.name)

            if st.button(f"Convert {uploaded_file.name}"):
                buffer = BytesIO()

                if convert_to == "CSV":
                    df.to_csv(buffer, index=False)
                    new_filename = uploaded_file.name.replace(file_ext, ".csv")
                    mime = "text/csv"
                else:
                    df.to_excel(buffer, index=False)
                    new_filename = uploaded_file.name.replace(file_ext, ".xlsx")
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)
                st.download_button(
                    label=f"⬇ Download {uploaded_file.name} as {convert_to}",
                    data=buffer,
                    file_name=new_filename,
                    mime=mime
                )

        st.success("🎉 Done processing this file!")
