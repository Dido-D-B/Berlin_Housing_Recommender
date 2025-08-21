from __future__ import annotations
import time
from pathlib import Path
from typing import Dict, List

import geopandas as gpd
import pandas as pd
from osmnx.features import features_from_polygon
from shapely.geometry import Polygon
import logging

# Optional progress bar
try:
    from tqdm import tqdm  # type: ignore
    _HAS_TQDM = True
except Exception:  # pragma: no cover
    _HAS_TQDM = False

LOGGER = logging.getLogger(__name__)
FAILED_PATH = Path("artifacts/failed_ortsteile.txt")

# -----------------------------
# 1) Config helpers
# -----------------------------
def default_tags() -> Dict[str, List[str]]:
    return {
        "shop": ["supermarket"],
        "amenity": [
            "cafe", "restaurant", "bar", "nightclub",
            "school", "kindergarten", "university",
            "clinic", "hospital", "pharmacy",
        ],
        "leisure": ["park", "playground"],
        "landuse": ["grass", "forest"],
        "natural": ["wood"],
    }

GROUPED_COLUMNS = {
    "cafes": ["cafe", "coffee", "tea"],
    "bakeries": ["bakery", "pastry", "bakery;pastry"],
    "green_space": ["park", "forest", "meadow", "wood", "grass"],
    "schools": ["school", "kindergarten", "university"],
    "medical": ["clinic", "hospital", "pharmacy"],
}

# -----------------------------
# 2) Fetch
# -----------------------------
def fetch_pois_for_polygon(
    polygon: Polygon,
    tags: Dict[str, List[str]] | None = None,
    rate_limit_s: float = 1.5,
    retries: int = 3,
    backoff_s: float = 2.0,
) -> gpd.GeoDataFrame:
    """Fetch raw OSM features for a single polygon with simple retry/backoff.

    Parameters
    ----------
    polygon : shapely.geometry.Polygon
        Boundary polygon to query.
    tags : dict | None
        OSM tags to request (defaults to `default_tags()`).
    rate_limit_s : float
        Sleep after a successful request to be polite to Overpass.
    retries : int
        Number of retry attempts on failure.
    backoff_s : float
        Base backoff seconds; actual wait grows exponentially per retry.
    """
    tags = tags or default_tags()

    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            gdf = features_from_polygon(polygon, tags)
            # Light rate limiting after success
            if rate_limit_s:
                time.sleep(rate_limit_s)
            return gdf
        except Exception as e:  # pragma: no cover
            last_exc = e
            LOGGER.warning(
                "Overpass fetch failed (attempt %s/%s): %s",
                attempt + 1,
                retries + 1,
                e,
                exc_info=True,
            )
            if attempt < retries:
                # exponential backoff: backoff_s * 2**attempt
                sleep_for = backoff_s * (2 ** attempt)
                time.sleep(sleep_for)
            else:
                break

    if last_exc is not None:
        raise last_exc
    return gpd.GeoDataFrame()

def fetch_all_pois_by_ortsteil(
    boundaries: gpd.GeoDataFrame,
    ortsteil_col: str = "OTEIL",
    tags: Dict[str, List[str]] | None = None,
    rate_limit_s: float = 1.5,
    retries: int = 3,
    backoff_s: float = 2.0,
    save_failed_path: Path = FAILED_PATH,
) -> gpd.GeoDataFrame:
    """Loop boundaries and fetch; robust to failures; adds 'ortsteil' column.

    Shows a progress bar if `tqdm` is available. Writes failed names to
    `save_failed_path` and logs a summary of successes/failures.
    """
    tags = tags or default_tags()
    collected: list[gpd.GeoDataFrame] = []
    failed: list[str] = []

    iter_rows = boundaries.itertuples(index=False)
    total = len(boundaries)
    iterator = tqdm(iter_rows, total=total, desc="POI scraping", unit="ortsteil") if _HAS_TQDM else iter_rows

    for row in iterator:
        name = getattr(row, ortsteil_col)
        polygon = getattr(row, "geometry")
        try:
            LOGGER.info("Fetching POIs for %s", name)
            gdf = fetch_pois_for_polygon(
                polygon,
                tags=tags,
                rate_limit_s=rate_limit_s,
                retries=retries,
                backoff_s=backoff_s,
            )
            if len(gdf):
                gdf = gdf.copy()
                gdf["ortsteil"] = name
                collected.append(gdf)
            else:
                LOGGER.info("No POIs returned for %s", name)
        except Exception as e:  # pragma: no cover
            LOGGER.error("Failed for %s: %s", name, e, exc_info=True)
            failed.append(str(name))

    if failed:
        save_failed_path.parent.mkdir(exist_ok=True, parents=True)
        save_failed_path.write_text("\n".join(failed))
        LOGGER.warning("Wrote failed list: %d entries to %s", len(failed), save_failed_path)

    if not collected:
        LOGGER.warning("No POIs collected for any Ortsteil.")
        return gpd.GeoDataFrame(geometry=[], crs=boundaries.crs)

    gdf_all = gpd.GeoDataFrame(pd.concat(collected, ignore_index=True), crs=boundaries.crs)
    LOGGER.info("Collected %d POI feature rows across %d Ortsteile", len(gdf_all), len(collected))
    return gdf_all

