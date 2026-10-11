import pandas as pd
from tools.visualization_tools import create_visualization

df = pd.read_csv("data/sales_2024.csv")
out = create_visualization(df, "line", "date", "revenue", group_by_month=True)
out["figure"].show()