import pandas as pd


def detect_date_columns(df: pd.DataFrame) -> list:
    """Find columns that look like dates (already datetime, or text that parses as dates)."""
    date_cols = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_cols.append(col)
        elif df[col].dtype == "object" or pd.api.types.is_string_dtype(df[col]):
            sample = df[col].dropna().head(20)
            if sample.empty:
                continue
            parsed = pd.to_datetime(sample, errors="coerce")
            if parsed.notna().mean() >= 0.9:
                date_cols.append(col)
    return date_cols


def profile_dataset(df: pd.DataFrame) -> dict:
    """Return a structured summary of the dataset."""
    date_cols = detect_date_columns(df)
    numeric_cols = [
        c for c in df.select_dtypes(include="number").columns if c not in date_cols
    ]
    categorical_cols = [
        c for c in df.columns if c not in numeric_cols and c not in date_cols
    ]

    missing = df.isna().sum()
    missing = {col: int(n) for col, n in missing.items() if n > 0}

    stats = {}
    if numeric_cols:
        stats = df[numeric_cols].describe().round(2).to_dict()

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "date_columns": date_cols,
        "missing_values": missing,
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_stats": stats,
    }