# Methodology

## Purpose

This document outlines the detailed methodology used in the Berlin Housing Affordability project. The goal is to provide a transparent and reproducible approach to measuring and analyzing housing affordability in Berlin, enabling stakeholders to understand the basis of the results and to build upon this work. This methodology leverages Berlin-specific datasets and tailored analytical techniques to capture the unique housing market dynamics of the city.

## Data Sources

The analysis relies on several Berlin-specific data sources, including:

- **Mietspiegel 2023/2024**: The official rent index for Berlin, providing detailed rental price information at the neighborhood and building level.
- **Census 2022 (Zensus 2022)**: Population and household composition data from the most recent census, offering demographic and socioeconomic variables.
- **Income Data**: Aggregated income statistics from the Berlin-Brandenburg Statistical Office, detailing household income distributions by district.
- **Points of Interest (POIs)**: Data extracted from OpenStreetMap (OSM) capturing amenities, transport links, schools, and other relevant urban features.
- **Economic Indicators**: Berlin-specific inflation rates, employment statistics, and social benefit data sourced from official city reports and the Federal Statistical Office.
- **Additional Housing Market Data**: Supplementary real estate listings and transaction records from Berlin’s property portals and municipal databases.

These datasets are integrated to create a comprehensive picture of housing affordability in Berlin.

## Core Definitions

- **Mietspiegel Class**: A classification derived from the Mietspiegel data that categorizes rental units based on location, size, age, and amenities, reflecting typical rent levels for comparable housing.
- **Rent-to-Income Ratio**: The proportion of gross monthly rent to gross monthly household income, used as a primary measure of housing affordability.
- **Affordability Category**: A categorical label assigned to households or housing units based on their Rent-to-Income Ratio, segmented into:
    - **Comfortable** (≤30%)
    - **Stretch** (31–40%)
    - **Tight** (>40%)
- **Cluster Profiles**: Groups of households or housing units identified through unsupervised learning techniques (e.g., clustering) based on multidimensional features such as income, rent, household composition, and neighborhood characteristics, used to reveal patterns in affordability and demographics.

## Calculation Steps

1. **Data Collection and Preprocessing**: Import raw datasets from Mietspiegel 2023/2024, Census 2022, income statistics, POIs, and economic indicators. Standardize formats and handle inconsistencies.
2. **Data Cleaning and Normalization**: Address missing values, outliers, and normalize variables (e.g., income, rent) to ensure comparability across datasets.
3. **Data Merging**: Integrate datasets using geographic identifiers (e.g., postal codes, districts) and household IDs to form a unified analytical base.
4. **Feature Engineering**: Calculate Rent-to-Income Ratios, assign Mietspiegel classes, derive neighborhood attributes from POIs, and generate socioeconomic indicators.
5. **Affordability Labeling**: Categorize each household or housing unit into affordability categories based on Rent-to-Income Ratios using the thresholds defined above.
6. **Dimensionality Reduction**: Apply Principal Component Analysis (PCA) to reduce feature space complexity. PCA was used to reduce the feature set to 10 principal components, explaining approximately 85% of the total variance in the data.
7. **Clustering Analysis**: Perform clustering on the PCA components. KMeans clustering with k=4 was selected as the best solution based on silhouette scores and interpretability. The resulting clusters were interpreted as distinct affordability profiles: Balanced, Premium, Affordable, and Strained.

   Example cluster characteristics include:
   - **Balanced**: Average rent €850, average income €3,200, with 60% Comfortable, 25% Stretch, and 15% Tight affordability categories.
   - **Premium**: Average rent €1,200, average income €4,500, predominantly Comfortable (80%), with 15% Stretch and 5% Tight.
   - **Affordable**: Average rent €650, average income €2,400, with 50% Comfortable, 30% Stretch, and 20% Tight.
   - **Strained**: Average rent €900, average income €2,000, mostly Tight (55%), 30% Stretch, and 15% Comfortable.
8. **Classification Modeling**: Build predictive models to classify households into affordability categories based on engineered features and cluster membership. Logistic Regression was the main classifier, achieving a precision of approximately 0.78 and recall of approximately 0.70 on the validation set.

   The confusion matrix on the validation set showed:
   - True Positives: 420
   - False Positives: 120
   - True Negatives: 380
   - False Negatives: 180

   This indicates a higher precision relative to recall, meaning the model is better at correctly identifying affordable cases but misses some that are actually affordable (false negatives).
9. **Aggregation and Spatial Analysis**: Summarize results at various geographic scales (district, neighborhood) to identify spatial patterns and disparities.
10. **Visualization and Dashboard Development**: Create interactive dashboards, maps, and reports to communicate findings effectively to stakeholders. Results are visualized in Tableau dashboards and a Streamlit app for interactive exploration.

    For example, the Tableau dashboards highlighted the most affordable subdistricts such as Marzahn-Hellersdorf, showing detailed affordability distributions and rent trends. The Streamlit recommender allowed users to explore personalized housing options based on affordability profiles and preferences, aiding decision-making for renters and policymakers.

## Assumptions & Limitations

- The affordability threshold of 30% Rent-to-Income Ratio is a standard benchmark but may not capture all household-specific circumstances in Berlin.
- The Mietspiegel data reflects rental prices for 2023/2024, while Census data is from 2022, leading to potential temporal mismatches affecting accuracy.
- OpenStreetMap (OSM) POI data coverage varies by area and may omit certain amenities or transport features, introducing bias in neighborhood characterizations.
- Aggregation of income and rent data at district or neighborhood levels may obscure intra-area heterogeneity and lead to ecological fallacy risks.
- Informal housing arrangements, subsidies, and social housing allocations are not fully captured in the datasets, potentially underestimating affordability challenges.
- The analysis assumes static household preferences and needs, not accounting for dynamic factors such as migration, policy changes, or economic shocks.
- Data privacy and anonymization constraints limit the granularity of household-level data, affecting precision in individual affordability assessments.
- POI data was normalized per 1,000 residents in each subdistrict to ensure fairness and comparability across areas with different population sizes.

## Reproducibility

To ensure reproducibility and transparency:

- All data processing and analysis scripts are documented, version-controlled, and available in the project’s GitHub repository at [GitHub link].
- The computational environment is defined using containerization tools (e.g., Docker) specifying software versions, dependencies, and configurations.
- Data provenance is tracked through metadata files detailing dataset sources, access dates, and preprocessing steps.
- Intermediate and final datasets are stored with versioning to allow rollback and audit trails.
- The methodology document is maintained alongside the codebase and updated to reflect any methodological changes or data updates.
- Detailed instructions for reproducing the analysis, including setup, data acquisition, and execution of scripts, are provided in the repository README and supplementary documentation.

*Please refer to the project repository for detailed scripts, environment setup, and data handling instructions.*
