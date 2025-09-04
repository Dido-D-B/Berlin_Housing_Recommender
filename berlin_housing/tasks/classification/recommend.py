"""
This module provides functions for generating housing recommendations by filtering,
ranking, and applying fallback strategies based on affordability, clusters, and amenities
in the Berlin Housing project.
"""

# Imports
from __future__ import annotations
import pandas as pd
from typing import Iterable, Optional, Dict, Any

# Compute ranking score from rent-to-income ratio with small amenity adjustments
def _score_row(row: pd.Series) -> float:
    """
    Compute a ranking score for a housing option based on its rent-to-income ratio,
    adjusted slightly by the presence of amenities.

    Parameters:
        row (pd.Series): A row from the DataFrame representing a housing option.

    Returns:
        float: The computed score where lower is better.
    """
    ratio = float(row.get("aff_rent_to_income", 1.0))
    bonus = 0.0
    for col in ("cafes", "restaurants", "supermarket", "green_space"):
        if col in row and pd.notnull(row[col]):
            bonus -= 0.0005 * float(row[col])
    return ratio + bonus

# Select a compact set of columns for the results table
def _compact_columns(df: pd.DataFrame, cluster_col: str) -> list[str]:
    """
    Select a subset of columns to present in the final recommendations output.

    Parameters:
        df (pd.DataFrame): The DataFrame containing housing data.
        cluster_col (str): The name of the cluster column.

    Returns:
        list[str]: A list of column names to include in the output.
    """
    base_cols = [c for c in [
        "bezirk", "ortsteil", cluster_col,
        "aff_rent_per_m2", "aff_est_monthly_rent", "aff_rent_to_income"
    ] if c in df.columns]
    for c in ("cafes", "restaurants", "supermarket", "green_space", "schools"):
        if c in df.columns:
            base_cols.append(c)
    return base_cols

# Filter → rank → return top‑k with graceful fallbacks and relaxed thresholds
def top_recommendations(
    df_with_aff: pd.DataFrame,
    *,
    preferred_clusters: Optional[Iterable[int]] = None,
    cluster_col: str = "k4_cluster",
    only_affordable: bool = True,
    k: int = 5,
    extra_filters: Optional[Dict[str, Any]] = None,
    fallback_if_empty: bool = True,
    # NEW: thresholds to try (in order) if nothing matches at the current threshold
    relax_thresholds: Optional[Iterable[float]] = (0.32, 0.35, 0.40),
) -> pd.DataFrame:
    """
    Generate top-k housing recommendations by filtering and ranking with fallback options.

    Parameters:
        df_with_aff (pd.DataFrame): DataFrame containing housing data with affordability info.
        preferred_clusters (Optional[Iterable[int]]): Clusters to prefer in filtering.
        cluster_col (str): Column name for clusters.
        only_affordable (bool): Whether to restrict to affordable options initially.
        k (int): Number of top recommendations to return.
        extra_filters (Optional[Dict[str, Any]]): Additional column-value filters to apply.
        fallback_if_empty (bool): Whether to attempt fallback strategies if no results.
        relax_thresholds (Optional[Iterable[float]]): Affordability thresholds to relax progressively.

    Returns:
        pd.DataFrame: Top-k recommendations with scores and notes about the filtering step.
    """
    df0 = df_with_aff.copy()

    # Apply optional extra filters upfront (e.g., district)
    if extra_filters:
        for col, val in extra_filters.items():
            if col in df0.columns:
                df0 = df0[df0[col] == val]

    def _apply_cluster(dfi: pd.DataFrame) -> pd.DataFrame:
        if preferred_clusters is not None and cluster_col in dfi.columns:
            dfi = dfi[dfi[cluster_col].isin(list(preferred_clusters))]
        return dfi

    def _rank_take(dfi: pd.DataFrame, note: str) -> pd.DataFrame:
        if dfi.empty:
            return dfi
        dfi = dfi.assign(_score=dfi.apply(_score_row, axis=1), _note=note)
        dfi = dfi.sort_values(by=["_score", "aff_rent_to_income"]).head(k)
        return dfi[_compact_columns(dfi, cluster_col) + ["_score", "_note"]]

    # Attempt A: exact filters 
    dfA = df0
    if only_affordable and "aff_label" in dfA:
        dfA = dfA[dfA["aff_label"]]
    dfA = _apply_cluster(dfA)
    out = _rank_take(dfA, note="exact_match")
    if not out.empty or not fallback_if_empty:
        return out

    # Attempt B: relax thresholds within same cluster(s) 
    if relax_thresholds and "aff_rent_to_income" in df0.columns:
        df_cluster = _apply_cluster(df0)
        for t in relax_thresholds:
            df_relax = df_cluster[df_cluster["aff_rent_to_income"] <= float(t)]
            out = _rank_take(df_relax, note=f"relaxed_threshold_{t:.2f}")
            if not out.empty:
                return out

    # Attempt C1: same cluster(s), ignore affordability 
    df_f1 = _apply_cluster(df0)
    out = _rank_take(df_f1, note="no_affordable_in_cluster")
    if not out.empty:
        return out

    # Attempt C2: affordable anywhere (drop cluster filter) 
    df_f2 = df0
    if "aff_label" in df_f2:
        df_f2 = df_f2[df_f2["aff_label"]]
    out = _rank_take(df_f2, note="affordable_other_clusters")
    if not out.empty:
        return out

    # Attempt C3: cheapest overall 
    return _rank_take(df0, note="cheapest_overall")