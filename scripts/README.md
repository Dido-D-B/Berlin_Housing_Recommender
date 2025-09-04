# scripts

This folder contains **standalone Python scripts** used during the Berlin Housing Affordability project. 

They are not part of the main `berlin_housing` package but support data preparation, exports, and orchestration tasks.

## Files

### `main.py`

Entry point for running multiple project steps in sequence.  

Useful for orchestrating cleaning, feature engineering, and modeling pipelines.

### `tables.py`

Generates and exports key tables from the cleaned datasets.  

Acts as a bridge between raw/cleaned data and the database.

### `pca_export.py`

Handles **Principal Component Analysis (PCA)** dimensionality reduction and exports the transformed data.  

Used mainly for clustering experiments.

## Notes

- Scripts in this folder are typically run manually or as part of ad-hoc experiments.
- For reusable logic, prefer importing functions from the `berlin_housing` package.
- Example:
  ```bash
  python scripts/tables.py
  python scripts/pca_export.py
  ```