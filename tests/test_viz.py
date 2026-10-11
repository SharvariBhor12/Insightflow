import pandas as pd

from tools.visualization_tools import create_visualization

df = pd.read_csv("data/sales_2024.csv")


def test_line_chart_by_month():
    out = create_visualization(df, "line", "date", "revenue", group_by_month=True)
    assert out["success"]
    assert out["figure"] is not None


def test_bar_chart_by_category():
    out = create_visualization(df, "bar", "region", "revenue")
    assert out["success"]


def test_histogram_needs_only_x():
    out = create_visualization(df, "histogram", "revenue")
    assert out["success"]


def test_unsupported_chart_type():
    out = create_visualization(df, "pie", "region", "revenue")
    assert not out["success"]


def test_bad_column():
    out = create_visualization(df, "bar", "nope", "revenue")
    assert not out["success"]


def test_line_without_y():
    out = create_visualization(df, "line", "date")
    assert not out["success"]