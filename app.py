import streamlit as st
from utils.file_loader import load_dataset, FileLoadError
from tools.data_tools import profile_dataset

st.set_page_config(page_title="InsightFlow", page_icon="📊", layout="wide")

st.title("📊 InsightFlow")
st.caption("Your AI data analyst. Upload a dataset and ask questions in plain English.")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = load_dataset(uploaded_file)
        st.success(f"Loaded **{uploaded_file.name}**: {df.shape[0]} rows × {df.shape[1]} columns")

        profile = profile_dataset(df)

        st.subheader("Dataset Profile")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", profile["rows"])
        c2.metric("Columns", profile["columns"])
        c3.metric("Duplicate rows", profile["duplicate_rows"])
        c4.metric("Columns with missing values", len(profile["missing_values"]))

        left, right = st.columns(2)
        with left:
            st.markdown("**Numeric columns**")
            st.write(profile["numeric_columns"] or "None")
            st.markdown("**Date columns**")
            st.write(profile["date_columns"] or "None")
        with right:
            st.markdown("**Categorical columns**")
            st.write(profile["categorical_columns"] or "None")
            st.markdown("**Missing values**")
            st.write(profile["missing_values"] or "None")

        with st.expander("Data types"):
            st.json(profile["dtypes"])

        if profile["numeric_stats"]:
            with st.expander("Basic statistics"):
                st.dataframe(df[profile["numeric_columns"]].describe().round(2))

        st.subheader("Preview")
        st.dataframe(df.head(10), use_container_width=True)
    except FileLoadError as e:
        st.error(str(e))
else:
    st.info("Upload a file to get started.")