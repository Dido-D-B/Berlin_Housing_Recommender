CREATE OR REPLACE TABLE `berlin-housing-468808.gold.fact_district_housing_stock`
CLUSTER BY district_id AS
SELECT
  LPAD(CAST(m.district_id AS STRING),2,'0') AS district_id,
  2024                                       AS year,
  total_apartments, owner_occupied_pct, tenant_occupied_pct, vacation_leisure_rental_pct,
  empty_apartments, empty_apartments_pct,
  avg_living_space_m2,
  apartment_owners, apartment_owner_pct, apartment_tenants, apartment_tenant_pct,
  apartment_avg_rooms, two_person_avg_rooms, avg_persons_per_household, avg_years_of_residence
FROM `berlin-housing-468808.silver.district_housing_stock` s
JOIN (
  SELECT DISTINCT district_id, bezirk FROM `berlin-housing-468808.silver.subdistrict_id_map`
) m ON LOWER(s.bezirk)=LOWER(m.bezirk);