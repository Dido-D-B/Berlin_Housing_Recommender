from pathlib import Path
from ..model import ClusteringConfig

# Central default configuration for clustering tasks
DEFAULT_CFG = ClusteringConfig(
    master_csv=Path("data/processed/final_master.csv"),
    pca_csv=Path("data/modeling/berlin_pca/berlin_subdistricts_pca.csv"),
    output_csv=Path("data/processed/final_master_with_k5_clusters.csv"),
    id_col="ortsteil",
    pc_prefix="PC",
    n_clusters=4,
    random_state=42,
)