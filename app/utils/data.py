# Import
import json
import os
import sys
import streamlit as st
from berlin_housing.io import load_master
from utils.geo import find_coords_columns, resolve_ortsteil_geojson

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# load JSON safely
def load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

@st.cache_data(show_spinner=False)    
def _load():
    df = load_master()
    pop_col = "total_population" if "total_population" in df.columns else None
    # Keep only columns we need for exploration
    base_cols = [c for c in [
        "bezirk", "ortsteil", "k4_cluster",
        "subdistrict_avg_median_income_eur",
        "subdistrict_avg_mietspiegel_classification",
        "cafes", "restaurant", "bar", "nightclub", "supermarket", "green_space", "schools",
    ] if c in df.columns]
    # Add population if present
    if pop_col and pop_col in df.columns:
        base_cols.append(pop_col)
    # include any coordinate columns if present
    lat_col, lon_col = find_coords_columns(df)
    coord_cols = [c for c in [lat_col, lon_col] if c]
    use_cols = list(dict.fromkeys(base_cols + coord_cols))
    # resolve geojson path via helper
    geo_path = resolve_ortsteil_geojson(PROJECT_ROOT)

    return df[use_cols].copy(), lat_col, lon_col, geo_path    