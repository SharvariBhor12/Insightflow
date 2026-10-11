import pandas as pd

from tools.stats_tools import compare_periods, detect_anomalies

df = pd.read_csv("data/sales_2024.csv")


def test_compare_periods_matches_manual_calculation():
    d = pd.to_datetime(df["date"])
    q2 = df.loc[d.dt.to_period("Q") == pd.Period("2024Q2"), "revenue"].sum()
    q3 = df.loc[d.dt.to_period("Q") == pd.Period("2024Q3"), "revenue"].sum()
    expected = round((q3 - q2) / q2 * 100, 2)

    out = compare_periods(df, "date", "revenue", "2024Q2", "2024Q3")
    assert out["success"]
    assert out["data"]["pct_change"] == expected


def test_compare_periods_bad_column():
    out = compare_periods(df, "date", "nope", "2024Q2", "2024Q3")
    assert not out["success"]


def test_compare_periods_non_numeric_column():
    out = compare_periods(df, "date", "region", "2024Q2", "2024Q3")
    assert not out["success"]


def test_detect_anomalies_runs():
    out = detect_anomalies(df, "date", "revenue")
    assert out["success"]


def test_detect_anomalies_too_few_periods():
    small = df.head(5)
    out = detect_anomalies(small, "date", "revenue")
    assert not out["success"]