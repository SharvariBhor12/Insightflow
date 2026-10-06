import streamlit as st
from utils.file_loader import load_dataset, FileLoadError

st.set_page_config(page_title="InsightFlow", page_icon="📊", layout="wide")

st.title("📊 InsightFlow")
st.caption("Your AI data analyst. Upload a dataset and ask questions in plain English.")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = load_dataset(uploaded_file)
        st.success(f"Loaded **{uploaded_file.name}**: {df.shape[0]} rows × {df.shape[1]} columns")
        st.subheader("Preview")
        st.dataframe(df.head(10), use_container_width=True)
    except FileLoadError as e:
        st.error(str(e))
else:
    st.info("Upload a file to get started.")