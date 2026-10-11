import pandas as pd

from agents.agent_tools import build_tools

df = pd.read_csv("data/sales_2024.csv")


def test_all_tools_are_built():
    tools, charts = build_tools(df)
    names = [t.name for t in tools]
    assert "sql_query" in names
    assert "make_chart" in names
    assert len(tools) == 7


def test_sql_tool_runs():
    tools, _ = build_tools(df)
    sql = next(t for t in tools if t.name == "sql_query")
    out = sql.invoke({"query": "SELECT COUNT(*) AS n FROM data"})
    assert str(len(df)) in out


def test_chart_tool_stores_figure():
    tools, charts = build_tools(df)
    chart_tool = next(t for t in tools if t.name == "make_chart")
    msg = chart_tool.invoke({"chart_type": "bar", "x": "region", "y": "revenue"})
    assert "Chart created" in msg
    assert len(charts) == 1


def test_tool_errors_return_text_not_crash():
    tools, _ = build_tools(df)
    sql = next(t for t in tools if t.name == "sql_query")
    out = sql.invoke({"query": "SELECT nope FROM data"})
    assert out.startswith("ERROR")