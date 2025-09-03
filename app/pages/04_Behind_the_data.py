# Imports
import streamlit as st
import os, sys
import io, base64
from PIL import Image
from utils.ui import inject_responsive_css, render_cluster_legend, render_footer

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Page configurations
icon_path = os.path.join(PROJECT_ROOT, "app", "images", "icon.png")
st.set_page_config(
    page_title="Berlin Housing - The Data",
    page_icon=icon_path,
    layout="wide",
)
# CSS
inject_responsive_css()

# UI
st.markdown(
    """
    <div style='border: 3px solid #A50034; background-color: #A50034; padding: 15px; text-align: center; border-radius: 6px;'>
        <h1 style='color: white; margin: 0;'>Behind the Data</h1>
        <p style='color: white; margin: 5px 0 0; font-size: 14px;'>
            Project by <a href="https://www.linkedin.com/in/dido-de-boodt/" target="_blank" style="color: white; text-decoration: underline;">Dido De Boodt</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True)

st.divider()
st.markdown("""**How were the subdistrict profiles created?** - Explore key insights from the exploratory data analysis, the clustering method, and cluster to profile mapping.""")
st.divider()

# Key Insights from the EDA
st.markdown("<h3 style='color:#A50034;'>Key Insights from the EDA</h3>", unsafe_allow_html=True)
st.markdown(
    """
Before applying clustering, we conducted an **exploratory data analysis (EDA)** of Berlin’s districts and subdistricts to understand
**distributions, correlations, and standout patterns** in housing, income, amenities, and density. Here are the main takeaways.
    """
)

# Small helper to render images consistently like the KMeans viz
def _display_image_centered(img_path: str, caption: str | None = None, base_width: int = 800):
    try:
        if not os.path.exists(img_path):
            st.info(f"(Visualization not available at: {os.path.basename(img_path)})")
            return
        img = Image.open(img_path)
        w_percent = base_width / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/png;base64,{b64}' title='{caption or ''}'/></div>",
            unsafe_allow_html=True,
        )
    except Exception:
        st.info("(Could not render image.)")

st.markdown(
        """
* **Rents vs. Income**: Clear disparities exist between median income levels and average rents per square meter across districts. Central districts (e.g. Mitte, Friedrichshain-Kreuzberg) show higher rents while peripheral districts (e.g. Marzahn-Hellersdorf, Spandau) remain more affordable relative to income.
* **Population Distribution**: Districts vary strongly in population size and density, with outer districts covering larger areas but housing fewer residents per km². This distinction highlights different urban dynamics between dense inner-city areas and suburban-style outer areas.
* **Socioeconomic Indicators**: Employment, income, and building stock show significant variance. For instance, Mitte concentrates economic activity, while districts such as Neukölln and Lichtenberg reflect more mixed socioeconomic profiles.
* **High Variation Within districts**: Even within the same district, subdistricts vary strongly in rent, income, and demographic composition.
* **Affordability Hotspots**: Certain subdistricts emerge as relatively affordable despite being located in otherwise expensive districts.
* **Population Structure**: Younger populations cluster in inner-city, vibrant areas, while outer districts often have higher shares of seniors.
* **Amenities & Services**: POI data (amenities) shows stark contrasts in access to cafes, bars, libraries, and green spaces, shaping neighborhood attractiveness.
* **Feature Correlations**: Some features are strongly correlated (population vs. households), but others (e.g., POIs vs. income) add complementary information.
        """
    )

st.markdown(
        """
Comparing **income** against **Mietspiegel** highlights neighborhoods where typical rent levels may exceed what local
median incomes would comfortably support — an **affordability gap** that motivated our profile naming and recommendations.
        """
    )
_display_image_centered(
        os.path.join(os.path.dirname(__file__), "..", "charts", "income_vs_mietspiegel.png"),
        caption="Income vs. Mietspiegel: visualizing potential affordability tension in some neighborhoods.",
        base_width=800,
    )

st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)
st.divider()

# Kmeans
st.markdown("<h3 style='color:#A50034;'>KMeans Clustering (4 clusters)</h3>", unsafe_allow_html=True)
st.write("**How we clustered Berlin's Subdistricts** — We standardized features (so each feature contributes fairly), ran K-Means on the engineered dataset, and picked **k = 4** using a combination of the **elbow** and **silhouette** methods. We then interpreted each cluster’s typical feature levels (rent, income, POIs, etc.) to name the profiles you see across the app.")

# k=4 viz with legend
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
caption_text = "Visualization of KMeans clustering with k=4, showing how neighborhoods group together based on housing and socioeconomic features."
st.markdown(
    f"<div style='text-align:center;'><img src='data:image/png;base64,{b64}' title='{caption_text}'/></div>",
    unsafe_allow_html=True
)
st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)

# Kmeans explanation
with st.expander("💡 What is K-Means?"):
    st.markdown(
        """
        **K-Means** is an unsupervised clustering algorithm that groups similar sub-districts together.  
        It works by:
        1) placing **k** centroids,  
        2) assigning each row (Ortsteil) to its nearest centroid (by distance),  
        3) recomputing centroids from assigned members, and  
        4) repeating until assignments stabilize.

        Because K-Means uses distances, we **standardize** features first (z-scores) so high-variance columns don’t dominate the result.
        """
    )

# Optimal k selection
st.markdown(
        """
        We evaluated several values of **k** (2–10) and looked at two complementary diagnostics:

        - **Elbow (inertia/WCSS):** gains flatten around **k ≈ 4**, meaning extra clusters bring diminishing returns.  
        - **Silhouette score:** separation/compactness is competitive around **k = 4**, while keeping clusters interpretable and sufficiently sized.

        Balancing **fit quality** and **interpretability**, we selected **k = 4**.  
        """
    )

# Show Elbow optimal k and silhouette score plots
if "show_plots" not in st.session_state:
    st.session_state["show_plots"] = False

toggle_label = "X Hide Elbow and Silhouette score plots" if st.session_state["show_plots"] else "✓ Show Elbow and Silhouette score plots"
if st.button(toggle_label, key="toggle_plots"):
    st.session_state["show_plots"] = not st.session_state["show_plots"]
    st.rerun()

if st.session_state["show_plots"]:
    elbow_path = os.path.join(os.path.dirname(__file__), "..", "charts", "elbow.png")
    silhouette_path = os.path.join(os.path.dirname(__file__), "..", "charts", "silhouette.png")
    for img_path, caption in [
        (elbow_path, "Elbow Method Plot: Shows inertia (within-cluster sum of squares) vs. k."),
        (silhouette_path, "Silhouette Score Plot: Shows average silhouette scores for different k."),
    ]:
        img = Image.open(img_path)
        base_width = 600
        w_percent = base_width / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/png;base64,{b64}' title='{caption}'/></div>",
            unsafe_allow_html=True
        )

st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
st.divider()

# Building the cluster profiles
st.markdown("<h3 style='color:#A50034;'>From Clusters to Profiles</h3>", unsafe_allow_html=True)
st.markdown(
    """
