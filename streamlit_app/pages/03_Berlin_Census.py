# Imports
import os, sys
import streamlit as st
from streamlit.components.v1 import html
from utils.ui import render_footer, inject_responsive_css

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Page Configurations
icon_path = os.path.join(PROJECT_ROOT, "streamlit_app", "images", "icon.png")
st.set_page_config(
    page_title="Berlin Housing - Census",
    page_icon=icon_path,
    layout="wide",
)

# CSS
inject_responsive_css()

# Title
st.markdown(
    """
    <div style='border: 3px solid #A50034; background-color: #A50034; padding: 15px; text-align: center; border-radius: 6px;'>
        <h1 style='color: white; margin: 0;'>Berlin Census</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='color: #A50034;'>Berlin Census 2022 Tableau dashboard</h3>",
    unsafe_allow_html=True,
)
st.write("This dashboard explores Berlin’s housing market and demographics using official data from the 2022 Berlin Census.")

# Original full Story (desktop-friendly)
STORY_URL = (
    "https://public.tableau.com/views/"
    "BerlinHousingPopulationDashboardBerlinCensus2022-BerlinRed/BerlinHousingPopulation"
    "?:showVizHome=no&:embed=y&:toolbar=bottom"
)

# Toggle between Story and mobile-friendly dashboards
view_mode = st.radio(
    "Viewing mode",
    ("Mobile-friendly dashboards", "Full Census Story"),
    index=0,
    horizontal=True,
)

# Tableau Public URL
DASHBOARDS = {
    "Overview": "https://public.tableau.com/views/BerlinCensusOverview-BerlinRedMobile/BerlinHousingOverview?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Districts": "https://public.tableau.com/views/BerlinCensusDistricts-BerlinRedMobile/DistrictDeepDive?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Patterns": "https://public.tableau.com/views/BerlinCensusPatterns-BerlinRedMobile/BerlinPatterns?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Population": "https://public.tableau.com/views/BerlinCensusPopulation-BerlinRedMobile/BerlinPopulation?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Income & Employment": "https://public.tableau.com/views/BerlinCensusEmployment-BerlinRedMobile/EmploymentIncome?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Households": "https://public.tableau.com/views/BerlinCensusHouseholds-BerlinRedMobile/BerlinHouseholds?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Apartments": "https://public.tableau.com/views/BerlinCensusApartments-BerlinRedMobile/BerlinApartments?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Rent & Tenants vs Owner": "https://public.tableau.com/views/BerlinCensusRent-BerlinRedMobile/RentOwnersTenants?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Housing Built Year": "https://public.tableau.com/views/BerlinCensusHousingBuiltYear-BerlinRedMobile/BuildingYears?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Heating & Energy Sources": "https://public.tableau.com/views/BerlinCensusHeatingandEnergy-BerlinRedMobile/HeatingEnergy?:showVizHome=no&:embed=y&:toolbar=bottom",
}

# Helper to render a responsive iframe
def render_tableau(url: str, height: int = 1100, aspect_ratio: float = 0.75):
    # aspect_ratio = height/width; 0.75 ~ 4:3 for desktop
    padding_pct = int(aspect_ratio * 100)
    # Inject a small responsive tweak for mobile: make the iframe taller on narrow screens
    st.markdown(
        f"""
        <style>
          @media (max-width: 900px) {{
            .tableau-wrap {{
              padding-bottom: 160% !important;  /* taller for phones */
            }}
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    responsive_iframe = f"""
    <div class="tableau-wrap" style="position: relative; padding-bottom: {padding_pct}%; height: 0; overflow: hidden; width: 100%;">
      <iframe src="{url}" frameborder="0" allowfullscreen loading="lazy"
              style="position: absolute; top:0; left:0; width:100%; height:100%; border:none;"></iframe>
    </div>
    """
    html(responsive_iframe, height=height)

# UI
if view_mode == "Full Census Story":
    render_tableau(STORY_URL)
else:
    # Selector for dashboards (default to Overview)
    choice = st.selectbox("Choose a dashboard", list(DASHBOARDS.keys()), index=0)
    render_tableau(DASHBOARDS[choice])

render_footer()