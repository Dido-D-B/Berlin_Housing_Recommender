# Ensure project root is importable
import os, sys
import json
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Imports
import streamlit as st
from services.recommender import get_top_k
from berlin_housing.config import DEFAULT_CLUSTER_COL
from utils.bookmarks import add_bookmark, remove_bookmark, is_bookmarked

# === Manual cultural facts (district + subdistrict) ===
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DISTRICTS_JSON_PATH = os.path.join(DATA_DIR, "districts_cultural_facts.json")
SUBDISTRICTS_JSON_PATH = os.path.join(DATA_DIR, "subdistricts_cultural_facts.json")

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

def district_slug(name: str) -> str:
    """Normalize a district name to a filename-friendly slug used by images.
    Example: "Tempelhof‑Schöneberg" -> "tempelhof-schoeneberg".
    """
    s = _norm(name)
    s = s.replace(" ", "-")  # spaces to dashes
    return s


def _normalize_filename_base(s: str) -> str:
    """Apply the same normalization as _norm, plus turn spaces/underscores to '-'."""
    if not isinstance(s, str):
        s = str(s) if s is not None else ""
    # unify dashes
    for d in _DASHES:
        s = s.replace(d, "-")
    s = s.replace("—", "-")
    # umlauts/ß
    repl = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
    for k, v in repl.items():
        s = s.replace(k, v)
    # spaces/underscores
    s = s.replace("_", "-")
    s = " ".join(s.strip().split()).lower().replace(" ", "-")
    return s


def find_district_images(bezirk: str, max_n: int = 4):
    """Return up to max_n image paths for a district by *normalizing* filenames.
    Accepts 'Charlottenburg–Wilmersdorf1.jpeg' (en‑dash) and 'charlottenburg-wilmersdorf1.jpg' alike.
    """
    slug = district_slug(bezirk)  # already normalized
    targets = {f"{slug}{i}" for i in range(1, max_n + 1)}
    exts = {".jpeg", ".jpg", ".png"}

    found = [None] * max_n
    try:
        for fname in os.listdir(IMAGES_DIR):
            root, ext = os.path.splitext(fname)
            if ext.lower() not in exts:
                continue
            norm_root = _normalize_filename_base(root)
            # If this file matches one of our targets, place it in the right slot
            for i in range(1, max_n + 1):
                if norm_root == f"{slug}{i}":
                    found[i - 1] = os.path.join(IMAGES_DIR, fname)
                    break
    except FileNotFoundError:
        return []

    return [p for p in found if p]

# robust dash/whitespace normalization to match keys reliably
_DASHES = "\u2013\u2014\u2012\u2212\u2010\u2011"  # en/em/figure/minus/hyphen variants

def _norm(s: str):
    if not isinstance(s, str):
        s = str(s) if s is not None else ""
    # unify dashes to ASCII '-'
    for d in _DASHES:
        s = s.replace(d, "-")
    # also normalize the commonly used em‑dash like '—' (U+2014)
    s = s.replace("—", "-")
    # normalize German umlauts and ß
    repl = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return " ".join(s.strip().split()).lower()

# load JSON safely
def _load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

_district_facts_raw = _load_json(DISTRICTS_JSON_PATH)
_subdistrict_facts_raw = _load_json(SUBDISTRICTS_JSON_PATH)

# build indices
# districts are keyed by district name directly
_DISTRICT_INDEX = { _norm(k): v for k, v in _district_facts_raw.items() }

# subdistricts may be keyed like "Bezirk—Ortsteil" but also contain fields; we index by (bezirk, ortsteil)
_SUBDISTRICT_INDEX = {}
for k, v in _subdistrict_facts_raw.items():
    b = v.get("bezirk") or ""
    o = v.get("ortsteil") or ""
    key = (_norm(b), _norm(o))
    _SUBDISTRICT_INDEX[key] = v


def get_district_blurb(bezirk: str):
    """Return dict with keys {blurb, image_path, source} or {} if missing."""
    return _DISTRICT_INDEX.get(_norm(bezirk), {})


def get_subdistrict_blurb(bezirk: str, ortsteil: str):
    """Return dict with keys {blurb, image_path, source, bezirk, ortsteil} or {} if missing."""
    return _SUBDISTRICT_INDEX.get((_norm(bezirk), _norm(ortsteil)), {})

# Cluster labels + notes for inline profiles
CLUSTER_LABELS = {0: "Balanced", 1: "Vibrant", 2: "Affordable", 3: "Prestige"}
CLUSTER_NOTES = {
    0: "Small, quiet, affordable neighborhoods with balanced age mix and modest amenities — good for families prioritizing calm and price.",
    1: "Large, amenity‑rich urban hubs with lots of cafés, restaurants and nightlife — lively, central, and convenient.",
    2: "Mid‑sized, value‑focused areas with the lowest average rents and fewer amenities — attractive for budget‑minded renters.",
    3: "Wealthy, high‑amenity hotspots with top scores for food, cafés and green space — trendy but pricier.",
}

st.set_page_config(page_title="Berlin Housing Recommender", layout="wide")

# Persist results across reruns so selections in the table don't clear it
if "results" not in st.session_state:
    st.session_state["results"] = None

# Header
st.title("Berlin Housing – Subdistrict Recommender")
st.caption("Filter by budget and cluster profile, then see Top‑5 picks.")

