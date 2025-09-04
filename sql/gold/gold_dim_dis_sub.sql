-- DIM DISTRICT
CREATE OR REPLACE TABLE `berlin-housing-468808.gold.dim_district` AS 
SELECT DISTINCT
  LPAD(CAST(district_id AS STRING),2,'0') AS district_id,
  INITCAP(bezirk)                         AS district_name
FROM `berlin-housing-468808.silver.subdistrict_id_map`;

-- DIM SUBDISTRICT
CREATE OR REPLACE TABLE `berlin-housing-468808.gold.dim_subdistrict` AS
SELECT DISTINCT
  LPAD(CAST(subdistrict_id AS STRING),3,'0') AS subdistrict_id,
  LPAD(CAST(district_id  AS STRING),2,'0')   AS district_id,
  INITCAP(ortsteil)                          AS subdistrict_name
FROM `berlin-housing-468808.silver.subdistrict_id_map`;