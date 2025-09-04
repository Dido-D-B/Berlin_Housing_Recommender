CREATE OR REPLACE FUNCTION `berlin-housing-468808.silver.norm_de`(s STRING)
RETURNS STRING AS (LOWER(
  REGEXP_REPLACE(
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
      TRIM(s), 'ä','ae'),'ö','oe'),'ü','ue'),'Ä','ae'),'Ö','oe'),'Ü','ue'),'ß','ss'),
    r'[\s\-_]+',' '
  )
));