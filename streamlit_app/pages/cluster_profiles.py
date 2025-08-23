# --- ensure project root is importable ---
import os, sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import pydeck as pdk

# Core loaders
from berlin_housing.io import load_master
from services.geo import load_geojson, subset_by_names, norm

# --------------------------------------------------------------------------------------
# Cluster names & profile descriptions (short + long)
# --------------------------------------------------------------------------------------
CLUSTER_NAMES = {
    0: "Balanced",
    1: "Vibrant",
    2: "Affordable",
    3: "Prestige",
}

CLUSTER_NOTES = {
    0: (
        "Quiet residential areas with modest incomes, limited nightlife & amenities,"
        " relatively small populations and generally better affordability. Good for families"
        " or anyone prioritizing calm + price." 
    ),
    1: (
        "Big, vibrant subdistricts with lots of cafés/bars/restaurants, parks and schools."
        " Central feel and strong infrastructure; affordability depends on income and size."
    ),
    2: (
        "Mid-sized neighborhoods with the lowest average rents. Fewer amenities than hubs,"
        " but attractive for value-seeking renters." 
    ),
    3: (
        "Affluent, trendy areas with the highest amenity density (cafés, restaurants, nightlife)"
        " and higher rents." 
    ),
}

# Consistent cluster colors (used in map and legend)
CLUSTER_PALETTE = {
    0: [31, 119, 180],   # Balanced (blue)
    1: [255, 127, 14],   # Vibrant (orange)
    2: [44, 160, 44],    # Affordable (green)
    3: [214, 39, 40],    # Prestige (red)
}

# Label mapping for nicer UI
CLUSTER_LABELS = CLUSTER_NAMES  # alias for clarity
LABEL_TO_ID = {v: k for k, v in CLUSTER_LABELS.items()}

# Try to detect coordinate columns if they exist in your master table
POSSIBLE_LAT = ["lat", "latitude", "y", "Lat"]
POSSIBLE_LON = ["lon", "longitude", "x", "Lon", "lng", "Lng"]


def find_coords_columns(df: pd.DataFrame):
    lat_col, lon_col = None, None
    for c in POSSIBLE_LAT:
        if c in df.columns:
            lat_col = c
            break
    for c in POSSIBLE_LON:
        if c in df.columns:
            lon_col = c
            break
    return lat_col, lon_col


# --------------------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------------------
st.set_page_config(page_title="Cluster profiles", layout="wide")
st.title("Cluster profiles")
st.caption("Explore Berlin subdistricts by cluster. Filter, read a short profile, and (if coordinates are available) see them on a map.")

# Load data
@st.cache_data(show_spinner=False)
def _load():
    df = load_master()
    # Keep only columns we need for exploration
    base_cols = [c for c in [
        "bezirk", "ortsteil", "k4_cluster",
        "subdistrict_avg_median_income_eur",
        "subdistrict_avg_mietspiegel_classification",
        "cafes", "restaurants", "supermarket", "green_space", "schools",
    ] if c in df.columns]
    # include any coordinate columns if present
    lat_col, lon_col = find_coords_columns(df)
    coord_cols = [c for c in [lat_col, lon_col] if c]
    use_cols = list(dict.fromkeys(base_cols + coord_cols))
    # try a few plausible locations for the geojson relative to project root
    candidates = [
        os.path.join(PROJECT_ROOT, "data", "berlin_ortsteil_boundaries.geojson"),  # check here first
        os.path.join(PROJECT_ROOT, "data", "processed", "berlin_ortsteil_boundaries.geojson"),
        os.path.join(PROJECT_ROOT, "berlin_ortsteil_boundaries.geojson"),
    ]
    geo_path = next((p for p in candidates if os.path.isfile(p)), None)

    return df[use_cols].copy(), lat_col, lon_col, geo_path


df, LAT_COL, LON_COL, GEO_PATH = _load()

