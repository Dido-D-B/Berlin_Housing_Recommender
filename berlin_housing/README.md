# berlin_housing

This folder contains the **Python package** for the Berlin Housing Affordability project.  

It provides modular code for data cleaning, feature engineering, and machine learning tasks (classification, clustering, recommendation).

## Structure

### `cleaning/`

Scripts for cleaning and preparing raw datasets:

- `clean_bezirk.py` – Cleaning district-level (Bezirk) data.  
- `clean_census.py` – Processing Berlin Census data.  
- `clean_ortsteil.py` – Cleaning subdistrict (Ortsteil) data.  
- `clean_shared.py` – Shared cleaning functions across datasets.  

### `poi/`

Code related to **Points of Interest (POI)**:

- `poi.py` – Extracting and processing POI data for subdistrict features.  

### `tasks/classification/`

Code for supervised ML tasks:

- `affordability.py` – Classification model for affordability categories.  
- `recommend.py` – Logic for generating subdistrict recommendations.  

### `tasks/clustering/`

Code for unsupervised ML tasks:

- `config.py` – Configurations for clustering.  
- `configs/default.py` – Default experiment settings.  
- `model.py` – Clustering models (e.g., KMeans, DBSCAN).  
- `train.py` – Training clustering models.  
- `predict.py` – Predicting cluster assignments.  
- `evaluate.py` – Evaluation of clustering models.  
- `viz.py` – Visualization utilities.  

## Notes
- Each submodule can be imported directly, e.g.:
  ```python
  from berlin_housing.cleaning.clean_bezirk import load_bezirk_data
  from berlin_housing.tasks.clustering.model import train_kmeans
  ```
- Shared constants and configurations live inside `config.py` or the `configs/` subfolder.
- This package is designed for **modularity**: cleaning → feature engineering → ML models → recommendations.