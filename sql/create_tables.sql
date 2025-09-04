-- =====================================================================
-- Berlin Housing – Base Objects
-- File: sql/create_tables.sql
-- Purpose: Create stable reference tables and reusable UDFs that all
--          downstream scripts (clean/ → silver/ → gold/) depend on.
-- Engine:  BigQuery Standard SQL
-- Usage:   Edit the placeholders PROJECT_ID and DATASET to match your
--          BigQuery project & dataset, then run the script in BigQuery
--          (or via: bq query --use_legacy_sql=false < create_tables.sql)
-- =====================================================================

-- ---------------------------------------------------------------------------------
-- OPTIONAL: If you keep references/clean/silver/gold as *folders in Git* only,
-- you likely have a single BigQuery dataset (e.g. `berlin_housing`).
-- Replace PROJECT_ID.DATASET below with that dataset.
-- ---------------------------------------------------------------------------------

-- =====================================================================
-- 1) Reusable Text Normalization UDF (for alias & spelling cleaning)
-- =====================================================================
-- Removes accents/diacritics, collapses whitespace, lowercases.
CREATE OR REPLACE FUNCTION `PROJECT_ID.DATASET.normalize_text`(s STRING)
RETURNS STRING AS (
  LOWER(
    REGEXP_REPLACE(
      REGEXP_REPLACE(NORMALIZE(s, NFKD), r"[\p{M}]", ""),  -- strip diacritics
      r"\s+", " "                                          -- collapse spaces
    )
  )
);

-- =====================================================================
-- 2) Reference Tables (hand‑maintained or loaded from CSV)
-- =====================================================================
-- These are stable lookups you load once (e.g., from data/references/*.csv)
-- and then join throughout the pipeline.

-- 2.1 Subdistrict ID mapping: canonical IDs + names
CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.subdistrict_id_mapping` (
  subdistrict_id     INT64      NOT NULL,   -- stable numeric ID you control
  ortsteil_name      STRING     NOT NULL,   -- official name (with umlauts)
  ortsteil_clean     STRING     NOT NULL,   -- normalized via normalize_text()
  bezirk_name        STRING     NOT NULL,   -- district official name
  bezirk_clean       STRING     NOT NULL,   -- normalized district name
  source             STRING,                -- where the mapping came from
  valid_from         DATE       DEFAULT DATE '2020-01-01',
  valid_to           DATE,
  is_current         BOOL       DEFAULT TRUE
);

-- 2.2 Unique alias reference for fuzzy/spelling harmonization
CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.unique_alias_reference` (
  entity_type    STRING   NOT NULL,   -- 'subdistrict' | 'district'
  alias          STRING   NOT NULL,   -- variant (e.g., 'prenzl brg', 'prenzlauer-berg')
  alias_clean    STRING   NOT NULL,   -- normalize_text(alias)
  canonical_name STRING   NOT NULL,   -- official label you want to keep
  canonical_clean STRING  NOT NULL,   -- normalize_text(canonical_name)
  notes          STRING,
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Helpful index via clustering for faster lookups
CREATE OR REPLACE TABLE `PROJECT_ID.DATASET.unique_alias_reference`
PARTITION BY DATE(created_at)
CLUSTER BY entity_type, alias_clean AS
SELECT * FROM `PROJECT_ID.DATASET.unique_alias_reference`;

-- =====================================================================
-- 3) Raw Landing Tables (optional)
-- =====================================================================
-- If you prefer to *load* raw CSVs before transforming, create simple
-- landing tables. If you use external tables instead, skip this section.

-- Example: Mietspiegel (minimal fields – extend to your schema as needed)
CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.raw_mietspiegel` (
  year                INT64,
  subdistrict_name    STRING,
  rent_class          STRING,     -- e.g., A..H or your numeric bins
  avg_rent_eur_m2     FLOAT64,
  sample_size         INT64
);

-- Example: Subdistrict demographics (aggregate level)
CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.raw_subdistrict_demographics` (
  year                INT64,
  subdistrict_name    STRING,
  total_population    INT64,
  age_0_17            INT64,
  age_18_29           INT64,
  age_30_44           INT64,
  age_45_64           INT64,
  age_65_plus         INT64
);

-- Example: POI counts (pre‑computed in Python/osmnx pipeline)
CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.raw_subdistrict_poi_counts` (
  subdistrict_name    STRING,
  cafes               INT64,
  restaurants         INT64,
  bars                INT64,
  nightclubs          INT64,
  libraries           INT64,
  schools             INT64,
  parks               INT64
);

-- =====================================================================
-- 4) Staging/Clean Targets (empty shells; populated by clean/*.sql)
-- =====================================================================
-- These tables are the *outputs* of your clean/ queries. We define
-- schemas so downstream layers can rely on stable column types.

CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.clean_subdistrict_spelling` (
  subdistrict_name     STRING,
  subdistrict_clean    STRING,
  normalized_name      STRING
);

CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.clean_subdistrict_alias` (
  alias                STRING,
  alias_clean          STRING,
  canonical_name       STRING,
  canonical_clean      STRING
);

-- =====================================================================
-- 5) Silver Targets (populated by silver/*.sql)
-- =====================================================================
-- Example schemas; adapt to your actual select lists.

CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.silver_subdistrict_mietspiegel` (
  subdistrict_id       INT64,
  year                 INT64,
  rent_class           STRING,
  avg_rent_eur_m2      FLOAT64
);

CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.silver_subdistrict_poi` (
  subdistrict_id       INT64,
  cafes                INT64,
  restaurants          INT64,
  bars                 INT64,
  nightclubs           INT64,
  libraries            INT64,
  schools              INT64,
  parks                INT64
);

-- =====================================================================
-- 6) Gold Targets (populated by gold/*.sql)
-- =====================================================================
-- Dimensions
CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.gold_dim_mietspiegel_class` (
  rent_class           STRING,
  class_order          INT64,     -- for chart sorting
  description          STRING
);

-- Facts
CREATE TABLE IF NOT EXISTS `PROJECT_ID.DATASET.gold_fact_subdistrict_age_groups` (
  subdistrict_id       INT64,
  year                 INT64,
  age_band             STRING,    -- e.g., '0‑17','18‑29','30‑44','45‑64','65+'
  population           INT64
);

-- =====================================================================
-- Notes:
-- • Only define schemas you truly need here. Your clean/silver/gold SQL
--   will usually use CREATE OR REPLACE TABLE ... AS SELECT to populate
--   these targets (or to recreate them end‑to‑end).
-- • If you prefer views for the gold layer, switch your gold/*.sql to
--   CREATE OR REPLACE VIEW and drop the corresponding CREATE TABLE here.
-- • If you use external tables for raw CSVs, replace the raw_* examples
--   with CREATE EXTERNAL TABLE definitions.
-- =====================================================================