from __future__ import annotations
import pandas as pd

# Generate a table of missing values and their percentage per column
def missing_table(df: pd.DataFrame) -> pd.DataFrame:
    mc = df.isna().sum()
    mp = (mc / len(df)) * 100
    res = pd.DataFrame({"Missing Values": mc, "Percent": mp})
    return res[res["Missing Values"] > 0].sort_values("Percent", ascending=False)

# Identify non-numeric object columns and return warnings with sample values
def non_numeric_warnings(df: pd.DataFrame, ignore: list[str] | None = None) -> list[str]:
    ignore = set(ignore or [])
    msgs = []
    for col in df.select_dtypes(include="object").columns:
        if col not in ignore:
            sample = df[col].dropna().unique()[:5]
            msgs.append(f"Column '{col}' is not numeric. Examples: {sample}")
    return msgs

# Generate a dictionary of unique values for all object columns
def unique_values_report(df: pd.DataFrame) -> dict[str, list]:
    return {c: df[c].dropna().unique().tolist() for c in df.select_dtypes(include="object").columns}