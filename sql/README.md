# SQL Layer

This folder contains the optional SQL layer for the Berlin Housing Affordability project.  

It organizes queries into **cleaning**, **references**, and **gold** tables, following a typical data warehouse layering approach (clean → reference → bronze → silver → gold).

## Structure

### `clean/`

Queries to normalize and clean raw subdistrict data:

- `clean_subdistrict_alias.sql` – Standardizes known aliases for subdistrict names.
- `clean_subdistrict_spelling.sql` – Fixes spelling variations and inconsistencies.

### `references/`

Reference tables used as lookup helpers:

- `subdistrict_id_mapping.sql` – Maps subdistrict names to consistent IDs.
- `unique_alias_reference.sql` – Stores unique aliases for cross-checking.

### `gold/`

Final analytical tables built from cleaned + referenced data:

- `gold_dim_age_bands.sql` – Dimension of age bands.
- `gold_dim_dis_sub.sql` – District–subdistrict relationships.
- `gold_dim_mietspiegel_class.sql` – Mietspiegel rent classes by subdistrict.
- `gold_dim_poi_groups.sql` – Points of interest grouped into categories.
- `gold_dist_hous_char.sql` – District housing characteristics.
- `gold_dist_infrastructure.sql` – District infrastructure indicators.
- `gold_dist_tourisme.sql` – Tourism-related metrics.
- `gold_fact_dist_demographics.sql` – District-level demographics fact table.
- `gold_fact_dist_hous_stock.sql` – District housing stock fact table.
- `gold_fact_sub_age_groups.sql` – Subdistrict age group fact table.
- `gold_sub_age.sql` – Subdistrict-level age distributions.
- `gold_sub_demographics.sql` – Subdistrict demographics fact table.
- `gold_sub_poi.sql` – Subdistrict points of interest fact table.

## Notes

- These SQL scripts are **illustrative**: they document how the data could be modeled
  in a warehouse (BigQuery, Snowflake, Postgres).
- The project primarily runs on the **Python pipeline**, but this layer shows how
  a structured **clean → gold** model could be built for reusability and BI tools.
- Not all scripts are required to run the app; they are included as an architectural
  reference and for transparency.