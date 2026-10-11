import pandas as pd
import plotly.express as px

CHART_TYPES = ["line", "bar", "histogram", "scatter"]


def create_visualization(
    df: pd.DataFrame,
    chart_type: str,
    x: str,
    y: str = None,
    group_by_month: bool = False,
    title: str = "",
) -> dict:
    """
    Build a Plotly chart.
    - line / bar: x and y required. If group_by_month is True, y is summed per month of x.
    - histogram: only x required.
    - scatter: x and y required.
    Returns {"success", "figure", "error"}.
    """
    chart_type = chart_type.lower().strip()

    if chart_type not in CHART_TYPES:
        return {"success": False, "figure": None, "error": f"Unsupported chart type '{chart_type}'. Use one of {CHART_TYPES}."}

    for col in (x, y):
        if col is not None and col not in df.columns:
            return {"success": False, "figure": None, "error": f"Column '{col}' not found. Available: {list(df.columns)}"}

    if chart_type != "histogram" and y is None:
        return {"success": False, "figure": None, "error": f"A '{chart_type}' chart needs a y column."}

    try:
        data = df.copy()

        if group_by_month:
            data[x] = pd.to_datetime(data[x], errors="coerce")
            data = data.dropna(subset=[x])
            data = data.groupby(data[x].dt.to_period("M"))[y].sum().reset_index()
            data[x] = data[x].astype(str)
        elif chart_type == "bar":
            data = data.groupby(x)[y].sum().reset_index()

        if chart_type == "line":
            fig = px.line(data, x=x, y=y, markers=True, title=title or f"{y} by {x}")
        elif chart_type == "bar":
            fig = px.bar(data, x=x, y=y, title=title or f"{y} by {x}")
        elif chart_type == "histogram":
            fig = px.histogram(data, x=x, title=title or f"Distribution of {x}")
        else:
            fig = px.scatter(data, x=x, y=y, title=title or f"{y} vs {x}")

        return {"success": True, "figure": fig, "error": None}
    except Exception as e:
        return {"success": False, "figure": None, "error": f"{type(e).__name__}: {e}"}