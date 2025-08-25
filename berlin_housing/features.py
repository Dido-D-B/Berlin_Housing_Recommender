from __future__ import annotations
import pandas as pd
import numpy as np

ID_COLS = ["bezirk", "ortsteil"]

# Return list of age-related population columns
def age_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("subdistrict_population_age_")]

# Return list of numeric POI-related columns (excluding IDs and population/area)
def poi_columns(df: pd.DataFrame) -> list[str]:
    exclude = set(ID_COLS + ["total_population", "subdistrict_area_km2"])
    return [c for c in df.columns
            if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]

# Add sanity check columns: sum of age groups and population difference
def add_sanity_checks(df: pd.DataFrame) -> pd.DataFrame:
    """Adds age_group_sum and pop_diff sanity columns."""
    ages = age_columns(df)
    out = df.copy()
    out["age_group_sum"] = out[ages].sum(axis=1)
    out["pop_diff"] = out["total_population"] - out["age_group_sum"]
    return out

# Engineer derived features: diversity, POI counts, densities, ratios
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds:
    - age_std_dev
    - total_pois
    - green_poi_total, green_poi_ratio
    - food_drink_total, food_drink_density (per 1k)
    - education_total, education_density (per 1k)
    - rent_to_income_ratio
    - employment_rate
    """
    out = df.copy()

    # Age diversity
    ages = age_columns(out)
    if ages:
        out["age_std_dev"] = out[ages].std(axis=1)
    else:
        out["age_std_dev"] = np.nan

    # POIs
    pois = poi_columns(out)
    out["total_pois"] = out[pois].sum(axis=1) if pois else 0

    # Green POIs (use whatever exists)
    green_candidates = ["green_space", "garden", "nature_reserve", "park", "forest", "wood", "meadow", "grass"]
    green_cols = [c for c in green_candidates if c in out.columns]
    out["green_poi_total"] = out[green_cols].sum(axis=1) if green_cols else 0
    out["green_poi_ratio"] = np.where(out["total_pois"] > 0, out["green_poi_total"] / out["total_pois"], np.nan)

    # Food & drink density per 1k (align names to your columns)
    food_drink_candidates = ["restaurant", "cafes", "bar", "fast_food", "nightclub"]
    fd_cols = [c for c in food_drink_candidates if c in out.columns]
    out["food_drink_total"] = out[fd_cols].sum(axis=1) if fd_cols else 0
    out["food_drink_density"] = out["food_drink_total"] / out["total_population"].replace({0: np.nan}) * 1000

    # Education per 1k
    edu_candidates = ["schools", "kindergarten", "university"]
    edu_cols = [c for c in edu_candidates if c in out.columns]
    out["education_total"] = out[edu_cols].sum(axis=1) if edu_cols else 0
    out["education_density"] = out["education_total"] / out["total_population"].replace({0: np.nan}) * 1000

    # Ratios
    if {"subdistrict_avg_mietspiegel_classification", "subdistrict_avg_median_income_eur"} <= set(out.columns):
        out["rent_to_income_ratio"] = out["subdistrict_avg_mietspiegel_classification"] / out["subdistrict_avg_median_income_eur"]
    else:
        out["rent_to_income_ratio"] = np.nan

    if {"subdistrict_total_full_time_employees", "total_population"} <= set(out.columns):
        out["employment_rate"] = out["subdistrict_total_full_time_employees"] / out["total_population"].replace({0: np.nan})
    else:
        out["employment_rate"] = np.nan

    return out

# Select final feature set for modeling (drop IDs and specified cols)
def select_model_features(df: pd.DataFrame, drop_cols: list[str] | None = None) -> pd.DataFrame:
    """Drop identifiers and any explicitly provided columns before scaling/PCA."""
    drop = set((drop_cols or []) + ID_COLS + ["classification_category", "subdistrict_avg_mietspiegel_classification"])
    keep = [c for c in df.columns if c not in drop and pd.api.types.is_numeric_dtype(df[c])]
    return df[keep].copy()