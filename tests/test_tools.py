import pandas as pd

from tools.analysis_tools import run_python_analysis
from tools.sql_tools import run_sql_query

df = pd.read_csv("data/sales_2024.csv")


# ---------- Pandas tool tests ----------

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


# ---------- SQL tool tests ----------

def test_sql_total_revenue():
    out = run_sql_query(df, "SELECT SUM(revenue) AS total FROM data")
    assert out["success"]
    assert str(int(df["revenue"].sum())) in out["output"]


def test_sql_groupby():
    out = run_sql_query(df, "SELECT region, SUM(revenue) AS rev FROM data GROUP BY region")
    assert out["success"]
    assert "West" in out["output"]


def test_sql_blocks_drop():
    out = run_sql_query(df, "DROP TABLE data")
    assert not out["success"]


def test_sql_blocks_multiple_statements():
    out = run_sql_query(df, "SELECT 1; DELETE FROM data")
    assert not out["success"]


def test_sql_bad_column_returns_error():
    out = run_sql_query(df, "SELECT nope FROM data")
    assert not out["success"]