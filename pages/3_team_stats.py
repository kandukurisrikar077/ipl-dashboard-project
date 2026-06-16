# pages/3_team_stats.py
import streamlit as st
from src.data_loader import load_matches, load_deliveries

st.set_page_config(layout="wide")
st.title("Team Stats")

matches = load_matches()
deliveries = load_deliveries()

st.write("Basic team-level stats (matches & runs).")
# runs per team across deliveries
team_runs = deliveries.groupby("batting_team")["total_runs"].sum().reset_index().rename(columns={"batting_team":"Team","total_runs":"Runs"})
st.table(team_runs.sort_values("Runs", ascending=False).head(20).set_index("Team"))
