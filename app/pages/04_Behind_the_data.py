# Imports
import streamlit as st
import os, sys
import io, base64
from PIL import Image
from utils.ui import inject_responsive_css, render_cluster_legend

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Page configurations
icon_path = os.path.join(PROJECT_ROOT, "streamlit_app", "images", "icon.png")
st.set_page_config(
    page_title="Berlin Housing - Data",
    page_icon=icon_path,
    layout="wide",
)
# CSS
inject_responsive_css()

# UI
st.markdown("""
    <div style="border: 2px solid #A50034; background-color: #A50034; color: white; text-align: center; padding: 10px; border-radius: 8px;">
        <h1>Behind the Data</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)
st.markdown(
    """
    This page highlights key insights from the **exploratory data analysis (EDA)** that shaped the Berlin housing recommender. 
    The following visualizations reveal patterns in affordability, income, and neighborhood clusters, providing the foundation for the recommendations.
    """
    )

# Clusters viz
st.markdown("<h3 style='color:#A50034;'>KMeans Clustering (4 clusters)</h3>", unsafe_allow_html=True)
render_cluster_legend()
img_path = os.path.join(os.path.dirname(__file__), "..", "charts", "kmeans_k4.png")
kmeans_img = Image.open(img_path)
base_width = 800
w_percent = base_width / float(kmeans_img.size[0])
h_size = int((float(kmeans_img.size[1]) * float(w_percent)))
kmeans_img = kmeans_img.resize((base_width, h_size))
buf = io.BytesIO()
kmeans_img.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode()
st.markdown(
    f"<div style='text-align:center;'><img src='data:image/png;base64,{b64}'/></div>",
    unsafe_allow_html=True
)
st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)
st.caption("Visualization of KMeans clustering with k=4, showing how neighborhoods group together based on housing and socioeconomic features.")

# Cluster Features Dropdown
st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)
cluster_features_options = {
    "Total Population": ("total_population.png", "Cluster comparison by Total Population"),
    "Average Mietspiegel": ("mietspiegel.png", "Cluster comparison by Average Mietspiegel"),
    "Median Income": ("median_income.png", "Cluster comparison by Median Income"),
}
selected_feature = st.selectbox(
    "Cluster Features",
    list(cluster_features_options.keys()),
    key="cluster_features"
)
feature_img, feature_caption = cluster_features_options[selected_feature]
st.image(os.path.join(os.path.dirname(__file__), "..", "charts", feature_img), use_container_width=True)
st.caption(feature_caption)

# Amenities Dropdown
st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
amenities_options = {
    "Green Spaces": ("green_spaces.png", "Cluster comparison by Green Spaces"),
    "Bars": ("bars.png", "Cluster comparison by Bars"),
    "Cafes": ("cafes.png", "Cluster comparison by Cafes"),
    "Restaurants": ("restaurants.png", "Cluster comparison by Restaurants"),
    "Nightclubs": ("nightclubs.png", "Cluster comparison by Nightclubs"),
}
selected_amenity = st.selectbox(
    "Amenities",
    list(amenities_options.keys()),
    key="amenities"
)
amenity_img, amenity_caption = amenities_options[selected_amenity]
st.image(os.path.join(os.path.dirname(__file__), "..", "charts", amenity_img), use_container_width=True)
st.caption(amenity_caption)
st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)
st.divider()

# Affordability class distribution
st.markdown("<h3 style='color:#A50034;'>Affordability Classification Distribution</h3>", unsafe_allow_html=True)
st.image(os.path.join(os.path.dirname(__file__), "..", "charts", "distribution_mietspiegel_class.png"), use_container_width=True)
st.caption("The distribution of Affordability Classes across listings, showing the prevalence of different affordability categories.")
st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)
st.divider()

# Income vs Mietspiegel
st.markdown("<h3 style='color:#A50034;'>Income vs Mietspiegel</h3>", unsafe_allow_html=True)
st.image(os.path.join(os.path.dirname(__file__), "..", "charts", "income_vs_mietspiegel.png"), use_container_width=True)
st.caption("A scatterplot illustrating the relationship between household income and Mietspiegel, highlighting affordability gaps in certain neighborhoods.")
st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)
st.divider()