import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Berlin Housing & Population Story", page_icon="📊", layout="wide")

st.title("Berlin Housing & Population — Story")
st.caption("Explore the Story published on Tableau Public.")

# --- Tableau Public URL for Story ---
STORY_URL = (
    "https://public.tableau.com/views/berlin_dashboard/"
    "BerlinHousingPopulation?:showVizHome=no&:embed=true"
)

# --- Helper to render a responsive iframe ---
def render_tableau(url: str, height: int = 1100, aspect_ratio: float = 0.75):
    # aspect_ratio = height/width; 0.75 ~ 4:3, looks good for Tableau Public
    padding_pct = int(aspect_ratio * 100)
    responsive_iframe = f"""
    <div style="position: relative; padding-bottom: {padding_pct}%; height: 0; overflow: hidden; width: 100%;">
      <iframe src="{url}" frameborder="0" allowfullscreen
              style="position: absolute; top:0; left:0; width:100%; height:100%; border:none;"></iframe>
    </div>
    """
    html(responsive_iframe, height=height)

# --- UI ---
st.subheader("Berlin Housing & Population — Story")
render_tableau(STORY_URL)
st.markdown(f"[Open Story in Tableau Public ↗]({STORY_URL})")