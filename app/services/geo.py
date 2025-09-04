"""
geo.py

Utility functions for handling geographic data in the Berlin Housing Affordability project.

This module provides:
- Normalization of German names (handling umlauts and case).
- Extraction of Ortsteil (subdistrict) names from GeoJSON feature properties.
- Loading of GeoJSON FeatureCollections.
- Subsetting GeoJSONs by a given list of subdistrict names.

These helpers ensure consistent matching of geographic entities across datasets and the app.
"""

# Imports
from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterable, Set, Tuple
import json

# Simple normalizer (handles umlauts + case) so names match reliably 
_UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
                          "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"})

def norm(s: str) -> str:
    """
    Normalize a string for consistent matching of German names.

    - Strips leading/trailing spaces
    - Converts to lowercase
    - Translates German umlauts (ä → ae, ö → oe, ü → ue, ß → ss)

    Args:
        s (str): Input string.

    Returns:
        str: Normalized string.
    """
    return (s or "").strip().lower().translate(_UMLAUT)

# Common property keys for Ortsteil names in GeoJSONs
NAME_KEYS = ("ortsteil", "OTEIL", "Ortsteil", "name", "spatial_alias", "bez_name")

def feature_name(props: Dict) -> str:
    """
    Extract the Ortsteil (subdistrict) name from a GeoJSON feature's properties.

    Tries multiple known property keys (`ortsteil`, `Ortsteil`, `name`, etc.).
    If not found, searches nested dictionaries.

    Args:
        props (dict): Properties of a GeoJSON feature.

    Returns:
        str: Extracted name, or an empty string if not found.
    """
    for k in NAME_KEYS:
        if k in props and props[k]:
            return str(props[k])
    # sometimes nested dicts contain the label
    for v in props.values():
        if isinstance(v, dict):
            for k in NAME_KEYS:
                if k in v and v[k]:
                    return str(v[k])
    return ""

# Load geojson
def load_geojson(path: str | Path) -> Dict:
    """
    Load a FeatureCollection GeoJSON file from disk.

    Args:
        path (str | Path): Path to the GeoJSON file.

    Returns:
        dict: Parsed GeoJSON dictionary.

    Raises:
        ValueError: If the file is not a FeatureCollection GeoJSON.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        gj = json.load(f)
    if gj.get("type") != "FeatureCollection":
        raise ValueError("Expected a FeatureCollection GeoJSON")
    return gj

# Return new feature collection
def subset_by_names(gj: Dict, allowed_names: Iterable[str]) -> Tuple[Dict, Set[str]]:
    """
    Create a subset of a GeoJSON FeatureCollection filtered by allowed names.

    Args:
        gj (dict): Input GeoJSON FeatureCollection.
        allowed_names (Iterable[str]): List or set of names to match.

    Returns:
        tuple:
            - dict: New GeoJSON FeatureCollection containing only matched features.
            - set[str]: Normalized names that were matched.
    """
    allowed: Set[str] = {norm(x) for x in allowed_names if x}
    feats, matched = [], set()
    for ft in gj.get("features", []):
        props = ft.get("properties", {}) or {}
        if norm(feature_name(props)) in allowed:
            feats.append(ft)
            matched.add(norm(feature_name(props)))
    return {"type": "FeatureCollection", "features": feats}, matched