# Data Dictionary for berlin_final_master_table.csv

| **Column Name**           | **Description**                                                     |
|---------------------------|-------------------------------------------------------------------|
| **id**                    | Unique identifier for each record.                                |
| **neighborhood**          | Name of the neighborhood or district within Berlin.              |

### Demographics
| **Column Name**           | **Description**                                                     |
|---------------------------|-------------------------------------------------------------------|
| **total_population**      | Total number of residents in the neighborhood.                    |
| **age_0_17**              | Number of residents aged 0 to 17 years.                           |
| **age_18_64**             | Number of residents aged 18 to 64 years.                          |
| **age_65_plus**           | Number of residents aged 65 years and older.                      |
| **share_female**          | Proportion of female residents in the neighborhood (0-1 scale).  |

### Income and Rent
| **Column Name**           | **Description**                                                     |
|---------------------------|-------------------------------------------------------------------|
| **median_income**         | Median household income in the neighborhood (in Euros).          |
| **average_rent**          | Average monthly rent price per square meter in the neighborhood.  |

### Employment
| **Column Name**           | **Description**                                                     |
|---------------------------|-------------------------------------------------------------------|
| **unemployment_rate**     | Percentage of unemployed residents in the neighborhood.           |

### Housing and Classification
| **Column Name**           | **Description**                                                     |
|---------------------------|-------------------------------------------------------------------|
| **housing_units**         | Total number of housing units available in the neighborhood.      |
| **year_built**            | Median year of construction for housing units in the area.        |
| **property_type**         | Dominant type of property (e.g., apartment, house).               |
| **rooms**                 | Average number of rooms per housing unit.                         |
| **square_meters**         | Average size of housing units in square meters.                   |
| **affordability_index**   | Composite index indicating housing affordability (higher = more affordable). |

### Public Transport and Amenities
| **Column Name**           | **Description**                                                     |
|---------------------------|-------------------------------------------------------------------|
| **public_transport_access** | Availability and accessibility of public transport options.     |
| **poi_schools**           | Number of schools in the neighborhood.                            |
| **poi_parks**             | Number of parks and green spaces in the neighborhood.            |
| **poi_shopping**          | Number of shopping facilities and commercial areas.              |

### Clusters
| **Column Name**           | **Description**                                                     |
|---------------------------|-------------------------------------------------------------------|
| **k4_cluster**            | Cluster assignment based on k-means clustering with 4 clusters, representing neighborhood typologies. |

*This data dictionary reflects the columns available in `berlin_final_master_table.csv` as derived from the processed dataset.*
