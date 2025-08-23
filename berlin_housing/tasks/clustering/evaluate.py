"""Evaluation and profiling helpers for clustering."""
from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def make_profile_table(
    merged_df: pd.DataFrame, cluster_col: str, features: list[str]
) -> pd.DataFrame:
    """Return mean feature table per cluster."""
    return merged_df.groupby(cluster_col)[features].mean(numeric_only=True)


def scale_profiles(profile_df: pd.DataFrame) -> pd.DataFrame:
    scaler = MinMaxScaler()
    return pd.DataFrame(
        scaler.fit_transform(profile_df),
        columns=profile_df.columns,
        index=profile_df.index,
    )