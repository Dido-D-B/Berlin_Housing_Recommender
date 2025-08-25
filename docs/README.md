# Berlin Housing Affordability

## Project Overview
The Berlin Housing Affordability project analyzes housing affordability across Berlin subdistricts (Ortsteile) by integrating multiple datasets including the Mietspiegel (rent index) for 2024, Census 2022 data, points of interest (POIs), and income datasets. The goal is to provide a detailed understanding of affordability and amenities throughout Berlin’s neighborhoods, enabling informed decisions.

## Key Features
- Interactive data visualizations of rental and housing trends in Berlin
- Analysis of affordability based on income and rent statistics
- Neighborhood-level breakdowns and comparisons
- Affordability categories based on rent-to-income ratios
- Principal Component Analysis (PCA) and clustering for dimensionality reduction and pattern discovery
- Recommender system to suggest affordable housing options
- Explain This assistant to provide insights and explanations of the data and models
- Tableau dashboards for interactive exploration of the data and results
- Downloadable reports and data summaries

## Data Sources
- Mietspiegel 2023/2024 cleaned directories for rental price data
- Census 2022 demographic and housing data
- Income datasets at subdistrict level
- Points of Interest (POIs) from OpenStreetMap (OSM)
- Employment statistics and building stock data from official sources

## Methodology Summary
This project uses the rent-to-income ratio as a primary affordability indicator, categorizing affordability into three groups: affordable (≤30%), moderate (31–40%), and unaffordable (>40%). Dimensionality reduction is performed using Principal Component Analysis (PCA) to capture key variability in the data. KMeans clustering (k=4) identifies distinct neighborhood groups based on affordability and related features. Finally, Logistic Regression is applied for classification tasks to predict affordability categories based on input features.

## Outputs
- Tableau dashboards presenting comprehensive visualizations of affordability patterns, rental trends, and demographic factors
- Streamlit recommender application that helps users find affordable housing options tailored to their preferences
- Explain This assistant, an interactive tool that provides detailed explanations of data insights, model results, and methodology

## How to Use
1. Clone or download the repository.
2. Install required dependencies as detailed in the main README.
3. Run the Streamlit recommender app locally to explore affordable housing suggestions.
4. Open the Tableau dashboards to interactively analyze rental and affordability data.
5. Use the Explain This assistant to explore documentation and gain deeper understanding of the data and models.

## Limitations
- Data year mismatches between datasets (e.g., Census 2022 vs Mietspiegel 2023/2024) may affect temporal consistency.
- Aggregated data at subdistrict level rather than individual rental listings limits granularity.
- Variability in OpenStreetMap coverage may impact the completeness of POI data.

## Contact
For questions, feedback, or collaboration opportunities, please contact the project maintainer at [your-email@example.com].