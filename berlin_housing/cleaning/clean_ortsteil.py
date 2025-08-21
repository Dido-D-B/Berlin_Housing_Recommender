# berlin_housing/cleaning/clean_ortsteil.py
from __future__ import annotations

from typing import List
import pandas as pd

# Shared helpers (you'll place these in cleaning/clean_shared.py)
from .clean_shared import (
    standardize_columns,
    coerce_dtypes,
    drop_duplicates_key,
    normalize_name,
    clean_bezirk_value,
    normalize_merge_keys,   # keep this in shared to reuse across modules
)

# Census utilities
from .clean_census import CensusCleanConfig, clean_census_2022


# ---------------------------------------------------------------------
# Core Ortsteil table cleaner
# ---------------------------------------------------------------------

def clean_ortsteil_tables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Ortsteil-level table.

    Actions:
      - standardize columns
      - harmonize column aliases: (oteil -> ortsteil), (plr_id -> ortsteil_id), (district -> bezirk)
      - trim/str-cast strings for ['ortsteil','bezirk']
      - derive normalized keys: ortsteil_norm, bezirk_norm
      - deduplicate on the strongest available ortsteil key
    """
    df1 = standardize_columns(df)

    alias_map = {
        "oteil": "ortsteil",        # from Geo boundary file
        "plr_id": "ortsteil_id",    # sometimes PLR used as id
        "district": "bezirk",
    }
    for k, v in alias_map.items():
        if k in df1.columns and v not in df1.columns:
            df1 = df1.rename(columns={k: v})

    # Strings
    str_candidates = [c for c in ["ortsteil", "bezirk"] if c in df1.columns]
    df1 = coerce_dtypes(df1, str_cols=str_candidates)

    # Normalized keys
    if "ortsteil" in df1.columns:
        df1["ortsteil_norm"] = df1["ortsteil"].map(normalize_name)
    if "bezirk" in df1.columns:
        df1["bezirk_norm"] = df1["bezirk"].map(normalize_name)

    # De-dupe
    key_cols = [c for c in ["ortsteil_id", "ortsteil_norm"] if c in df1.columns]
    if key_cols:
        df1 = drop_duplicates_key(df1, key_cols)

    return df1


# ---------------------------------------------------------------------
# Census → Ortsteil builder (wraps the generic census cleaner)
# ---------------------------------------------------------------------

def build_census_ortsteil_table(
    census_raw: pd.DataFrame,
    *,
    integer_cols: List[str] | None = None,
    float_cols: List[str] | None = None,
) -> pd.DataFrame:
    """
    Replicates the census_2022_table_building notebook for Ortsteile.

    1) Clean census with the generic cleaner
    2) (Optionally) select/aggregate columns to your modeling schema
    3) Return one-row-per-ortsteil frame ready to join with POIs
    """
    cfg = CensusCleanConfig(
        id_col="ortsteil_id",
        name_col="ortsteil",
        bezirk_col="bezirk",
        integer_cols=integer_cols or [],
        float_cols=float_cols or [],
    )
    census = clean_census_2022(census_raw, cfg)

    # Example: to keep a subset:
    # keep = ["ortsteil_id","ortsteil","bezirk","population_total","median_age", ...]
    # census = census[keep]

    # Strong uniqueness guard
    key_cols = [c for c in ["ortsteil_id", "ortsteil_norm"] if c in census.columns]
    if key_cols:
        _ = drop_duplicates_key(census, key_cols)  # no assignment — just a sanity check pattern

    return census


# ---------------------------------------------------------------------
# Ortsteil population pivot (age & gender) + totals/shares
# ---------------------------------------------------------------------

def pivot_subdistrict_population(df_ort_population: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot age & gender distributions to wide form and compute totals + shares per Ortsteil.
    Expected columns in input: ['Bezirk','Ortsteil','Age group','Gender','Frequency']
    """
    # --- Age pivot ---
    age = (
        df_ort_population
        .pivot_table(index=["Bezirk", "Ortsteil"], columns="Age group", values="Frequency", aggfunc="sum")
        .reset_index()
        .rename(columns={
            "Bezirk": "bezirk",
            "Ortsteil": "ortsteil",
            "00_05": "subdistrict_population_age_0_5",
            "05_10": "subdistrict_population_age_5_10",
            "10_15": "subdistrict_population_age_10_15",
            "15_20": "subdistrict_population_age_15_20",
            "20_25": "subdistrict_population_age_20_25",
            "25_30": "subdistrict_population_age_25_30",
            "30_35": "subdistrict_population_age_30_35",
            "35_40": "subdistrict_population_age_35_40",
            "40_45": "subdistrict_population_age_40_45",
            "45_50": "subdistrict_population_age_45_50",
            "50_55": "subdistrict_population_age_50_55",
            "55_60": "subdistrict_population_age_55_60",
            "60_65": "subdistrict_population_age_60_65",
            "65_70": "subdistrict_population_age_65_70",
            "70_75": "subdistrict_population_age_70_75",
            "75_80": "subdistrict_population_age_75_80",
            "80_85": "subdistrict_population_age_80_85",
            "85_90": "subdistrict_population_age_85_90",
            "90_95": "subdistrict_population_age_90_95",
            "95 und älter": "subdistrict_population_age_95_plus",
        })
    )

    # --- Gender pivot ---
    gender = (
        df_ort_population
        .pivot_table(index=["Bezirk", "Ortsteil"], columns="Gender", values="Frequency", aggfunc="sum")
        .reset_index()
        .rename(columns={
            "Bezirk": "bezirk",
            "Ortsteil": "ortsteil",
            1: "subdistrict_male_population",
            2: "subdistrict_female_population",
        })
    )

    # --- name cleaning to lower-case (as in notebook) ---
    def _clean_bezirk_simple(x: str) -> str:
        return clean_bezirk_value(x)

    def _clean_ortsteil_simple(x: str) -> str:
        return str(x).strip().lower() if pd.notna(x) else ""

    age["bezirk"] = age["bezirk"].map(_clean_bezirk_simple)
    gender["bezirk"] = gender["bezirk"].map(_clean_bezirk_simple)
    age["ortsteil"] = age["ortsteil"].map(_clean_ortsteil_simple)
    gender["ortsteil"] = gender["ortsteil"].map(_clean_ortsteil_simple)

    # --- Merge age + gender ---
    pop = age.merge(gender, on=["bezirk", "ortsteil"], how="outer")

    # --- Totals and shares ---
    pop["total_population"] = pop["subdistrict_male_population"].fillna(0) + pop["subdistrict_female_population"].fillna(0)

    seniors_cols = [
        "subdistrict_population_age_65_70",
        "subdistrict_population_age_70_75",
        "subdistrict_population_age_75_80",
        "subdistrict_population_age_80_85",
        "subdistrict_population_age_85_90",
        "subdistrict_population_age_90_95",
        "subdistrict_population_age_95_plus",
    ]
    youth_cols = [
        "subdistrict_population_age_0_5",
        "subdistrict_population_age_5_10",
        "subdistrict_population_age_10_15",
        "subdistrict_population_age_15_20",
    ]

    pop["subdistrict_senior_population"] = pop[seniors_cols].sum(axis=1, min_count=1)
    pop["subdistrict_youth_population"] = pop[youth_cols].sum(axis=1, min_count=1)

    pop["subdistrict_senior_share"] = (pop["subdistrict_senior_population"] / pop["total_population"]).astype("float")
    pop["subdistrict_youth_share"] = (pop["subdistrict_youth_population"] / pop["total_population"]).astype("float")

    pop["subdistrict_middle_age_population"] = (
        pop["total_population"] - (pop["subdistrict_youth_population"].fillna(0) + pop["subdistrict_senior_population"].fillna(0))
    )
    pop["subdistrict_middle_age_population"] = (pop["subdistrict_middle_age_population"] / pop["total_population"]).astype("float")

    return pop


