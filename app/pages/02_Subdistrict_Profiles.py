"""
02_Subdistrict_Profiles.py

Streamlit page to explore Berlin subdistrict (Ortsteil) profiles on an interactive map
and summary table. Users can filter by lifestyle clusters and drill into cultural facts.

The page:
- Loads the master dataset and GeoJSON boundaries
- Filters data by selected clusters and (optionally) a chosen Ortsteil
- Colors subdistrict polygons by cluster and renders a deck.gl map
- Shows a tidy table with POIs and optional sorting presets
"""

# Ensure project root is importable
import os, sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Imports    
import streamlit as st
import pandas as pd
import pydeck as pdk
from utils.constants import CLUSTER_NAMES as CLUSTER_LABELS, CLUSTER_NOTES, CLUSTER_PALETTE, LABEL_TO_ID
from utils.geo import load_geojson, norm, pick_feature_name, feature_name
from utils.ui import build_profiles_table, render_footer, inject_responsive_css
from utils.content import get_district_blurb, get_subdistrict_blurb
from utils.data import _load
from utils.text import format_german_title

# Page Configuration
icon_path = os.path.join(PROJECT_ROOT, "app", "images", "icon.png")
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
        <h1 style='color: white; margin: 0;'>Berlin Subdistrict Profiles</h1>
        <p style='color: white; margin: 5px 0 0; font-size: 14px;'>
            Project by <a href="https://www.linkedin.com/in/dido-de-boodt/" target="_blank" style="color: white; text-decoration: underline;">Dido De Boodt</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True)

st.divider()
st.markdown("""**Explore the subdstricts and their profiles** - The map shows Berlin’s subdistricts colored by their profiles. Use the settings in the sidebar to filter the map and summary table by subdistrict profile(s), or pick a subdistrict from the drop-down menu to explore it in detail.""")
st.divider()

st.caption("These profiles are based on clustering Berlin’s 96 subdistricts (Ortsteile) using demographic, housing, and amenity data. Each cluster groups areas with similar rent levels, income patterns, and local amenities into lifestyle categories.")

if st.button("💡 Learn how the cluster profiles were created", key="to_behind_data"):
    st.switch_page("../app/pages/04_Behind_the_data.py")

# Load data
df, LAT_COL, LON_COL, GEO_PATH = _load()

all_clusters = sorted(df["k4_cluster"].dropna().unique().tolist())
all_cluster_labels = [CLUSTER_LABELS.get(i, str(i)) for i in all_clusters]

# Sidebar filters
with st.sidebar:
    st.header("⚙️ Settings")
    clusters_labels = st.multiselect(
        "Select Subdistrict Profile(s)",
        options=all_cluster_labels,
        default=all_cluster_labels,
        help="Choose one or more lifestyle clusters",
    )
    # Map labels back to numeric IDs for filtering
    clusters = [LABEL_TO_ID.get(lbl, lbl) for lbl in clusters_labels]
    # Only offer Ortsteile that belong to the selected clusters
    df_cluster_scope = df[df["k4_cluster"].isin(clusters)]
    raw_orts = sorted(df_cluster_scope["ortsteil"].dropna().astype(str).unique().tolist())
    display_orts = [format_german_title(o) for o in raw_orts]
    DISP2RAW = dict(zip(display_orts, raw_orts))

    # Subdistrict drop-down (shows pretty names but we retain mapping to raw values)
    selected_ort_disp = st.selectbox(
        "Subdistrict (Ortsteil)",
        options=["All subdistricts"] + display_orts,
        index=0,
        help="Start typing to quickly find an Ortsteil. List reflects the selected clusters.",
        key="ort_select",
    )

    # Resolve the selected display label back to the raw ortsteil value
    sel_raw = None
    if selected_ort_disp and selected_ort_disp != "All subdistricts":
        sel_raw = DISP2RAW.get(selected_ort_disp, selected_ort_disp)


# Filter the frame
mask = df["k4_cluster"].isin(clusters)
if sel_raw:
    mask &= df["ortsteil"].astype(str) == sel_raw
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

# Map
MAP_HEIGHT = 650  # Height for the map canvas
GEO_PATH = os.path.join(PROJECT_ROOT, "data", "static", "berlin_ortsteil_boundaries.parquet")
# Fixed opacity for subdistrict profile fill colors (RGBA alpha)
MAP_OPACITY = 110

