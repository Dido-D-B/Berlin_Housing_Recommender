"""
geo.py (utils)

Utilities for geographic data in the Streamlit app layer.

This module provides helpers to:
- Find district images by normalized filenames (handles umlauts/dashes/case)
- Detect latitude/longitude column names in DataFrames
- Pick a human-readable feature name from GeoJSON properties
- Resolve common locations of the Ortsteil boundary GeoJSON
- Add cluster-based colors to GeoJSON features for deck.gl layers
"""

# Imports
import os
import pandas as pd
from typing import List
from typing import Dict, Iterable, Set, Tuple
from utils.text import normalize_filename_base as _normalize_filename_base, district_slug, norm
from copy import deepcopy

# --- Unified geo helpers (merged) ---
# Common property keys for Ortsteil names in GeoJSONs
NAME_KEYS = ("ortsteil", "OTEIL", "Ortsteil", "ortsteil_name", "GEN", "BEZ", "name", "spatial_alias", "bez_name")

def load_geojson(path: str):
    """
    Load a boundary file from either GeoJSON (*.geojson/*.json) or GeoParquet (*.parquet)
    and return a GeoJSON-like dict (FeatureCollection).
    """
    import os, json
    p = str(path)
    ext = os.path.splitext(p)[1].lower()
    if ext == ".parquet":
        try:
            import geopandas as gpd
        except Exception as e:
            raise RuntimeError("geopandas is required to read .parquet boundary files") from e
        gdf = gpd.read_parquet(p)
        return json.loads(gdf.to_json())
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def feature_name(props: Dict) -> str:
    """
    Extract the Ortsteil (subdistrict) name from a GeoJSON feature's properties.

    Tries multiple known property keys (`ortsteil`, `Ortsteil`, `ortsteil_name`, etc.).
    If not found, searches nested dictionaries and finally returns the first non-empty string value.
    """
    # Prefer keys we commonly see
    for k in NAME_KEYS:
        if k in props and props[k]:
            return str(props[k]).strip()
    # Sometimes nested dicts contain the label
    for v in props.values():
        if isinstance(v, dict):
            for k in NAME_KEYS:
                if k in v and v[k]:
                    return str(v[k]).strip()
    # Fallback: first non-empty string value
    for v in props.values():
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

def subset_by_names(gj: Dict, allowed_names: Iterable[str]) -> Tuple[Dict, Set[str]]:
    """
    Create a subset of a GeoJSON FeatureCollection filtered by allowed names.

    Returns (subset_feature_collection, matched_name_keys)
    """
    allowed: Set[str] = {norm(x) for x in allowed_names if x}
    feats, matched = [], set()
    for ft in gj.get("features", []):
        props = ft.get("properties", {}) or {}
        fname = feature_name(props) or pick_feature_name(props)
        key = norm(fname)
        if key in allowed:
            feats.append(ft)
            matched.add(key)
    return {"type": "FeatureCollection", "features": feats}, matched

# Image directory resolution: default to streamlit_app/images unless DISTRICT_IMAGES_DIR is set.
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_IMAGES_DIR_DEFAULT = os.path.join(_BASE_DIR, "images")
IMAGES_DIR = os.environ.get("DISTRICT_IMAGES_DIR", _IMAGES_DIR_DEFAULT)

# Locate up to N district images by normalizing filenames (handles umlauts/dashes/case).
def find_district_images(bezirk: str, max_n: int = 4, images_dir: str | None = None) -> List[str]:
    """
    Return up to `max_n` image file paths for a district by normalizing filenames.

    Matches files like "Charlottenburg–Wilmersdorf1.jpeg" and
    "charlottenburg-wilmersdorf1.jpg" via a normalized root name.

    Args:
        bezirk (str): District name (e.g., "Charlottenburg-Wilmersdorf").
        max_n (int): Maximum number of images to return, in order 1..max_n.
        images_dir (str | None): Directory to search; defaults to `IMAGES_DIR`.

    Returns:
        list[str]: Image paths found in slot order (1..max_n), missing slots skipped.
    """
    if not bezirk:
        return []

    images_dir = images_dir or IMAGES_DIR
    slug = district_slug(bezirk)  # already normalized
    exts = {".jpeg", ".jpg", ".png"}

    # Map expected roots (slug1..slugN) to slots 0..N-1
    targets = {f"{slug}{i}": i - 1 for i in range(1, max_n + 1)}
    found: list[str | None] = [None] * max_n

    try:
        for fname in os.listdir(images_dir):
            root, ext = os.path.splitext(fname)
            if ext.lower() not in exts:
                continue
            norm_root = _normalize_filename_base(root)
            slot = targets.get(norm_root)
            if slot is not None and 0 <= slot < max_n:
                found[slot] = os.path.join(images_dir, fname)
    except FileNotFoundError:
        return []

    # Return only discovered files, in order
    return [p for p in found if p]

