

"""
Clustering module for Berlin Housing project.

Runs KMeans on PCA features (PC1..PCn) to assign a cluster to each
subdistrict (ortsteil), merges labels back into the master table, and
writes an updated CSV.

You can import and call `run()` from other modules, or execute this file
as a script.
"""
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

# ---------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------

@dataclass
class ClusteringConfig:
    master_csv: Path = Path("data/processed/final_master.csv")
    pca_csv: Path = Path("data/modeling/berlin_pca/berlin_subdistricts_pca.csv")
    output_csv: Path = Path("data/processed/final_master_with_k4_clusters.csv")
    id_col: str = "ortsteil"
    pc_prefix: str = "PC"
    n_clusters: int = 4
    random_state: int = 42


# ---------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------

def _load_data(cfg: ClusteringConfig) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load master and PCA dataframes from disk."""
    master = pd.read_csv(cfg.master_csv)
    pca = pd.read_csv(cfg.pca_csv)
    return master, pca


def _select_pc_matrix(pca_df: pd.DataFrame, pc_prefix: str) -> Tuple[np.ndarray, List[str]]:
    """Return X matrix of principal components and the list of PC columns."""
    pc_cols = [c for c in pca_df.columns if c.startswith(pc_prefix)]
    if not pc_cols:
        raise ValueError(f"No PCA columns found with prefix '{pc_prefix}'.")
    X = pca_df[pc_cols].values
    return X, pc_cols


def _fit_kmeans(X: np.ndarray, n_clusters: int, random_state: int) -> KMeans:
    """Fit KMeans and return the model."""
    model = KMeans(n_clusters=n_clusters, random_state=random_state)
    model.fit(X)
    return model


def _evaluate_clusters(X: np.ndarray, labels: np.ndarray) -> dict:
    """Compute common clustering quality metrics for quick logging."""
    # Guard against degenerate labels
    if len(np.unique(labels)) < 2:
        return {"silhouette": np.nan, "calinski_harabasz": np.nan, "davies_bouldin": np.nan}
    return {
        "silhouette": float(silhouette_score(X, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(X, labels)),
        "davies_bouldin": float(davies_bouldin_score(X, labels)),
    }


def run(cfg: ClusteringConfig = ClusteringConfig()) -> pd.DataFrame:
    """
    Execute the KMeans (k=4 by default) pipeline and write the updated
    master CSV with a new `k4_cluster` column.

    Returns
    -------
    pd.DataFrame
        The merged dataframe that was written to `cfg.output_csv`.
    """
    # Load data
    master, pca = _load_data(cfg)

    # Extract PC matrix
    X, pc_cols = _select_pc_matrix(pca, cfg.pc_prefix)

    # Keep a copy of identifiers
    ids = pca[cfg.id_col].copy()

    # Fit KMeans
    kmeans = _fit_kmeans(X, cfg.n_clusters, cfg.random_state)
    labels = kmeans.labels_

    # Optional: quick evaluation for logs
    metrics = _evaluate_clusters(X, labels)
    print(
        "[KMeans] k=%d | silhouette=%.3f | calinski=%.1f | davies_bouldin=%.3f"
        % (
            cfg.n_clusters,
            metrics.get("silhouette", np.nan),
            metrics.get("calinski_harabasz", np.nan),
            metrics.get("davies_bouldin", np.nan),
        )
    )

    # Prepare labels dataframe
    labels_df = pd.DataFrame({cfg.id_col: ids.values, f"k{cfg.n_clusters}_cluster": labels})

    # Merge into master table
    merged = master.merge(labels_df, on=cfg.id_col, how="left")

    # Persist
    cfg.output_csv.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(cfg.output_csv, index=False)
    print(f"[WRITE] Wrote clustered master to: {cfg.output_csv}")

    return merged


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Allow running this file directly: `python -m berlin_housing.tasks.clustering.model`
    _ = run()