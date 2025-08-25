# Imports
import os
import pandas as pd
from typing import List
from utils.text import normalize_filename_base as _normalize_filename_base, district_slug, norm
from copy import deepcopy

# Image directory resolution: default to streamlit_app/images unless DISTRICT_IMAGES_DIR is set.
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_IMAGES_DIR_DEFAULT = os.path.join(_BASE_DIR, "images")
IMAGES_DIR = os.environ.get("DISTRICT_IMAGES_DIR", _IMAGES_DIR_DEFAULT)

# Locate up to N district images by normalizing filenames (handles umlauts/dashes/case).
def find_district_images(bezirk: str, max_n: int = 4, images_dir: str | None = None) -> List[str]:
    """Return up to max_n image paths for a district by *normalizing* filenames.

    We match files like 'Charlottenburg–Wilmersdorf1.jpeg' (en‑dash) and
    'charlottenburg-wilmersdorf1.jpg' alike by normalizing the root name.

    Parameters
    ----------
    bezirk : str
        District name (e.g., "Charlottenburg-Wilmersdorf").
    max_n : int
        Maximum number of images to return, in order 1..max_n.
    images_dir : Optional[str]
        Directory to search. Defaults to IMAGES_DIR (env override supported).
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

# Candidate column names we consider when auto-detecting coordinates.
POSSIBLE_LAT = ["lat", "latitude", "y", "Lat"]
POSSIBLE_LON = ["lon", "longitude", "x", "Lon", "lng", "Lng"]

# Heuristically detect latitude/longitude column names in a dataframe.
def find_coords_columns(df: pd.DataFrame):
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
    for k in ("ortsteil", "OTEIL", "Ortsteil", "name", "spatial_alias", "bez_name"):
        if k in props and props[k]:
            return str(props[k])
    return ""

# Resolve the Ortsteil GeoJSON path by checking a few common project locations.
def resolve_ortsteil_geojson(project_root: str) -> str|None:
    candidates = [
        os.path.join(project_root, "data", "berlin_ortsteil_boundaries.geojson"),
        os.path.join(project_root, "data", "processed", "berlin_ortsteil_boundaries.geojson"),
        os.path.join(project_root, "berlin_ortsteil_boundaries.geojson"),
    ]
    return next((p for p in candidates if os.path.isfile(p)), None)

# Add cluster color/style info to each GeoJSON feature (used by deck.gl layer).
def colorize_geojson_by_cluster(geojson_fc: dict, ortsteil_to_cluster: dict, palette: dict) -> dict:
    fc = {"type": "FeatureCollection", "features": []}
    for ft in geojson_fc.get("features", []):
        props = dict(ft.get("properties", {}) or {})
        name = ""
        for k in ("ortsteil", "OTEIL", "Ortsteil", "name", "spatial_alias", "bez_name"):
            if k in props and props[k]:
                name = str(props[k]); break
        cl = ortsteil_to_cluster.get(norm(name))
        rgb = palette.get(cl, [180, 180, 180])
        props["fill_color"] = rgb + [80]
        props["k4_cluster"] = cl
        new_ft = dict(ft)
        new_ft["properties"] = props
        fc["features"].append(new_ft)
    return fc