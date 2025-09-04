CREATE OR REPLACE TABLE `berlin-housing-468808.gold.fact_district_tourism`
CLUSTER BY district_id AS
SELECT
  LPAD(CAST(m.district_id AS STRING),2,'0') AS district_id,
  2024                                       AS year,
  SAFE_CAST(guests_2024 AS INT64)            AS guests,
  SAFE_CAST(overnight_stays_2024 AS INT64)   AS overnight_stays,
  SAFE_CAST(overnight_stays_change_2023_2024 AS FLOAT64) AS yoy_change_pct
FROM `berlin-housing-468808.silver.district_tourism` s
JOIN (
  SELECT DISTINCT district_id, bezirk FROM `berlin-housing-468808.silver.subdistrict_id_map`
) m ON LOWER(s.bezirk)=LOWER(m.bezirk);