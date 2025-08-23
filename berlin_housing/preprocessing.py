# berlin_housing/preprocessing.py
from __future__ import annotations
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

def make_scaler(kind: str = "standard"):
    if kind == "standard":
        return StandardScaler()
    if kind == "minmax":
        return MinMaxScaler()
    raise ValueError("kind must be 'standard' or 'minmax'")

def fit_scale(df_num: pd.DataFrame, kind: str = "standard") -> tuple[pd.DataFrame, object]:
    scaler = make_scaler(kind)
    Xs = scaler.fit_transform(df_num)
    return pd.DataFrame(Xs, columns=df_num.columns, index=df_num.index), scaler

def apply_variance_threshold(df_num: pd.DataFrame, threshold: float = 0.0) -> tuple[pd.DataFrame, VarianceThreshold]:
    vt = VarianceThreshold(threshold=threshold)
    Xr = vt.fit_transform(df_num)
    cols = df_num.columns[vt.get_support()]
    return pd.DataFrame(Xr, columns=cols, index=df_num.index), vt


# --- Unified preprocessing pipeline (imputation + optional scaling) ---

def make_preprocessor(kind: str = "standard", impute_strategy: str = "median") -> Pipeline:
    """Create a preprocessing pipeline with imputation + optional scaling.

    Parameters
    ----------
    kind : {'standard', 'minmax', 'none'}
        Which scaler to use. 'none' disables scaling.
    impute_strategy : {'median', 'mean', 'most_frequent'}
        Strategy for SimpleImputer.
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


def fit_transform_preprocessor(preproc: Pipeline, X_df: pd.DataFrame) -> tuple[pd.DataFrame, Pipeline]:
    """Fit the preprocessor and return a DataFrame with same index/columns.

    Returns
    -------
    X_tr_df : pd.DataFrame
        Transformed features (imputed + scaled if configured)
    preproc : Pipeline
        The fitted preprocessing pipeline
    """
    X_tr = preproc.fit_transform(X_df)
    return pd.DataFrame(X_tr, columns=X_df.columns, index=X_df.index), preproc