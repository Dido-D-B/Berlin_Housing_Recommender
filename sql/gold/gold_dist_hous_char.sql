CREATE OR REPLACE TABLE `berlin-housing-468808.gold.fact_district_housing_characteristics`
CLUSTER BY district_id AS
SELECT
  LPAD(CAST(m.district_id AS STRING),2,'0') AS district_id,
  2024                                       AS year,
  central_heating_pct, floor_heating_pct, block_heating_pct, stove_heating_pct, no_heating_pct,
  gas_pct, oil_pct, mixed_energy_pct, solar_pct, wood_pellets_pct, biomass_pct, electric_pct, coal_pct, no_energy_source_pct,
  built_pre_1950_pct, built_1950_1969_pct, built_1970_1989_pct, built_1990_2009_pct, built_2010_plus_pct
FROM `berlin-housing-468808.silver.district_housing_characteristics` s
JOIN (
  SELECT DISTINCT district_id, bezirk FROM `berlin-housing-468808.silver.subdistrict_id_map`
) m ON LOWER(s.bezirk)=LOWER(m.bezirk);