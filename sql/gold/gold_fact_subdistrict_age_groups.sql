-- Add age_band_id into fact_subdistrict_age
CREATE OR REPLACE TABLE gold.fact_subdistrict_age_groups AS
SELECT
    f.subdistrict_id,
    d.age_band_id,
    f.population
FROM
    gold.fact_subdistrict_age f
JOIN
    gold.dim_age_band d
    ON f.age_band_label = d.label;