all_clusters = sorted(df["k4_cluster"].dropna().unique().tolist())
all_cluster_labels = [CLUSTER_LABELS.get(i, str(i)) for i in all_clusters]

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    clusters_labels = st.multiselect(
        "Select clusters",
        options=all_cluster_labels,
        default=all_cluster_labels,
        help="Choose one or more lifestyle clusters",
    )
    # Map labels back to numeric IDs for filtering
    clusters = [LABEL_TO_ID.get(lbl, lbl) for lbl in clusters_labels]
    search = st.text_input("Search subdistrict (Ortsteil)", value="")

# --- Legend (only when more than one cluster is selected)
    if len(clusters) > 1:
        st.markdown("**Cluster color key**")
        ids_for_legend = clusters if set(clusters) != set(all_clusters) else all_clusters
        legend_cols = st.columns(len(ids_for_legend))
        for i, cid in enumerate(ids_for_legend):
            rgb = CLUSTER_PALETTE.get(cid, [180, 180, 180])
            box = (
                f"<div style='width:18px;height:18px;border-radius:3px;"
                f"background-color: rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.85);"
                f"display:inline-block;margin-right:8px;border:1px solid rgba(0,0,0,0.25)'></div>"
            )
            st.markdown(box + f"{CLUSTER_LABELS.get(cid, str(cid))}", unsafe_allow_html=True)


# Filter the frame
mask = df["k4_cluster"].isin(clusters)
if search:
    mask &= df["ortsteil"].str.contains(search, case=False, na=False)

df_filt = df[mask].copy()

# --- Profile cards (always show)
labels_to_show = clusters_labels if set(clusters_labels) != set(all_cluster_labels) else all_cluster_labels
cols = st.columns(max(1, len(labels_to_show)))
for i, lbl in enumerate(labels_to_show):
    cid = LABEL_TO_ID.get(lbl)
    with cols[i % len(cols)]:
        st.subheader(f"{lbl}")
        st.write(CLUSTER_NOTES.get(cid, ""))


# --- Map
st.subheader("Map")

if LAT_COL and LON_COL:
    st.caption("Point map (lat/lon columns detected).")
    view_state = pdk.ViewState(
        latitude=float(df_filt[LAT_COL].mean()) if not df_filt.empty else 52.52,
        longitude=float(df_filt[LON_COL].mean()) if not df_filt.empty else 13.405,
        zoom=10,
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_filt,
        get_position=[LON_COL, LAT_COL],
        get_radius=120,
        pickable=True,
        auto_highlight=True,
    )
    tooltip = {"html": "<b>{OTEIL}</b><br/>Cluster: {k4_cluster}", "style": {"backgroundColor": "#262730", "color": "white"}}
    
    st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v10", initial_view_state=view_state, layers=[layer], tooltip=tooltip))