try:
    gj = load_geojson(GEO_PATH)
    # --- DEBUG: show how names compare between boundaries and dataframe ---
    try:
        # Collect a sample of names from the boundary file
        boundary_names = []
        for ft in gj.get("features", [])[:120]:
            props = ft.get("properties", {}) or {}
            nm = feature_name(props) or pick_feature_name(props)
            if nm:
                boundary_names.append(str(nm))
        # Collect names from the dataframe
        df_names = df["ortsteil"].dropna().astype(str).tolist()
        # Normalize for comparison
        boundary_keys = {norm(x) for x in boundary_names}
        df_keys = {norm(x) for x in df_names}
        only_in_boundary = sorted(list(boundary_keys - df_keys))[:20]
        only_in_df = sorted(list(df_keys - boundary_keys))[:20]
    except Exception as _dbg_e:
        st.caption(f"Debug name check failed: {_dbg_e}")
    # Decide which features to include based on current filter
    allowed = set(df_filt["ortsteil"].astype(str).apply(lambda x: norm(x)).unique().tolist())
    include_all = (len(allowed) == 0) or (len(allowed) == len(df["ortsteil"].astype(str).unique()))

    # Prepare lookups for tooltip enrichment
    pop_col = "total_population" if "total_population" in df.columns else None
    tooltip_cols = ["bezirk"]
    if pop_col:
        tooltip_cols.append(pop_col)
    lut_df = df[["ortsteil"] + tooltip_cols].dropna(subset=["ortsteil"]).copy()
    lut_df["__key"] = lut_df["ortsteil"].astype(str).apply(lambda x: norm(x))
    LUT = lut_df.set_index("__key").to_dict(orient="index")

    # Base outline layer for the whole city (no fill)
    base_outline = pdk.Layer(
        "GeoJsonLayer",
        gj,
        pickable=False,
        stroked=True,
        filled=False,
        get_line_color=[150, 150, 150, MAP_OPACITY],
        line_width_min_pixels=1,
    )

    # Map Ortsteil -> cluster (lowercased for matching)
    o2c = {
        norm(str(o)): int(c)
        for o, c in df[["ortsteil", "k4_cluster"]].dropna().values
    }

    missing_names = []

    # Attach color per feature based on its cluster, filtering using allowed set
    subset_colored = {"type": "FeatureCollection", "features": []}
    for ft in gj.get("features", []):
        # Skip features not in the current allowed set (unless showing all)
        props = ft.get("properties", {}) or {}
        orig_name = feature_name(props) or pick_feature_name(props)
        name_key = norm(str(orig_name))
        if not include_all and name_key not in allowed:
            continue
        cl = o2c.get(name_key)
        rec = LUT.get(name_key, {})

        rgb = CLUSTER_PALETTE.get(cl, [180, 180, 180])
        color = rgb + [int(MAP_OPACITY)]
        props = dict(props)
        # Enrich properties for tooltip
        props["fill_color"] = color
        props["k4_cluster"] = cl
        props["ortsteil_display"] = orig_name
        if rec:
            if "bezirk" in rec:
                props["bezirk"] = rec.get("bezirk")
            if pop_col and pop_col in rec and rec.get(pop_col) is not None:
                try:
                    pop_val = int(float(rec.get(pop_col)))
                    props["population"] = pop_val
                    props["population_fmt"] = f"{pop_val:,}".replace(",", ".")  # 1.234.567 style
                except Exception:
                    props["population"] = rec.get(pop_col)
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
        get_line_color=[200, 140, 0, MAP_OPACITY],
        line_width_min_pixels=1,
    )
    tooltip = {
        "html": "<b>{ortsteil_display}</b><br/>Bezirk: {bezirk}<br/>Population: {population_fmt}",
        "style": {"backgroundColor": "#262730", "color": "white"}
    }

    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v10",
            initial_view_state=view_state,
            layers=[base_outline, geo_layer],
            views=[pdk.View("MapView")],
            tooltip=tooltip,
            map_provider="mapbox",
        ),
        height=MAP_HEIGHT,
        use_container_width=True,
    )
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
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
with st.expander("💡 What is the Mietspiegel classification?"):
    st.markdown(
            """
               The *Berliner Mietspiegel* is the official rent index published by the city of Berlin. Every street (and even house number ranges) is assigned a Wohnlage (residential location) class that reflects how desirable and expensive the location is considered.
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

# Sort Table Summary
st.markdown(
    "<div style='margin-top:8px;'><b>Sort by</b></div>",
    unsafe_allow_html=True,
)
sort_choice = st.radio(
    "Sort presets",
    options=["District", "Most Green", "Most Schools", "Most Night Life", "Most Affordable"],
    index=0,
    horizontal=True,
    label_visibility="collapsed",
)

# Table
if not df_filt.empty:
    # If a single subdistrict is selected, show its cultural summary and KPI compare
    if 'selected_ort_disp' in locals() and selected_ort_disp and selected_ort_disp != "All subdistricts":
        with st.expander("Cultural facts & context", expanded=True):
            # locate the selected row safely using the raw ortsteil value
            try:
                _row = df.loc[df["ortsteil"].astype(str) == sel_raw].iloc[0]
            except Exception:
                _row = {}
            bezirk_raw = str(_row.get("bezirk", "")).strip() if isinstance(_row, pd.Series) else ""
            bezirk_disp = format_german_title(bezirk_raw) if bezirk_raw else ""
            ortsteil_disp = selected_ort_disp

            # District facts
            d_info = get_district_blurb(bezirk_disp) if bezirk_disp else {}
            if d_info.get("blurb"):
                st.markdown("#### District: " + bezirk_disp)
                st.write(d_info.get("blurb"))

            # Subdistrict facts
            sd_info = get_subdistrict_blurb(bezirk_disp, ortsteil_disp)
            if sd_info.get("blurb"):
                st.markdown("#### Subdistrict: " + ortsteil_disp)
                st.write(sd_info.get("blurb"))

    display_df = build_profiles_table(df_filt, CLUSTER_LABELS)

    try:
        needed = [c for c in ["bar", "nightclub"] if c in df_filt.columns]
        if needed and "Subdistrict" in display_df.columns and "ortsteil" in df_filt.columns:
            left = display_df.copy()
            left["__key"] = left["Subdistrict"].astype(str).apply(lambda x: norm(x))

            right = df_filt[["ortsteil"] + needed].copy()
            right["__key"] = right["ortsteil"].astype(str).apply(lambda x: norm(x))

            display_df = (
                left.merge(right[["__key"] + needed], on="__key", how="left")
                    .drop(columns=["__key"], errors="ignore")
            )
    except Exception:
        pass

    # Clean up headers for presentation
    rename_map = {}
    if "bar" in display_df.columns:
        rename_map["bar"] = "Bars"
    if "nightclub" in display_df.columns:
        rename_map["nightclub"] = "Nightclubs"
    if rename_map:
        display_df = display_df.rename(columns=rename_map)

    # Apply sort to the DISPLAY table (not the raw df)
    if sort_choice and sort_choice != "District":
        import unicodedata
        # Map preset to likely display column names via keyword matching
        keyword_map = {
            "Most Green": ["green", "🌳"],
            "Most Schools": ["school"],
            # Prefer Bars, then Cafés for Night Life
            "Most Night Life": ["bars", "bar", "cafes", "cafés", "café", "night", "club", "pub", "nightclub", "nightclubs"],
            # Only Mietspiegel/Wohnlage, not generic terms that collide with income
            "Most Affordable": ["mietspiegel", "wohnlage"],
        }
        def _ascii_lower(s: str) -> str:
            try:
                return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
            except Exception:
                return str(s).lower()
        def pick_display_col(df_cols, keywords):
            cols_norm = [(c, _ascii_lower(c)) for c in df_cols]
            # 1) Exact keyword match first
            for kw in keywords:
                for c_orig, c_norm in cols_norm:
                    if c_norm == kw:
                        return c_orig
            # 2) Prefer startswith matches
            for kw in keywords:
                for c_orig, c_norm in cols_norm:
                    if c_norm.startswith(kw):
                        return c_orig
            # 3) Then contains matches
            for kw in keywords:
                for c_orig, c_norm in cols_norm:
                    if kw in c_norm:
                        return c_orig
            return None

        # Special handling: if Most Affordable, explicitly prefer the Mietspiegel/Wohnlage column
        if sort_choice == "Most Affordable":
            # Exact header first
            if "Avg. Mietspiegel class" in display_df.columns:
                target_col = "Avg. Mietspiegel class"
            else:
                # any column that clearly refers to Mietspiegel/Wohnlage
                pref = [c for c in display_df.columns if _ascii_lower(c).find("mietspiegel") >= 0 or _ascii_lower(c).find("wohnlage") >= 0]
                target_col = pref[0] if pref else None
        elif sort_choice == "Most Night Life":
            if "Nightclubs" in display_df.columns:
                target_col = "Nightclubs"
            elif "Bars" in display_df.columns:
                target_col = "Bars"
            elif "nightclub" in display_df.columns:
                target_col = "nightclub"
            elif "bar" in display_df.columns:
                target_col = "bar"
            elif "bars" in display_df.columns:
                target_col = "bars"
            else:
                target_col = None
        else:
            target_col = None
        if target_col is None:
            target_col = pick_display_col(display_df.columns, keyword_map.get(sort_choice, []))

        if target_col:
            # Replaced block for robust numeric cleaning
            ser = display_df[target_col]
            # Robust numeric coercion: collapse thin/regular spaces and strip non-digits (keeps minus)
            cleaned = (
                ser.astype(str)
                   .str.replace("\u00A0", " ")             # NBSP -> space
                   .str.replace(r"\s+", "", regex=True)     # remove any spaces (e.g., "1 383" -> "1383")
                   .str.replace(r"[^\d\-\.]", "", regex=True)  # drop currency and other symbols
            )
            # If both ',' and '.' are possible in source, at this stage only '.' may remain; treat as decimal if present
            num = pd.to_numeric(cleaned, errors="coerce")
            if num.notna().mean() >= 0.5:
                display_df["__sortkey__"] = num
                asc = True if sort_choice == "Most Affordable" else False
                display_df = display_df.sort_values("__sortkey__", ascending=asc, na_position="last").drop(columns="__sortkey__")
            else:
                asc = True if sort_choice == "Most Affordable" else False
                display_df = display_df.sort_values(target_col, ascending=asc, key=lambda s: s.astype(str).str.lower())
    elif sort_choice == "District":
        # Try to sort by the first column (usually the Ortsteil name) if present
        first_col = display_df.columns[0] if len(display_df.columns) > 0 else None
        if first_col:
            display_df = display_df.sort_values(first_col, ascending=True, key=lambda s: s.astype(str).str.lower())

    st.dataframe(display_df, hide_index=True, use_container_width=True)
else:
    st.warning("No rows match the current filters.")

render_footer()