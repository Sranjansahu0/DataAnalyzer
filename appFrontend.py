import streamlit as st
import requests
import pandas as pd
import numpy as np

API_URL = "http://127.0.0.1:8000"

st.title("Data Analyzer Web App")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("## Preview")
    st.dataframe(df.head())

    column = st.selectbox("Select column to Analyze", df.columns)

    if st.button("Analyze"):
        data_json = df.replace({np.nan: None}).to_dict(orient="records")
        response = requests.post(API_URL + "/summary", json = {"data":data_json, "column":column})

        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(f"Statistics of column: {column}")
                st.json(result)

    if st.button("Show Missing Data"):
        data_json = df.replace({np.nan: None}).to_dict(orient = "records")
        response = requests.post(API_URL + "/missing", json = {"data":data_json, "column":column})
        st.write("## Missing Value Summary")
        st.json(response.json())

    if st.button("Find Correlation"):
        data_json = df.replace({np.nan: None}).to_dict(orient = "records")
        response = requests.post(API_URL + "/correlation", json = {"data": data_json})

        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                st.error(result["error"])
            else:
                correlation = result.get("correlation", result)
                corr_df = pd.DataFrame(correlation)
                st.write("### correlation matrix")
                st.dataframe(corr_df, use_container_width = True)
        else:
            st.error("Error fetching correlation matrix")
