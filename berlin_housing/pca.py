"""PCA utilities for the Berlin Housing project.

This module provides functions to fit PCA models, generate 2D visualizations,
and reduce data dimensions until a target explained variance is reached.
"""

# Imports
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

# Fit PCA on dataframe X and return fitted model and transformed matrix
def fit_pca(X: pd.DataFrame, n_components=None, random_state: int | None = 42):
    """
    Fit a PCA model to the input DataFrame and transform the data.

    Parameters
    ----------
    X : pd.DataFrame
        The input data to fit the PCA model on.
    n_components : int or None, optional
        Number of principal components to keep. If None, all components are kept.
    random_state : int or None, optional
        Random seed for reproducibility.

    Returns
    -------
    pca : sklearn.decomposition.PCA
        The fitted PCA model.
    Z : np.ndarray
        The transformed data matrix after applying PCA.
    """
    pca = PCA(n_components=n_components, random_state=random_state)
    Z = pca.fit_transform(X)
    return pca, Z

# Reduce to 2D PCA for visualization and return dataframe with optional labels
def pca_2d_for_viz(X: pd.DataFrame, labels: pd.Series | None = None) -> pd.DataFrame:
    """
    Perform PCA reducing data to 2 components for visualization purposes.

    Parameters
    ----------
    X : pd.DataFrame
        Input data to be reduced to 2 principal components.
    labels : pd.Series or None, optional
        Optional labels to add as a column to the returned DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the two principal components as columns 'PC1' and 'PC2'.
        If labels are provided, an additional column 'ortsteil' is included.
    list of float
        Explained variance ratio of the two principal components.
    """
    pca, Z = fit_pca(X, n_components=2)
    out = pd.DataFrame(Z, columns=["PC1", "PC2"], index=X.index)
    if labels is not None:
        out["ortsteil"] = labels.values
    return out, pca.explained_variance_ratio_.tolist()

# Run PCA until target explained variance is reached; return reduced data, model, cumulative variance
def pca_until_variance(X: pd.DataFrame, target: float = 0.90, random_state: int | None = 42):
    """
    Apply PCA to reduce dimensionality until the cumulative explained variance reaches a target threshold.

    Parameters
    ----------
    X : pd.DataFrame
        Input data to apply PCA on.
    target : float, optional
        Target cumulative explained variance ratio to reach (default is 0.90).
    random_state : int or None, optional
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the transformed data with components selected to reach the target variance.
    sklearn.decomposition.PCA
        The fitted PCA model.
    list of float
        Cumulative explained variance ratio for all components.
    """
    pca = PCA(random_state=random_state).fit(X)
    cum = np.cumsum(pca.explained_variance_ratio_)
    k = int(np.argmax(cum >= target) + 1)
    Z = pca.transform(X)[:, :k]
    cols = [f"PC{i+1}" for i in range(k)]
    return pd.DataFrame(Z, columns=cols, index=X.index), pca, cum.tolist()