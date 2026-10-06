import pandas as pd


class FileLoadError(Exception):
    """Raised when an uploaded file cannot be loaded."""


def load_dataset(uploaded_file) -> pd.DataFrame:
    """Load a CSV or Excel upload into a DataFrame."""
    name = uploaded_file.name.lower()

    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            raise FileLoadError("Unsupported file type. Please upload a CSV or Excel file.")
    except FileLoadError:
        raise
    except Exception as e:
        raise FileLoadError(f"Could not read the file: {e}")

    if df.empty:
        raise FileLoadError("The file is empty. Please upload a dataset with data.")

    return df