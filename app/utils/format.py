"""
format.py

Formatting helpers for consistent display in the Berlin Housing Affordability app.

This module provides functions to format numbers as euro amounts or plain integers,
with thousands separators using spaces.
"""

# Format euro
def fmt_eur(x):
    """
    Format a value as a euro amount with thousands separators.

    Args:
        x (float|int|str): Numeric value.

    Returns:
        str: Value formatted like "€1 200". If parsing fails, returns input unchanged.
    """
    try:
        return f"€{int(round(float(x))):,}".replace(",", " ")
    except Exception:
        return x

# Format integer
def fmt_int(x):
    """
    Format a value as an integer with thousands separators.

    Args:
        x (float|int|str): Numeric value.

    Returns:
        str: Value formatted like "1 200". If parsing fails, returns input unchanged.
    """
    try:
        return f"{int(round(float(x))):,}".replace(",", " ")
    except Exception:
        return x