**How we turned clusters into profiles** — After fitting K‑Means (k=4), we profiled each cluster by comparing its
**standardized feature means**. We looked for consistent patterns across affordability and amenity intensity to craft human‑readable names.
    """
)

with st.expander("💡 Naming the clusters"):
    st.markdown(
        """
- **Affordable** → *Lower rent indicators* (below‑avg Mietspiegel z) with *low‑to‑mid income* and *moderate amenities*.
- **Vibrant** → *High amenity density* (cafés/bars/nightlife) with *mid rents* and *mid‑to‑high income*.
- **Balanced** → *Mid rents*, *mid income*, and *mixed amenities* (the ‘middle ground’ cluster).
- **Prestige** → *High rent indicators* with *high income*, often *amenity‑rich cores* or *prime locations*.

These labels are **summaries** of typical feature levels, not rules for every single sub‑district.
        """
    )

# Cluster Features Dropdown
st.write("Below you can explore key features and amenities accross the clusters. This analysis was part of what shaped the cluster profiles.")
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
feature_img_path = os.path.join(os.path.dirname(__file__), "..", "charts", feature_img)
img = Image.open(feature_img_path)
base_width = 800
w_percent = base_width / float(img.size[0])
h_size = int((float(img.size[1]) * float(w_percent)))
img = img.resize((base_width, h_size))
buf = io.BytesIO()
img.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode()
st.markdown(
    f"<div style='text-align:center;'><img src='data:image/png;base64,{b64}' title='{feature_caption}'/></div>",
    unsafe_allow_html=True
)

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
amenity_img_path = os.path.join(os.path.dirname(__file__), "..", "charts", amenity_img)
img = Image.open(amenity_img_path)
base_width = 800
w_percent = base_width / float(img.size[0])
h_size = int((float(img.size[1]) * float(w_percent)))
img = img.resize((base_width, h_size))
buf = io.BytesIO()
img.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode()
st.markdown(
    f"<div style='text-align:center;'><img src='data:image/png;base64,{b64}' title='{amenity_caption}'/></div>",
    unsafe_allow_html=True
)
st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)
render_footer()