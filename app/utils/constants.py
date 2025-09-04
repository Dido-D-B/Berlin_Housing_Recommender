"""
constants.py

Central definitions of cluster names, labels, notes, and colors
for use across the Berlin Housing Affordability app.

These constants ensure consistent naming, labeling, and visualization
of subdistrict cluster profiles across pages, maps, charts, and tables.
"""

# Mapping from cluster ID → human-readable name
CLUSTER_NAMES = {0: "Balanced", 1: "Vibrant", 2: "Affordable", 3: "Prestige"}

# Initial short notes per cluster (placeholder, overridden below)
CLUSTER_NOTES = {
    0: "Quiet residential areas ...",
    1: "Big, vibrant subdistricts ...",
    2: "Mid-sized neighborhoods ...",
    3: "Affluent, trendy areas ...",
}

# RGB color palette for clusters (used for map layers and charts)
CLUSTER_PALETTE = {
    0: [31, 119, 180],   # Balanced (blue)
    1: [255, 127, 14],   # Vibrant (orange)
    2: [44, 160, 44],    # Affordable (green)
    3: [214, 39, 40],    # Prestige (red)
}

# Reverse lookup: cluster label string → cluster ID
LABEL_TO_ID = {v: k for k, v in CLUSTER_NAMES.items()}

# Duplicate of CLUSTER_NAMES for inline display in profiles/recommender
CLUSTER_LABELS = {0: "Balanced", 1: "Vibrant", 2: "Affordable", 3: "Prestige"}

# Detailed descriptive notes per cluster (used in profiles and recommendations)
CLUSTER_NOTES = {
    0: "Small, quiet, affordable neighborhoods with balanced age mix and modest amenities — good for families prioritizing calm and price.",
    1: "Large, amenity‑rich urban hubs with lots of cafés, restaurants and nightlife — lively, central, and convenient.",
    2: "Mid‑sized, value‑focused areas with the lowest average rents and fewer amenities — attractive for budget‑minded renters.",
    3: "Wealthy, high‑amenity hotspots with top scores for food, cafés and green space — trendy but pricier.",
}

# Household size assumptions (for quick affordability by household type) 
HOUSEHOLD_M2 = {
    "Single": 35,
    "Couple": 55,
    "Family": {"base": 55, "per_child": 15},   # 55 + 15 per child
    "WG": {"per_person": 18},                  # per person (private room + shared areas)
    "Senior": 40,
}

# Household-type POI weighting for ranking (applied if columns exist in results)
HH_WEIGHTS = {
    "Family": {"green_spaces": 1.0, "playgrounds": 1.0, "schools": 0.8, "nightclub": -0.5},
    "WG": {"cafes": 0.7, "bar": 0.7, "restaurant": 0.4, "transit_stops": 0.8},
    "Senior": {"green_spaces": 0.8, "pharmacies": 0.8, "clinics": 0.6, "nightclub": -0.4},
}

# Amenity columns mapping (UI label -> dataframe column). Only applied if the column exists in results.
AMENITY_COLUMNS = {
    "Cafes": "cafes",
    "Restaurants": "restaurant",
    "Bars": "bar",
    "Nightclubs": "nightclub",
    "Green spaces": "green_spaces",
    "Playgrounds": "playgrounds",
    "Schools": "schools",
    "Libraries": "libraries",
    "Transit access": "transit_stops",
    "Pharmacies": "pharmacies",
    "Clinics": "clinics",
}