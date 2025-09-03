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
icon_path = os.path.join(PROJECT_ROOT, "app", "images", "icon.png")
st.set_page_config(
    page_title="Berlin Housing - Census",
    page_icon=icon_path,
    layout="wide",
)

# CSS
inject_responsive_css()

# UI
st.markdown(
    """
    <div style='border: 3px solid #A50034; background-color: #A50034; padding: 15px; text-align: center; border-radius: 6px;'>
        <h1 style='color: white; margin: 0;'>Berlin Census 2022 Dashboards</h1>
        <p style='color: white; margin: 5px 0 0; font-size: 14px;'>
            Project by <a href="https://www.linkedin.com/in/dido-de-boodt/" target="_blank" style="color: white; text-decoration: underline;">Dido De Boodt</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True)

st.divider()
st.markdown("""**Explore Berlin’s Census data** - with these interactive Tableau dashboards. Discover demographics and housing information using official data from the 2022 Berlin Census.""")
st.divider()

# Tableau Public URL
DASHBOARDS = {
    "Overview": "https://public.tableau.com/views/BerlinCensus2022-Overviewmobile/BerlinHousingOverview?:showVizHome=no&:embed=y&:toolbar=bottom",
    "District Deep Dive": "https://public.tableau.com/views/BerlinCensus2022-DistrictDeepDivemobile/DistrictDeepDive?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Patterns": "https://public.tableau.com/views/BerlinCensus2022-Patternsmobile/BerlinPatterns?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Population": "https://public.tableau.com/views/BerlinCensus2022-Populationmobile/BerlinPopulation?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Income & Employment": "https://public.tableau.com/views/BerlinCensus2022-IncomeEmploymentmobile/EmploymentIncome?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Households": "https://public.tableau.com/views/BerlinCensus2022-Householdsmobile/BerlinHouseholds?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Apartments": "https://public.tableau.com/views/BerlinCensus2022-Apartmentsmobile/BerlinApartments?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Rent & Tenants vs Owner": "https://public.tableau.com/views/BerlinCensus2022-RentOwnersTenantsmobile/RentOwnersTenants?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Housing Built Year": "https://public.tableau.com/views/BerlinCensus2022-BuildingYearmobile/BuildingYears?:showVizHome=no&:embed=y&:toolbar=bottom",
    "Heating & Energy Sources": "https://public.tableau.com/views/BerlinCensus2022-HeatingEnergymobile/HeatingEnergy?:showVizHome=no&:embed=y&:toolbar=bottom",
}

# Helper to render a responsive iframe
def render_tableau(url: str, height: int = 900, aspect_ratio: float = 0.6):
    # aspect_ratio = height/width; 0.75 ~ 4:3 for desktop
    padding_pct = int(aspect_ratio * 100)
    # Inject a small responsive tweak for mobile: make the iframe taller on narrow screens
    st.markdown(
        f"""
        <style>
          @media (max-width: 900px) {{
            .tableau-wrap {{
              padding-bottom: 120% !important;  /* better fit for phones */
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

# Selector for dashboards (default to Overview)
choice = st.selectbox("Choose a dashboard", list(DASHBOARDS.keys()), index=0)
render_tableau(DASHBOARDS[choice])

render_footer()