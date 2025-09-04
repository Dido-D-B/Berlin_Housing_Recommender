# Run from repo root:  python scripts/tables.py --all
"""
This script builds Berlin Housing master tables (Bezirk, Ortsteil, Final) from raw or cleaned data sources.
It processes, enriches, and merges various datasets to produce comprehensive master tables, and saves the outputs
to specified locations. The script can be run as a command-line interface (CLI) with argparse options to build
individual tables (--bezirk, --ortsteil, --final) or all tables at once (--all).
"""

# Imports
from __future__ import annotations
import os
import argparse
import pandas as pd
import geopandas as gpd
import logging

# Ensure package can be imported
import sys
sys.path.append(os.path.abspath("."))

from berlin_housing import config
from berlin_housing.cleaning import (
    build_bezirk_enrichment,
    build_ortsteil_master_table,
)
from berlin_housing.poi import (
    fetch_all_pois_by_ortsteil,
    add_tag_columns,
    count_pois_per_ortsteil,
    group_poi_columns,
    merge_poi_to_master,
)

# - Tourism Helpers -
# Select a column name from candidates in colnames, allowing substrings if needed
def _pick(colnames, candidates, allow_substring=True):
    cols = list(colnames)
    lower_map = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    if allow_substring:
        for c in cols:
            cl = c.lower()
            for cand in candidates:
                if cand.lower() in cl:
                    return c
    raise KeyError(f"None of {candidates} found in columns: {cols}")

# Load and merge tourism data frames for overnight stays and guests
def load_tourism_frames(totals_path, changes_path):
    totals = pd.read_csv(totals_path)
    changes = pd.read_csv(changes_path)

    dist_tot = _pick(totals.columns,  ["Bezirke", "Bezirk", "district"])
    dist_chg = _pick(changes.columns, ["Bezirke", "Bezirk", "district"])

    guests_col    = _pick(totals.columns, ["Guests"])
    overnight_col = _pick(totals.columns, ["Overnightstays", "Overnight stays", "overnight_stays"])
    change_col    = _pick(changes.columns, ["Change", "Overnightstays Change", "Overnight stays Change", "Change %", "pct_change"])

    totals_mini = totals[[dist_tot, guests_col, overnight_col]].rename(columns={
        dist_tot: "Bezirke",
        guests_col: "Guests",
        overnight_col: "overnight stays",
    })
    changes_mini = changes[[dist_chg, change_col]].rename(columns={
        dist_chg: "Bezirke",
        change_col: "Overnight stays Change",
    })

    merged = totals_mini.merge(changes_mini, on="Bezirke", how="left")
    overnight_stays = merged[["Bezirke", "overnight stays", "Overnight stays Change"]]
    guests = totals_mini[["Bezirke", "Guests"]]
    return overnight_stays, guests

# - Builder Helpers -
# Build the Bezirk master table by enriching various datasets
def build_bezirk_master() -> pd.DataFrame:
    bridges   = pd.read_csv(config.BRIDGES_CSV)
    cinemas   = pd.read_csv(config.CINEMAS_CSV)
    libraries = pd.read_csv(config.LIBRARIES_CSV)
    cars      = pd.read_csv(config.CARS_CSV)
    toilets   = pd.read_csv(config.TOILETS_CSV)
    trees     = pd.read_csv(config.TREES_CSV)
    census_d  = pd.read_csv(config.CENSUS_DISTRICT)

    overnight_stays, guests = load_tourism_frames(config.TOURISM_TOTALS, config.TOURISM_CHANGES)
    # Ensure Guests has a Year column for the cleaning module (it filters by Year)
    if "Year" not in guests.columns:
        guests["Year"] = 2024

    df = build_bezirk_enrichment(
        bridges=bridges,
        cinemas=cinemas,
        libraries=libraries,
        cars=cars,
        toilets=toilets,
        overnight_stays=overnight_stays,
        guests=guests,
        trees=trees,
        census=census_d,
    )
    return df

