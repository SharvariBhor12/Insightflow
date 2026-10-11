import pandas as pd


def _prepare(df: pd.DataFrame, date_col: str, value_col: str):
    """Validate columns and return a copy with a parsed date column."""
    for col in (date_col, value_col):
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found. Available: {list(df.columns)}")
    if not pd.api.types.is_numeric_dtype(df[value_col]):
        raise ValueError(f"Column '{value_col}' is not numeric.")

    data = df[[date_col, value_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data = data.dropna(subset=[date_col, value_col])
    if data.empty:
        raise ValueError("No valid rows after parsing dates and values.")
    return data


def compare_periods(
    df: pd.DataFrame, date_col: str, value_col: str, period_a: str, period_b: str
) -> dict:
    """
    Compare the total of value_col between two periods.
    Periods use pandas period strings, e.g. '2024Q2', '2024Q3', or '2024-07'.
    Returns {"success", "output", "error", "data"}.
    """
    try:
        data = _prepare(df, date_col, value_col)
        results = {}
        for label in (period_a, period_b):
            period = pd.Period(label)
            mask = data[date_col].dt.to_period(period.freq) == period
            results[label] = float(data.loc[mask, value_col].sum())

        a, b = results[period_a], results[period_b]
        if a == 0:
            return {"success": False, "output": "", "error": f"{period_a} total is 0, cannot compute % change.", "data": {}}

        change = b - a
        pct = change / a * 100
        text = (
            f"{value_col} in {period_a}: {a:,.2f}\n"
            f"{value_col} in {period_b}: {b:,.2f}\n"
            f"Change: {change:,.2f} ({pct:+.2f}%)"
        )
        return {
            "success": True,
            "output": text,
            "error": None,
            "data": {"period_a": a, "period_b": b, "change": change, "pct_change": round(pct, 2)},
        }
    except Exception as e:
        return {"success": False, "output": "", "error": f"{type(e).__name__}: {e}", "data": {}}


def detect_anomalies(
    df: pd.DataFrame, date_col: str, value_col: str, freq: str = "M", threshold: float = 2.0
) -> dict:
    """
    Aggregate value_col by period (freq 'M' = month, 'W' = week, 'D' = day),
    then flag periods whose z-score is beyond +/- threshold.
    """
    try:
        data = _prepare(df, date_col, value_col)
        series = data.groupby(data[date_col].dt.to_period(freq))[value_col].sum()

        if len(series) < 4:
            return {"success": False, "output": "", "error": "Not enough periods to detect anomalies (need at least 4).", "data": {}}

        std = series.std()
        if std == 0:
            return {"success": True, "output": "No anomalies: all periods have identical values.", "error": None, "data": {"anomalies": []}}

        z = (series - series.mean()) / std
        flagged = z[z.abs() > threshold]

        if flagged.empty:
            text = f"No anomalies found at threshold {threshold} across {len(series)} periods."
            return {"success": True, "output": text, "error": None, "data": {"anomalies": []}}

        lines = [f"{str(p)}: total={series[p]:,.2f}, z-score={z[p]:+.2f}" for p in flagged.index]
        anomalies = [{"period": str(p), "total": float(series[p]), "z": round(float(z[p]), 2)} for p in flagged.index]
        return {"success": True, "output": "Anomalies found:\n" + "\n".join(lines), "error": None, "data": {"anomalies": anomalies}}
    except Exception as e:
        return {"success": False, "output": "", "error": f"{type(e).__name__}: {e}", "data": {}}