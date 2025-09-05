# Berlin Housing Affordability Project

<img width="2936" height="1562" alt="image" src="https://github.com/user-attachments/assets/65b1abf6-d242-494a-b446-8ebd3cb4ca8f" />

This project explores **where to live in Berlin** by combining housing affordability with lifestyle and subdistrict characteristics.  

It integrates official open data, census statistics, and Mietspiegel (rent index) information with feature engineering and machine learning to build detailed **subdistrict profiles**.

The goal is to create a **data-driven recommender app** that helps residents and newcomers answer:

👉 *“Which Berlin subdistricts best match my budget and preferences?”*

## Project Overview

The project includes:

- Collecting and integrating multiple Berlin datasets (census, rents, income, employment, POIs, buildings, etc.).
- Cleaning and preprocessing data at both **district (Bezirk)** and **subdistrict (Ortsteil)** level.
- Feature engineering (POIs, rent-to-income ratios, etc.).
- Dimensionality reduction with **PCA** for clustering.
- **KMeans clustering** to segment subdistricts into profiles (Affordable, Vibrant, Balanced, Prestige).
- A **rule-based classification model** to predict affordability categories.
- An interactive **Streamlit app** to explore recommendations and data.
- Supplementary **Tableau dashboards** for visual storytelling.

## Repository Structure

```
Berlin_Housing_Affordability/
│
├── app/                 # Streamlit app
│   ├── charts/          # Saved plots from notebooks
│   ├── data/            # JSON files with cultural facts
│   ├── images/          # District images and Berlin Bear images home page
│   ├── pages/           # Multi-page UI (Recommender, Subdistrict Profiles, Census, Q&A, Bookmarks)
│   ├── services/        # Backend helpers for app
│   ├── utils/           # Reusable UI/data functions
│   └── Home/            # Main landing page for the Streamlit app
│
├── berlin_housing/      # Python package with modular code
│   ├── cleaning/        # Data cleaning scripts
│   ├── poi/             # POI feature extraction
│   └── tasks/           # Classification & clustering models
│
├── data/                # Raw & processed data
├── docs/                # Documentation, glossary, FAQ, reports
├── models/              # Saved ML model 
├── notebooks/           # Jupyter notebooks (EDA, experiments)
├── scripts/             # Standalone scripts (tables, PCA export, main)
├── sql/                 # SQL scripts for building/querying the database
├── tableau/             # Tableau dashboards
├── README.md/           # This file
└── requirements.txt/    # Project dependencies
```

## Data Collection & Cleaning

### Sources

- **Census 2022** (population, households, demographics)
- **Mietspiegel 2024** (official rent index with street-level granularity)
- **Income & Employment statistics** (by district and subdistrict)
- **Points of Interest (POI)**: cafés, restaurants, schools, libraries, nightlife, etc.
- **Geospatial data**: subdistrict boundaries, street directories
- **Public services**: libraries, cinemas, tourism, transport, etc.

### Cleaning

Cleaning modules are located in `berlin_housing/cleaning/`:

- `clean_bezirk.py`: processes district-level data
- `clean_ortsteil.py`: handles subdistrict-level data
- `clean_census.py`: integrates census 2022
- `clean_shared.py`: shared helper functions

Output: **master tables** at Bezirk and Ortsteil levels, ready for feature engineering.

## Feature Engineering

- **Rent-to-income ratios** for affordability classification  
- **POI densities** (cafés, restaurants, schools, etc.) per subdistrict  
- **Employment & household composition** features  
- **Normalized per-capita values** for fair comparisons  

Final features are consolidated into a single dataset (`berlin_final_master_table.csv`).

## Dimensionality Reduction: PCA

- Applied **Principal Component Analysis (PCA)** to reduce high-dimensional feature space.  
- Exported principal components with `scripts/pca_export.py`.  
- Retained enough components to explain **90–95% variance**.  

## Clustering: KMeans

- **KMeans** applied to PCA-transformed features.  
- Evaluated cluster quality with inertia and silhouette scores.  
- Chose **k = 4** clusters:
  1. **Affordable** – Low rents, modest POI density, lower incomes.  
  2. **Vibrant** – High POI density, young population, higher rents.  
  3. **Balanced** – Middle-income, mixed characteristics.  
  4. **Prestige** – Central, expensive, culturally dense.  

Clustering modules: `berlin_housing/tasks/clustering/`

## Classification: Rule-based Affordability

- Developed a **rule-based classifier** to label subdistricts into affordability categories.  
- Rules combine **rent-to-income ratios** with thresholds derived from Mietspiegel and census data.  
- Modules in `berlin_housing/tasks/classification/`.

## The Streamlit App

Located in the `app/` folder. Multi-page app with:

### **Home**
- Project introduction and navigation.

### **01_Recommender**
- Users input **income**, **household size**, and **preferences**.
- Returns **recommended subdistricts** ranked by affordability and POI profile.

### **02_Subdistrict Profiles**
- Interactive **map of Berlin** with tooltips.
- Subdistrict-level deep dive: demographics, rents, POIs, cultural facts.

### **03_Berlin Census**
- Census 2022 data explorer.
- Switch views (population, employment, etc.).

### **04_Behind the Data**
- Transparency page: methodology, data sources, key insights from EDA.
- Visualizations of PCA, clustering, and feature importance.

### **98_Q&A**
- Integrated “Explain This” helper for FAQs and glossary.

### **99_Bookmarks**
- User’s saved favorite subdistricts.

## Tableau Dashboards

Complementary dashboards (in `tableau/`) for storytelling:
- Berlin Census 2022 story (population, employment, housing).
- Interactive dashboards with annotations.

## Getting Started

### 1. Clone repo

```bash
git clone https://github.com/Dido-D-B/Berlin_Housing_Affordability.git
cd Berlin_Housing_Affordability
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app/Home.py
```

## Author

**Dido De Boodt**  
- [GitHub](https://github.com/Dido-D-B)  
- [LinkedIn](https://linkedin.com/in/dido-de-boodt)  
- [Tableau Public](https://public.tableau.com/app/profile/dido.deboodt)  

## Credits

This project would not have been possible without the use of **open data provided by the city of Berlin** and supporting tools and libraries.

### Data Sources
- Amt für Statistik Berlin-Brandenburg (Census 2022, demographic statistics)
- Berlin Mietspiegel 2023 & 2024 (official rent index)
- Berlin Open Data Portal (employment, income, public services, geospatial data)
- OpenStreetMap (Points of Interest)

### Tools & Libraries
- **Python** (pandas, numpy, scikit-learn, matplotlib, seaborn, geopandas, osmnx, streamlit)
- **Tableau** (for dashboard visualizations)
- **VS Code** (for development and modular structuring)

Special thanks to the open-source community for guidance and inspiration.

