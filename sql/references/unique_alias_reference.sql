-- Unique reference (one row per canonical name)
CREATE OR REPLACE TABLE `berlin-housing-468808.silver.subdistrict_reference_unique` AS
SELECT * EXCEPT(rn)
FROM (
  SELECT r.*,
         ROW_NUMBER() OVER (
           PARTITION BY r.bezirk_std, r.ortsteil_std
           ORDER BY r.subdistrict_id
         ) AS rn
  FROM `berlin-housing-468808.silver.subdistrict_reference` r
)
WHERE rn = 1;

-- Unique alias (one raw -> one canonical)
CREATE OR REPLACE TABLE `berlin-housing-468808.silver.subdistrict_alias_unique` AS
SELECT * EXCEPT(rn)
FROM (
  SELECT a.*,
         ROW_NUMBER() OVER (
           PARTITION BY a.bezirk_alias, a.ortsteil_alias
           ORDER BY a.ortsteil_canonical
         ) AS rn
  FROM `berlin-housing-468808.silver.subdistrict_alias` a
)
WHERE rn = 1;