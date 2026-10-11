import re
import sqlite3

import pandas as pd

BLOCKED_SQL = [
    "insert", "update", "delete", "drop", "alter", "create", "replace",
    "attach", "detach", "pragma", "vacuum", "reindex", "truncate",
]


def get_schema(df: pd.DataFrame) -> str:
    """Describe the table the SQL tool exposes, so the agent knows what to query."""
    cols = ", ".join(f"{c} ({t})" for c, t in df.dtypes.astype(str).items())
    return f"Table name: data\nColumns: {cols}"


def run_sql_query(df: pd.DataFrame, query: str) -> dict:
    """
    Run a read-only SELECT query against the DataFrame (table name: data).
    Returns {"success": bool, "output": str, "error": str | None}.
    """
    cleaned = query.strip().rstrip(";").strip()

    if ";" in cleaned:
        return {"success": False, "output": "", "error": "Only one SQL statement is allowed."}

    if not re.match(r"^(select|with)\b", cleaned, flags=re.IGNORECASE):
        return {"success": False, "output": "", "error": "Only SELECT queries are allowed."}

    for word in BLOCKED_SQL:
        if re.search(rf"\b{word}\b", cleaned, flags=re.IGNORECASE):
            return {
                "success": False,
                "output": "",
                "error": f"Blocked: query contains a disallowed keyword ({word}).",
            }

    conn = sqlite3.connect(":memory:")
    try:
        df.to_sql("data", conn, index=False)
        result = pd.read_sql_query(cleaned, conn)
    except Exception as e:
        return {"success": False, "output": "", "error": f"{type(e).__name__}: {e}"}
    finally:
        conn.close()

    if result.empty:
        return {"success": True, "output": "Query returned no rows.", "error": None}

    return {"success": True, "output": result.head(50).to_string(index=False)[:3000], "error": None}