import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000"

st.title("Data Analyzer Web App")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("## Preview")
    st.dataframe(df.head())

    # Store correlation matrix so it doesn't disappear on re-run
    if "corr_matrix" not in st.session_state:
        st.session_state.corr_matrix = None

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
            st.write("Correlation Analysis")
            st.write("### 📊 Data Visualization")

            # Convert uploaded data to JSON form for backend
            data_json = df.replace({np.nan: None}).to_dict(orient="records")  # Convert NaN to None so FastAPI accepts it

            response = requests.post(API_URL + "/correlation", json={"data": data_json})  # Call backend correlation API

            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.session_state.corr_matrix = pd.DataFrame(result["correlation"])
                    st.success("Correlation matrix generated successfully")
                    #correlation = result.get("correlation", result)
                    #corr_df = pd.DataFrame(correlation)
                    #st.write("### correlation matrix")
                    #st.dataframe(corr_df, use_container_width = True)'''
            else:
                st.error("Error fetching correlation matrix")
                #corr_df = None

    #---Show visulisation only if correlation exist---
    if st.session_state.corr_matrix is not None:
        corr_df = st.session_state.corr_matrix

        st.write("## correlation matrix table")
        st.dataframe(corr_df, use_container_width = True)

        st.write("---")
        st.write("## Visualization Options")
        vis_type = st.selectbox("Choose visualisation Type",["Heatmap","Scatter Plot"])

        # heatmap
        if vis_type == "Heatmap":
            st.write("### Heatmap")
            fig,ax = plt.subplots()
            cax = ax.matshow(corr_df)
            fig.colorbar(cax)
            ax.set_xticks(range(len(corr_df.columns)))
            ax.set_yticks(range(len(corr_df.columns)))
            ax.set_xticklabels(corr_df.columns, rotation = 45)
            ax.set_yticklabels(corr_df.columns)
            st.pyplot(fig)

        #Scatter plot
        elif vis_type == "Scatter Plot":
            st.write("### Scatter Plot between between two numeric columns")
            numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()

            #Dropdowns for X and Y axes
            x_col = st.selectbox("Select X-axis", numeric_cols)
            y_col = st.selectbox("Select Y-axis", numeric_cols)

            fig,ax = plt.subplots()
            ax.scatter(df[x_col],df[y_col])
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"{y_col} vs {x_col}")
            st.pyplot(fig)
