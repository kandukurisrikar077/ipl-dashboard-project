# pages/4_season_analysis.py
import streamlit as st
from src.features import season_top_batsmen, season_top_bowlers
from src.data_loader import load_matches

st.set_page_config(layout="wide")
st.title("Season Analysis")

matches = load_matches()
seasons = sorted(matches["season"].dropna().unique())
season = st.selectbox("Select Season", seasons, index=len(seasons)-1 if seasons else 0)

if season:
    st.subheader(f"Top Batsmen in {season}")
    tb = season_top_batsmen(season, top_n=10)
    st.table(tb.set_index("Player"))

    st.subheader(f"Top Bowlers in {season}")
    tw = season_top_bowlers(season, top_n=10)
    st.table(tw.set_index("Player"))