# Candidate column names considered when auto-detecting coordinates.
POSSIBLE_LAT = ["lat", "latitude", "y", "Lat"]
POSSIBLE_LON = ["lon", "longitude", "x", "Lon", "lng", "Lng"]

# Heuristically detect latitude/longitude column names in a dataframe.
def find_coords_columns(df: pd.DataFrame):
    """
    Heuristically detect latitude/longitude column names in a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        tuple[str | None, str | None]: (lat_col, lon_col) if detected, else (None, None).
    """
    lat_col, lon_col = None, None
    for c in POSSIBLE_LAT:
        if c in df.columns:
            lat_col = c
            break
    for c in POSSIBLE_LON:
        if c in df.columns:
            lon_col = c
            break
    return lat_col, lon_col

# Pick a human-readable feature name from GeoJSON properties using common keys.
def pick_feature_name(props: dict) -> str:
    """
    Return the best display name for a GeoJSON feature based on common keys
    found in Berlin Ortsteil boundary files. Falls back gracefully.
    """
    if not isinstance(props, dict):
        return ""
    # Preferred keys (ordered)
    candidates = [
        "ortsteil",          # normalized lower-case
        "Ortsteil",          # title case
        "ortsteil_name",     # simplified/parquet export
        "GEN",               # common in DE datasets
        "name",              # generic
        "BEZ",               # sometimes used
    ]
    for k in candidates:
        if k in props and props[k]:
            return str(props[k]).strip()
    # Fallback: first non-empty string value
    for v in props.values():
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

# Resolve the Ortsteil GeoJSON path by checking a few common project locations.
def resolve_ortsteil_geojson(project_root: str) -> str|None:
    """
    Resolve the Ortsteil GeoJSON path by checking common project locations.

    Args:
        project_root (str): Absolute path to the repository root.

    Returns:
        str | None: Path to the GeoJSON if found; otherwise None.
    """
    candidates = [
        os.path.join(project_root, "data", "berlin_ortsteil_boundaries.geojson"),
        os.path.join(project_root, "data", "processed", "berlin_ortsteil_boundaries.geojson"),
        os.path.join(project_root, "berlin_ortsteil_boundaries.geojson"),
    ]
    return next((p for p in candidates if os.path.isfile(p)), None)

# Add cluster color/style info to each GeoJSON feature (used by deck.gl layer).
def colorize_geojson_by_cluster(geojson_fc: dict, ortsteil_to_cluster: dict, palette: dict) -> dict:
    """
    Add per-feature fill colors and cluster IDs to a GeoJSON FeatureCollection.

    Uses `ortsteil_to_cluster` (keyed by normalized name) to look up cluster ID and applies
    a color from `palette`. Appends an alpha channel (80) for translucent fills.

    Args:
        geojson_fc (dict): Input FeatureCollection GeoJSON.
        ortsteil_to_cluster (dict): Mapping of normalized names → cluster ID.
        palette (dict): Mapping of cluster ID → [r, g, b].

    Returns:
        dict: A new FeatureCollection with enriched feature properties.
    """
    fc = {"type": "FeatureCollection", "features": []}
    for ft in geojson_fc.get("features", []):
        props = dict(ft.get("properties", {}) or {})
        name = feature_name(props) or pick_feature_name(props)
        cl = ortsteil_to_cluster.get(norm(name))
        rgb = palette.get(cl, [180, 180, 180])
        props["fill_color"] = rgb + [180]  # higher alpha so fills are clearly visible
        props["k4_cluster"] = cl
        new_ft = dict(ft)
        new_ft["properties"] = props
        fc["features"].append(new_ft)
    return fc