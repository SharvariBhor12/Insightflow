import streamlit as st
from utils.file_loader import load_dataset, FileLoadError
from utils.llm import LLMError
from tools.data_tools import profile_dataset
from agents.simple_qa import simple_answer

st.set_page_config(page_title="InsightFlow", page_icon="📊", layout="wide")

st.title("📊 InsightFlow")
st.caption("Your AI data analyst. Upload a dataset and ask questions in plain English.")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = load_dataset(uploaded_file)
        st.success(f"Loaded **{uploaded_file.name}**: {df.shape[0]} rows × {df.shape[1]} columns")

        profile = profile_dataset(df)

        with st.expander("Dataset Profile", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rows", profile["rows"])
            c2.metric("Columns", profile["columns"])
            c3.metric("Duplicate rows", profile["duplicate_rows"])
            c4.metric("Columns with missing values", len(profile["missing_values"]))

            left, right = st.columns(2)
            with left:
                st.markdown("**Numeric columns**")
                st.write(", ".join(profile["numeric_columns"]) or "None")
                st.markdown("**Date columns**")
                st.write(", ".join(profile["date_columns"]) or "None")
            with right:
                st.markdown("**Categorical columns**")
                st.write(", ".join(profile["categorical_columns"]) or "None")
                st.markdown("**Missing values**")
                st.write(profile["missing_values"] or "None")

        with st.expander("Preview"):
            st.dataframe(df.head(10), use_container_width=True)

        st.subheader("Ask a question")
        question = st.text_input("Example: What is the total revenue?")

        if st.button("Ask") and question.strip():
            with st.spinner("Thinking..."):
                try:
                    answer = simple_answer(question, profile)
                    st.markdown("**Plain LLM answer (no tools):**")
                    st.write(answer)
                except LLMError as e:
                    st.error(str(e))
    except FileLoadError as e:
        st.error(str(e))
else:
    st.info("Upload a file to get started.")