import streamlit as st
import os
import base64
from utils.ui import render_footer, safe_switch, inject_responsive_css

# Ensure project root is importable
icon_path = os.path.join(os.path.dirname(__file__), "images", "icon.png")
st.set_page_config(
    page_title="Berlin Housing - Home",
    page_icon=icon_path,
    layout="wide",)


# Targets for Navigation
PAGE_RECOMMENDER = "pages/01_Recommender.py"  # page with recommender inputs
PAGE_PROFILES = "pages/02_Subdistrict_Profiles.py"  # profile explorer page (adjust if different)
PAGE_TABLEAU_STORY = "pages/03_Berlin_Census.py"  # Tableau Story page

# Hero Section
st.markdown(
    """
    <div style='border: 3px solid #A50034; background-color: #A50034; padding: 15px; text-align: center; border-radius: 6px;'>
        <h1 style='color: white; margin: 0;'>Berlin Housing Explorer</h1>
        <p style='color: white; margin: 5px 0 0; font-size: 14px;'>
            Created by <a href="https://www.linkedin.com/in/dido-de-boodt/" target="_blank" style="color: white; text-decoration: underline;">Dido De Boodt</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True)

st.divider()
st.markdown("""**Where to live in Berlin** - Find the right district for you! Use the recommender, explore subdistrict profiles, or deep-dive into the Berlin Census with an interactive dashboard.""")
st.divider()

# Layout with image left and buttons right
col_img, col_btns = st.columns([2, 1])
with col_img:
    hero_img_path = os.path.join(os.path.dirname(__file__), "images", "berlin.jpg")
    st.image(hero_img_path, use_container_width=True)
    st.caption("Photo by [Jonas Tebbe](https://unsplash.com/@jonastebbe?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash) on [Unsplash](https://unsplash.com/photos/white-tower-in-the-middle-of-city-LDMDCVtQqR4?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash)")

with col_btns:
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #f0f0f0;
            color: black;
            border-radius: 6px;
            border: 2px solid #A50034;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #8B002B;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True)
    if st.button("Start with the Recommender", use_container_width=True):
        safe_switch(PAGE_RECOMMENDER)
    st.caption("Get subdistrict suggestions based on income, affordability, and preferences.")
    st.markdown("<div style='margin-bottom:70px'></div>", unsafe_allow_html=True)

    if st.button("Explore Subdistrict Profiles", use_container_width=True):
        safe_switch(PAGE_PROFILES)
    st.caption("See maps, cluster profiles, and neighborhood summaries.")
    st.markdown("<div style='margin-bottom:70px'></div>", unsafe_allow_html=True)

    if st.button("Open the Berlin Census Dashboard", use_container_width=True):
        safe_switch(PAGE_TABLEAU_STORY)
    st.caption("Interactive storytelling with Census 2022 & housing context.")
st.divider()

# Highlights (static data)
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Population", "3,850,809")
with c2:
    st.metric("Districts", "12")
with c3:
    st.metric("Subdistricts", "96")
st.divider()

# How to Use
col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("""
    <div style='border: 2px solid #A50034; background-color: #A50034; padding: 8px; text-align: center; border-radius: 4px;'>
        <h2 style='color: white; margin: 0; font-size: 20px;'>How to use this web app</h2>
    </div>
    """,
    unsafe_allow_html=True)
    st.markdown("<h3 style='color:#A50034;'>Recommender</h3>", unsafe_allow_html=True)
    st.markdown("""
        * Provide your **net income** with **affordability threshold** (e.g. 30–40%), **desired apartment size**, and desired subdistrict profiles (Balanced, Vibrant, Affordable, and Prestige).
        * **Review results** — Sort & filter the recommended subdistricts; open the **profile** of any result for details. Here you can explore cultural facts, images, and amenities.""")
    st.markdown("<h3 style='color:#A50034;'>Subdistrict Profiles</h3>", unsafe_allow_html=True)
    st.markdown("""
        * Explore the subdistrict profiles and their subdistricts on a map.
        * Discover subdistrict features like median income, mietspiegel class, and amaneties (cafes, supermarkets, green spaces, and schools)""")

with col_right:
    bear_explorer_path = os.path.join(os.path.dirname(__file__), "images", "bear_explorer.png")
    try:
        with open(bear_explorer_path, "rb") as f:
            bear_explorer_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="min-height: 400px; display:flex; align-items:center; justify-content:center;">
                <img src="data:image/png;base64,{bear_explorer_b64}" style="width: 400px; height: 400px; object-fit: contain; max-width:100%;">
            </div>
            """,
            unsafe_allow_html=True)
    except Exception:
        st.markdown('<div style="min-height: 400px; display:flex; align-items:center; justify-content:center;">', unsafe_allow_html=True)
        st.image(bear_explorer_path, width=400, output_format="PNG")
        st.markdown('</div>', unsafe_allow_html=True)
st.divider()

col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("<h3 style='color:#A50034;'>Districts</h3>", unsafe_allow_html=True)
    st.markdown("""
        * Explore the district Tableau dashboard built with data from the most recent Berlin Census (2022)
        * Contains information about income, rent, population, employment, housing, etc. """)
    st.markdown("<h3 style='color:#A50034;'>Berlin Census Dashboard</h3>", unsafe_allow_html=True)
    st.markdown( """
        * Interactive Tableau story at district level with demographics, income, housing stock, employment, amenities, and rent context.
        * Use filters to compare districts across categories and track trends from the 2022 Census combined with housing datasets. """)
    st.markdown("<h3 style='color:#A50034;'>Bookmark favorites</h3>", unsafe_allow_html=True)
    st.markdown(
        """
        * Save shortlists of subdistricts to revisit and compare.
        """)

