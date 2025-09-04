"""
recommender.py

Service functions for generating housing recommendations in the Berlin Housing Affordability project.

This module wraps together:
- Loading the master dataset
- Computing affordability per subdistrict
- Filtering and ranking top recommended subdistricts
"""

# Imports
import pandas as pd
from berlin_housing.io import load_master
from berlin_housing import add_affordability, top_recommendations
from berlin_housing.config import (
    DEFAULT_MIETSPIEGEL_COL, DEFAULT_INCOME_COL, DEFAULT_CLUSTER_COL
)
from utils.constants import HOUSEHOLD_M2

# Get top k recommended subdistricts
def get_top_k(
    monthly_income_eur: float,
    size_m2: int,
    threshold: float,
    preferred_clusters: list[int],
    k: int = 5,
    relax_thresholds=(0.32, 0.35, 0.40),
) -> pd.DataFrame:
    """
    Generate top-k recommended Berlin subdistricts based on user income, apartment size, and preferences.

    This function:
    - Loads the master dataset
    - Adds affordability classification given income, size, and rent threshold
    - Filters recommendations by preferred cluster profiles
    - Returns the top-k results

    Args:
        monthly_income_eur (float): User's monthly household income in euros.
        size_m2 (int): Desired apartment size in square meters.
        threshold (float): Affordability threshold (fraction of income spent on rent).
        preferred_clusters (list[int]): Cluster IDs the user is interested in (e.g., [0,1]).
        k (int, optional): Number of recommendations to return. Default is 5.
        relax_thresholds (tuple, optional): Progressive thresholds for relaxing affordability
            constraints if not enough matches are found.

    Returns:
        pd.DataFrame: Top-k recommended subdistricts with affordability and cluster information.
    """
    df = load_master()
    df_aff = add_affordability(
        df,
        monthly_income_eur=monthly_income_eur,
        size_m2=size_m2,
        threshold=threshold,
        mietspiegel_col=DEFAULT_MIETSPIEGEL_COL,
        income_col=DEFAULT_INCOME_COL,
    )
    top = top_recommendations(
        df_aff,
        preferred_clusters=preferred_clusters,
        cluster_col=DEFAULT_CLUSTER_COL,
        k=k,
        relax_thresholds=relax_thresholds,
    )
    return top

# Estimate required apartment size
def estimate_required_sqm(hh_type: str, *, children: int = 0, wg_people: int = 3) -> int:
    if hh_type == "Single":
        return HOUSEHOLD_M2["Single"]
    if hh_type == "Couple":
        return HOUSEHOLD_M2["Couple"]
    if hh_type == "Family":
        return HOUSEHOLD_M2["Family"]["base"] + children * HOUSEHOLD_M2["Family"]["per_child"]
    if hh_type == "WG":
        return wg_people * HOUSEHOLD_M2["WG"]["per_person"]
    if hh_type == "Senior":
        return HOUSEHOLD_M2["Senior"]
    return HOUSEHOLD_M2["Single"]