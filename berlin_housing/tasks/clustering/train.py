"""Train KMeans on PCA features, write clustered master CSV, and save the model."""
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
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return path

 # Run clustering training pipeline and optionally save KMeans model
def run_training(
    cfg: ClusteringConfig = DEFAULT_CFG,
    model_out: Path | None = Path("models/kmeans_k4.joblib"),
) -> Path:
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