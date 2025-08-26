HOME_COPY = {
    "recommender": """
        * Provide your **net income** with an **affordability threshold** (e.g. 30–40%), 
        * **desired apartment size**, and desired subdistrict profiles (Balanced, Vibrant, Affordable, and Prestige).  
        * **Review results** — Sort & filter the recommended subdistricts. Open the **profile** of any result for more details, including cultural facts, images, and amenities.""",
    "subdistrict_profiles": """
        * Explore the subdistrict profiles and their subdistricts on a map.
        * Discover subdistrict features like median income, mietspiegel class, and amaneties (cafes, supermarkets, green spaces, and schools)""",
    "districts": """
        * Explore the district Tableau dashboard built with data from the most recent Berlin Census (2022)
        * Contains information about income, rent, population, employment, housing, etc. """,
    "census": """
        * Interactive Tableau story at district level with demographics, income, housing stock, employment, amenities, and rent context.
        * Use filters to compare districts across categories and track trends from the 2022 Census combined with housing datasets.""",
    "bookmarks": """
        * Save shortlists of subdistricts to revisit and compare.""",
    "datasources": """
        - **Mietspiegel 2024** — official Berlin rental reference (Senatsverwaltung). Cleaned street directory extracts used to map streets → **Mietspiegel classes** and typical rent bands:
        - **Census 2022** (Zensus; Amt für Statistik Berlin‑Brandenburg / Destatis):district level information - population, households, age, housing characteristics)
        - **District (Bezirk) tables** (sources: Amt für Statistik Berlin‑Brandenburg, Berlin Open Data): employment, buildings, rent per m2, median income
        - **Subdistrict (Ortsteil) & Features** (2024): age groups (groeped per 5 years), gender, rent, income, amenities, amenities densities
        - **Geospatial layers & external**:
            - OpenStreetMap (boundaries & POIs via OSMnx) — attribution: © OpenStreetMap contributors
            - Berlin Open Data portal datasets (amenities, environment, infrastructure)
            - (Optional cross‑checks) Public district summaries from Kaggle (descriptive only)""",
    "tools": """
        - **Python**: pandas, numpy, **geopandas**, shapely, pyproj, osmnx, requests, regex, **scikit‑learn** (StandardScaler, PCA, K‑Means, DBSCAN, Logistic Regression), matplotlib/plotly
        - **Data collection**: Selenium (Mietspiegel interactive table scraping), Berlin **WFS**/Open Data APIs, PDF → CSV extraction
        - **App & viz**: **Streamlit** (this app), **Tableau** (district dashboard), **Python** (exploratory and report notebooks)
        - **Workflow**: VS Code, virtual environments (py3.10), Jupyter, git/GitHub""",
    "notes": """
        - Harmonized district/subdistrict keys; normalized names (ä→ae, ö→oe, ü→ue, ß→ss). 
        - Derived indicators: youth/senior shares, POI per‑capita and per‑km² densities, rent‑to‑income ratios, affordability thresholds.
        - Consolidated into master tables for **EDA → PCA → clustering → recommender**.""",
    "images": """
        - District and subdistrict cultural images used in this app were sourced from **Unsplash** (free to use, attribution required).
        - Credits are included below each image in the app, following the [Unsplash License](https://unsplash.com/license)."""
}