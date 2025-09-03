HOME_COPY = {
    "recommender": """
        * Provide your **net income** with an **affordability threshold** (e.g. 30–40%), desired subdistrict profiles (Balanced, Vibrant, Affordable, and Prestige), and other preferences.  
        * **Review results**: Sort & filter the recommended subdistricts. Open the **profile** of any result for more details, including cultural facts, images, and amenities.""",
    "subdistrict_profiles": """
        * Explore the subdistrict profiles on a map.
        * Discover subdistrict features like median income, mietspiegel class, and amenaties""",
    "census": """
        * Interactive Tableau dashboards at district level with demographics, income, housing stock, employment, amenities, and rent context.
        * Use filters to compare districts across categories and track trends from the 2022 Census combined with housing datasets.""",
    "data": """
        * Explore key insights from the exploratory data analysis of the data
        * Learn more about how the subdistricts were clustered and how we went from clusters to profiles
""",   
    "bookmarks": """
        * Use the project assistent to ask questions about this project in the Q&A section
        * Bookmark subdistricts to revisit and compare in the Bookmark section""",    
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
    "images": """
        - District and subdistrict cultural images used in this app were sourced from **Unsplash** (free to use, attribution required).
        - Credits are included below each image in the app, following the [Unsplash License](https://unsplash.com/license)."""
}