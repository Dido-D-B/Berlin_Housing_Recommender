import streamlit as st
import pandas as pd

def show_results(df: pd.DataFrame):
    if df.empty:
        st.info("No results for the current settings.")
        return
    for _, r in df.iterrows():
        with st.container(border=True):
            st.subheader(f"{r.get('ortsteil','?').title()} ({r.get('bezirk','?').title()})")
            st.write(
                f"Cluster: **{r.get('k4_cluster','?')}** · "
                f"€/{r.get('aff_rent_per_m2',0):.2f}/m² · "
                f"Rent-to-income: **{r.get('aff_rent_to_income',0):.1%}**"
            )
            note = r.get("_note")
            if note and note != "exact_match":
                st.caption(f"Note: {note.replace('_',' ')}")