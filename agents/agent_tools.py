import json

import pandas as pd
from langchain_core.tools import tool

from tools.analysis_tools import run_python_analysis
from tools.data_tools import profile_dataset
from tools.sql_tools import get_schema, run_sql_query
from tools.stats_tools import compare_periods, detect_anomalies
from tools.visualization_tools import create_visualization


def build_tools(df: pd.DataFrame):
    """Create all agent tools bound to this DataFrame.
    Returns (tools_list, charts_list). Charts created by the agent are appended to charts_list."""
    charts = []

    @tool
    def get_dataset_info() -> str:
        """Get the dataset profile: row count, column names, data types, numeric/categorical/date
        columns, missing values, duplicates. Use this first when you are unsure what columns exist."""
        return json.dumps(profile_dataset(df), default=str)[:3000]

    @tool
    def get_table_schema() -> str:
        """Get the SQL table name and column types. Use before writing SQL if unsure of column names."""
        return get_schema(df)

    @tool
    def sql_query(query: str) -> str:
        """Run ONE read-only SQL SELECT query on the table named 'data'. Best for aggregations,
        group-by, top-N, filtering, and monthly or quarterly totals (use strftime for dates in SQLite)."""
        out = run_sql_query(df, query)
        return out["output"] if out["success"] else f"ERROR: {out['error']}"

    @tool
    def python_analysis(code: str) -> str:
        """Run Pandas code on a DataFrame named df. The code MUST assign its final answer to a
        variable named result. pandas is available as pd and numpy as np. No imports, no file access.
        Use for calculations that are awkward in SQL, such as percentage changes or pivots."""
        out = run_python_analysis(df, code)
        return out["output"] if out["success"] else f"ERROR: {out['error']}"

    @tool
    def compare_two_periods(date_col: str, value_col: str, period_a: str, period_b: str) -> str:
        """Compare the total of a numeric column between two periods and return the change and percent
        change. Periods look like '2024Q2', '2024Q3' or '2024-07'. Use for questions such as
        'did revenue drop in Q3 vs Q2'."""
        out = compare_periods(df, date_col, value_col, period_a, period_b)
        return out["output"] if out["success"] else f"ERROR: {out['error']}"

    @tool
    def find_anomalies(date_col: str, value_col: str, freq: str = "M") -> str:
        """Find unusual periods in a time series of totals using z-scores. freq: 'M' monthly,
        'W' weekly, 'D' daily. Use when asked about unusual patterns or spikes."""
        out = detect_anomalies(df, date_col, value_col, freq=freq)
        return out["output"] if out["success"] else f"ERROR: {out['error']}"

    @tool
    def make_chart(chart_type: str, x: str, y: str = "", group_by_month: bool = False, title: str = "") -> str:
        """Create a chart. chart_type: 'line' for trends over time, 'bar' for comparing categories,
        'histogram' for distributions (y not needed), 'scatter' for relationships between two numeric
        columns. For a monthly trend, use line with x set to the date column, y set to a numeric
        column, and group_by_month true."""
        out = create_visualization(df, chart_type, x, y or None, group_by_month, title)
        if not out["success"]:
            return f"ERROR: {out['error']}"
        charts.append(out["figure"])
        return f"Chart created: {chart_type} of {y or x}."

    tools = [
        get_dataset_info,
        get_table_schema,
        sql_query,
        python_analysis,
        compare_two_periods,
        find_anomalies,
        make_chart,
    ]
    return tools, charts