# -----------------------------
# 3) Normalize
# -----------------------------
def add_tag_columns(gdf: gpd.GeoDataFrame, tags: Dict[str, List[str]] | None = None) -> gpd.GeoDataFrame:
    """Flatten OSM keys into main_tag and tag_value (your notebook logic)."""
    tags = tags or default_tags()
    g = gdf.copy()
    if g.empty:
        g["main_tag"] = None
        g["tag_value"] = None
        return g

    keys = list(tags.keys())
    g["main_tag"] = g.apply(
        lambda r: next((k for k in keys if k in g.columns and pd.notnull(r.get(k))), None), axis=1
    )
    g["tag_value"] = g.apply(lambda r: r.get(r["main_tag"]) if pd.notnull(r["main_tag"]) else None, axis=1)

    mask = g["tag_value"].astype(str).str.contains(";")
    if mask.any():
        g = g.assign(tag_value=g["tag_value"].astype(str))
        g = g.assign(tag_value=g["tag_value"].str.split(";")).explode("tag_value").reset_index(drop=True)
        g["tag_value"] = g["tag_value"].str.strip()

    return g

# -----------------------------
# 4) Aggregate counts per Ortsteil
# -----------------------------
def count_pois_per_ortsteil(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """Pivot counts: rows=ortsteil, columns=tag_value, values=count."""
    if gdf.empty:
        return pd.DataFrame({"ortsteil": []})
    piv = (
        gdf.dropna(subset=["ortsteil", "tag_value"])\
          .groupby(["ortsteil", "tag_value"])\
          .size()\
          .unstack(fill_value=0)\
          .reset_index()
    )
    piv.columns.name = None
    return piv

def group_poi_columns(df_counts: pd.DataFrame, groups: Dict[str, List[str]] = GROUPED_COLUMNS) -> pd.DataFrame:
    """Optional: create grouped columns and drop sources when present."""
    df = df_counts.copy()
    for new_col, cols in groups.items():
        exist = [c for c in cols if c in df.columns]
        if exist:
            df[new_col] = df[exist].sum(axis=1)
            df.drop(columns=exist, inplace=True, errors="ignore")
    return df

# -----------------------------
# 5) Merge with master table
# -----------------------------
def normalize_ortsteil_name(name: str | float) -> str:
    if pd.isna(name):
        return ""
    s = str(name).lower().strip()
    return (
        s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    )

def merge_poi_to_master(df_master: pd.DataFrame, df_counts: pd.DataFrame) -> pd.DataFrame:
    m = df_master.copy()
    p = df_counts.copy()
    m["ortsteil_norm"] = m["ortsteil"].map(normalize_ortsteil_name)
    p["ortsteil_norm"] = p["ortsteil"].map(normalize_ortsteil_name)

    out = m.merge(p.drop(columns=["ortsteil"]), on="ortsteil_norm", how="left", suffixes=("", "_poi"))
    out.drop(columns=["ortsteil_norm"], inplace=True)
    # fill NaNs for POI counts with 0
    poi_cols = [c for c in out.columns if c not in df_master.columns]
    if poi_cols:
        out[poi_cols] = out[poi_cols].fillna(0).astype("int64")
    return out