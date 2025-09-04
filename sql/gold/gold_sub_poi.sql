CREATE OR REPLACE TABLE `berlin-housing-468808.gold.fact_subdistrict_poi`
CLUSTER BY subdistrict_id, poi_name AS
WITH src AS (
  SELECT
    LPAD(CAST(p.subdistrict_id AS STRING), 3, '0') AS subdistrict_id,
    2024 AS year,                                -- set your snapshot year
    -- keep only the POI columns we want to UNPIVOT
    p.alcohol, p.animal_training, p.antiques, p.art, p.bar, p.bathing_place, p.books,
    p.butcher, p.childcare, p.clothes, p.community_centre, p.confectionery, p.convenience,
    p.deli, p.dog_park, p.electronics, p.fitness_station, p.florist, p.fountain, p.garden,
    p.greenfield, p.greengrocer, p.hairdresser, p.ice_cream, p.kiosk, p.marina,
    p.nature_reserve, p.nightclub, p.parking, p.pitch, p.playground, p.restaurant,
    p.second_hand, p.stationery, p.supermarket, p.tea, p.art_2, p.theatre, p.travel_agency,
    p.vacant, p.wine, p.yes, p.cafes, p.bakeries, p.green_space, p.schools, p.medical
  FROM `berlin-housing-468808.silver_norm.subdistrict_poi` p
),
long AS (
  SELECT
    subdistrict_id,
    year,
    poi_name,
    SAFE_CAST(cnt AS INT64) AS poi_count
  FROM src
  UNPIVOT (cnt FOR poi_name IN (
    alcohol, animal_training, antiques, art, bar, bathing_place, books, butcher, childcare, clothes,
    community_centre, confectionery, convenience, deli, dog_park, electronics, fitness_station,
    florist, fountain, garden, greenfield, greengrocer, hairdresser, ice_cream, kiosk, marina,
    nature_reserve, nightclub, parking, pitch, playground, restaurant, second_hand, stationery,
    supermarket, tea, art_2, theatre, travel_agency, vacant, wine, yes, cafes, bakeries, green_space,
    schools, medical
  ))
)
SELECT * FROM long;