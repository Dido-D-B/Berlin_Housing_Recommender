# Imports
import os, sys
import streamlit as st
from services.recommender import get_top_k
from berlin_housing.config import DEFAULT_CLUSTER_COL
from utils.bookmarks import add_bookmark, remove_bookmark, is_bookmarked
from utils.text import _DASHES, norm, normalize_filename_base, district_slug, de_pretty
from utils.data import load_json
from utils.content import get_district_blurb, get_subdistrict_blurb, get_image_credit
from utils.geo import find_district_images
from utils.geo import IMAGES_DIR
from utils.constants import CLUSTER_LABELS, CLUSTER_NOTES
from utils.ui import render_footer, render_subdistrict_reco_table, inject_responsive_css
from PIL import Image, ImageOps

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Page Configurations
icon_path = os.path.join(PROJECT_ROOT, "streamlit_app", "images", "icon.png")
st.set_page_config(
    page_title="Berlin Housing - Recommender",
    page_icon=icon_path,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS
inject_responsive_css()

# Household size assumptions (for quick affordability by household type) 
HOUSEHOLD_M2 = {
    "Single": 35,
    "Couple": 55,
    "Family": {"base": 55, "per_child": 15},   # 55 + 15 per child
    "WG": {"per_person": 18},                  # per person (private room + shared areas)
    "Senior": 40,
}

# Estimate required apartment size
def estimate_required_sqm(hh_type: str, *, children: int = 0, wg_people: int = 3) -> int:
    if hh_type == "Single":
        return HOUSEHOLD_M2["Single"]
    if hh_type == "Couple":
        return HOUSEHOLD_M2["Couple"]
    if hh_type == "Family":
        return HOUSEHOLD_M2["Family"]["base"] + children * HOUSEHOLD_M2["Family"]["per_child"]
    if hh_type == "WG":
        return wg_people * HOUSEHOLD_M2["WG"]["per_person"]
    if hh_type == "Senior":
        return HOUSEHOLD_M2["Senior"]
    return HOUSEHOLD_M2["Single"]

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

# Helper: center-crop & resize images to a fixed card size (pixel-perfect alignment)
@st.cache_data(show_spinner=False)
def _fit_image_for_card(path: str, size=(1200, 700)):
    """Return a PIL image center-cropped to the given size.
    We cache by (path, mtime, size) so edits invalidate automatically."""
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        mtime = 0
    # Key includes size so different pages/sizes can coexist
    key = (path, mtime, size)
    # Use an inner cache dict tied to the outer cache
    if not hasattr(_fit_image_for_card, "_cache"):
        _fit_image_for_card._cache = {}
    if key in _fit_image_for_card._cache:
        return _fit_image_for_card._cache[key]
    img = Image.open(path).convert("RGB")
    fitted = ImageOps.fit(img, size, Image.LANCZOS, centering=(0.5, 0.5))
    _fit_image_for_card._cache[key] = fitted
    return fitted

# Uniform image presentation: same height + neat cropping
st.markdown(
    """
     <style>
     /* Subtle card style and rounded corners */
     .stImage img,
     .stImage > img,
     figure img { 
         border-radius: 6px; 
         display: block; 
     }
     /* Fix uneven layout caused by different credit-line lengths */
     .credit-fixed {
         height: 24px;                 /* reserve one line of space */
         overflow: hidden;
         white-space: nowrap;
         text-overflow: ellipsis;
         margin-top: 6px;
     }
     </style>
  """,
    unsafe_allow_html=True,
)

# Persist results across reruns so selections in the table don't clear it
if "results" not in st.session_state:
    st.session_state["results"] = None

st.markdown(
    """
    <div style='border: 3px solid #A50034; background-color: #A50034; padding: 15px; text-align: center; border-radius: 6px;'>
        <h1 style='color: white; margin: 0;'>Subdistrict Recommender</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='color:#A50034;'>Get top 5 recommended subdistricts</h3>",
    unsafe_allow_html=True,
)
st.write("Use the filters under **Your Preferences** in the sidebar to input income, **household type**, and preferred subdistrict profile. Use **Advanced Settings** to adjust affordability and (optionally) apartment size.")
st.caption("Recommendations are generated by comparing household income, apartment size, and affordability threshold with Mietspiegel rent data. Subdistricts are filtered by your chosen cluster profile and ranked by affordability. The system shows up to 10 subdistricts that best match these inputs.")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Your Preferences")

    # Subdistrict profile FILTER
    if isinstance(CLUSTER_LABELS, dict):
        cluster_names = [CLUSTER_LABELS[k] for k in sorted(CLUSTER_LABELS.keys())]
        cluster_map = {v: k for k, v in CLUSTER_LABELS.items()}
    else:
        cluster_names = ["Balanced", "Vibrant", "Affordable", "Prestige"]
        cluster_map = {name: i for i, name in enumerate(cluster_names)}

    clusters = st.multiselect(
        "Preferred Subdistrict profile(s)",
        options=cluster_names,
        default=["Vibrant"],
        help="Lifestyle profile"
    )

    # Household type controls
    hh_type = st.selectbox(
        "Household type",
        ["Single", "Couple", "Family", "WG", "Senior"],
        index=0,
        help="We use this to estimate a reasonable apartment size for affordability."
    )
    children = 0
    wg_people = 3
    if hh_type == "Family":
        children = st.number_input("Number of children", min_value=0, max_value=6, value=1, step=1)
    if hh_type == "WG":
        wg_people = st.number_input("Number of people in the WG", min_value=2, max_value=10, value=3, step=1)

    # Pre-compute household-based size for use in Advanced Settings
    _hh_required_sqm = estimate_required_sqm(hh_type, children=children, wg_people=wg_people)

    # Income field depends on household type
    income_label = "Monthly household income (€)" if hh_type != "WG" else "Monthly personal income (€)"
    income_help = (
        "Total take-home for everyone in the household." if hh_type != "WG" else
        "Your own monthly budget for rent (we price a single room in a shared flat)."
    )
    income = st.number_input(income_label, min_value=500, max_value=10000, value=3500, step=50, help=income_help)

    prefer_quiet = None  # will be set in Advanced Settings

    with st.expander("Advanced Settings"):
        # Amenity preferences
        amenity_labels = list(AMENITY_COLUMNS.keys())
        selected_amenities = st.multiselect(
            "Prioritize amenities (optional)",
            options=amenity_labels,
            default=[],
            help="Boost areas with these amenities (if available in data)."
        )
        amenity_strength = st.slider(
            "Amenity importance",
            min_value=0.2, max_value=2.0, value=1.0, step=0.1,
            help="How strongly to prioritize the selected amenities in ranking."
        )

        # Quieter areas preference
        prefer_quiet = st.checkbox(
            "Prefer quieter areas",
            value=False,
            help="Lightly downweights nightlife (bars, nightclubs) where data is available."
        )

        # Affordability threshold
        thr = st.slider(
            "Affordability threshold (rent/income)",
            0.20, 0.50, 0.30, 0.01, format="%.2f"
        )

        # How many results
        k = st.slider("How many results?", 3, 10, 5)

        # Relaxed threshold fallback
        relaxed = st.checkbox(
            "Allow relaxed threshold fallback",
            value=True,
            help="If enabled, the recommender will gradually relax the affordability threshold (e.g., 0.32, 0.35, 0.40) if no matches are found."
        )
        relax_seq = (0.32, 0.35, 0.40) if relaxed else ()

        # Household-based size
        use_hh_size = st.checkbox(
            "Use household-based size (recommended)",
            value=True,
            help="If checked, the app will estimate m² from your household type. Uncheck to set m² manually."
        )
        if not use_hh_size:
            size = st.slider("Apartment size (m²)", min_value=30, max_value=100, value=60, step=5)
        else:
            size = _hh_required_sqm
            st.info(f"Using **{size} m²** based on the selected household type.")

        # For WGs, use per-person room size for affordability comparisons
        size_for_calc = size
        if hh_type == "WG":
            size_for_calc = HOUSEHOLD_M2["WG"]["per_person"]

    # Brief size summary below Advanced Settings
    _mode = "household-based" if use_hh_size else "custom"
    st.caption(f"Size used for affordability: **{size} m²** ({_mode}).")

# Run recommender
st.markdown(
    """
    <style>
    div.stButton > button[kind="secondary"] {
        background-color: #f0f0f0;
        color: black;
        border-radius: 6px;
        border: 2px solid #A50034;
        font-weight: bold;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #A50034;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
if st.button("🔍 Find Subdistricts", use_container_width=True):
    if clusters:
        preferred_clusters = [cluster_map[name] for name in clusters]
    else:
        preferred_clusters = [0, 1, 2, 3]
    new_results = get_top_k(
        monthly_income_eur=income,
        size_m2=size_for_calc,
        threshold=thr,
        preferred_clusters=preferred_clusters,
        k=k,
        relax_thresholds=relax_seq,
    )
    # Save to session so UI interactions 
    st.session_state["results"] = new_results

# Always read from session state to display current results
results = st.session_state.get("results")

if results is None:
    st.markdown(
        """
        <div style='background-color: #f5f5f5; padding: 12px; border-radius: 6px; border: 1px solid #ddd;'>
            Set your preferences and click <b>Find Subdistricts</b> to see recommendations.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    if results.empty:
        st.warning("No matches. Try increasing threshold or apartment size.")
    else:
        st.success(f"Showing {len(results)} recommendation(s).")
        # Household-aware ranking: add a small POI-based score if columns exist
        base_weights = HH_WEIGHTS.get(hh_type, {}).copy()
        # User amenity boosts
        user_weights = {}
        for lbl in selected_amenities:
            col = AMENITY_COLUMNS.get(lbl)
            if col:
                user_weights[col] = user_weights.get(col, 0.0) + amenity_strength
        # Quiet preference reduces nightlife a bit
        if prefer_quiet:
            for col in ["bar", "nightclub"]:
                user_weights[col] = user_weights.get(col, 0.0) - 0.5
        # Merge weights (user overrides add to base)
        weights = base_weights
        for k, v in user_weights.items():
            weights[k] = weights.get(k, 0.0) + v
        if weights and not results.empty:
            import numpy as np
            results = results.copy()
            score = np.zeros(len(results), dtype=float)
            for col, w in weights.items():
                if col in results.columns:
                    col_vals = results[col].astype(float)
                    std = col_vals.std(ddof=0)
                    if std and not np.isnan(std) and std > 0:
                        score += w * (col_vals - col_vals.mean()) / std
            results["hh_match_score"] = score
            # Prefer higher match score, then lower estimated rent if available
            sort_cols = ["hh_match_score"]
            ascending = [False]
            if "aff_est_monthly_rent" in results.columns:
                sort_cols.append("aff_est_monthly_rent")
                ascending.append(True)
            results.sort_values(sort_cols, ascending=ascending, inplace=True)

        if hh_type == "WG":
            st.caption(f"Estimated cold rent calculations priced a **single room (~{HOUSEHOLD_M2['WG']['per_person']} m²)** against your **personal** income. The total flat size (≈ {size} m² for {wg_people} people) is shown for context.")
        else:
            st.caption(f"Estimated cold rent calculations used **{size} m²** for a **{hh_type}** household against **household income**.")

        # Summarize amenity preferences if any
        if selected_amenities or prefer_quiet:
            parts = []
            if selected_amenities:
                parts.append("prioritizing: " + ", ".join(selected_amenities))
            if prefer_quiet:
                parts.append("quieter areas")
            st.caption("Ranking tweaks — " + "; ".join(parts) + f" (strength ×{amenity_strength:.1f}).")

        # Render standardized table (clean names + €, % + selection)
        edited, selected_rows = render_subdistrict_reco_table(
            results.copy(),
            cluster_labels=CLUSTER_LABELS,
            cluster_col=DEFAULT_CLUSTER_COL,
        )

        # Show the cluster profile(s) when row is selected
        if not selected_rows.empty and DEFAULT_CLUSTER_COL in selected_rows.columns:
            sel_clusters = list(dict.fromkeys(selected_rows[DEFAULT_CLUSTER_COL].tolist()))  # preserve order, unique
            cols = st.columns(len(sel_clusters))
            for i, cl in enumerate(sel_clusters):
                with cols[i]:
                    st.subheader(CLUSTER_LABELS.get(int(cl), str(cl)))
                    st.write(CLUSTER_NOTES.get(int(cl), ""))
            
            # Bookmark actions 
            for _idx, _row in selected_rows.iterrows():
                bezirk_val = str(_row.get("bezirk", "")).strip()
                ortsteil_val = str(_row.get("ortsteil", "")).strip()
                cluster_label = str(_row.get("Cluster", "")).strip()
                est_rent = _row.get("aff_est_monthly_rent", None)

                key = f"{bezirk_val}—{ortsteil_val}"
                meta = {
                    "cluster": cluster_label if cluster_label else None,
                    "est_monthly_rent": float(est_rent) if est_rent is not None else None,
                }

                c1, c2, c3, c4 = st.columns([3, 3, 3, 2])
                with c1:
                    st.markdown(f"**District:** {de_pretty(bezirk_val)}")
                with c2:
                    st.markdown(f"**Subdistrict:** {de_pretty(ortsteil_val)}")
                with c3:
                    st.markdown(f"**Cluster:** {cluster_label if cluster_label else '—'}")
                with c4:
                    if is_bookmarked(key):
                        if st.button("🗑️ Remove", key=f"unbm_{key}", use_container_width=True):
                            remove_bookmark(key)
                            st.toast(f"Removed {ortsteil_val} from bookmarks")
                            st.rerun()
                    else:
                        if st.button("⭐ Bookmark", key=f"bm_{key}", use_container_width=True):
                            add_bookmark(bezirk=bezirk_val, subdistrict=ortsteil_val, meta=meta)
                            st.toast(f"Added {ortsteil_val} to bookmarks")

                with st.expander("Cultural facts & context", expanded=True):
                    # District facts
                    d_info = get_district_blurb(bezirk_val)
                    sd_info = get_subdistrict_blurb(bezirk_val, ortsteil_val)

                    if d_info.get("blurb"):
                        st.markdown("#### District: " + de_pretty(bezirk_val))
                        st.write(d_info.get("blurb"))
                        images_from_json = []
                        if isinstance(d_info.get("images"), list):
                            images_from_json = [
                                os.path.join(IMAGES_DIR, img) if not os.path.isabs(img) else img
                                for img in d_info.get("images")
                                if isinstance(img, str) and img
                            ]
                        elif isinstance(d_info.get("image_path"), str) and d_info.get("image_path"):
                            p = d_info.get("image_path")
                            images_from_json = [os.path.join(IMAGES_DIR, p) if not os.path.isabs(p) else p]

                        district_imgs = images_from_json or find_district_images(bezirk_val)
                        if district_imgs:
                            cols = st.columns(min(4, len(district_imgs)))
                            for i, img_path in enumerate(district_imgs[:4]):
                                with cols[i % len(cols)]:
                                    # Keep all images the same visual size; width is handled by CSS
                                    st.image(_fit_image_for_card(img_path), use_container_width=True)
                                    credit_line = get_image_credit(bezirk_val, i)
                                    # Keep a fixed-height credit area so cards line up, even if empty
                                    st.markdown("<div class='credit-fixed'>", unsafe_allow_html=True)
                                    if credit_line:
                                        st.caption(credit_line)
                                    else:
                                        st.caption("\u00A0")  # non-breaking space to reserve height
                                    st.markdown("</div>", unsafe_allow_html=True)

                    # Subdistrict facts
                    if sd_info.get("blurb"):
                         st.markdown("#### Subdistrict: " + de_pretty(ortsteil_val))
                         st.write(sd_info.get("blurb"))

            st.caption("Tip: tick one or more rows to see the matching cluster profile and subdistrict descriptions.")
        
        # Reset recommendation
        st.divider()
        if st.button("Reset search", use_container_width=True):
            st.session_state["results"] = None
            st.rerun()

render_footer()            
