# pages/1_home.py
import streamlit as st
from src.data_loader import load_lifetime
from src.features import top_batsmen_overall, top_bowlers_overall

st.set_page_config(layout="wide")
st.title("🔥 Most Active Players in IPL 🔥")

lifetime = load_lifetime()

st.sidebar.markdown("### IPL Dashboard Navigation")
st.sidebar.write(f"Players (lifetime dataset) \n\n {lifetime.shape[0]}")

st.header("Quick Top Lists")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Lifetime Batsmen (by IPL runs)")
    tb = top_batsmen_overall(10)
    st.table(tb.rename(columns={"Player":"Player","Runs":"Runs"}).set_index("Player"))

with col2:
    st.subheader("Top Lifetime Bowlers (by wickets)")
    tb2 = top_bowlers_overall(10)
    st.table(tb2.set_index("Player"))
