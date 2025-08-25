# Imports
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from typing import Dict, Tuple
from utils.format import fmt_eur, fmt_int

# Reusable footer function
def render_footer():
    st.markdown(
        """
        <div style="text-align: center; margin-top: 2em; font-size: 0.9em; color: gray;">
            Made by <a href="https://www.linkedin.com/in/dido-de-boodt/" target="_blank" rel="noopener">Dido</a> with ❤️ in Berlin<br/>
            This app is for educational and exploratory purposes; figures may differ from official publications.<br/>
            <a href="/" style="color: gray; text-decoration: underline;">Credits</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Helper for safe navigation that won't crash if the page isn't present
def safe_switch(target: str):
    try:
        st.switch_page(target)
    except Exception:
        st.info(
            f"Couldn't open `{target}` automatically. "
            "Please use the sidebar to navigate."
        )    

# Create subdistrict profile table
def build_profiles_table(df: pd.DataFrame, cluster_labels: dict) -> pd.DataFrame:
    display_df = df.copy()
    def _de_pretty(s: str) -> str:
        if not isinstance(s, str):
            return ""
        s = s.strip().lower()
        parts = []
        for token in s.replace("–", "-").split("-"):
            token = " ".join(w.capitalize() for w in token.split())
            parts.append(token)
        out = "-".join(parts)
        for a, b in [("Ae", "Ä"), ("Oe", "Ö"), ("Ue", "Ü"), ("ae", "ä"), ("oe", "ö"), ("ue", "ü"), ("ss", "ß")]:
            out = out.replace(a, b)
        return out
    if "k4_cluster" in display_df.columns:
        display_df["Cluster"] = display_df["k4_cluster"].map(cluster_labels)
    if "bezirk" in display_df.columns:
        display_df["bezirk"] = display_df["bezirk"].astype(str).apply(_de_pretty)
    if "ortsteil" in display_df.columns:
        display_df["ortsteil"] = display_df["ortsteil"].astype(str).apply(_de_pretty)
    cols_order = [
        "bezirk", "ortsteil", "Cluster",
        "subdistrict_avg_median_income_eur",
        "subdistrict_avg_mietspiegel_classification",
        "cafes", "restaurants", "supermarket", "green_space", "schools",
    ]
    cols_order = [c for c in cols_order if c in display_df.columns]
    display_df = display_df[cols_order]
    rename_map = {
        "bezirk": "District",
        "ortsteil": "Subdistrict",
        "subdistrict_avg_median_income_eur": "Avg. median income",
        "subdistrict_avg_mietspiegel_classification": "Avg. Mietspiegel class",
        "cafes": "Cafés",
        "restaurants": "Restaurants",
        "supermarket": "Supermarkets",
        "green_space": "Green spaces",
        "schools": "Schools",
    }
    display_df = display_df.rename(columns=rename_map)
    # Round Mietspiegel class if present
    if "Avg. Mietspiegel class" in display_df.columns:
        display_df["Avg. Mietspiegel class"] = pd.to_numeric(
            display_df["Avg. Mietspiegel class"], errors="coerce"
        ).round()
    if "Avg. median income" in display_df.columns:
        display_df["Avg. median income"] = display_df["Avg. median income"].apply(fmt_eur)
    for c in ["Cafés", "Restaurants", "Supermarkets", "Green spaces", "Schools"]:
        if c in display_df.columns:
            display_df[c] = display_df[c].apply(fmt_int)
    sort_cols = [c for c in ["Cluster", "District", "Subdistrict"] if c in display_df.columns]
    if sort_cols:
        display_df = display_df.sort_values(sort_cols)
    return display_df.reset_index(drop=True)

# Create recomendation table
def render_subdistrict_reco_table(
    df: pd.DataFrame,
    cluster_labels: Dict[int, str] | None = None,
    cluster_col: str = "k4_cluster",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Render a clean subdistrict recommendation table and return (edited_df, selected_rows).

    Expects columns (if present): 
      - 'bezirk', 'ortsteil'
      - numeric: 'aff_est_monthly_rent', 'aff_rent_per_m2', 'aff_rent_to_income' (0..1)
      - cluster id column (default 'k4_cluster')

    Parameters
    ----------
    df : DataFrame
        Source results (will be copied).
    cluster_labels : dict[int,str] | None
        Mapping from cluster id -> human label (e.g., {0:'Balanced', ...}).
    cluster_col : str
        Name of the numeric cluster column in df.

    Returns
    -------
    edited_df : DataFrame
        The DataFrame as shown in the editor (including the 'Select' column).
    selected_rows : DataFrame
        Filter of rows where 'Select' is True (empty if none).
    """
    work = df.copy()

    # Helpers
    def _de_pretty(s: str) -> str:
        if not isinstance(s, str):
            return ""
        s = s.strip().lower()
        parts = []
        for token in s.replace("–", "-").split("-"):
            token = " ".join(w.capitalize() for w in token.split())
            parts.append(token)
        out = "-".join(parts)
        # Restore common German transliterations
        for a, b in [("Ae", "Ä"), ("Oe", "Ö"), ("Ue", "Ü"), ("ae", "ä"), ("oe", "ö"), ("ue", "ü"), ("ss", "ß")]:
            out = out.replace(a, b)
        return out

    # Derive display columns
    # Cluster label
    if cluster_col in work.columns and cluster_labels:
        work["Cluster"] = work[cluster_col].map(cluster_labels).fillna(work[cluster_col].astype(str))

    # Human-facing name columns
    if "bezirk" in work.columns:
        work["District"] = work["bezirk"].astype(str).apply(_de_pretty)
    else:
        work["District"] = ""
    if "ortsteil" in work.columns:
        work["Subdistrict"] = work["ortsteil"].astype(str).apply(_de_pretty)
    else:
        work["Subdistrict"] = ""

    # Numeric display columns (keep numeric; format via column_config)
    work["Est. Monthly Rent (€)"] = pd.to_numeric(work.get("aff_est_monthly_rent"), errors="coerce")
    work["Rent per m² (€)"] = pd.to_numeric(work.get("aff_rent_per_m2"), errors="coerce")
    work["Rent / Income (%)"] = pd.to_numeric(work.get("aff_rent_to_income"), errors="coerce") * 100.0

    # Selection column
    if "Select" not in work.columns:
        work.insert(0, "Select", False)

    # Column order for display (only include if present)
    column_order = [
        "Select",
        "District",
        "Subdistrict",
        "Cluster",
        "Est. Monthly Rent (€)",
        "Rent per m² (€)",
        "Rent / Income (%)",
    ]
    column_order = [c for c in column_order if c in work.columns]

    # Render
    edited = st.data_editor(
        work,
        hide_index=True,
        use_container_width=True,
        column_order=column_order,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select", help="Tick a row to see its cluster profile and subdistrict details"
            ),
            "District": st.column_config.TextColumn("District"),
            "Subdistrict": st.column_config.TextColumn("Subdistrict"),
            "Cluster": st.column_config.TextColumn("Cluster"),
            "Est. Monthly Rent (€)": st.column_config.NumberColumn("Est. Monthly Rent (€)", format="€%.0f"),
            "Rent per m² (€)": st.column_config.NumberColumn("Rent per m² (€)", format="€%.2f"),
            "Rent / Income (%)": st.column_config.NumberColumn("Rent / Income (%)", format="%.1f%%"),
        },
        disabled=[c for c in work.columns if c != "Select"],
    )

    # Selected rows
    try:
        selected = edited[edited["Select"]]
    except Exception:
        selected = work.iloc[0:0]

    return edited, selected

