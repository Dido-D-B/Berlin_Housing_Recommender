# Imports
import os, sys
import streamlit as st
import pandas as pd
import pydeck as pdk

# Core loaders
from berlin_housing.io import load_master
from services.geo import load_geojson, subset_by_names, norm
from utils.constants import CLUSTER_NAMES as CLUSTER_LABELS, CLUSTER_NOTES, CLUSTER_PALETTE, LABEL_TO_ID
from utils.geo import find_coords_columns, resolve_ortsteil_geojson, pick_feature_name, colorize_geojson_by_cluster 
from utils.ui import build_profiles_table, render_footer, inject_responsive_css

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Page Configurations
icon_path = os.path.join(PROJECT_ROOT, "streamlit_app", "images", "icon.png")
st.set_page_config(
    page_title="Berlin Housing - Profiles",
    page_icon=icon_path,
    layout="wide",
)

# CSS
inject_responsive_css()

# UI
st.markdown(
    """
    <div style='border: 3px solid #A50034; background-color: #A50034; padding: 15px; text-align: center; border-radius: 6px;'>
        <h1 style='color: white; margin: 0;'>Subdistrict Profiles</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='color: #A50034;'>Filter for subdstrict profile(s)</h3>",
    unsafe_allow_html=True,
)
st.write("See the subdistricts on a map colored by their profile and explore their features in a summary table!")
st.caption("These profiles are based on clustering Berlin’s 96 subdistricts (Ortsteile) using demographic, housing, and amenity data. Each cluster groups areas with similar rent levels, income patterns, and local amenities into lifestyle categories.")

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
    # resolve geojson path via helper
    geo_path = resolve_ortsteil_geojson(PROJECT_ROOT)

    return df[use_cols].copy(), lat_col, lon_col, geo_path

df, LAT_COL, LON_COL, GEO_PATH = _load()

all_clusters = sorted(df["k4_cluster"].dropna().unique().tolist())
all_cluster_labels = [CLUSTER_LABELS.get(i, str(i)) for i in all_clusters]

# Sidebar filters
with st.sidebar:
    st.header("⚙️ Filter")
    clusters_labels = st.multiselect(
        "Select clusters",
        options=all_cluster_labels,
        default=all_cluster_labels,
        help="Choose one or more lifestyle clusters",
    )
    # Map labels back to numeric IDs for filtering
    clusters = [LABEL_TO_ID.get(lbl, lbl) for lbl in clusters_labels]
    search = st.text_input("Search subdistrict (Ortsteil)", value="")

# Filter the frame
mask = df["k4_cluster"].isin(clusters)
if search:
    norm_search = norm(search)
    mask &= df["ortsteil"].apply(lambda x: norm(str(x))).str.contains(norm_search, case=False, na=False)

df_filt = df[mask].copy()

# Profile cards
labels_to_show = clusters_labels if set(clusters_labels) != set(all_cluster_labels) else all_cluster_labels
cols = st.columns(max(1, len(labels_to_show)))
for i, lbl in enumerate(labels_to_show):
    cid = LABEL_TO_ID.get(lbl)
    with cols[i % len(cols)]:
        rgb = CLUSTER_PALETTE.get(cid, [165, 0, 52])
        hex_color = '#%02x%02x%02x' % tuple(rgb)
        st.markdown(
            f"<h3 style='color: {hex_color};'>{lbl}</h3>",
            unsafe_allow_html=True,
        )
        st.write(CLUSTER_NOTES.get(cid, ""))


# Map (allow manual selection if auto-detect failed)
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

    missing_names = []

    # Attach color per feature based on its cluster
    subset_colored = {"type": "FeatureCollection", "features": []}
    for ft in subset.get("features", []):
        props = ft.get("properties", {}) or {}
        name_key = norm(pick_feature_name(props))
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

    view_state = pdk.ViewState(
        latitude=52.52,
        longitude=13.405,
        zoom=9.2,
        min_zoom=9.2,
        max_zoom=9.2,
        interactive=False,
    )

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
    tooltip = {"html": "<b>{OTEIL}</b>", "style": {"backgroundColor": "#262730", "color": "white"}}

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",
        initial_view_state=view_state,
        layers=[base_outline, geo_layer],
        views=[pdk.View("MapView")],
        tooltip=tooltip,
        map_provider="mapbox",
    ))
    st.caption(f"Boundary map from GeoJSON file (Berlin Open Data)")

    if missing_names:
        with st.expander("Unmatched features", expanded=False):
            st.write("Couldn't color these names (no cluster mapping):", sorted(set(missing_names)))

except Exception as e:
    st.info("Couldn't render GeoJSON map. " + str(e))

# Summary + table
st.markdown(
    """
    <div style='border: 2px solid #A50034; background-color: #A50034; padding: 8px; text-align: center; border-radius: 4px; margin-top: 15px; margin-bottom: 10px;'>
        <h3 style='color: white; margin: 0; font-size: 18px;'>Summary</h3>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("Subdistricts shown: ", len(df_filt))
st.write("Clusters selected: ", len(clusters))

if not df_filt.empty:
    display_df = build_profiles_table(df_filt, CLUSTER_LABELS)
    st.caption("The ‘Avg. Mietspiegel class’ shows the average residential location category (Wohnlage) of all streets in a subdistrict, from 1 (simple) to 4 (very good). Higher values indicate more desirable locations with higher rents.")
    with st.expander("What is the Mietspiegel classification?"):
        st.markdown(
            """
               The Berliner Mietspiegel is the official rent index published by the city of Berlin. Every street (and even house number ranges) is assigned a Wohnlage (residential location) class that reflects how desirable and expensive the location is considered.
            """)
        st.markdown(
            """
               **The classes are**:
               * 1 = einfache Wohnlage (simple location): lower demand, fewer amenities, lower rents.
               * 2 = mittlere Wohnlage (average location): typical Berlin residential areas.
               * 3 = gute Wohnlage (good location): higher demand, better infrastructure and amenities, higher rents.
               * 4 = sehr gute Wohnlage (very good location): top addresses, prestigious neighborhoods, highest rents.
            """
        )
    st.dataframe(display_df, hide_index=True, use_container_width=True)
else:
    st.warning("No rows match the current filters.")

render_footer()