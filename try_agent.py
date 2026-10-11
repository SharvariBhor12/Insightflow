import sys

import pandas as pd

from agents.analyst_agent import run_agent

df = pd.read_csv("data/sales_2024.csv")
question = " ".join(sys.argv[1:]) or "Which region has the highest total revenue?"

answer, messages, charts, plan = run_agent(df, question)

print("=== PLAN ===")
print(plan)

print("\n=== TOOL TRAIL ===")
for m in messages:
    if getattr(m, "tool_calls", None):
        for c in m.tool_calls:
            print(f"CALL  {c['name']}  {c['args']}")
    elif m.type == "tool":
        print(f"RESULT {m.content[:200]}")

print("\n=== FINAL ANSWER ===")
print(answer)
print(f"\nCharts created: {len(charts)}")