with col_right:
    bear_city_path = os.path.join(os.path.dirname(__file__), "images", "bear_city.png")
    try:
        with open(bear_city_path, "rb") as f:
            bear_explorer_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="min-height: 400px; display:flex; align-items:center; justify-content:center;">
                <img src="data:image/png;base64,{bear_explorer_b64}" style="width: 400px; height: 400px; object-fit: contain; max-width:100%;">
            </div>
            """,
            unsafe_allow_html=True)
    except Exception:
        st.markdown('<div style="min-height: 400px; display:flex; align-items:center; justify-content:center;">', unsafe_allow_html=True)
        st.image(bear_city_path, width=400, output_format="PNG")
        st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# Credits & Data Sources
col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("""
        <div style='border: 2px solid #A50034; background-color: #A50034; padding: 8px; text-align: center; border-radius: 4px;'>
            <h2 style='color: white; margin: 0; font-size: 20px;'>Credits & Data Sources</h2>
        </div>
        """,
        unsafe_allow_html=True)
    st.markdown("")
    st.markdown(
    """
    - **Mietspiegel 2024** — official Berlin rental reference (Senatsverwaltung). Cleaned street directory extracts used to map streets → **Mietspiegel classes** and typical rent bands:
    - **Census 2022** (Zensus; Amt für Statistik Berlin‑Brandenburg / Destatis):district level information - population, households, age, housing characteristics)
    - **District (Bezirk) tables** (sources: Amt für Statistik Berlin‑Brandenburg, Berlin Open Data): employment, buildings, rent per m2, median income
    - **Subdistrict (Ortsteil) & Features** (2024): age groups (groeped per 5 years), gender, rent, income, amenities, amenities densities
    - **Geospatial layers & external**:
      - OpenStreetMap (boundaries & POIs via OSMnx) — attribution: © OpenStreetMap contributors
      - Berlin Open Data portal datasets (amenities, environment, infrastructure)
      - (Optional cross‑checks) Public district summaries from Kaggle (descriptive only)
    """)
    
with col_right:
    bear_analyst_path = os.path.join(os.path.dirname(__file__), "images", "bear_analyst.png")
    try:
        with open(bear_analyst_path, "rb") as f:
            bear_analyst_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="min-height: 400px; display:flex; align-items:center; justify-content:center;">
                <img src="data:image/png;base64,{bear_analyst_b64}" style="width: 400px; height: 400px; object-fit: contain; max-width:100%;">
            </div>
            """,
            unsafe_allow_html=True)
    except Exception:
        st.markdown('<div style="min-height: 400px; display:flex; align-items:center; justify-content:center;">', unsafe_allow_html=True)
        st.image(bear_analyst_path, width=400, output_format="PNG")
        st.markdown('</div>', unsafe_allow_html=True)
st.divider()

col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("""
    <div style='border: 2px solid #A50034; background-color: #A50034; padding: 8px; text-align: center; border-radius: 4px;'>
        <h2 style='color: white; margin: 0; font-size: 20px;'>Tools & stack</h2>
    </div>
    """,
    unsafe_allow_html=True)
    st.markdown("<h3 style='color:#A50034;'>Tools</h3>", unsafe_allow_html=True)
    st.markdown("""
    - **Python**: pandas, numpy, **geopandas**, shapely, pyproj, osmnx, requests, regex, **scikit‑learn** (StandardScaler, PCA, K‑Means, DBSCAN, Logistic Regression), matplotlib/plotly
    - **Data collection**: Selenium (Mietspiegel interactive table scraping), Berlin **WFS**/Open Data APIs, PDF → CSV extraction
    - **App & viz**: **Streamlit** (this app), **Tableau** (district dashboard), **Python** (exploratory and report notebooks)
    - **Workflow**: VS Code, virtual environments (py3.10), Jupyter, git/GitHub""")
    st.markdown("<h3 style='color:#A50034;'>Notes on processing & feature engineering</h3>", unsafe_allow_html=True)
    st.markdown("""
        - Harmonized district/subdistrict keys; normalized names (ä→ae, ö→oe, ü→ue, ß→ss). 
        - Derived indicators: youth/senior shares, POI per‑capita and per‑km² densities, rent‑to‑income ratios, affordability thresholds.
        - Consolidated into master tables for **EDA → PCA → clustering → recommender**.""") 
st.divider()
st.markdown("<h3 style='color:#A50034;'>Images</h3>", unsafe_allow_html=True)
st.markdown("""
    - District and subdistrict cultural images used in this app were sourced from **Unsplash** (free to use, attribution required).
    - Credits are included below each image in the app, following the [Unsplash License](https://unsplash.com/license).""")
    
with col_right:
    bear_python_path = os.path.join(os.path.dirname(__file__), "images", "bear_python.png")
    try:
        with open(bear_python_path, "rb") as f:
            bear_analyst_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="min-height: 400px; display:flex; align-items:center; justify-content:center;">
                <img src="data:image/png;base64,{bear_analyst_b64}" style="width: 400px; height: 400px; object-fit: contain; max-width:100%;">
            </div>
            """,
            unsafe_allow_html=True)
    except Exception:
        st.markdown('<div style="min-height: 400px; display:flex; align-items:center; justify-content:center;">', unsafe_allow_html=True)
        st.image(bear_python_path, width=400, output_format="PNG")
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()
render_footer()