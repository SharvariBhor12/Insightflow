import pandas as pd
from tools.stats_tools import compare_periods, detect_anomalies

df = pd.read_csv("data/sales_2024.csv")
print(compare_periods(df, "date", "revenue", "2024Q2", "2024Q3")["output"])
print()
print(detect_anomalies(df, "date", "revenue")["output"])