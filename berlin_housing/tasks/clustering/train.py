"""Train KMeans on PCA features, write clustered master CSV, and save the model."""

# Imports
import joblib
from __future__ import annotations
from pathlib import Path
from .configs import DEFAULT_CFG
from .model import (
    ClusteringConfig,
    _load_data,
    _select_pc_matrix,
    _fit_kmeans,
)
 # Save trained model to disk with joblib
def save_model(model, path: Path) -> Path:
    """
    Save the trained clustering model to disk.

    Parameters:
    model: The trained clustering model object to be saved.
    path (Path): The file path where the model will be saved.

    Returns:
    Path: The path to the saved model file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return path

 # Run clustering training pipeline and optionally save KMeans model
def run_training(
    cfg: ClusteringConfig = DEFAULT_CFG,
    model_out: Path | None = Path("models/kmeans_k4.joblib"),
) -> Path:
    """
    Execute the clustering training pipeline and optionally save the trained KMeans model.

    Parameters:
    cfg (ClusteringConfig): Configuration parameters for clustering, including number of clusters and PCA prefix.
    model_out (Path | None): Optional path to save the trained KMeans model. If None, the model is not saved.

    Returns:
    Path: The path to the saved model if saved; otherwise, an empty Path object.
    """
    master, pca = _load_data(cfg)
    X, _ = _select_pc_matrix(pca, cfg.pc_prefix)

    km = _fit_kmeans(X, cfg.n_clusters, cfg.random_state)

    if model_out is not None:
        saved = save_model(km, model_out)
        print(f"[MODEL] Saved KMeans to: {saved}")
        return saved
    return Path()

# CLI
if __name__ == "__main__":
    run_training()