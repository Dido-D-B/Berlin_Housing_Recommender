# Imports
import os
from typing import Dict, Tuple, Any
from utils.data import load_json as _load_json
from utils.text import norm as _norm, district_slug  # district_slug kept for future use

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DATA_DIR = os.path.join(_BASE_DIR, "data")

DISTRICTS_JSON_PATH = os.environ.get(
    "DISTRICTS_JSON_PATH",
    os.path.join(_DATA_DIR, "districts_cultural_facts.json"),
)

SUBDISTRICTS_JSON_PATH = os.environ.get(
    "SUBDISTRICTS_JSON_PATH",
    os.path.join(_DATA_DIR, "subdistricts_cultural_facts.json"),
)

# Path for image credits JSON
IMAGE_CREDITS_PATH = os.environ.get(
    "IMAGE_CREDITS_PATH",
    os.path.join(_DATA_DIR, "image_credits.json"),
)

_DISTRICT_INDEX: Dict[str, Any] = {}
_SUBDISTRICT_INDEX: Dict[Tuple[str, str], Any] = {}

# Load district and subdistrict cultural facts JSON (either dict or list formats).
_district_facts_raw = _load_json(DISTRICTS_JSON_PATH) or {}
_subdistrict_facts_raw = _load_json(SUBDISTRICTS_JSON_PATH) or {}

# District facts can be a dict {"bezirk": {...}} or a list of dicts with a name key
if isinstance(_district_facts_raw, dict):
    _DISTRICT_INDEX = { _norm(k): v for k, v in _district_facts_raw.items() }
elif isinstance(_district_facts_raw, list):
    for v in _district_facts_raw:
        if not isinstance(v, dict):
            continue
        # try common keys: name/bezirk/title
        name = v.get("name") or v.get("bezirk") or v.get("title") or ""
        if name:
            _DISTRICT_INDEX[_norm(name)] = v

# Subdistrict facts may be dict or list
if isinstance(_subdistrict_facts_raw, dict):
    _iterable = _subdistrict_facts_raw.values()
elif isinstance(_subdistrict_facts_raw, list):
    _iterable = _subdistrict_facts_raw
else:
    _iterable = []

for v in _iterable:
    if not isinstance(v, dict):
        continue
    b = v.get("bezirk") or v.get("district") or ""
    o = v.get("ortsteil") or v.get("subdistrict") or v.get("locality") or ""
    key = (_norm(b), _norm(o))
    if key != ("", ""):
        _SUBDISTRICT_INDEX[key] = v

# Load image credits JSON: maps district slug → list of credit strings.
_IMAGE_CREDITS = _load_json(IMAGE_CREDITS_PATH) or {}

# Public API
def get_district_blurb(bezirk: str) -> dict:
    """Return dict with keys {blurb, image_path, source} or {} if missing.

    Looks up by normalized district name.
    """
    if not bezirk:
        return {}
    return _DISTRICT_INDEX.get(_norm(bezirk), {})

# Lookup subdistrict blurb by normalized district + subdistrict name.
def get_subdistrict_blurb(bezirk: str, ortsteil: str) -> dict:
    """Return dict with keys {blurb, image_path, source, bezirk, ortsteil} or {} if missing.

    Looks up by normalized (district, subdistrict) pair.
    """
    if not bezirk or not ortsteil:
        return {}
    return _SUBDISTRICT_INDEX.get((_norm(bezirk), _norm(ortsteil)), {})

# Image credits API
def get_image_credit(bezirk: str, idx: int) -> str:
    """Return the credit line for the district image at zero-based index idx.
    Uses the credits JSON mapping: slug -> list[str]. Returns empty string if missing.
    """
    if not bezirk or idx is None or idx < 0:
        return ""
    try:
        slug = district_slug(bezirk)
        credits = _IMAGE_CREDITS.get(slug, [])
        if isinstance(credits, list) and 0 <= idx < len(credits):
            val = credits[idx]
            return val if isinstance(val, str) else ""
    except Exception:
        pass
    return ""
