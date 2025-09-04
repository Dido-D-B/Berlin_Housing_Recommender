CREATE OR REPLACE TABLE `berlin-housing-468808.gold.dim_poi_group` (
  poi_group_id INT64,
  poi_group_name STRING
);
INSERT INTO `berlin-housing-468808.gold.dim_poi_group` VALUES
(1,'amenities'),(2,'food_drink'),(3,'entertainment'),(4,'green'),(5,'children');

CREATE OR REPLACE TABLE `berlin-housing-468808.gold.dim_poi_type` (
  poi_type_id INT64,
  poi_group_id INT64,
  poi_name STRING
);
INSERT INTO `berlin-housing-468808.gold.dim_poi_type` VALUES
-- amenities
(101,1,'clothes'),(102,1,'second_hand'),(103,1,'hairdresser'),(104,1,'fitness_station'),
(105,1,'community_centre'),(106,1,'electronics'),(107,1,'stationery'),(108,1,'medical'),
(109,1,'books'),(110,1,'travel_agency'),(111,1,'vacant'),(112,1,'yes'),
-- food & drink
(201,2,'bar'),(202,2,'alcohol'),(203,2,'kiosk'),(204,2,'nightclub'),(205,2,'restaurant'),
(206,2,'wine'),(207,2,'cafes'),(208,2,'bakeries'),(209,2,'confectionery'),(210,2,'convenience'),
(211,2,'deli'),(212,2,'supermarket'),(213,2,'ice_cream'),(214,2,'tea'),(215,2,'greengrocer'),
-- entertainment / culture
(301,3,'antiques'),(302,3,'art'),(303,3,'art_2'),(304,3,'theatre'),(305,3,'bathing_place'),
-- green / outdoor
(401,4,'dog_park'),(402,4,'florist'),(403,4,'garden'),(404,4,'fountain'),(405,4,'greenfield'),
(406,4,'marina'),(407,4,'nature_reserve'),(408,4,'green_space'),(409,4,'pitch'),(410,4,'parking'),
-- children / education
(501,5,'childcare'),(502,5,'playground'),(503,5,'schools');