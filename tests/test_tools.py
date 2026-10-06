import pandas as pd

from tools.analysis_tools import run_python_analysis

df = pd.read_csv("data/sales_2024.csv")


def test_total_revenue():
    out = run_python_analysis(df, "result = df['revenue'].sum()")
    assert out["success"]
    assert out["output"] == str(df["revenue"].sum())


def test_groupby():
    out = run_python_analysis(df, "result = df.groupby('region')['revenue'].sum()")
    assert out["success"]
    assert "West" in out["output"]


def test_blocks_import():
    out = run_python_analysis(df, "import os\nresult = 1")
    assert not out["success"]


def test_blocks_file_access():
    out = run_python_analysis(df, "result = open('.env').read()")
    assert not out["success"]


def test_missing_result_variable():
    out = run_python_analysis(df, "x = 5")
    assert not out["success"]


def test_bad_column_returns_error_not_crash():
    out = run_python_analysis(df, "result = df['nope'].sum()")
    assert not out["success"]