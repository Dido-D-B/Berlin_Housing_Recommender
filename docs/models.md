# Models Used in the Berlin Housing Affordability Project

## Overview
This document provides an outline of the various models applied in the Berlin Housing Affordability project. Each section includes a brief description of the model, its purpose, and specific details related to implementation, parameters, and results.

## Principal Component Analysis (PCA)
### Purpose
PCA is used for dimensionality reduction and to identify the main components that explain the variance in the housing data.

### Implementation Details
- Number of components chosen: 20
- Explained variance ratio: Approximately 90%
- Preprocessing steps: Scaled inputs using standard scaling to normalize features before applying PCA

### Results
- Interpretation of principal components: The 20 components capture the majority of variance in housing-related features, effectively summarizing income, rent levels, demographic factors, and points of interest.
- Impact on subsequent modeling: PCA outputs were used to reduce feature dimensionality, improving model efficiency and reducing multicollinearity in clustering and classification tasks.

## Clustering

### KMeans
#### Purpose
KMeans clustering is applied to group similar housing units based on selected features.

#### Implementation Details
- Number of clusters: 4
- Initialization method: k-means++
- Features used: Income, Mietspiegel (rent index), demographics, points of interest (POIs)

#### Results
- Cluster characteristics:
  - Balanced: Areas with moderate income and rent levels, stable demographics.
  - Premium: High-income neighborhoods with higher rents and upscale amenities.
  - Affordable: Lower-income areas with below-average rents and diverse demographics.
  - Strained: Regions with economic challenges, lower income, but higher rent burdens.
- Visualization: Cluster profiles were visualized using scatter plots and heatmaps highlighting feature distributions across clusters.

### DBSCAN
#### Purpose
DBSCAN is used to identify clusters of arbitrary shape and detect outliers in the housing data.

#### Implementation Details
- Epsilon (eps) value: 0.5
- Minimum samples: 5
- Features used: Same as KMeans (income, Mietspiegel, demographics, POIs)

#### Results
- Number and size of clusters: DBSCAN identified several small clusters but produced a large number of noise points.
- Outlier detection: Many data points were labeled as noise, making the clustering less interpretable compared to KMeans.
- Overall, DBSCAN was less effective for this dataset due to high noise and complexity.

## Classification
### Purpose
Classification models are employed to predict housing affordability categories or other relevant labels.

### Models Used
- Logistic Regression as the main model
- Random Forest tested as an alternative

### Implementation Details
- Features selected: Income, Mietspiegel class, rent-to-income ratio, demographics, points of interest (POIs)
- Training/test split: 70/30 split
- Hyperparameter tuning: GridSearchCV used for optimizing model parameters

### Results
- Performance metrics:
  - Precision: Approximately 0.78
  - Recall: Approximately 0.70
  - F1-score: Approximately 0.74
- Confusion matrix: The model showed balanced performance across affordability categories, with most misclassifications occurring between adjacent affordability levels.

## Notes on Fairness & Interpretability
- Fairness considerations: Analysis revealed disparities in income and rent distributions across different Berlin districts, raising concerns about potential bias in model predictions. Efforts were made to assess and mitigate bias by examining model performance across subgroups and ensuring equitable treatment.
- Interpretability methods: Feature importance analysis and SHAP (SHapley Additive exPlanations) values were employed to explain model decisions, highlighting key drivers such as income levels, rent-to-income ratio, and demographic variables.
- Limitations: While interpretability tools provided insights, some complex interactions remain challenging to fully explain. Ongoing work aims to enhance transparency and fairness in model deployment.

---

*Please fill in the placeholders above with specific details from your project to complete this documentation.*
