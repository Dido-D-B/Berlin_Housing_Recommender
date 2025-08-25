# Frequently Asked Questions (FAQ)

> Tip: We group alternative phrasings with slashes so the “Explain This” assistant can match more ways of asking the same thing.

---
## Project Purpose / Ownership

### What is the purpose of this project? / What is the goal of this project? / Why does this project exist? / What problem does this project solve?

The project analyzes housing affordability across Berlin’s 12 districts (Bezirke) and 96 subdistricts (Ortsteile). It helps residents, researchers, and policymakers understand where rent is more/less affordable relative to local incomes, and why.

### Why Berlin? / Why focus only on Berlin housing?

Berlin faces unique housing pressures with rapid rent increases, diverse demographics, and strong policy debates. It provides a rich and timely case study for affordability analysis.

### Will the project expand to other cities?

Possibly. While the current focus is Berlin, the same framework could be adapted to other German or European cities if comparable datasets are available.

### Who owns or maintains this project? / Who is behind this project? / Who built this?

This project is created and maintained by **Dido De Boodt**, a Data Analyst & Data Science student based in Berlin. Dido combines skills in Python, SQL, Tableau, and Machine Learning with a strong background in customer care and social impact projects.

Feel free to reach out!

- [LinkedIn](https://www.linkedin.com/in/dido-de-boodt/)  
- [GitHub](https://github.com/Dido-D-B)  
- [Tableau Public](https://public.tableau.com/app/profile/dido.de.boodt/vizzes)

### Who is this for? / Who can benefit from this project?

Renters, families planning a move, journalists, urban planners, researchers, and policymakers—anyone needing a transparent, data‑driven view of Berlin housing affordability.

### Is this financial or legal advice? / Can I rely on this for contracts or rent negotiations?

No. This is an analytical tool for education and exploration. Always verify details with landlords, official sources, or legal counsel.

---
## Data Sources

### Where does the data come from? / What are the data sources? / Which datasets are used?

- **Mietspiegel 2023/2024** (cleaned street directories)
- **Census 2022** (Zensus 2022)
- **Income datasets** (district / subdistrict level)
- **Points of Interest (POIs)** from OpenStreetMap (OSM)
- **Employment & building stock** (official releases)
See `docs/README.md` and `docs/methodology.md` for file names and details.

### How often is the data updated? / How current is the data? / What is the update schedule?

This app shows **trends**, not real‑time listings. The Mietspiegel for 2024 was used as well as subdistrict data from 2024. The most recent Berlin Census contains data for 2022.

### What is the geographic coverage? / Does this cover all of Berlin?

Yes—12 Bezirke and 96 Ortsteile. Some indicators may be sparser in a few areas; see **Limitations**.

### Are the sources reliable? / How do you validate data quality?

Official/statistical sources were used where possible and run consistency checks during preprocessing. POI completeness depends on OSM community coverage.

### How are incomes measured? / Gross vs net income?

We use **median net household income** (after taxes and transfers). Gross incomes would overstate affordability.

### How are dwelling sizes chosen? / What is the reference apartment size?

We apply reference dwelling sizes (e.g., 1‑room = 40m², 2‑room = 60m², etc.) based on Mietspiegel conventions. See `docs/methodology.md` for the mapping.

### Why use Mietspiegel instead of rental listings?

Mietspiegel is an **official rent index**, updated every two years, designed to reflect typical rents without the short‑term volatility of listings like WG‑Gesucht or ImmobilienScout24. Listings are still useful for current snapshots but less stable for analysis.

---
## Methodology

### How was the data preprocessed? / What preprocessing steps were applied? / How did you prepare the data?

We standardized income, rent, and demographic variables, created ratios (e.g., rent-to-income, POIs per 1,000 residents), and applied scaling before PCA. Missing values were imputed or dropped depending on the variable, and outliers were examined for plausibility before inclusion.

### How was the data cleaned? / What cleaning steps were used? / Did you remove errors or duplicates?

Datasets from official sources were checked for consistency, column renaming and normalization (e.g., ü → ue for technical joins) were performed, and values were converted to standard units. Duplicate rows, invalid geometries, and misaligned district/subdistrict names were resolved.

### How was EDA (Exploratory Data Analysis) performed? / What visualizations were used? / How was data analysed? 

EDA included summary statistics, histograms, scatterplots, and correlation heatmaps. We also produced geospatial choropleth maps, PCA variance plots, and clustering radar charts to better understand housing, income, and amenity patterns across Berlin.

### How was the data extracted? / Where did the raw data come from technically? / How did you collect the datasets?

- Mietspiegel street directories were scraped and cleaned.
- Berlin open data (Census, employment, buildings, population) was downloaded as CSV.
- OpenStreetMap (OSM) points of interest were extracted with `osmnx` and `geopandas`.
All raw files were then merged into master tables at the district and subdistrict level.

### How is affordability calculated? / What is the rent‑to‑income ratio? / How do you measure affordability?

Affordability is based on **rent‑to‑income ratio**: estimated monthly rent ÷ median **net** household income (same geography). Categories:
- **Comfortable** ≤ 30%
- **Stretch** 31–40%
- **Tight** > 40%
(Thresholds documented in `docs/methodology.md`.)

### What classification is used for affordability? / How are affordability categories assigned?

Affordability is **rule‑based** using rent‑to‑income thresholds: Comfortable (≤30%), Stretch (31–40%), Tight (>40%). No predictive ML model is used for this classification.

### How do you estimate monthly rent? / What rent is used? / Cold vs warm rent?

We primarily use **cold rent (Kaltmiete)** from Mietspiegel. Estimated monthly rent = **rent per m² × reference dwelling size**. If warm rent (Warmmiete) data is available, we indicate it explicitly.

### What does Mietspiegel mean and why is it used? / Why rely on the rent index?

The **Mietspiegel** is Berlin’s official rent index, offering standardized, legally recognized rent levels by location, dwelling type, and vintage.

### How are POIs used? / Why include POIs? / What is POI density?

POIs (e.g., cafes, parks, supermarkets, transit) provide context for neighborhood amenities. We compute **densities per 1,000 residents** to compare fairly across areas.

### How do you aggregate Mietspiegel to subdistrict level? / How do street classes become a subdistrict number?

Street‑level classes are aggregated to the Ortsteil (subdistrict). See `docs/methodology.md` for the exact aggregation/weighting method and caveats near boundaries.

### Why combine data from different years? / Why are there temporal mismatches?

To produce stable indicators when sources publish on different cycles (e.g., Census 2022 vs. Mietspiegel 2023/2024). We document year differences and limitations in the methodology.

### What models are used? / What is the ML pipeline? / How were the subdistrict profiles created?

- **PCA** to reduce dimensionality (20 components, 90% variance)
- **KMeans** clustering (k=4: Balanced, Premium, Affordable, Strained)
See `docs/models.md` for details and metrics.

### How do you ensure fairness and interpretability? / How do you avoid bias?

We evaluate performance across subgroups, use transparent features (income, rent, demographics, POIs), and apply SHAP/feature importance for interpretability. See `docs/models.md`.

### Why use PCA? / Why reduce dimensions?

PCA helps summarize dozens of correlated features into fewer components while retaining most of the variance. This makes clustering more stable and interpretable.

### Why KMeans? / Why not DBSCAN or another clustering algorithm?

We tested multiple algorithms. KMeans (k=4) provided clear, interpretable clusters (Balanced, Premium, Affordable, Strained). DBSCAN produced highly uneven cluster sizes, making recommendations less useful.

### How do you validate clusters?

We evaluated cluster cohesion and separation with metrics like silhouette scores, and also validated interpretability through comparison with known district characteristics.

---
## App Usage

### How do I use the app to find affordable areas for my budget? / Search within my budget?

Enter your **monthly budget** and (optionally) rooms/household size. The app highlights Ortsteile where estimated rent is inside your range and shows the rent‑to‑income category.

### Can I filter by rooms / family size / apartment size?

Yes—filters help tailor estimates. Default reference sizes are documented in `docs/methodology.md`.

### Can I compare neighborhoods side‑by‑side? / How do I do comparisons?

Use the comparison view/table to select multiple Ortsteile or Bezirke and compare core metrics (rent/m², income, ratio, POIs, cluster).

### How do I interpret cluster profiles? / What do Balanced / Premium / Affordable / Strained mean?

They summarize patterns in affordability and context (income, rent, POIs). See the **Cluster Profiles** panel and `docs/models.md` for narrative descriptions.

### How are subdistricts recommended? / How does the recommender work?

The recommender matches your budget and household inputs against subdistrict profiles (rent, income, cluster). Results are filtered by affordability category and displayed in tables and maps.

### Does the app use cold or warm rent? / Can I switch?

Default is **cold rent (Kaltmiete)**. If warm rent is supported on a page, it’s labeled and selectable.

### Can I save or download results? / Export recommendations?

Most views support exporting tables or screenshots. Where available, use the download buttons.

### How do I interpret affordability colors on the map?

Green areas = Comfortable (≤30% rent‑to‑income), Orange = Stretch (31–40%), Red = Tight (>40%). These match the affordability thresholds.

### Can I search by district name or postal code?

Yes—search works by district and subdistrict names. Postal codes are not fully supported yet but may be added.

### Are results available in German as well?

Currently most explanations are in English. The UI supports German names, and German descriptions can be added through contributions.

### What is the Tableau dashboard? / How does it differ from the app?

The Tableau dashboard provides an interactive **story format** with maps and trends. It is optimized for desktop viewing, while a separate **mobile version** of the dashboards is embedded in the app for smaller screens. Both cover census, district, and affordability insights.

### Is the Explain This assistant available everywhere? / How do I open help?

Yes—open the **Help / Explain This** tab, or click the **💬 Explain** button to open the sidebar helper. Answers come from the local `docs/` knowledge base with citations.

### What if I don’t get an answer? / The assistant says it can’t find it—what do I do?

Add the missing explanation to `docs/glossary.md`, `docs/data_dictionary.md`, or `docs/methodology.md` (whichever fits). Refresh the app and ask again.

### Can I ask in German? / Do I have to use English?

English works best because the docs are written in English. German queries often work if the terms exist in the docs. You can add German entries to the docs for better coverage.

### How do I reset filters or start a new search?

Use the **Reset** button near the results table/maps or refresh the page.

### Where do the images come from? / Who created the visuals?

Most images (e.g., bears, icons, subdistrict and district illustrations) were generated or designed for this project. Image credits are noted in `docs/image_credits.json` and displayed within the app.

### How are cultural fact profiles created? / Where do the cultural facts come from?

Each district and subdistrict includes short cultural fact profiles. These are drawn from curated texts (Wikipedia summaries, local knowledge, or custom-written descriptions). They provide social and cultural context alongside affordability metrics.

### Can I contribute images or cultural texts? / How do I suggest new cultural facts?

Yes—open a GitHub issue or pull request with proposed images (with clear licensing) or cultural fact text. Contributions are welcome.

---
## Reliability & Limitations

### How accurate are the predictions and recommendations? / Can I trust the outputs?

They’re based on historical/official data and statistical models. Use them as guidance, then verify with current listings and local context.

### Why might results differ from WG‑Gesucht/ImmobilienScout24? / Why don’t prices match listings?

Listings reflect the **live market** with short‑term fluctuations, fees, and specifics. Our indicators show **structural/typical** conditions from official data.

### What are the main caveats? / Data limitations?

- Publication cycles differ (e.g., Zensus 2022 vs Mietspiegel 2024)
- OSM POI coverage varies by area
- Aggregation can hide within‑area variability
- No live listings; not legal/financial advice

### How current is the data? / Does it reflect 2025 prices?

The core data uses Mietspiegel 2024 and Census 2022. Affordability reflects structural conditions, not exact 2025 listings.

### Why are small subdistricts less reliable?

Some Ortsteile have fewer households or sparse POI data in OSM, so results there may be less robust. Interpret cautiously.

### Do you collect personal data? / Privacy / Cookies?

No personal information is collected by the app. See repository notes for any analytics settings (default: none).

---
## Technical & Reproducibility

### Can I reproduce the analysis? / Is the code public? / How do I run this locally?

Yes—clone the repo, create a virtual environment, install dependencies, and run the Streamlit app. See the main README.

### How do I cite sources? / Do answers include citations?

The assistant cites source files/sections (e.g., **Glossary.md**, **Methodology.md**) at the end of responses when relevant.

### Why does the assistant say “No documents found in ./docs”? / Docs not loading?

Launch the app from the project root **or** set `EXPLAIN_DOCS_DIR` to the absolute `docs/` path. After editing docs, refresh to re‑index.

### What embeddings or search do you use? / Can we switch to semantic search?

Currently TF‑IDF with boosts for glossary definitions. You can upgrade to embeddings + FAISS later while keeping the same `docs/` structure.

### What version of Python and Streamlit are used?

The project was developed in **Python 3.10+** with **Streamlit 1.33+**.

### What libraries are essential to the project?

Key libraries: Pandas, GeoPandas, Scikit‑learn, OSMnx, Matplotlib, Seaborn, Plotly, and Streamlit.

### Is the app open source? / Can I fork and reuse the code?

Yes—the repository is open on GitHub. You can fork it, adapt datasets, or extend features. See `LICENSE` for terms.

---
## Contribution

### How can I contribute or report an issue? / Suggest improvements? / Request features?

Open a GitHub issue or pull request. We welcome bug reports, new data sources, doc additions, and UX suggestions.

### Can I contribute translations? / Is there a plan for multilingual support?

Yes—adding German or other language texts to the docs or cultural facts is welcome.

### Can I add my own dataset (e.g., noise, air quality, green space)?

Yes—open a pull request with the dataset and integration notes. Contributions that enrich affordability context are encouraged.

### I found an error in the data—how do I report it? / Can you fix a wrong value?

Please open an issue with details (datasource, location, screenshot). We’ll verify and correct in the next update.

---
## Quick Answers (Cheat Sheet)

- **Mietspiegel** — Berlin’s official rent index (every ~2 years). 
- **Rent‑to‑Income** — Estimated monthly rent ÷ median net household income.
- **Affordability** — Comfortable ≤30%, Stretch 31–40%, Tight >40%.
- **POI Density** — Amenity counts per 1,000 residents.
- **Clusters** — KMean (k=4): Balanced, Premium, Affordable, Strained.
- **Coverage** — 12 Bezirke, 96 Ortsteile.