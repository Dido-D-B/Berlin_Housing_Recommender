# Imports
import pandas as pd
from __future__ import annotations
from .clean_shared import (
    standardize_columns,
    coerce_dtypes,
    drop_duplicates_key,
    normalize_name,
    clean_bezirk_value,
    apply_clean_bezirk,
)

 # Utility: ensure uniqueness by Bezirk
def _ensure_unique_by_bezirk(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    Guarantee one row per 'bezirk'.
    - numeric columns -> sum
    - non-numeric    -> first
    """
    if "bezirk" not in df.columns or df.empty:
        return df

    if not df["bezirk"].duplicated().any():
        return df

    num_cols = df.select_dtypes(include="number").columns.tolist()
    agg_map = {c: "sum" for c in num_cols}
    for c in df.columns:
        if c not in agg_map and c != "bezirk":
            agg_map[c] = "first"

    out = df.groupby("bezirk", as_index=False).agg(agg_map)
    out = out.drop_duplicates(subset=["bezirk"])
    return out

# Core Bezirk table cleaner
def clean_bezirk_tables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Bezirk-level table.

    Actions:
      - standardize/rename bezirk column to `bezirk`
      - coerce numerical indicators (leave as-is; only ensure `bezirk` is str)
      - build `bezirk_norm` for joins
      - ensure one row per bezirk
    """
    df1 = standardize_columns(df)
    if "bezirk" not in df1.columns:
        for candidate in ("district", "bezirk_name"):
            if candidate in df1.columns:
                df1 = df1.rename(columns={candidate: "bezirk"})
                break
    df1 = coerce_dtypes(df1, str_cols=["bezirk"])
    if "bezirk" in df1.columns:
        df1["bezirk_norm"] = df1["bezirk"].map(normalize_name)
    df1 = drop_duplicates_key(df1, ["bezirk_norm"]) if "bezirk_norm" in df1.columns else df1
    return df1


# District enrichment table cleaners (bridges, cinemas, libraries, cars, toilets, tourism, trees, census slice)
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

 # Clean cinemas dataset
def clean_cinemas_df(df_cinemas: pd.DataFrame) -> pd.DataFrame:
    df = df_cinemas.copy()
    df = df.dropna(subset=["Bezirk"]).rename(columns={
        "Bezirk": "bezirk",
        "Movie Theaters": "district_movie_theaters",
    })
    df = apply_clean_bezirk(df, "bezirk")
    df["district_movie_theaters"] = pd.to_numeric(df["district_movie_theaters"], errors="coerce").astype("Int64")
    return df

 # Clean libraries dataset
def clean_libraries_df(df_libraries: pd.DataFrame) -> pd.DataFrame:
    df = df_libraries.copy()
    df = df.rename(columns={
        "Bezirk": "bezirk",
        "Libraries": "district_libraries",
        "visits": "district_libraries_visits",
        "borrowings": "district_libraries_borrowings",
    })
    df = apply_clean_bezirk(df, "bezirk")
    df["district_libraries_visits"] = (
        df["district_libraries_visits"].astype(str).str.replace(",", "", regex=False).astype("Int64")
    )
    df["district_libraries_borrowings"] = (
        df["district_libraries_borrowings"].astype(str).str.replace(",", "", regex=False).astype("Int64")
    )
    return df

 # Clean cars dataset
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

 # Aggregate toilets dataset
def aggregate_toilets_df(df_toilets: pd.DataFrame) -> pd.DataFrame:
    df = (
        df_toilets.groupby("Bezirk").agg(district_public_toilets=("ID", "count")).reset_index()
        .rename(columns={"Bezirk": "bezirk"})
    )
    df = apply_clean_bezirk(df, "bezirk")
    return df

 # Clean overnight stays dataset
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

 # Clean guests dataset
def clean_guests_df(df_guests: pd.DataFrame) -> pd.DataFrame:
    df = df_guests.copy()

    # If Year exists, prefer 2024, else max-year; otherwise skip the filter
    if "Year" in df.columns:
        if (df["Year"] == 2024).any():
            df = df[df["Year"] == 2024]
        else:
            try:
                df = df[df["Year"] == df["Year"].max()]
            except Exception:
                pass
        df = df.drop(columns=[c for c in ["Year", "Overnightstays"] if c in df.columns], errors="ignore")

    df = df.rename(columns={
        "Bezirke": "bezirk",
        "Guests": "district_tourism_guests_2024",
    })
    df = apply_clean_bezirk(df, "bezirk")

    if "district_tourism_guests_2024" in df.columns:
        df["district_tourism_guests_2024"] = (
            df["district_tourism_guests_2024"]
            .astype(str).str.replace(",", "", regex=False).str.replace(" ", "", regex=False)
            .pipe(pd.to_numeric, errors="coerce").astype("Int64")
        )

    df = _ensure_unique_by_bezirk(df, "guests")
    return df

 # Clean trees dataset
def clean_trees_df(df_trees: pd.DataFrame) -> pd.DataFrame:
    df = df_trees.copy().rename(columns={
        "Bezirk": "bezirk",
        "Street\ntrees\ntotal": "district_street_trees",
    })
    df = apply_clean_bezirk(df, "bezirk")
    df["district_street_trees"] = df["district_street_trees"].astype(str).str.replace(" ", "", regex=False).astype("Int64")
    return df

# Clean census data
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

    # Convert all non-bezirk columns to numeric
    for col in df.columns.difference(["bezirk"]):
        s = df[col].astype(str).str.replace(",", "", regex=False).str.strip()
        if s.str.contains(".").any():
            df[col] = pd.to_numeric(s, errors="coerce")
        else:
            df[col] = pd.to_numeric(s, errors="coerce").astype("Int64")

    df = df.fillna(0)

    # Collapse to one row per bezirk
    num_cols = df.select_dtypes(include=["number", "Int64"]).columns.tolist()
    agg_map = {c: "sum" for c in num_cols}
    out = df.groupby("bezirk", as_index=False).agg(agg_map)
    out = out.drop_duplicates(subset=["bezirk"])  # enforce uniqueness
    return out

# Enrichment merge (final Bezirk master)
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
    """Merge all district-level enrichment sources into a single master table (join order mirrors notebook)."""
    b  = _ensure_unique_by_bezirk(clean_bridges_df(bridges), "bridges")
    c  = _ensure_unique_by_bezirk(clean_cinemas_df(cinemas), "cinemas")
    l  = _ensure_unique_by_bezirk(clean_libraries_df(libraries), "libraries")
    ca = _ensure_unique_by_bezirk(clean_cars_df(cars), "cars")
    t  = _ensure_unique_by_bezirk(aggregate_toilets_df(toilets), "toilets")
    o  = _ensure_unique_by_bezirk(clean_overnight_stays_df(overnight_stays), "overnight_stays")
    g  = _ensure_unique_by_bezirk(clean_guests_df(guests), "guests")
    tr = _ensure_unique_by_bezirk(clean_trees_df(trees), "trees")
    cz = _ensure_unique_by_bezirk(clean_census_district_df(census), "census")

    master = (
        b.merge(c, on="bezirk", how="outer")
         .merge(ca, on="bezirk", how="outer")
         .merge(g, on="bezirk", how="outer")
         .merge(o, on="bezirk", how="outer")
         .merge(tr, on="bezirk", how="outer")
         .merge(l, on="bezirk", how="outer")
         .merge(cz, on="bezirk", how="outer")
    )

    master = _ensure_unique_by_bezirk(master, "master")
    return master


# Notebook-style Bezirk master (alternate builder)
def build_bezirk_master_notebook_style(
    buildings: pd.DataFrame,
    employment: pd.DataFrame,
    households: pd.DataFrame,
    median_income: pd.DataFrame,
    population: pd.DataFrame,
    rent_m2: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate multiple district-level datasets into a single master table (as in the notebook).
    """
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

    # best-effort numeric coercion for object cols
    for col in master.columns:
        if master[col].dtype == "object":
            try:
                master[col] = (
                    master[col].replace(r"[^0-9\.\-]", "", regex=True).astype(float)
                )
            except ValueError:
                pass

    return master


# Public API of this module
__all__ = [
    "clean_bezirk_tables",
    "clean_bridges_df",
    "clean_cinemas_df",
    "clean_libraries_df",
    "clean_cars_df",
    "aggregate_toilets_df",
    "clean_overnight_stays_df",
    "clean_guests_df",
    "clean_trees_df",
    "clean_census_district_df",
    "build_bezirk_enrichment",
    "build_bezirk_master_notebook_style",
]