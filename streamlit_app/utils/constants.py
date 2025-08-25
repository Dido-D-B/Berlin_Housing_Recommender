# Constants defining cluster names, descriptions, colors, and mappings for use across the app.

# Human-readable names for each cluster ID.
CLUSTER_NAMES = {0: "Balanced", 1: "Vibrant", 2: "Affordable", 3: "Prestige"}

# Initial short notes for each cluster ID (unused if overridden below).
CLUSTER_NOTES = {
    0: "Quiet residential areas ...",
    1: "Big, vibrant subdistricts ...",
    2: "Mid-sized neighborhoods ...",
    3: "Affluent, trendy areas ...",
}

# RGB color palette for clusters (used in maps and charts).
CLUSTER_PALETTE = {
    0: [31, 119, 180],   # Balanced (blue)
    1: [255, 127, 14],   # Vibrant (orange)
    2: [44, 160, 44],    # Affordable (green)
    3: [214, 39, 40],    # Prestige (red)
}

# Reverse mapping from cluster label string → cluster ID.
LABEL_TO_ID = {v: k for k, v in CLUSTER_NAMES.items()}

# Cluster labels repeated for inline profile display.
CLUSTER_LABELS = {0: "Balanced", 1: "Vibrant", 2: "Affordable", 3: "Prestige"}

# Detailed descriptive notes for each cluster, used in subdistrict profiles and recommender outputs.
CLUSTER_NOTES = {
    0: "Small, quiet, affordable neighborhoods with balanced age mix and modest amenities — good for families prioritizing calm and price.",
    1: "Large, amenity‑rich urban hubs with lots of cafés, restaurants and nightlife — lively, central, and convenient.",
    2: "Mid‑sized, value‑focused areas with the lowest average rents and fewer amenities — attractive for budget‑minded renters.",
    3: "Wealthy, high‑amenity hotspots with top scores for food, cafés and green space — trendy but pricier.",
}