# Build Ortsteil base and POI-enriched master tables
def build_ortsteil_master() -> tuple[pd.DataFrame, pd.DataFrame]:
    logger = logging.getLogger(__name__)

    # 1) Base table
    pop = pd.read_csv(config.ORTS_POP_CSV)
    ri  = pd.read_csv(config.ORTS_RI_CSV)
    base = build_ortsteil_master_table(df_population=pop, df_rent_income=ri)

    # 2) Acquire POI counts
    poi_counts_df: pd.DataFrame | None = None
    try:
        # Prefer precomputed counts if available
        poi_counts_df = pd.read_csv(config.POI_COUNTS_CSV)
        logger.info("Loaded POI counts from %s", config.POI_COUNTS_CSV)
    except FileNotFoundError:
        # If not available, try to scrape using boundaries
        boundaries_path = getattr(config, "ORTSTEIL_BOUNDARIES_PATH", None)
        name_col = getattr(config, "ORTSTEIL_NAME_COLUMN", "OTEIL")
        if boundaries_path and os.path.exists(boundaries_path):
            logger.warning("POI counts not found; scraping via boundaries at %s", boundaries_path)
            boundaries = gpd.read_file(boundaries_path)
            if name_col not in boundaries.columns:
                raise KeyError(f"ORTSTEIL_NAME_COLUMN '{name_col}' not found in boundaries file; available columns: {list(boundaries.columns)}")
            raw = fetch_all_pois_by_ortsteil(boundaries, ortsteil_col=name_col)
            norm = add_tag_columns(raw)
            counts = count_pois_per_ortsteil(norm)
            # Optional grouped rollups (cafes, green_space, etc.)
            counts = group_poi_columns(counts)

            # Persist counts for next run
            os.makedirs(os.path.dirname(config.POI_COUNTS_CSV), exist_ok=True)
            counts.to_csv(config.POI_COUNTS_CSV, index=False)
            poi_counts_df = counts
            logger.info("Saved POI counts to %s", config.POI_COUNTS_CSV)
        else:
            logger.warning("No POI counts and no boundaries provided; skipping POI enrichment.")

    # 3) Merge POIs onto base
    if poi_counts_df is not None and not poi_counts_df.empty:
        enriched = merge_poi_to_master(base, poi_counts_df)
    else:
        enriched = base.copy()

    return base, enriched

# Build the final master table from the POI-enriched Ortsteil table
def build_final_master(ortsteil_with_poi: pd.DataFrame) -> pd.DataFrame:
    # Final master currently equals Ortsteil master enriched with POIs
    return ortsteil_with_poi.copy()

# Save a DataFrame to CSV and print confirmation
def save_outputs(name: str, df: pd.DataFrame, path_csv: str):
    os.makedirs(os.path.dirname(path_csv), exist_ok=True)
    df.to_csv(path_csv, index=False)
    print(f"✓ Saved {name}: {df.shape[0]:,} rows × {df.shape[1]:,} cols")
    print(f"  - {path_csv}")

# Command-line interface to build selected master tables
def main():
    ap = argparse.ArgumentParser(description="Build Berlin Housing master tables from raw data.")
    ap.add_argument("--bezirk", action="store_true", help="Build only bezirk master.")
    ap.add_argument("--ortsteil", action="store_true", help="Build only ortsteil master.")
    ap.add_argument("--final", action="store_true", help="Build only final master (depends on ortsteil).")
    ap.add_argument("--all", action="store_true", help="Build all tables.")
    args = ap.parse_args()

    if not any([args.bezirk, args.ortsteil, args.final, args.all]):
        ap.print_help()
        return

    if args.all or args.bezirk:
        bezirk = build_bezirk_master()
        save_outputs("bezirk_master", bezirk, config.BEZIRK_MASTER_OUT)

    if args.all or args.ortsteil or args.final:
        ortsteil_base, ortsteil_with_poi = build_ortsteil_master()
        # Save base Ortsteil master
        save_outputs("ortsteil_master", ortsteil_base, config.ORTSTEIL_MASTER_OUT)
        # Save POI-enriched Ortsteil master alongside it
        ortsteil_with_poi_path = os.path.join(config.PROCESSED_DIR, "ortsteil_master_with_poi.csv")
        save_outputs("ortsteil_master_with_poi", ortsteil_with_poi, ortsteil_with_poi_path)
        # quick sanity: show how many new columns POIs added
        added_cols = [c for c in ortsteil_with_poi.columns if c not in ortsteil_base.columns]
        print(f"POI columns added: {len(added_cols)}")

    if args.all or args.final:
        try:
            # Prefer the freshly built POI-enriched table if we just built it above
            final = build_final_master(ortsteil_with_poi)
        except UnboundLocalError:
            # Otherwise load from processed outputs
            base_path = config.ORTSTEIL_MASTER_OUT
            poi_path  = os.path.join(config.PROCESSED_DIR, "ortsteil_master_with_poi.csv")
            if os.path.exists(poi_path):
                ortsteil_with_poi = pd.read_csv(poi_path)
                final = build_final_master(ortsteil_with_poi)
            else:
                # Fallback: load base and pass through as final
                ortsteil_base = pd.read_csv(base_path)
                final = build_final_master(ortsteil_base)
        save_outputs("final_master", final, config.FINAL_MASTER_OUT)

if __name__ == "__main__":
    main()