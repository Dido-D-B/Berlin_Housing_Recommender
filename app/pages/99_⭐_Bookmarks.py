# Imports
import os, sys
import streamlit as st
from utils.bookmarks import list_bookmarks, remove_bookmark, clear_bookmarks, to_json
from utils.ui import render_footer, inject_responsive_css

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Page Configurations
st.set_page_config(
    page_title="Berlin Housing - Bookmarks",
    page_icon='⭐',
    layout="wide",
)

# CSS
inject_responsive_css()

# UI
st.markdown(
    """
    <div style='border: 3px solid #A50034; background-color: #A50034; padding: 15px; text-align: center; border-radius: 6px;'>
        <h1 style='color: white; margin: 0;'>Bookmarked Subdistricts</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

rows = list_bookmarks()
st.caption(f"You have **{len(rows)}** bookmarked subdistrict(s).")

if not rows:
    st.markdown(
        """
        <div style='background-color: #f5f5f5; padding: 12px; border-radius: 6px; border: 1px solid #ddd;'>
            No bookmarks yet. Add some from the <a href='/Recommender' target='_self' style='color:#A50034; text-decoration:none; font-weight:bold;'>Recommender</a> results.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Simple table look
    headers = ["Bezirk", "Subdistrict", "Cluster", "Est. Monthly Rent (€)", "Actions"]
    st.write("")

    for entry in rows:
        key = entry["key"]
        bezirk = entry.get("bezirk", "")
        subdistrict = entry.get("subdistrict", "")
        meta = entry.get("meta", {}) or {}

        cluster = meta.get("cluster", "—")
        rent = meta.get("est_monthly_rent", "—")

        cols = st.columns([2, 3, 2, 2, 2])
        cols[0].markdown(f"**{bezirk}**")
        cols[1].markdown(f"{subdistrict}")
        cols[2].markdown(f"{cluster}")
        cols[3].markdown(f"{rent}")
        with cols[4]:
            if st.button("Remove", key=f"rm_{key}", use_container_width=True):
                remove_bookmark(key)
                st.rerun()

    st.divider()
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("🗑️ Clear all bookmarks", type="secondary"):
            clear_bookmarks()
            st.rerun()
    with c2:
        st.download_button(
            "⬇️ Export as JSON",
            data=to_json(),
            file_name="berlin_bookmarks.json",
            mime="application/json",
        )
        
render_footer()