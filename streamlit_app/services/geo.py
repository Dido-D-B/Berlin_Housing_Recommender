from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Iterable, Set, Tuple

# --- simple normalizer (handles umlauts + case) so names match reliably ---
_UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
                          "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"})
def norm(s: str) -> str:
    return (s or "").strip().lower().translate(_UMLAUT)

# Common property keys for Ortsteil names in GeoJSONs
NAME_KEYS = ("ortsteil", "OTEIL", "Ortsteil", "name", "spatial_alias", "bez_name")

def feature_name(props: Dict) -> str:
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

# ---------- public helpers your page imports ----------

def load_geojson(path: str | Path) -> Dict:
    """Load a FeatureCollection GeoJSON from disk."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        gj = json.load(f)
    if gj.get("type") != "FeatureCollection":
        raise ValueError("Expected a FeatureCollection GeoJSON")
    return gj

def subset_by_names(gj: Dict, allowed_names: Iterable[str]) -> Tuple[Dict, Set[str]]:
    """
    Return a new FeatureCollection containing only features whose name
    matches one of allowed_names (after normalization). Also return the
    set of matched normalized names.
    """
    allowed: Set[str] = {norm(x) for x in allowed_names if x}
    feats, matched = [], set()
    for ft in gj.get("features", []):
        props = ft.get("properties", {}) or {}
        if norm(feature_name(props)) in allowed:
            feats.append(ft)
            matched.add(norm(feature_name(props)))
    return {"type": "FeatureCollection", "features": feats}, matched