else:
    st.caption("Boundary map from GeoJSON (no lat/lon columns detected).")
    # Diagnostics: show where we're looking
    with st.expander("Debug: GeoJSON path check", expanded=False):
        st.write({
            "PROJECT_ROOT": PROJECT_ROOT,
            "auto_candidates": [
                os.path.join(PROJECT_ROOT, "data", "processed", "berlin_ortsteil_boundaries.geojson"),
                os.path.join(PROJECT_ROOT, "data", "berlin_ortsteil_boundaries.geojson"),
                os.path.join(PROJECT_ROOT, "berlin_ortsteil_boundaries.geojson"),
            ],
        })
        # List data/processed to confirm file presence
        data_proc = os.path.join(PROJECT_ROOT, "data", "processed")
        if os.path.isdir(data_proc):
            st.write("Contents of data/processed:")
            try:
                st.write(sorted(os.listdir(data_proc)))
            except Exception as _e:
                st.write(str(_e))
        else:
            st.write("data/processed does not exist at:", data_proc)
    # Allow manual selection if auto-detect failed
    if not GEO_PATH or not os.path.isfile(GEO_PATH):
        st.warning("GeoJSON not found at the usual locations.")
        default_guess = os.path.join(PROJECT_ROOT, "data", "processed", "berlin_ortsteil_boundaries.geojson")
        user_geo = st.text_input(
            "Path to GeoJSON (absolute or relative to project root):",
            value=default_guess,
        )
        if user_geo:
            guess = user_geo
            if not os.path.isabs(guess):
                guess = os.path.join(PROJECT_ROOT, guess)
            if os.path.isfile(guess):
                GEO_PATH = guess

    if not GEO_PATH or not os.path.isfile(GEO_PATH):
        st.stop()

    try:
        gj = load_geojson(GEO_PATH)
        # Filter geojson to the subset of displayed Ortsteile
        subset, matched = subset_by_names(gj, df_filt["ortsteil"].unique())

        # Base outline layer for the whole city (no fill)
        base_outline = pdk.Layer(
            "GeoJsonLayer",
            gj,
            pickable=False,
            stroked=True,
            filled=False,
            get_line_color=[150, 150, 150, 180],
            line_width_min_pixels=1,
        )

        # Map Ortsteil -> cluster (lowercased for matching)
        o2c = {
            norm(str(o)): int(c)
            for o, c in df[["ortsteil", "k4_cluster"]].dropna().values
        }

        # Helper to pick a name from properties (similar to services.geo)
        def _pick_name(props):
            for k in ("ortsteil", "OTEIL", "Ortsteil", "name", "spatial_alias", "bez_name"):
                if k in props and props[k]:
                    return str(props[k])
            return ""

        missing_names = []

        # Attach color per feature based on its cluster
        subset_colored = {"type": "FeatureCollection", "features": []}
        for ft in subset.get("features", []):
            props = ft.get("properties", {}) or {}
            name_key = norm(_pick_name(props))
            cl = o2c.get(name_key)
            if cl is None:
                missing_names.append(name_key)
            rgb = CLUSTER_PALETTE.get(cl, [180, 180, 180])
            color = rgb + [80]  # add alpha
            props = dict(props)
            props["fill_color"] = color
            props["k4_cluster"] = cl
            new_ft = dict(ft)
            new_ft["properties"] = props
            subset_colored["features"].append(new_ft)

        view_state = pdk.ViewState(latitude=52.52, longitude=13.405, zoom=9.2)

        geo_layer = pdk.Layer(
            "GeoJsonLayer",
            subset_colored,
            pickable=True,
            stroked=True,
            filled=True,
            extruded=False,
            get_fill_color="properties.fill_color",
            get_line_color=[200, 140, 0, 140],
            line_width_min_pixels=1,
        )
        tooltip = {"html": "<b>{OTEIL}</b><br/>Cluster: {k4_cluster}", "style": {"backgroundColor": "#262730", "color": "white"}}
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v10",
            initial_view_state=view_state,
            layers=[base_outline, geo_layer],
            tooltip=tooltip
        ))

        if missing_names:
            st.caption(
                ":information_source: Some features couldn't be matched to a cluster (showing grey). "
                f"Count: {len(set(missing_names))}."
            )

        missing = set(df_filt["ortsteil"].str.lower()) - matched
        if missing:
            st.caption(":warning: Some Ortsteile not in GeoJSON: " + ", ".join(sorted(missing)))
    except Exception as e:
        st.info("Couldn't render GeoJSON map. " + str(e))

# --- Summary + table
st.subheader("Summary")
left, right = st.columns([1, 2])
with left:
    st.metric("Subdistricts shown", len(df_filt))
    st.metric("Clusters selected", len(clusters))

with right:
    if not df_filt.empty:
        show_cols = [c for c in [
            "bezirk", "ortsteil", "k4_cluster",
            "subdistrict_avg_median_income_eur",
            "subdistrict_avg_mietspiegel_classification",
            "cafes", "restaurants", "supermarket", "green_space", "schools",
            LAT_COL, LON_COL,
        ] if c in df_filt.columns]
        st.dataframe(df_filt[show_cols].sort_values(["k4_cluster", "bezirk", "ortsteil"]).reset_index(drop=True), use_container_width=True)
    else:
        st.warning("No rows match the current filters.")