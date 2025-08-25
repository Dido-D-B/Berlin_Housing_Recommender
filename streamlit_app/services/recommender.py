# Imports
import pandas as pd
from berlin_housing.io import load_master
from berlin_housing import add_affordability, top_recommendations
from berlin_housing.config import (
    DEFAULT_MIETSPIEGEL_COL, DEFAULT_INCOME_COL, DEFAULT_CLUSTER_COL
)

# Get top k recommended subdistricts
def get_top_k(
    monthly_income_eur: float,
    size_m2: int,
    threshold: float,
    preferred_clusters: list[int],
    k: int = 5,
    relax_thresholds=(0.32, 0.35, 0.40),
) -> pd.DataFrame:
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