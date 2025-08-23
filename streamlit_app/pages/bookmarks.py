# streamlit_app/pages/bookmarks.py
import streamlit as st
from utils.bookmarks import list_bookmarks, remove_bookmark, clear_bookmarks, to_json

st.set_page_config(page_title="Bookmarks", page_icon="⭐", layout="wide")
st.title("⭐ Bookmarked Subdistricts")

rows = list_bookmarks()
st.caption(f"You have **{len(rows)}** bookmarked subdistrict(s).")

if not rows:
    st.info("No bookmarks yet. Add some from the Recommender results or any Subdistrict Profile.")
else:
    # Simple table look
    # You can swap this for st.data_editor if you want inline editing
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

st.caption("Tip: use the back/forward buttons or the sidebar to navigate.")