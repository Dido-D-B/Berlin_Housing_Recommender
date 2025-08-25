"""Assign clusters using a saved KMeans model to a PCA CSV (for app use)."""
import pandas as pd
import joblib
from __future__ import annotations
from pathlib import Path
from .model import ClusteringConfig, _select_pc_matrix
from .configs import DEFAULT_CFG

def assign_clusters(
    pca_csv: Path | None = None,
    model_path: Path = Path("../models/kmeans_k4.joblib"),
    cfg: ClusteringConfig = DEFAULT_CFG,
) -> pd.DataFrame:
    if pca_csv is None:
        pca_csv = cfg.pca_csv
    pca = pd.read_csv(pca_csv)

    km = joblib.load(model_path)
    X, _ = _select_pc_matrix(pca, cfg.pc_prefix)
    labels = km.predict(X)

    out = pca[[cfg.id_col]].copy()
    out[f"k{cfg.n_clusters}_cluster"] = labels
    return out

# CLI
if __name__ == "__main__":
    df = assign_clusters()
    print(df.head())