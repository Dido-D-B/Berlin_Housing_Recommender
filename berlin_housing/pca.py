# berlin_housing/pca.py
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

def fit_pca(X: pd.DataFrame, n_components=None, random_state: int | None = 42):
    pca = PCA(n_components=n_components, random_state=random_state)
    Z = pca.fit_transform(X)
    return pca, Z

def pca_2d_for_viz(X: pd.DataFrame, labels: pd.Series | None = None) -> pd.DataFrame:
    pca, Z = fit_pca(X, n_components=2)
    out = pd.DataFrame(Z, columns=["PC1", "PC2"], index=X.index)
    if labels is not None:
        out["ortsteil"] = labels.values
    return out, pca.explained_variance_ratio_.tolist()

def pca_until_variance(X: pd.DataFrame, target: float = 0.90, random_state: int | None = 42):
    pca = PCA(random_state=random_state).fit(X)
    cum = np.cumsum(pca.explained_variance_ratio_)
    k = int(np.argmax(cum >= target) + 1)
    Z = pca.transform(X)[:, :k]
    cols = [f"PC{i+1}" for i in range(k)]
    return pd.DataFrame(Z, columns=cols, index=X.index), pca, cum.tolist()