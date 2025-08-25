# Imports
import pandas as pd
from __future__ import annotations
from typing import Iterable, Mapping

# Convert a string into simple snake_case form
def _to_snake(name: str) -> str:
    """Simple snake_case normalizer used for headers."""
    return (
        name.strip()
        .replace("ß", "ss")
        .replace(" ", "_")
        .replace("-", "_")
        .lower()
    )

# Standardize dataframe column names to snake_case
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with snake_case, trimmed column names."""
    out = df.copy()
    out.columns = [_to_snake(c) for c in out.columns]
    return out

# Rename columns using case-insensitive snake_case mapping
def rename_columns(df: pd.DataFrame, mapping: Mapping[str, str]) -> pd.DataFrame:
    """
    Rename columns using a case-insensitive mapping (keys matched after snake_case).
    Example:
        rename_columns(df, {"Ortsteil": "ortsteil", "District": "bezirk"})
    """
    df2 = standardize_columns(df)
    norm_map = {_to_snake(k): v for k, v in mapping.items()}
    return df2.rename(columns=norm_map)

# Normalize German names (umlauts/ß) for safe joins
def normalize_name(s: str | float | None) -> str:
    """
    Normalize German names to ASCII-ish for safe joins (ae/oe/ue/ss), lowercased/trimmed.
    """
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    s2 = str(s).strip().lower()
    return (
        s2.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )

# Coerce columns to Int64, float, or string types with cleaning
def coerce_dtypes(
    df: pd.DataFrame,
    *,
    int_cols: Iterable[str] | None = None,
    float_cols: Iterable[str] | None = None,
    str_cols: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Coerce groups of columns to Int64/float/str (trimmed).
    Unknown or bad values become <NA> (for ints) or NaN (for floats).
    """
    out = df.copy()
    for c in int_cols or []:
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("Int64")
    for c in float_cols or []:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    for c in str_cols or []:
        out[c] = out[c].astype("string").str.strip()
    return out

# Drop duplicate rows based on key columns
def drop_duplicates_key(df: pd.DataFrame, keys: Iterable[str]) -> pd.DataFrame:
    """Drop duplicate rows by key columns, keeping the first occurrence."""
    return df.drop_duplicates(subset=list(keys), keep="first").reset_index(drop=True)

# Ensure key columns are unique, raise error if not
def assert_unique(df: pd.DataFrame, keys: Iterable[str]) -> None:
    """Raise if (keys) are not unique."""
    dup = df.duplicated(subset=list(keys)).sum()
    if dup:
        raise ValueError(f"Expected unique keys {list(keys)} but found {dup} duplicates")

# Normalize Bezirk/Ortsteil names for merging
def normalize_merge_keys(df: pd.DataFrame, bezirk_col: str = "bezirk", ortsteil_col: str = "ortsteil") -> pd.DataFrame:
    """
    Lowercase/strip and replace German umlauts for join keys.
    Matches the normalization used throughout the notebooks.
    """
    out = df.copy()

    def _norm(s: pd.Series) -> pd.Series:
        s = s.astype(str).str.strip().str.lower()
        s = (
            s.str.replace("ö", "oe", regex=False)
             .str.replace("ü", "ue", regex=False)
             .str.replace("ä", "ae", regex=False)
             .str.replace("ß", "ss", regex=False)
        )
        return s

    if bezirk_col in out.columns:
        out[bezirk_col] = _norm(out[bezirk_col])
    if ortsteil_col in out.columns:
        out[ortsteil_col] = _norm(out[ortsteil_col])
    return out

# Normalize Bezirk string values to consistent form
def clean_bezirk_value(bezirk: str) -> str:
    """
    Normalize Bezirk strings to a consistent, join-friendly form.
    Replicates the notebook logic: umlauts→oe, strip dots/spaces, kebab-case, and fix truncations.
    """
    if bezirk is None:
        return ""
    s = str(bezirk)
    s = s.replace("ö", "oe").replace("Ö", "oe")
    s = s.replace(".", "")
    s = s.lower().strip().replace(" ", "-")
    mapping = {
        "charlbg-wilmersd": "charlottenburg-wilmersdorf",
        "friedrh-kreuzb": "friedrichshain-kreuzberg",
        "marzahn-hellersd": "marzahn-hellersdorf",
        "steglitz-zehlend": "steglitz-zehlendorf",
        "tempelh-schoeneb": "tempelhof-schoeneberg",
    }
    return mapping.get(s, s) or s

# Apply clean_bezirk_value across a dataframe column
def apply_clean_bezirk(df: pd.DataFrame, col: str = "bezirk") -> pd.DataFrame:
    """Apply clean_bezirk_value to a column and return a copy."""
    out = df.copy()
    out[col] = out[col].map(clean_bezirk_value)
    return out

# Public API
__all__ = [
    # column/name normalization
    "_to_snake",
    "standardize_columns",
    "rename_columns",
    "normalize_name",
    # dtype/duplicate helpers
    "coerce_dtypes",
    "drop_duplicates_key",
    "assert_unique",
    "normalize_merge_keys",
    # bezirk normalization
    "clean_bezirk_value",
    "apply_clean_bezirk",
]