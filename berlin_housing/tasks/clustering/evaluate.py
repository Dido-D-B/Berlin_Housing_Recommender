import pandas as pd
from __future__ import annotations
from sklearn.preprocessing import MinMaxScaler

# Create a cluster profile table by computing mean feature values per cluster
def make_profile_table(
    merged_df: pd.DataFrame, cluster_col: str, features: list[str]
) -> pd.DataFrame:
    """Return mean feature table per cluster."""
    return merged_df.groupby(cluster_col)[features].mean(numeric_only=True)

# Scale cluster profiles to 0–1 range using MinMaxScaler
def scale_profiles(profile_df: pd.DataFrame) -> pd.DataFrame:
    scaler = MinMaxScaler()
    return pd.DataFrame(
        scaler.fit_transform(profile_df),
        columns=profile_df.columns,
        index=profile_df.index,
    )