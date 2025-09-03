# Imports
import streamlit as st
import os
import base64
from utils.ui import render_footer, safe_switch, render_image, inject_responsive_css
from utils.home_copy import HOME_COPY

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
            Project by <a href="https://www.linkedin.com/in/dido-de-boodt/" target="_blank" style="color: white; text-decoration: underline;">Dido De Boodt</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True)

st.divider()
st.markdown("""**Where to live in Berlin** - Find the right district for you! Use the recommender, explore subdistrict profiles, or deep-dive into the Berlin Census with an interactive dashboard.""")
st.divider()

# Layout with image left and quick action buttons right
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

# How to Use part 1
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("""
    <div style='border: 2px solid #A50034; background-color: #A50034; padding: 8px; text-align: center; border-radius: 4px;'>
        <h2 style='color: white; margin: 0; font-size: 20px;'>How to use this web app</h2>
    </div>
    """,
    unsafe_allow_html=True)

    # Recommender
    st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)    
    st.markdown("<h3 style='color:#A50034;'>Recommender</h3>", unsafe_allow_html=True)
    st.markdown(HOME_COPY["recommender"])

    # Subdistrict Profiles
    st.markdown("<h3 style='color:#A50034;'>Subdistrict Profiles</h3>", unsafe_allow_html=True)
    st.markdown(HOME_COPY["subdistrict_profiles"])

# Image Berlin Bear Explorer    
with col_right:
    render_image(os.path.join(os.path.dirname(__file__), "images", "bear_explorer.png"))

st.divider()

col_left, col_right = st.columns([2, 1])

# How to use part 2
with col_left:
    # Cencus
    st.markdown("<h3 style='color:#A50034;'>Berlin Census</h3>", unsafe_allow_html=True)
    st.markdown(HOME_COPY["census"])

    # Behind the data
    st.markdown("<h3 style='color:#A50034;'>Behind the data</h3>", unsafe_allow_html=True)
    st.markdown(HOME_COPY["data"])

    # Bookmarks
    st.markdown("<h3 style='color:#A50034;'>Q&A and Bookmarks</h3>", unsafe_allow_html=True)
    st.markdown(HOME_COPY["bookmarks"])

# Image Berlin Bear in the city   
with col_right:
        render_image(os.path.join(os.path.dirname(__file__), "images", "bear_city.png"))

st.divider()

# Data Sources
col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("""
        <div style='border: 2px solid #A50034; background-color: #A50034; padding: 8px; text-align: center; border-radius: 4px;'>
            <h2 style='color: white; margin: 0; font-size: 20px;'>Data Sources</h2>
        </div>
        """,
        unsafe_allow_html=True)
    st.markdown("")
    st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)
    st.markdown(HOME_COPY["datasources"])

# Image Berlin Bear Data Analyst
with col_right:
    render_image(os.path.join(os.path.dirname(__file__), "images", "bear_analyst.png"))

st.divider()

col_left, col_right = st.columns([2, 1])
with col_left:
    # Tools 
    st.markdown("""
    <div style='border: 2px solid #A50034; background-color: #A50034; padding: 8px; text-align: center; border-radius: 4px;'>
        <h2 style='color: white; margin: 0; font-size: 20px;'>Tools</h2>
    </div>
    """,
    unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)    
    st.markdown(HOME_COPY["tools"])
    st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)

    # Images Credits
    st.markdown("""
    <div style='border: 2px solid #A50034; background-color: #A50034; padding: 8px; text-align: center; border-radius: 4px;'>
        <h2 style='color: white; margin: 0; font-size: 20px;'>Images</h2>
    </div>
    """,
    unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)
    st.markdown(HOME_COPY["images"])

st.divider()

# Image Berlin Bear Data Scientist
with col_right:
    render_image(os.path.join(os.path.dirname(__file__), "images", "bear_python.png"))

render_footer()
