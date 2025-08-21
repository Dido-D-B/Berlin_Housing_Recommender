import os

# repo root = parent of this file's directory
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# --- Global flags ---
# If True, the builder will prefer scraping POIs via poi.py (using boundaries)
# instead of loading a precomputed CSV. The CSV path below is then used as a cache/output.
FORCE_SCRAPE_POI = True

# District-level (Bezirk)
BRIDGES_CSV      = os.path.join(DATA_DIR, "berlin_bridges.csv")
CINEMAS_CSV      = os.path.join(DATA_DIR, "berlin_cinemas.csv")
LIBRARIES_CSV    = os.path.join(DATA_DIR, "berlin_libraries_2023.csv")
CARS_CSV         = os.path.join(DATA_DIR, "berlin_passenger_cars.csv")
TOILETS_CSV      = os.path.join(DATA_DIR, "berlin_public_toilets.csv")
TREES_CSV        = os.path.join(DATA_DIR, "berlin_trees.csv")
CENSUS_DISTRICT  = os.path.join(DATA_DIR, "berlin_census_2022.csv")
TOURISM_TOTALS   = os.path.join(DATA_DIR, "berlin_tourism_guests_overnightstays_2023_2024.csv")
TOURISM_CHANGES  = os.path.join(DATA_DIR, "berlin_tourism_overnightstays_changes_2023_2024.csv")

 # Ortsteil-level
ORTS_POP_CSV     = os.path.join(DATA_DIR, "berlin_ortsteil_population.csv")  # or use subdistrict_2020 file
ORTS_RI_CSV      = os.path.join(DATA_DIR, "berlin_ortsteil_rent_income.csv")

# Ortsteil boundaries for POI scraper
ORTSTEIL_BOUNDARIES_PATH = os.path.join(DATA_DIR, "berlin_ortsteil_boundaries.geojson")
ORSTEIL_NAME_FALLBACKS = ["OTEIL", "Ortsteil", "ORT_NAME", "name"]  # tried in this order
ORTSTEIL_NAME_COLUMN = "OTEIL"  # preferred name; builder may fall back to the list above

# POI scraper settings (used by poi.py)
POI_RATE_LIMIT_S = 1.5
POI_RETRIES = 3
POI_BACKOFF_S = 2.0

# POI counts cache (written by the scraper; can be reused on subsequent runs)
# When FORCE_SCRAPE_POI=True, this path is treated as an output location.
POI_COUNTS_CSV = os.path.join(PROCESSED_DIR, "poi_counts_per_ortsteil.csv")

# Processed outputs (what we save after building)
BEZIRK_MASTER_OUT   = os.path.join(PROCESSED_DIR, "bezirk_master.csv")
ORTSTEIL_MASTER_OUT = os.path.join(PROCESSED_DIR, "ortsteil_master.csv")
FINAL_MASTER_OUT    = os.path.join(PROCESSED_DIR, "final_master.csv")