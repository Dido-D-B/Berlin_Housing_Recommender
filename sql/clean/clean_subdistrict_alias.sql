CREATE OR REPLACE TABLE `berlin-housing-468808.silver.subdistrict_alias` (
  bezirk_alias STRING,        -- raw input spelling
  ortsteil_alias STRING,      -- raw input spelling
  ortsteil_canonical STRING   -- your canonical (lowercase ASCII)
);

INSERT INTO `berlin-housing-468808.silver.subdistrict_alias`
  (bezirk_alias, ortsteil_alias, ortsteil_canonical)
VALUES
  -- Pankow
  ('Pankow','Französisch Buchholz','franzoesisch buchholz'),
  ('Pankow','Niederschönhausen','niederschoenhausen'),
  ('Pankow','Weißensee','weissensee'),
  -- Reinickendorf
  ('Reinickendorf','Konradshöhe','konradshoehe'),
  ('Reinickendorf','Lübars','luebars'),
  ('Reinickendorf','Märkisches Viertel','maerkisches viertel'),
  -- Tempelhof-Schöneberg
  ('Tempelhof-Schöneberg','Schöneberg','schoeneberg'),
  -- Treptow-Köpenick
  ('Treptow-Köpenick','Grünau','gruenau'),
  ('Treptow-Köpenick','Köpenick','koepenick'),
  ('Treptow-Köpenick','Müggelheim','mueggelheim'),
  ('Treptow-Köpenick','Niederschöneweide','niederschoeneweide'),
  ('Treptow-Köpenick','Oberschöneweide','oberschoeneweide'),
  ('Treptow-Köpenick','Plänterwald','plaenterwald'),
  ('Treptow-Köpenick','Schmöckwitz','schmoeckwitz'),
  -- Steglitz-Zehlendorf: Schlachtensee is locality in Zehlendorf
  ('Steglitz-Zehlendorf','Schlachtensee','zehlendorf');