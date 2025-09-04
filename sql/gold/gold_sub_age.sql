CREATE OR REPLACE TABLE `berlin-housing-468808.gold.fact_subdistrict_age`
CLUSTER BY subdistrict_id, age_band_label AS
WITH src AS (
  SELECT
    LPAD(CAST(p.subdistrict_id AS STRING), 3, '0') AS subdistrict_id,
    2024    AS year,
    p.age_0_5, p.age_5_10, p.age_10_15, p.age_15_20, p.age_20_25,
    p.age_25_30, p.age_30_35, p.age_35_40, p.age_40_45, p.age_45_50,
    p.age_50_55, p.age_55_60, p.age_60_65, p.age_65_70, p.age_70_75,
    p.age_75_80, p.age_80_85, p.age_85_90, p.age_90_95, p.age_95_plus
  FROM `berlin-housing-468808.silver_norm.subdistrict_population` p
),
long AS (
  SELECT
    subdistrict_id,
    year,
    REPLACE(age_label, 'age_', '')     AS age_band_label,
    SAFE_CAST(pop AS INT64)            AS population
  FROM src
  UNPIVOT (pop FOR age_label IN (
    age_0_5, age_5_10, age_10_15, age_15_20, age_20_25, age_25_30, age_30_35, age_35_40,
    age_40_45, age_45_50, age_50_55, age_55_60, age_60_65, age_65_70, age_70_75, age_75_80,
    age_80_85, age_85_90, age_90_95, age_95_plus
  ))
)
SELECT * FROM long;