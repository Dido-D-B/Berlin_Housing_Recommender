from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping

import pandas as pd

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Helpers (generic, reusable across census/district/subdistrict tables)
# ---------------------------------------------------------------------

def _to_snake(name: str) -> str:
    return (
        name.strip()
        .replace("ß", "ss")
        .replace(" ", "_")
        .replace("-", "_")
        .lower()
    )


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with snake_case, trimmed column names."""
    out = df.copy()
    out.columns = [_to_snake(c) for c in out.columns]
    return out


def rename_columns(df: pd.DataFrame, mapping: Mapping[str, str]) -> pd.DataFrame:
    """Rename columns using a case-insensitive mapping (keys matched after snake_case)."""
    df2 = standardize_columns(df)
    norm_map = {_to_snake(k): v for k, v in mapping.items()}
    return df2.rename(columns=norm_map)


def coerce_dtypes(
    df: pd.DataFrame,
    *,
    int_cols: Iterable[str] | None = None,
    float_cols: Iterable[str] | None = None,
    str_cols: Iterable[str] | None = None,
) -> pd.DataFrame:
    out = df.copy()
    for c in int_cols or []:
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("Int64")
    for c in float_cols or []:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    for c in str_cols or []:
        out[c] = out[c].astype("string").str.strip()
    return out


def drop_duplicates_key(df: pd.DataFrame, keys: Iterable[str]) -> pd.DataFrame:
    return df.drop_duplicates(subset=list(keys), keep="first").reset_index(drop=True)


def assert_unique(df: pd.DataFrame, keys: Iterable[str]) -> None:
    """Raise if (keys) are not unique."""
    dup = df.duplicated(subset=list(keys)).sum()
    if dup:
        raise ValueError(f"Expected unique keys {list(keys)} but found {dup} duplicates")


def normalize_name(s: str | float | None) -> str:
    """Normalize German names to ASCII-ish for safe joins (ae/oe/ue/ss)."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    s2 = str(s).strip().lower()
    return (
        s2.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


def clean_bezirk_value(bezirk: str) -> str:
    """Normalize Bezirk strings to a consistent, join-friendly form.
    Replicates the notebook logic: umlauts→oe, strip dots/spaces, kebab-case, and fix truncations.
    """
    if bezirk is None:
        return ""
    s = str(bezirk)
    s = s.replace("ö", "oe").replace("Ö", "oe")
    s = s.replace(".", "")
    s = s.lower().strip().replace(" ", "-")
    mapping = {
        "charlbg-wilmersd": "charlottenburg-wilmersdorf",
        "friedrh-kreuzb": "friedrichshain-kreuzberg",
        "marzahn-hellersd": "marzahn-hellersdorf",
        "steglitz-zehlend": "steglitz-zehlendorf",
        "tempelh-schoeneb": "tempelhof-schoeneberg",
    }
    return mapping.get(s, s) or s


def apply_clean_bezirk(df: pd.DataFrame, col: str = "bezirk") -> pd.DataFrame:
    out = df.copy()
    out[col] = out[col].map(clean_bezirk_value)
    return out


# ---------------------------------------------------------------------
# Domain: CENSUS 2022 (district-level and subdistrict-level cleaners)
# ---------------------------------------------------------------------

@dataclass
class CensusCleanConfig:
    # provide your real column names from the notebook here
    id_col: str = "ortsteil_id"  # or AGS/plr_id if you have it
    name_col: str = "ortsteil"   # display name
    bezirk_col: str = "bezirk"
    # numeric blocks to coerce
    integer_cols: List[str] = None
    float_cols: List[str] = None

    def __post_init__(self):
        if self.integer_cols is None:
            self.integer_cols = []
        if self.float_cols is None:
            self.float_cols = []


def clean_census_2022(df: pd.DataFrame, cfg: CensusCleanConfig) -> pd.DataFrame:
    """Clean raw Census 2022 table (either district or subdistrict level).

    Steps (mirror your notebook):
      1) Standardize/rename columns
      2) Coerce dtypes for numeric blocks
      3) Trim strings; derive normalized keys for joining
      4) Drop/resolve duplicates
    """
    LOGGER.info("Cleaning Census 2022 table …")

    # 1) standardize column names
    df1 = standardize_columns(df)

    # 2) canonical column aliases (edit mapping to your real headers)
    mapping = {
        cfg.id_col: "ortsteil_id",
        cfg.name_col: "ortsteil",
        cfg.bezirk_col: "bezirk",
    }
    df1 = rename_columns(df1, mapping)

    # 3) coerce numerics & strip strings
    df1 = coerce_dtypes(df1, int_cols=cfg.integer_cols, float_cols=cfg.float_cols, str_cols=["ortsteil", "bezirk"])

    # 4) normalized join keys
    if "ortsteil" in df1.columns:
        df1["ortsteil_norm"] = df1["ortsteil"].map(normalize_name)
    if "bezirk" in df1.columns:
        df1["bezirk_norm"] = df1["bezirk"].map(normalize_name)

    # 5) de-duplicate on the strongest key available
    key_cols = [c for c in ["ortsteil_id", "ortsteil_norm"] if c in df1.columns]
    if key_cols:
        df1 = drop_duplicates_key(df1, key_cols)

    return df1


# ---------------------------------------------------------------------
# Domain: DISTRICT (Bezirk) tables
# ---------------------------------------------------------------------

def clean_bezirk_tables(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Bezirk-level table. Paste your notebook logic here.

    Typical actions:
      - standardize/rename bezirk column to `bezirk`
      - coerce numerical indicators
      - build `bezirk_norm` for joins
      - ensure one row per bezirk

    For name normalization, see `clean_bezirk_value`.
    """
    df1 = standardize_columns(df)
    if "bezirk" not in df1.columns:
        # example: some sources use 'district' or 'bezirk_name'
        for candidate in ("district", "bezirk_name"):
            if candidate in df1.columns:
                df1 = df1.rename(columns={candidate: "bezirk"})
                break
    df1 = coerce_dtypes(df1, str_cols=["bezirk"])
    if "bezirk" in df1.columns:
        df1["bezirk_norm"] = df1["bezirk"].map(normalize_name)
    df1 = drop_duplicates_key(df1, ["bezirk_norm"]) if "bezirk_norm" in df1.columns else df1
    return df1


# -----------------------------
# District enrichment table cleaners (bridges, cinemas, libraries, cars, toilets, tourism, trees)
# -----------------------------

def clean_bridges_df(df_bridges: pd.DataFrame) -> pd.DataFrame:
    df = df_bridges.copy()
    df = df.rename(columns={
        "Bezirk": "bezirk",
        "Total bridges¹": "district_total_bridges",
        "City streets": "district_bridges_city_streets",
        "Green spaces": "district_bridges_green_spaces",
    })
    df = apply_clean_bezirk(df, "bezirk")
    return df


def clean_cinemas_df(df_cinemas: pd.DataFrame) -> pd.DataFrame:
    df = df_cinemas.copy()
    df = df.dropna(subset=["Bezirk"]).rename(columns={
        "Bezirk": "bezirk",
        "Movie Theaters": "district_movie_theaters",
    })
    df = apply_clean_bezirk(df, "bezirk")
    df["district_movie_theaters"] = pd.to_numeric(df["district_movie_theaters"], errors="coerce").astype("Int64")
    return df


def clean_libraries_df(df_libraries: pd.DataFrame) -> pd.DataFrame:
    df = df_libraries.copy()
    df = df.rename(columns={
        "Bezirk": "bezirk",
        "Libraries": "district_libraries",
        "visits": "district_libraries_visits",
        "borrowings": "district_libraries_borrowings",
    })
    df = apply_clean_bezirk(df, "bezirk")
    # remove thousands separators then cast
    df["district_libraries_visits"] = (
        df["district_libraries_visits"].astype(str).str.replace(",", "", regex=False).astype("Int64")
    )
    df["district_libraries_borrowings"] = (
        df["district_libraries_borrowings"].astype(str).str.replace(",", "", regex=False).astype("Int64")
    )
    return df


def clean_cars_df(df_cars: pd.DataFrame) -> pd.DataFrame:
    df = df_cars.copy().rename(columns={
        "Bezirk": "bezirk",
        "Total": "district_total_cars",
        "Privat": "district_private_cars",
        "Private cars per 100 inhabitants": "district_private_cars_per_100_inhabitants",
    })
    df = apply_clean_bezirk(df, "bezirk")
    df["district_total_cars"] = df["district_total_cars"].astype(str).str.replace(" ", "", regex=False).astype("Int64")
    df["district_private_cars"] = df["district_private_cars"].astype(str).str.replace(" ", "", regex=False).astype("Int64")
    df["district_private_cars_per_100_inhabitants"] = pd.to_numeric(
        df["district_private_cars_per_100_inhabitants"], errors="coerce"
    )
    return df


def aggregate_toilets_df(df_toilets: pd.DataFrame) -> pd.DataFrame:
    df = (
        df_toilets.groupby("Bezirk").agg(district_public_toilets=("ID", "count")).reset_index()
        .rename(columns={"Bezirk": "bezirk"})
    )
    df = apply_clean_bezirk(df, "bezirk")
    return df


def clean_overnight_stays_df(df_overnight_stays: pd.DataFrame) -> pd.DataFrame:
    df = df_overnight_stays.copy().rename(columns={
        "Bezirke": "bezirk",
        "overnight stays": "district_tourism_overnightstays_2024",
        "Overnight stays Change": "district_tourism_overnightstays_change_2023_2024",
    })
    df = apply_clean_bezirk(df, "bezirk")
    df["district_tourism_overnightstays_2024"] = (
        df["district_tourism_overnightstays_2024"].astype(str).str.replace(",", "", regex=False).astype("Int64")
    )
    df["district_tourism_overnightstays_change_2023_2024"] = (
        df["district_tourism_overnightstays_change_2023_2024"].astype(str).str.replace(",", "", regex=False).astype("Int64")
    )
    return df


def clean_guests_df(df_guests: pd.DataFrame) -> pd.DataFrame:
    df = df_guests.copy()
    df = df[df["Year"] == 2024].drop(columns=["Year", "Overnightstays"], errors="ignore")
    df = df.rename(columns={
        "Bezirke": "bezirk",
        "Guests": "district_tourism_guests_2024",
    })
    df = apply_clean_bezirk(df, "bezirk")
    df["district_tourism_guests_2024"] = (
        df["district_tourism_guests_2024"].astype(str).str.replace(",", "", regex=False).astype("Int64")
    )
    return df


def clean_trees_df(df_trees: pd.DataFrame) -> pd.DataFrame:
    df = df_trees.copy().rename(columns={
        "Bezirk": "bezirk",
        "Street\ntrees\ntotal": "district_street_trees",
    })
    df = apply_clean_bezirk(df, "bezirk")
    df["district_street_trees"] = df["district_street_trees"].astype(str).str.replace(" ", "", regex=False).astype("Int64")
    return df


def clean_census_district_df(df_census: pd.DataFrame) -> pd.DataFrame:
    df = df_census.copy().rename(columns={
        "district": "bezirk",
        "central_heating_percentage": "district_central_heating_percentage",
        "floor_heating_percentage": "district_floor_heating_percentage",
        "block_heating_percentage": "district_block_heating_percentage",
        "stove_heating_percentage": "district_stove_heating_percentage",
        "no_heating_percentage": "district_no_heating_percentage",
        "gas_energy_percentage": "district_gas_energy_percentage",
        "oil_energy_percentage": "district_oil_energy_percentage",
        "mixed_energy_sources_percentage": "district_mixed_energy_sources_percentage",
        "solar_energy_percentage": "district_solar_energy_percentage",
        "wood_pellets_energy_percentage": "district_wood_pellets_energy_percentage",
        "biomass_energy_percentage": "district_biomass_energy_percentage",
        "electric_energy_percentage": "district_electric_energy_percentage",
        "coal_energy_percentage": "district_coal_energy_percentage",
        "no_energy_source_percentage": "district_no_energy_source_percentage",
        "<1950_percentage": "district_housing_built_before_1950_percentage",
        ">2010_percentage": "district_housing_built_after_2010_percentage",
        "total_apartments": "district_total_apartments",
        "occupied_by_owner_percentage": "district_occupied_by_owner_percentage",
        "residentual_rental_percentage": "district_residential_rental_percentage",
        "vacation_leisure_rental_percentage": "district_vacation_leisure_rental_percentage",
        "empty": "district_empty_apartments",
        "empty_percentage": "district_empty_apartments_percentage",
        "avarage_living_space_m2_x": "district_average_living_space_m2",
        "employed": "district_employed",
        "unemployed": "district_unemployed",
        "employed_percentage": "district_employed_percentage",
        "unemployed_percentage": "district_unemployed_percentage",
        "not_working": "district_not_working",
        "not_working_percentage": "district_not_working_percentage",
        "labor_force": "district_labor_force",
        "male_labor_force": "district_male_labor_force",
        "female_labor_force": "district_female_labor_force",
        "total_households": "district_total_households",
        "single_household": "district_single_households",
        "couples_without_children": "district_couples_without_children",
        "couples_with_children": "district_couples_with_children",
        "single_parents": "district_single_parents",
        "WG": "district_shared_apartments",
        "only_seniors": "district_only_seniors_households",
        "owner_percentage": "district_apartment_owner_percentage",
        "tenant_percentage": "district_apartment_tenant_percentage",
        "average_rooms": "district_apartment_average_rooms",
        "average_person_per_household": "district_average_persons_per_household",
        "average_years_of_residence": "district_average_years_of_residence",
        "full_time_employees": "district_full_time_employees",
        "median_income": "district_median_income",
        "total_population": "district_total_population",
        "men_population": "district_male_population",
        "women_population": "district_female_population",
        "single": "district_single_population",
        "couples": "district_couples_population",
        "widowed": "district_widowed_population",
        "divorced": "district_divorced_population",
        "other_civil_status": "district_other_civil_status_population",
        "average_age": "district_average_age",
        "<18": "district_population_under_18",
        "18-29": "district_population_18_29",
        "30-49": "district_population_30_49",
        "50-64": "district_population_50_64",
        ">65": "district_population_65_plus",
        "<18_percentage": "district_population_under_18_percentage",
        "18-29_percentage": "district_population_18_29_percentage",
        "30-49_percentage": "district_population_30_49_percentage",
        "50-64_percentage": "district_population_50_64_percentage",
        ">65_percentage": "district_population_65_plus_percentage",
        "couples_without_children_percentage": "district_couples_without_children_percentage",
        "couples_with_children_percentage": "district_couples_with_children_percentage",
        "owner": "district_apartment_owners",
        "tenant": "district_apartment_tenants",
        "men_population_percentage": "district_male_population_percentage",
        "women_population_percentage": "district_female_population_percentage",
    })
    # Drop columns listed as not needed in the notebook
    drop_cols = [
        "floor_heating", "block_heating", "stove_heating", "no_heating", "gas_energy",
        "oil_energy", "mixed_energy_sources", "solar_energy", "wood_pellets_energy",
        "biomass_energy", "electric_energy", "coal_energy", "no_energy_source", "<1950",
        "1950-1969", "1970-1989", "1990-2009", ">2010", "occupied_by_owner",
        "residentual_rental", "vacation_leisure_rental", "avarage_cold_rent_m2",
        "Unnamed: 51", "vacancy_rate", "single_household_percentage", "single_parents_percentage",
        "WG_percentage", "only_seniors_percentage", "seniors_and_young_adults", "seniors_and_young_adults_percentage",
        "EUR_per_squared_meter", "1_person_EUR_per_squared_meter",
        "3_person_EUR_per_squared_meter", "4_person_EUR_per_squared_meter",
        "5_person_EUR_per_squared_meter", "6_person_EUR_per_squared_meter",
        "1_person_average_rooms", "3_person_average_rooms",
        "4_person_average_rooms", "5_person_average_rooms", "6_person_average_rooms",
        "avarage_living_space_m2_y", "single_percentage", "couples_percentage", "widowed_percentage",
        "divorced_percentage", "other_civil_status_percentage", "<10", "10-19", "20-29", "30-39", "40-49",
        "50-59", "60-69", "70-79", ">80", "<10_percentage", "10-19_percentage", "20-29_percentage",
        "30-39_percentage", "40-49_percentage", "50-59_percentage", "60-69_percentage",
        "70-79_percentage", ">80_percentage",
    ]
    df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

    # Clean bezirk values
    df["bezirk"] = df["bezirk"].map(clean_bezirk_value)

    # Convert all non-bezirk columns: remove commas and cast to numeric (int if possible)
    for col in df.columns.difference(["bezirk"]):
        s = df[col].astype(str).str.replace(",", "", regex=False).str.strip()
        # If any dot present, treat as float; otherwise try int
        if s.str.contains(".").any():
            df[col] = pd.to_numeric(s, errors="coerce")
        else:
            df[col] = pd.to_numeric(s, errors="coerce").astype("Int64")

    df = df.fillna(0)
    return df


def build_bezirk_enrichment(
    *,
    bridges: pd.DataFrame,
    cinemas: pd.DataFrame,
    libraries: pd.DataFrame,
    cars: pd.DataFrame,
    toilets: pd.DataFrame,
    overnight_stays: pd.DataFrame,
    guests: pd.DataFrame,
    trees: pd.DataFrame,
    census: pd.DataFrame,
) -> pd.DataFrame:
    """Merge all district-level enrichment sources into a single master table, replicating the notebook join order."""
    b = clean_bridges_df(bridges)
    c = clean_cinemas_df(cinemas)
    l = clean_libraries_df(libraries)
    ca = clean_cars_df(cars)
    t = aggregate_toilets_df(toilets)
    o = clean_overnight_stays_df(overnight_stays)
    g = clean_guests_df(guests)
    tr = clean_trees_df(trees)
    cz = clean_census_district_df(census)

    master = (
        b.merge(c, on="bezirk", how="outer")
         .merge(ca, on="bezirk", how="outer")
         .merge(g, on="bezirk", how="outer")
         .merge(o, on="bezirk", how="outer")
         .merge(tr, on="bezirk", how="outer")
         .merge(l, on="bezirk", how="outer")
    )
    master = master.merge(cz, on="bezirk", how="outer")
    return master


# ---------------------------------------------------------------------
# Domain: SUBDISTRICT (Ortsteil) tables
# ---------------------------------------------------------------------

def clean_ortsteil_tables(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Ortsteil-level table. Paste logic from your *subdistrict cleaning* notebook.

    Typical actions:
      - rename id/name/bezirk columns
      - coerce numeric demographic columns
      - fix weird whitespaces/encodings in names
      - derive `ortsteil_norm` and `bezirk_norm`
      - ensure one row per ortsteil
    """
    df1 = standardize_columns(df)

    # Example: harmonize common variants (edit to match your file)
    alias_map = {
        "oteil": "ortsteil",  # from Geo boundary file
        "plr_id": "ortsteil_id",
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
# Pipelines that mirror your notebooks step-by-step
# ---------------------------------------------------------------------

def build_census_ortsteil_table(
    census_raw: pd.DataFrame,
    *,
    integer_cols: List[str] | None = None,
    float_cols: List[str] | None = None,
) -> pd.DataFrame:
    """Replicates the *census_2022_table_building* notebook for Ortsteile.

    1) Clean census table
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

    # TODO: add your column selections/renames derived from the notebook
    # e.g., keep = ["ortsteil_id","ortsteil","bezirk","population_total","median_age", …]
    # census = census[keep]

    assert_unique(census, [c for c in ["ortsteil_id", "ortsteil_norm"] if c in census.columns])
    return census


def build_bezirk_master(bezirk_raw: pd.DataFrame) -> pd.DataFrame:
    """Replicates your *district cleaning* notebook to a single tidy table."""
    bez = clean_bezirk_tables(bezirk_raw)
    assert_unique(bez, ["bezirk_norm"]) if "bezirk_norm" in bez.columns else None
    return bez


def build_ortsteil_master(ortsteil_raw: pd.DataFrame) -> pd.DataFrame:
    """Replicates your *subdistrict cleaning* notebook to a single tidy table."""
    ort = clean_ortsteil_tables(ortsteil_raw)
    assert_unique(ort, ["ortsteil_norm"]) if "ortsteil_norm" in ort.columns else None
    return ort


# ---------------------------------------------------------------------
# Subdistrict (Ortsteil) population + rent/income builders (from notebooks)
# ---------------------------------------------------------------------

def pivot_subdistrict_population(df_ort_population: pd.DataFrame) -> pd.DataFrame:
    """Replicates notebook logic to pivot age & gender distributions to wide form
    and compute totals + shares per Ortsteil.
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


def build_street_lookup(df_streets: pd.DataFrame) -> pd.DataFrame:
    """Replicates notebook street lookup creation.
    Input expects columns: ['strassenna','bezirk','stadtteil']
    Returns columns: ['street_name','bezirk','ortsteil'] lower-cased & stripped.
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


def build_ortsteil_rent_income(
    df_miet: pd.DataFrame,
    df_income: pd.DataFrame,
    street_lookup: pd.DataFrame,
) -> pd.DataFrame:
    """Merge Mietspiegel (street-level) and PLR median income to Ortsteil level.
    Mirrors the notebook: normalize street names, join lookup, map classification, aggregate to Ortsteil.
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

    # Normalize keys for safety
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


def normalize_merge_keys(df: pd.DataFrame, bezirk_col: str = "bezirk", ortsteil_col: str = "ortsteil") -> pd.DataFrame:
    """Lowercase/strip and replace German umlauts for join keys (matches notebook)."""
    out = df.copy()
    def _norm(s: pd.Series) -> pd.Series:
        s = s.astype(str).str.strip().str.lower()
        s = s.str.replace("ö", "oe", regex=False).str.replace("ü", "ue", regex=False).str.replace("ä", "ae", regex=False).str.replace("ß", "ss", regex=False)
        return s
    if bezirk_col in out.columns:
        out[bezirk_col] = _norm(out[bezirk_col])
    if ortsteil_col in out.columns:
        out[ortsteil_col] = _norm(out[ortsteil_col])
    return out


def build_ortsteil_master_table(df_population: pd.DataFrame, df_rent_income: pd.DataFrame) -> pd.DataFrame:
    """Final merge (population × rent/income) per Ortsteil, replicating notebook last step."""
    pop = normalize_merge_keys(df_population.copy(), "bezirk", "ortsteil")
    ri = normalize_merge_keys(df_rent_income.copy(), "bezirk", "ortsteil")
    master = pop.merge(ri, on=["bezirk", "ortsteil"], how="inner")
    return master


# ---------------------------------------------------------------------
# Additional cleaning functions (street directory, notebook-style bezirk master)
# ---------------------------------------------------------------------

def clean_street_directory(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw street directory (from split PDF extraction) into a consistent table."""
    # Split into left and right halves
    df_left = df.iloc[:, 0:5].copy()
    df_right = df.iloc[:, 5:12].copy()

    df_left.columns = ["street_name", "location_code", "house_number_range", "house_number_scheme", "classification"]
    df_right.columns = ["street_name", "location_code", "house_number_range", "house_number_scheme", "classification"]

    df_left = df_left.dropna(subset=["street_name"])
    df_right = df_right.dropna(subset=["street_name"])

    df_combined = pd.concat([df_left, df_right], ignore_index=True)

    # Ensure column is string
    df_combined["location_code"] = df_combined["location_code"].astype(str).fillna("")

    # Split into parts
    split_cols = df_combined["location_code"].str.split(" ", n=2, expand=True)
    df_combined["district_code"] = split_cols[0]
    df_combined["street_side"] = split_cols[1]
    df_combined["house_number"] = split_cols[2]

    df_combined.drop(columns=["location_code"], inplace=True)
    df_combined = df_combined[df_combined["classification"].notna()]
    df_combined = df_combined.drop_duplicates()

    # Merge house number with range
    df_combined["house_number_range"] = df_combined.apply(
        lambda row: f"{row['house_number']} {row['house_number_range']}".strip()
        if pd.notnull(row['house_number']) and pd.notnull(row['house_number_range'])
        else row['house_number_range'] if pd.isnull(row['house_number']) else str(row['house_number']),
        axis=1
    )
    df_combined.drop(columns=["house_number"], inplace=True)
    df_combined["house_number_range"] = df_combined["house_number_range"].fillna("whole street")

    scheme_map = {"K": "Complete street","F": "Consecutive numbering","G": "Even numbers only","U": "Odd numbers only"}
    df_combined["house_number_scheme_label"] = df_combined["house_number_scheme"].map(scheme_map)

    district_map = {
        "ChWi": "Charlottenburg-Wilmersdorf","FrKr": "Friedrichshain-Kreuzberg","Lich": "Lichtenberg",
        "MaHe": "Marzahn-Hellersdorf","Mitt": "Mitte","Neuk": "Neukölln","Pank": "Pankow",
        "Rein": "Reinickendorf","Span": "Spandau","StZe": "Steglitz-Zehlendorf","TrKö": "Treptow-Köpenick",
        "TSch": "Tempelhof-Schöneberg"
    }
    df_combined["district"] = df_combined["district_code"].map(district_map)
    df_combined.drop(columns=["district_code"], inplace=True)

    side_map = {"W": "West (pre-2000)","O": "East + West-Staaken (pre-2000)"}
    df_combined["street_side"] = df_combined["street_side"].map(side_map)

    df_combined.rename(columns={
        "house_number_scheme": "house_number_scheme_code",
        "house_number_scheme_label": "house_number_scheme",
        "street_side": "territorial_side"
    }, inplace=True)

    columns_order = ["street_name","district","territorial_side","house_number_range","house_number_scheme_code","house_number_scheme","classification"]
    return df_combined[columns_order]


def build_bezirk_master_notebook_style(
    buildings: pd.DataFrame,
    employment: pd.DataFrame,
    households: pd.DataFrame,
    median_income: pd.DataFrame,
    population: pd.DataFrame,
    rent_m2: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate multiple district-level datasets into a single master table (as in notebook)."""
    rent_agg = rent_m2.groupby("district").agg({
        "minRent": "mean","avgRent": "mean","maxRent": "mean","minBuy": "mean","avgBuy": "mean"
    }).reset_index()

    rent_agg.rename(columns={
        "minRent": "district_min_rent_m2","avgRent": "district_avg_rent_m2","maxRent": "district_max_rent_m2",
        "minBuy": "district_min_buy_m2","avgBuy": "district_avg_buy_m2"
    }, inplace=True)

    master = (
        buildings
        .merge(employment, on="district", how="outer")
        .merge(households, on="district", how="outer")
        .merge(median_income, on="district", how="outer")
        .merge(population, on="district", how="outer")
        .merge(rent_agg, on="district", how="outer")
    )

    for col in master.columns:
        if master[col].dtype == "object":
            try:
                master[col] = (
                    master[col].replace(r"[^0-9\.\-]", "", regex=True).astype(float)
                )
            except ValueError:
                pass

    return master
