-- Recreate the canonical subdistrict ID map (96 rows)
CREATE OR REPLACE TABLE `berlin-housing-468808.gold.subdistrict_id_map` AS
SELECT * FROM UNNEST([
  -- 1) MITTE (01x)
  STRUCT(1 AS district_id, 101 AS subdistrict_id, 'mitte' AS bezirk, 'mitte' AS ortsteil),
  STRUCT(1, 102, 'mitte', 'moabit'),
  STRUCT(1, 103, 'mitte', 'hansaviertel'),
  STRUCT(1, 104, 'mitte', 'tiergarten'),
  STRUCT(1, 105, 'mitte', 'wedding'),
  STRUCT(1, 106, 'mitte', 'gesundbrunnen'),

  -- 2) FRIEDRICHSHAIN-KREUZBERG (02x)
  STRUCT(2, 201, 'friedrichshain-kreuzberg', 'friedrichshain'),
  STRUCT(2, 202, 'friedrichshain-kreuzberg', 'kreuzberg'),

  -- 3) PANKOW (03x)
  STRUCT(3, 301, 'pankow', 'prenzlauer berg'),
  STRUCT(3, 302, 'pankow', 'weissensee'),
  STRUCT(3, 303, 'pankow', 'blankenburg'),
  STRUCT(3, 304, 'pankow', 'heinersdorf'),
  STRUCT(3, 305, 'pankow', 'karow'),
  STRUCT(3, 306, 'pankow', 'stadtrandsiedlung malchow'),
  STRUCT(3, 307, 'pankow', 'pankow'),
  STRUCT(3, 308, 'pankow', 'blankenfelde'),
  STRUCT(3, 309, 'pankow', 'buch'),
  STRUCT(3, 310, 'pankow', 'franzoesisch buchholz'),
  STRUCT(3, 311, 'pankow', 'niederschoenhausen'),
  STRUCT(3, 312, 'pankow', 'rosenthal'),
  STRUCT(3, 313, 'pankow', 'wilhelmsruh'),

  -- 4) CHARLOTTENBURG-WILMERSDORF (04x)
  STRUCT(4, 401, 'charlottenburg-wilmersdorf', 'charlottenburg'),
  STRUCT(4, 402, 'charlottenburg-wilmersdorf', 'wilmersdorf'),
  STRUCT(4, 403, 'charlottenburg-wilmersdorf', 'schmargendorf'),
  STRUCT(4, 404, 'charlottenburg-wilmersdorf', 'grunewald'),
  STRUCT(4, 405, 'charlottenburg-wilmersdorf', 'westend'),
  STRUCT(4, 406, 'charlottenburg-wilmersdorf', 'charlottenburg-nord'),
  STRUCT(4, 407, 'charlottenburg-wilmersdorf', 'halensee'),

  -- 5) SPANDAU (05x)
  STRUCT(5, 501, 'spandau', 'spandau'),
  STRUCT(5, 502, 'spandau', 'haselhorst'),
  STRUCT(5, 503, 'spandau', 'siemensstadt'),
  STRUCT(5, 504, 'spandau', 'staaken'),
  STRUCT(5, 505, 'spandau', 'gatow'),
  STRUCT(5, 506, 'spandau', 'kladow'),
  STRUCT(5, 507, 'spandau', 'hakenfelde'),
  STRUCT(5, 508, 'spandau', 'falkenhagener feld'),
  STRUCT(5, 509, 'spandau', 'wilhelmstadt'),

  -- 6) STEGLITZ-ZEHLENDORF (06x)
  STRUCT(6, 601, 'steglitz-zehlendorf', 'steglitz'),
  STRUCT(6, 602, 'steglitz-zehlendorf', 'lichterfelde'),
  STRUCT(6, 603, 'steglitz-zehlendorf', 'lankwitz'),
  STRUCT(6, 604, 'steglitz-zehlendorf', 'zehlendorf'),
  STRUCT(6, 605, 'steglitz-zehlendorf', 'dahlem'),
  STRUCT(6, 606, 'steglitz-zehlendorf', 'nikolassee'),
  STRUCT(6, 607, 'steglitz-zehlendorf', 'wannsee'),

  -- 7) TEMPELHOF-SCHOENEBERG (07x)
  STRUCT(7, 701, 'tempelhof-schoeneberg', 'schoeneberg'),
  STRUCT(7, 702, 'tempelhof-schoeneberg', 'friedenau'),
  STRUCT(7, 703, 'tempelhof-schoeneberg', 'tempelhof'),
  STRUCT(7, 704, 'tempelhof-schoeneberg', 'mariendorf'),
  STRUCT(7, 705, 'tempelhof-schoeneberg', 'marienfelde'),
  STRUCT(7, 706, 'tempelhof-schoeneberg', 'lichtenrade'),

  -- 8) NEUKOELLN (08x)
  STRUCT(8, 801, 'neukoelln', 'neukoelln'),
  STRUCT(8, 802, 'neukoelln', 'britz'),
  STRUCT(8, 803, 'neukoelln', 'buckow'),
  STRUCT(8, 804, 'neukoelln', 'rudow'),
  STRUCT(8, 805, 'neukoelln', 'gropiusstadt'),

  -- 9) TREPTOW-KOEPENICK (09x)
  STRUCT(9, 901, 'treptow-koepenick', 'alt-treptow'),
  STRUCT(9, 902, 'treptow-koepenick', 'plaenterwald'),
  STRUCT(9, 903, 'treptow-koepenick', 'baumschulenweg'),
  STRUCT(9, 904, 'treptow-koepenick', 'johannisthal'),
  STRUCT(9, 905, 'treptow-koepenick', 'niederschoeneweide'),
  STRUCT(9, 906, 'treptow-koepenick', 'altglienicke'),
  STRUCT(9, 907, 'treptow-koepenick', 'adlershof'),
  STRUCT(9, 908, 'treptow-koepenick', 'bohnsdorf'),
  STRUCT(9, 909, 'treptow-koepenick', 'oberschoeneweide'),
  STRUCT(9, 910, 'treptow-koepenick', 'koepenick'),
  STRUCT(9, 911, 'treptow-koepenick', 'friedrichshagen'),
  STRUCT(9, 912, 'treptow-koepenick', 'rahnsdorf'),
  STRUCT(9, 913, 'treptow-koepenick', 'gruenau'),
  STRUCT(9, 914, 'treptow-koepenick', 'mueggelheim'),
  STRUCT(9, 915, 'treptow-koepenick', 'schmoeckwitz'),

  -- 10) MARZAHN-HELLERSDORF (10xx)
  STRUCT(10, 1001, 'marzahn-hellersdorf', 'marzahn'),
  STRUCT(10, 1002, 'marzahn-hellersdorf', 'biesdorf'),
  STRUCT(10, 1003, 'marzahn-hellersdorf', 'kaulsdorf'),
  STRUCT(10, 1004, 'marzahn-hellersdorf', 'mahlsdorf'),
  STRUCT(10, 1005, 'marzahn-hellersdorf', 'hellersdorf'),

  -- 11) LICHTENBERG (11xx)
  STRUCT(11, 1101, 'lichtenberg', 'friedrichsfelde'),
  STRUCT(11, 1102, 'lichtenberg', 'karlshorst'),
  STRUCT(11, 1103, 'lichtenberg', 'lichtenberg'),
  STRUCT(11, 1104, 'lichtenberg', 'falkenberg'),
  STRUCT(11, 1105, 'lichtenberg', 'wartenberg'),
  STRUCT(11, 1106, 'lichtenberg', 'malchow'),
  STRUCT(11, 1109, 'lichtenberg', 'neu-hohenschoenhausen'),
  STRUCT(11, 1110, 'lichtenberg', 'alt-hohenschoenhausen'),
  STRUCT(11, 1111, 'lichtenberg', 'fennpfuhl'),
  STRUCT(11, 1112, 'lichtenberg', 'rummelsburg'),

  -- 12) REINICKENDORF (12xx)
  STRUCT(12, 1201, 'reinickendorf', 'reinickendorf'),
  STRUCT(12, 1202, 'reinickendorf', 'tegel'),
  STRUCT(12, 1203, 'reinickendorf', 'konradshoehe'),
  STRUCT(12, 1204, 'reinickendorf', 'heiligensee'),
  STRUCT(12, 1205, 'reinickendorf', 'frohnau'),
  STRUCT(12, 1206, 'reinickendorf', 'hermsdorf'),
  STRUCT(12, 1207, 'reinickendorf', 'waidmannslust'),
  STRUCT(12, 1208, 'reinickendorf', 'luebars'),
  STRUCT(12, 1209, 'reinickendorf', 'wittenau'),
  STRUCT(12, 1210, 'reinickendorf', 'maerkisches viertel'),
  STRUCT(12, 1211, 'reinickendorf', 'borsigwalde')
]);