"""This module provides preprocessing utilities for the Berlin Housing project, including scaling, variance thresholding, imputation, and pipelines."""

# Imports
from __future__ import annotations
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# Create a scaler object (StandardScaler or MinMaxScaler)
def make_scaler(kind: str = "standard"):
    """Create and return a scaler object based on the specified kind.

    Parameters
    ----------
    kind : str
        Type of scaler to create ('standard' or 'minmax').

    Returns
    -------
    scaler : StandardScaler or MinMaxScaler
        The scaler instance.
    """
    if kind == "standard":
        return StandardScaler()
    if kind == "minmax":
        return MinMaxScaler()
    raise ValueError("kind must be 'standard' or 'minmax'")

# Fit and apply scaler to numeric dataframe, return scaled dataframe and scaler
def fit_scale(df_num: pd.DataFrame, kind: str = "standard") -> tuple[pd.DataFrame, object]:
    """Fit a scaler to the numeric dataframe and transform it.

    Parameters
    ----------
    df_num : pd.DataFrame
        Numeric dataframe to scale.
    kind : str
        Type of scaler to use ('standard' or 'minmax').

    Returns
    -------
    tuple
        Tuple containing the scaled dataframe and the fitted scaler object.
    """
    scaler = make_scaler(kind)
    Xs = scaler.fit_transform(df_num)
    return pd.DataFrame(Xs, columns=df_num.columns, index=df_num.index), scaler

# Remove low-variance features using VarianceThreshold
def apply_variance_threshold(df_num: pd.DataFrame, threshold: float = 0.0) -> tuple[pd.DataFrame, VarianceThreshold]:
    """Apply variance thresholding to remove low-variance features.

    Parameters
    ----------
    df_num : pd.DataFrame
        Numeric dataframe to apply variance thresholding.
    threshold : float
        Features with variance below this threshold will be removed.

    Returns
    -------
    tuple
        Tuple containing the dataframe with selected features and the fitted VarianceThreshold object.
    """
    vt = VarianceThreshold(threshold=threshold)
    Xr = vt.fit_transform(df_num)
    cols = df_num.columns[vt.get_support()]
    return pd.DataFrame(Xr, columns=cols, index=df_num.index), vt

# Build preprocessing pipeline with imputation and optional scaling
def make_preprocessor(kind: str = "standard", impute_strategy: str = "median") -> Pipeline:
    """Create a preprocessing pipeline with imputation + optional scaling.

    Parameters
    ----------
    kind : {'standard', 'minmax', 'none'}
        Which scaler to use. 'none' disables scaling.
    impute_strategy : {'median', 'mean', 'most_frequent'}
        Strategy for SimpleImputer.

    Returns
    -------
    Pipeline
        A sklearn Pipeline with imputation and optional scaling steps.
    """
    if kind == "standard":
        scaler = StandardScaler()
    elif kind == "minmax":
        scaler = MinMaxScaler()
    elif kind == "none":
        scaler = None
    else:
        raise ValueError("kind must be 'standard', 'minmax', or 'none'")

    steps = [("imputer", SimpleImputer(strategy=impute_strategy))]
    if scaler is not None:
        steps.append(("scaler", scaler))
    return Pipeline(steps)

# Fit preprocessing pipeline and return transformed dataframe
def fit_transform_preprocessor(preproc: Pipeline, X_df: pd.DataFrame) -> tuple[pd.DataFrame, Pipeline]:
    """Fit the preprocessor and return a DataFrame with same index/columns.

    Parameters
    ----------
    preproc : Pipeline
        The preprocessing pipeline to fit.
    X_df : pd.DataFrame
        Input dataframe to transform.

    Returns
    -------
    tuple
        Tuple containing the transformed dataframe and the fitted pipeline.
    """
    X_tr = preproc.fit_transform(X_df)
    return pd.DataFrame(X_tr, columns=X_df.columns, index=X_df.index), preproc