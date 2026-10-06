import re

import numpy as np
import pandas as pd

BLOCKED_PATTERNS = [
    r"\bimport\b", r"\bopen\s*\(", r"\bexec\s*\(", r"\beval\s*\(",
    r"\bcompile\s*\(", r"\bglobals\b", r"\blocals\b", r"\bgetattr\b",
    r"\bsetattr\b", r"\bdelattr\b", r"\binput\s*\(", r"__",
    r"\bos\b", r"\bsys\b", r"\bsubprocess\b", r"\bshutil\b",
    r"\.to_csv", r"\.to_excel", r"\.to_pickle", r"\.read_",
    r"\.to_sql", r"\.to_json",
]

SAFE_BUILTINS = {
    "len": len, "sum": sum, "min": min, "max": max, "abs": abs,
    "round": round, "sorted": sorted, "range": range, "list": list,
    "dict": dict, "set": set, "tuple": tuple, "str": str, "int": int,
    "float": float, "bool": bool, "enumerate": enumerate, "zip": zip,
    "any": any, "all": all,
}


def run_python_analysis(df: pd.DataFrame, code: str) -> dict:
    """
    Run restricted Pandas code. The code must assign its answer to `result`.
    Returns {"success": bool, "output": str, "error": str | None}.
    """
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, code):
            return {
                "success": False,
                "output": "",
                "error": f"Blocked: code contains a disallowed pattern ({pattern}).",
            }

    scope = {"df": df.copy(), "pd": pd, "np": np}
    try:
        exec(code, {"__builtins__": SAFE_BUILTINS}, scope)
    except Exception as e:
        return {"success": False, "output": "", "error": f"{type(e).__name__}: {e}"}

    if "result" not in scope:
        return {
            "success": False,
            "output": "",
            "error": "Code ran but did not set a variable named `result`.",
        }

    result = scope["result"]
    if isinstance(result, (pd.DataFrame, pd.Series)):
        text = result.head(50).to_string()
    else:
        text = str(result)

    return {"success": True, "output": text[:3000], "error": None}