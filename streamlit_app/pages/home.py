

import streamlit as st

# ---------- Page Config ----------
st.set_page_config(
    page_title="Berlin Housing Affordability — Home",
    page_icon="🏠",
    layout="wide",
)

# ---------- (Optional) Targets for Navigation ----------
# If a switch doesn't work, update these paths to match your repo structure.
PAGE_RECOMMENDER = "app.py"  # main app with recommender inputs
PAGE_PROFILES = "pages/subdistrict_profiles.py"  # profile explorer page (adjust if different)
PAGE_TABLEAU_STORY = "pages/tableau_census_2022.py"  # Tableau Story page
PAGE_COMPARE = "pages/compare_subdistricts.py"  # (future) compare view
PAGE_INSIGHTS = "pages/insights.py"  # (future) data insights view

# Helper for safe navigation that won't crash if the page isn't present
def safe_switch(target: str):
    try:
        # Streamlit 1.25+ provides switch_page
        st.switch_page(target)
    except Exception:
        st.info(
            f"Couldn't open `{target}` automatically. "
            "Please adjust the constants at the top of `home.py` to match your file names, "
            "or use the sidebar to navigate."
        )

# ---------- Hero Section ----------
st.title("Berlin Housing Affordability Dashboard")
st.markdown(
    """
    **Find where you can afford to live in Berlin** — powered by the Mietspiegel, Census 2022, and rich neighborhood features.
    Use the recommender, explore subdistrict profiles, and deep-dive with the interactive Tableau Story.
    """
)

# ---------- Quick Actions ----------
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔎 Start with the Recommender", use_container_width=True):
            safe_switch(PAGE_RECOMMENDER)
        st.caption("Enter income, size, and affordability threshold to get personalized suggestions.")
    with c2:
        if st.button("🗺️ Explore Subdistrict Profiles", use_container_width=True):
            safe_switch(PAGE_PROFILES)
        st.caption("See maps, cluster profiles, and neighborhood summaries.")
    with c3:
        if st.button("📖 Open the Tableau Story", use_container_width=True):
            safe_switch(PAGE_TABLEAU_STORY)
        st.caption("Interactive storytelling with Census 2022 & housing context.")

st.divider()

# ---------- How to Use ----------
st.subheader("How to use this app")
st.markdown(
    """
    1. **Recommender** — Provide your **net income**, **desired apartment size**, and **affordability threshold** (e.g. 30–40%).
    2. **Review results** — Sort & filter the recommended subdistricts; open the **profile** of any result for details.
    3. **Bookmark favorites** *(coming up)* — Save shortlists of subdistricts to revisit and compare.
    4. **Compare** *(coming up)* — Put 2–3 subdistricts side-by-side for rents, income, demographics, and POIs.
    5. **Insights** *(coming up)* — Explore mini-charts and affordability heatmaps.
    6. **Tableau Story** — Dive deeper into **Census 2022** patterns with an interactive narrative view.
    """
)

# ---------- Highlights (static placeholders; wire up to live KPIs later) ----------
with st.container():
    h1, h2, h3 = st.columns(3)
    with h1:
        st.metric("Subdistricts covered", value="96", delta=None)
    with h2:
        st.metric("Rent datapoints", value="Mietspiegel 2023–2024", delta=None)
    with h3:
        st.metric("Latest census", value="2022", delta=None)

st.divider()

# ---------- Credits & Data Sources ----------
st.subheader("Credits & Data Sources")
st.markdown(
    """
    **Data**
    - Berlin **Mietspiegel** 2023–2024 (official rental reference)
    - **Census 2022** (Statistisches Bundesamt / Amt für Statistik Berlin-Brandenburg)
    - **Berlin Open Data** (district amenities, infrastructure, environment)

    **Project**
    - Concept, data engineering & app by **Dido De Boodt**  
    - GitHub: _add link_ · Tableau Public: _add link_  
    - Contact: _add link_
    """
)

# ---------- Navigation to Roadmap / Next Features ----------
st.subheader("Roadmap")
st.markdown(
    """
    - ✅ Embedded **Tableau Story** page
    - ✅ **Bookmarks** for favorite subdistricts
    - 🔜 **Compare** 2–3 subdistricts side-by-side
    - 🔜 **Dynamic Filters** (POIs, age mix, green space, nightlife, family-friendly)
    - 🔜 **Insights** page with mini-charts & heatmaps
    - ✅ **Cultural facts** per subdistrict
    - 🔜 **Custom theme** & mobile polish
    """
)

st.info(
    "Tip: If any navigation button doesn't open the target page, use the sidebar or update the page constants at the top of this file."
)

# ---------- Footer ----------
st.write("")
st.caption(
    "Made with ❤️ in Berlin · This app is for educational and exploratory purposes; figures may differ from official publications."
)