# ---------------------------------------------------------------------
# Street directory lookup (for Mietspiegel joins)
# ---------------------------------------------------------------------

def build_street_lookup(df_streets: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the street directory to a lookup for Mietspiegel joins.
    Input expects: ['strassenna','bezirk','stadtteil']
    Returns: ['street_name','bezirk','ortsteil'] lower-cased & stripped.
    """
    df = df_streets.copy()
    df["strassenna"] = df["strassenna"].astype(str).str.strip().str.lower()
    df["bezirk"] = df["bezirk"].astype(str).str.strip().str.lower()
    df["stadtteil"] = df["stadtteil"].astype(str).str.strip().str.lower()
    lookup = (
        df[["strassenna", "bezirk", "stadtteil"]]
        .drop_duplicates()
        .rename(columns={"strassenna": "street_name", "stadtteil": "ortsteil"})
    )
    return lookup


# ---------------------------------------------------------------------
# Ortsteil rent + income aggregation (Mietspiegel × PLR)
# ---------------------------------------------------------------------

def build_ortsteil_rent_income(
    df_miet: pd.DataFrame,
    df_income: pd.DataFrame,
    street_lookup: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge Mietspiegel (street-level) and PLR median income to Ortsteil level.

    Steps:
      - normalize street names & districts
      - join street lookup to both Mietspiegel and PLR
      - merge on (bezirk, ortsteil)
      - map classification (einfach/mittel/gut → 1/2/3)
      - aggregate to Ortsteil
      - fill missing income by district mean
    """
    # Mietspiegel prep + merge to lookup
    miet = df_miet.copy()
    miet["street_name"] = miet["street_name"].astype(str).str.strip().str.lower()
    miet["district"] = miet["district"].astype(str).str.strip().str.lower()
    miet = miet.merge(street_lookup, left_on=["street_name", "district"], right_on=["street_name", "bezirk"], how="left")

    # Income prep + merge to lookup
    inc = df_income.copy()
    inc["street_name"] = inc["PLR"].astype(str).str.strip().str.lower()
    plr_mapped = inc.merge(street_lookup, on="street_name", how="left")

    # Merge Mietspiegel + PLR on (bezirk, ortsteil)
    sub = miet.merge(plr_mapped, on=["bezirk", "ortsteil"], how="outer", suffixes=("", "_plr"))

    # Normalize keys
    for col in ("bezirk", "ortsteil"):
        sub[col] = sub[col].astype(str).str.strip().str.lower()

    # Classification mapping
    classification_map = {"einfach": 1, "mittel": 2, "gut": 3}
    if "classification" in sub.columns:
        sub["classification"] = sub["classification"].astype(str).str.strip().str.lower().map(classification_map)

    # Numeric coercions
    for col in ("full_time_employees", "median_income_eur"):
        if col in sub.columns:
            sub[col] = pd.to_numeric(sub[col], errors="coerce")

    # Aggregate to Ortsteil level
    agg = (
        sub.groupby(["bezirk", "ortsteil"]).agg(
            subdistrict_avg_mietspiegel_classification=("classification", "mean"),
            subdistrict_total_full_time_employees=("full_time_employees", "sum"),
            subdistrict_avg_median_income_eur=("median_income_eur", "mean"),
        ).reset_index()
    )

    # Fill NaNs in income with district mean
    if "subdistrict_avg_median_income_eur" in agg.columns:
        agg["subdistrict_avg_median_income_eur"] = (
            agg.groupby("bezirk")["subdistrict_avg_median_income_eur"].transform(lambda s: s.fillna(s.mean()))
        )

    return agg


# ---------------------------------------------------------------------
# Final Ortsteil master (population × rent/income)
# ---------------------------------------------------------------------

def build_ortsteil_master_table(df_population: pd.DataFrame, df_rent_income: pd.DataFrame) -> pd.DataFrame:
    """
    Final merge (population × rent/income) per Ortsteil, replicating the last notebook step.
    """
    pop = normalize_merge_keys(df_population.copy(), "bezirk", "ortsteil")
    ri = normalize_merge_keys(df_rent_income.copy(), "bezirk", "ortsteil")
    master = pop.merge(ri, on=["bezirk", "ortsteil"], how="inner")
    return master


def build_ortsteil_master(ortsteil_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Single tidy Ortsteil table cleaner (wrapper used by notebooks).
    """
    ort = clean_ortsteil_tables(ortsteil_raw)
    # If you have ortsteil_norm, keep a guard:
    if "ortsteil_norm" in ort.columns:
        _ = drop_duplicates_key(ort, ["ortsteil_norm"])
    return ort


__all__ = [
    "clean_ortsteil_tables",
    "build_census_ortsteil_table",
    "pivot_subdistrict_population",
    "build_street_lookup",
    "build_ortsteil_rent_income",
    "build_ortsteil_master_table",
    "build_ortsteil_master",
]