# CSS helper mobile friendly
def inject_responsive_css():
    import streamlit as st
    st.markdown("""
    <style>
      /* Tighten page padding on mobile */
      @media (max-width: 900px){
        .block-container { padding-left: 1rem; padding-right: 1rem; }
      }

      /* Make Streamlit columns stack on small screens */
      @media (max-width: 900px){
        div[data-testid="column"] { flex: 1 1 100% !important; width: 100% !important; }
      }

      /* Full-width buttons, larger tap targets on mobile */
      @media (max-width: 900px){
        div.stButton > button { width: 100%; padding: 0.9rem 1rem; }
      }

      /* Sidebar: keep it compact on small screens */
      @media (max-width: 900px){
        section[data-testid="stSidebar"] { width: 0; min-width: 0; overflow: hidden; }
      }

      /* Images should never overflow */
      img, .stImage img { max-width: 100% !important; height: auto !important; }

      /* Dataframes & charts should fit container */
      .stDataFrame, .stPlotlyChart, .stAltairChart, .stVegaLiteChart { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper: render cluster legend with colors
def render_cluster_legend():
    """Render a horizontal legend with colored swatches for cluster profiles.
    Tries to use a shared color map if present; otherwise falls back to defaults.
    """
    # Mapping from cluster id to profile name
    cluster_name_map = {0: "Balanced", 1: "Vibrant", 2: "Affordable", 3: "Prestige"}

    # Try to use a shared color mapping if available
    color_map = None
    try:
        # Option A: stored in session state by the map page
        color_map = st.session_state.get("CLUSTER_COLOR_MAP")
    except Exception:
        color_map = None

    if not color_map:
        try:
            # Option B: import from a shared module if it exists
            from utils.constants import CLUSTER_COLOR_MAP as _SHARED_COLORS  # type: ignore
            color_map = _SHARED_COLORS
        except Exception:
            color_map = None

    # Fallback colors (tweak if you want to match the map exactly)
    if not color_map:
        color_map = {
            0: "#1f77b4",  # Balanced
            1: "#ff7f0e",  # Vibrant
            2: "#2ca02c",  # Affordable
            3: "#d62728",  # Prestige
        }

    # Build HTML legend
    items_html = []
    for cid in [0, 1, 2, 3]:
        name = cluster_name_map[cid]
        color = color_map.get(cid, "#999999")
        items_html.append(
            (
                "<div style='display:flex; align-items:center; margin:4px 10px;'>"
                f"<span style='display:inline-block; width:14px; height:14px; border-radius:50%; background:{color}; border:1px solid rgba(0,0,0,0.25); margin-right:8px;'></span>"
                f"<span>{name}</span>"
                "</div>"
            )
        )

    legend_html = (
        "<div style='display:flex; flex-wrap:wrap; justify-content:center; gap:6px; color:dimgray; font-size:14px; margin-top:4px; margin-bottom:10px;'>"
        + "".join(items_html)
        + "</div>"
    )
    components.html(legend_html, height=60)
