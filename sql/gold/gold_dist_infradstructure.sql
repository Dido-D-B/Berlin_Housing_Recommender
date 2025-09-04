CREATE OR REPLACE TABLE `berlin-housing-468808.gold.fact_district_infrastructure`
CLUSTER BY district_id AS
SELECT
  LPAD(CAST(m.district_id AS STRING),2,'0') AS district_id,
  2024                                       AS year,
  num_bridges_total, num_bridges_city_streets, num_bridges_green_spaces,
  movie_theaters, total_cars, private_cars, private_cars_per_100,
  num_street_trees, num_libraries, library_visits, library_borrowings
FROM `berlin-housing-468808.silver.district_infrastructure` s
JOIN (
  SELECT DISTINCT district_id, bezirk FROM `berlin-housing-468808.silver.subdistrict_id_map`
) m ON LOWER(s.bezirk)=LOWER(m.bezirk);