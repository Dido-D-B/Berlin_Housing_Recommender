from __future__ import annotations
import pandas as pd
from typing import Iterable, Optional, Dict, Any

# Compute ranking score from rent-to-income ratio with small amenity adjustments
def _score_row(row: pd.Series) -> float:
    ratio = float(row.get("aff_rent_to_income", 1.0))
    bonus = 0.0
    for col in ("cafes", "restaurants", "supermarket", "green_space"):
        if col in row and pd.notnull(row[col]):
            bonus -= 0.0005 * float(row[col])
    return ratio + bonus

# Select a compact set of columns for the results table
def _compact_columns(df: pd.DataFrame, cluster_col: str) -> list[str]:
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
    Filter -> rank -> Top‑k with graceful fallbacks.

    Order of attempts:
      A) exact filters (affordable + preferred cluster)
      B) if empty and relax_thresholds provided:
           try same cluster(s) with progressively higher affordability
           thresholds (uses aff_rent_to_income <= t)
      C) if still empty and fallback_if_empty:
           1) 'no_affordable_in_cluster'  -> ignore affordability, keep cluster(s)
           2) 'affordable_other_clusters' -> keep affordability, drop cluster(s)
           3) 'cheapest_overall'          -> ignore both
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