# Sidebar controls
with st.sidebar:
    st.header("Your Preferences")
    income = st.number_input("Monthly household income (€)", min_value=500, max_value=10000, value=3500, step=50)
    size = st.slider("Apartment size (m²)", min_value=30, max_value=100, value=60, step=5)
    thr = st.slider("Affordability threshold (rent/income)", 0.20, 0.50, 0.30, 0.01, format="%.2f")
    cluster_names = ["Balanced", "Vibrant", "Affordable", "Prestige"]
    cluster_map = {"Balanced": 0, "Vibrant": 1, "Affordable": 2, "Prestige": 3}
    clusters = st.multiselect(
        "Preferred cluster(s)",
        options=cluster_names,
        default=["Vibrant"],
        help="Lifestyle profile"
    )
    k = st.slider("How many results?", 3, 10, 5)

    relaxed = st.checkbox("Allow relaxed threshold fallback", value=True)
    relax_seq = (0.32, 0.35, 0.40) if relaxed else ()

    st.markdown("---")
    if st.button("⭐ View Bookmarks", use_container_width=True):
        try:
            st.switch_page("pages/bookmarks.py")
        except Exception:
            st.info("Open the **Bookmarks** page from the sidebar Pages list.")

# Run recommender
if st.button("Find subdistricts", use_container_width=True):
    if clusters:
        preferred_clusters = [cluster_map[name] for name in clusters]
    else:
        preferred_clusters = [0, 1, 2, 3]
    new_results = get_top_k(
        monthly_income_eur=income,
        size_m2=size,
        threshold=thr,
        preferred_clusters=preferred_clusters,
        k=k,
        relax_thresholds=relax_seq,
    )
    # Save to session so UI interactions (checkbox clicks) don't clear the table
    st.session_state["results"] = new_results

# Always read from session state to display current results
results = st.session_state.get("results")

if results is None:
    st.info("Set your preferences and click **Find subdistricts** to see recommendations.")
else:
    if results.empty:
        st.warning("No matches. Try increasing threshold or apartment size.")
    else:
        st.success(f"Showing {len(results)} recommendation(s).")

        # Build a clean, user-facing table
        display_df = results.copy()

        # Add human-friendly cluster label while keeping numeric id for logic
        if DEFAULT_CLUSTER_COL in display_df.columns:
            display_df["Cluster"] = display_df[DEFAULT_CLUSTER_COL].map(CLUSTER_LABELS)

        # Derive user-facing columns
        display_df["Est. Monthly Rent (€)"] = display_df.get("aff_est_monthly_rent", 0).round(0).apply(lambda x: f"{int(x):,}")
        display_df["Rent per m² (€)"] = display_df.get("aff_rent_per_m2", 0).round(2)
        display_df["Rent / Income (%)"] = (display_df.get("aff_rent_to_income", 0) * 100).round(1)

        # Selection column as a simple way to "click" a row
        if "Select" not in display_df.columns:
            display_df.insert(0, "Select", False)

        # Column ordering for display (keep technical cols hidden by not listing them)
        column_order = [
            "Select",
            "bezirk",
            "ortsteil",
            "Cluster",
            "Est. Monthly Rent (€)",
            "Rent per m² (€)",
            "Rent / Income (%)",
        ]

        # Render the cleaned table
        edited = st.data_editor(
            display_df,
            hide_index=True,
            use_container_width=True,
            column_order=column_order,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select", help="Tick a row to see its cluster profile"
                ),
                "bezirk": st.column_config.TextColumn("District"),
                "ortsteil": st.column_config.TextColumn("Subdistrict"),
                "Est. Monthly Rent (€)": st.column_config.TextColumn(
                    "Est. Monthly Rent (€)"
                ),
                "Rent per m² (€)": st.column_config.NumberColumn(
                    "Rent per m² (€)", format="%.2f"
                ),
                "Rent / Income (%)": st.column_config.NumberColumn(
                    "Rent / Income (%)", format="%.1f"
                ),
                "Cluster": st.column_config.TextColumn("Cluster"),
            },
            disabled=[c for c in display_df.columns if c != "Select"],
        )

        # If the user selected any rows, show the cluster profile(s)
        try:
            selected_rows = edited[edited["Select"]]
        except Exception:
            selected_rows = display_df.iloc[0:0]

        if not selected_rows.empty and DEFAULT_CLUSTER_COL in selected_rows.columns:
            sel_clusters = list(dict.fromkeys(selected_rows[DEFAULT_CLUSTER_COL].tolist()))  # preserve order, unique
            st.markdown("### Selected cluster profiles")
            cols = st.columns(len(sel_clusters))
            for i, cl in enumerate(sel_clusters):
                with cols[i]:
                    st.subheader(CLUSTER_LABELS.get(int(cl), str(cl)))
                    st.write(CLUSTER_NOTES.get(int(cl), ""))
            
            # Bookmark actions for each selected row 
            # Build action columns per selected row
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
                    st.markdown(f"**District:** {bezirk_val}")
                with c2:
                    st.markdown(f"**Subdistrict:** {ortsteil_val}")
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
                        st.markdown("#### District: " + bezirk_val)
                        st.write(d_info.get("blurb"))
                        # Try JSON-declared images, then fallback to auto-discovery from /images
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
                                    st.image(img_path, use_container_width=True)
                    else:
                        st.caption("No district cultural blurb found yet.")

                    # Subdistrict facts
                    if sd_info.get("blurb"):
                        st.markdown("#### Subdistrict: " + ortsteil_val)
                        st.write(sd_info.get("blurb"))
                    else:
                        st.caption("No subdistrict cultural blurb found yet.")
        else:
            st.caption("Tip: tick one or more rows to see the matching cluster profile and subdistrict descriptions.")

        st.divider()
        if st.button("Reset search", use_container_width=True):
            st.session_state["results"] = None
            st.rerun()