CREATE OR REPLACE TABLE `berlin-housing-468808.gold.fact_subdistrict_demographics`
CLUSTER BY subdistrict_id AS
SELECT
  LPAD(CAST(p.subdistrict_id AS STRING), 3, '0') AS subdistrict_id,
  2024   AS year,
  SAFE_CAST(p.population_total         AS INT64) AS population_total,
  SAFE_CAST(p.population_female        AS INT64) AS population_female,
  SAFE_CAST(p.population_male          AS INT64) AS population_male,
  SAFE_CAST(p.youth_population         AS INT64) AS youth_population,
  SAFE_CAST(p.middle_age_population    AS INT64) AS middle_age_population,
  SAFE_CAST(p.senior_population        AS INT64) AS senior_population
FROM `berlin-housing-468808.silver_norm.subdistrict_population` p;