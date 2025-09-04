CREATE OR REPLACE TABLE `silver.subdistrict_mietspiegel` AS
SELECT
  INITCAP(TRIM(ortsteil)) AS ortsteil,
  classification_category AS mietspiegel_class,
  SAFE_CAST(subdistrict_avg_mietspiegel_classification AS FLOAT64) AS mietspiegel,
  SAFE_CAST(subdistrict_total_full_time_employees AS FLOAT64)      AS full_time_employees,
  SAFE_CAST(subdistrict_avg_median_income_eur AS FLOAT64)          AS median_income
FROM `bronze.subdistrict_mietspiegel`;