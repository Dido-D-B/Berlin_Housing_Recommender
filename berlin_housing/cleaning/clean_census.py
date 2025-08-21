# berlin_housing/cleaning/clean_census.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd

# Expect these helpers to live in cleaning/clean_shared.py
from .clean_shared import (
    standardize_columns,
    rename_columns,
    coerce_dtypes,
    drop_duplicates_key,
    normalize_name,
)

# ---------------------------------------------------------------------
# Census: Generic cleaner configurable for district or ortsteil levels
# ---------------------------------------------------------------------

@dataclass
class CensusCleanConfig:
    """
    Configuration for cleaning a Census 2022 table.

    Map your raw column names (as they appear in the source) to canonical names:
      - id_col: unique id (e.g., AGS, PLR, ortsteil_id)
      - name_col: display name (e.g., 'ortsteil' or 'district')
      - bezirk_col: district name column if present
    Also provide numeric column lists for dtype coercion.
    """
    id_col: str = "ortsteil_id"   # or AGS/PLR if you have that instead
    name_col: str = "ortsteil"    # display name column in your raw file
    bezirk_col: str = "bezirk"    # district name column in your raw file

    integer_cols: List[str] | None = None
    float_cols: List[str] | None = None

    def __post_init__(self):
        if self.integer_cols is None:
            self.integer_cols = []
        if self.float_cols is None:
            self.float_cols = []


def clean_census_2022(df: pd.DataFrame, cfg: CensusCleanConfig) -> pd.DataFrame:
    """
    Clean a raw Census 2022 table (district or subdistrict).

    Steps (mirrors your notebooks):
      1) Standardize/rename columns to canonical names
      2) Coerce numeric blocks and trim strings
      3) Derive normalized keys for safe joins
      4) Drop duplicates on strongest key available
    """
    # 1) Standardize column names to snake_case
    df1 = standardize_columns(df)

    # 2) Canonical aliases based on provided config
    mapping = {
        cfg.id_col: "ortsteil_id",
        cfg.name_col: "ortsteil",
        cfg.bezirk_col: "bezirk",
    }
    df1 = rename_columns(df1, mapping)

    # 3) Coerce dtypes
    df1 = coerce_dtypes(
        df1,
        int_cols=cfg.integer_cols,
        float_cols=cfg.float_cols,
        str_cols=[c for c in ["ortsteil", "bezirk"] if c in df1.columns],
    )

    # 4) Normalized join keys
    if "ortsteil" in df1.columns:
        df1["ortsteil_norm"] = df1["ortsteil"].map(normalize_name)
    if "bezirk" in df1.columns:
        df1["bezirk_norm"] = df1["bezirk"].map(normalize_name)

    # 5) De‑duplicate on strongest available key
    key_cols = [c for c in ["ortsteil_id", "ortsteil_norm"] if c in df1.columns]
    if key_cols:
        df1 = drop_duplicates_key(df1, key_cols)

    return df1


__all__ = [
    "CensusCleanConfig",
    "clean_census_2022",
]