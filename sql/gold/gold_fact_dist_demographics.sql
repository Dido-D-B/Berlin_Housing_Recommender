CREATE OR REPLACE TABLE `berlin-housing-468808.gold.fact_district_demographics`
CLUSTER BY district_id AS
SELECT
  LPAD(CAST(m.district_id AS STRING),2,'0') AS district_id,
  2024                                       AS year,
  population_total, population_male, population_male_pct,
  population_female, population_female_pct, average_age,
  population_under_18, population_under_18_pct,
  population_18_29,   population_18_29_pct,
  population_30_49,   population_30_49_pct,
  population_50_64,   population_50_64_pct,
  population_65_plus, population_65_plus_pct,
  single_population, couples_population, widowed_population,
  divorced_population, other_civil_status_population,
  total_households, single_households, couples_without_children,
  couples_without_children_pct, couples_with_children, couples_with_children_pct,
  single_parents, shared_apartments, only_seniors_households,
  labor_force, male_labor_force, female_labor_force,
  employed, employed_pct, unemployed, unemployed_pct, not_working, not_working_pct,
  full_time_employees, median_income,
  min_rent_m2, avg_rent_m2, max_rent_m2, min_buy_m2, avg_buy_m2,
  apartment_avg_rooms, two_person_avg_rooms, two_person_eur_per_m2
FROM `berlin-housing-468808.silver.district_demographics` s
JOIN (
  SELECT DISTINCT district_id, bezirk FROM `berlin-housing-468808.silver.subdistrict_id_map`
) m ON LOWER(s.bezirk)=LOWER(m.bezirk);