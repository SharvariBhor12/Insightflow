import pandas as pd
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from tools.sql_tools import run_sql_query
from utils.llm import get_llm

df = pd.read_csv("data/sales_2024.csv")


@tool
def sql_query(query: str) -> str:
    """Run a read-only SQL SELECT query on the sales table named 'data'.
    Columns: order_id, date, product, category, region, customer_id,
    units, unit_price, revenue."""
    out = run_sql_query(df, query)
    return out["output"] if out["success"] else f"ERROR: {out['error']}"


llm = get_llm().bind_tools([sql_query])

messages = [HumanMessage("What is the total revenue?")]

# Step 1: the LLM decides what to do
ai_msg = llm.invoke(messages)
print("1) Tool calls requested by the LLM:")
print(ai_msg.tool_calls)

# Step 2: WE run the tool and send the result back
messages.append(ai_msg)
for call in ai_msg.tool_calls:
    result = sql_query.invoke(call["args"])
    print("\n2) Tool result:")
    print(result)
    messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

# Step 3: the LLM reads the result and answers
final = llm.invoke(messages)
print("\n3) Final answer:")
print(final.text)