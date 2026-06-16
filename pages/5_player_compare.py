# pages/5_player_compare.py
import streamlit as st
import pandas as pd
from src.data_loader import load_lifetime
from src.features import combined_player_profile

st.set_page_config(layout="wide")
st.title("Player Comparison")

lifetime = load_lifetime()
name_col = None
for c in ["Player_Name","Player","player_name","player"]:
    if c in lifetime.columns:
        name_col = c
        break
players = sorted(lifetime[name_col].dropna().unique()) if name_col else []

col1, col2 = st.columns(2)
with col1:
    p1 = st.selectbox("Player 1", players, index=0 if players else None, key="p1")
with col2:
    p2 = st.selectbox("Player 2", players, index=1 if len(players)>1 else 0, key="p2")

if p1 and p2:
    prof1 = combined_player_profile(p1)
    prof2 = combined_player_profile(p2)

    table = [
        ("Total Runs", prof1.get("lifetime_runs",0), prof2.get("lifetime_runs",0)),
        ("Average", round(prof1.get("lifetime_avg",0),2), round(prof2.get("lifetime_avg",0),2)),
        ("Strike Rate", round(prof1.get("lifetime_sr",0),2), round(prof2.get("lifetime_sr",0),2)),
        ("IPL Runs", prof1.get("ipl_runs",0), prof2.get("ipl_runs",0)),
        ("IPL 4s", prof1.get("ipl_4s",0), prof2.get("ipl_4s",0)),
        ("IPL 6s", prof1.get("ipl_6s",0), prof2.get("ipl_6s",0)),
        ("IPL Wickets", prof1.get("ipl_wickets",0), prof2.get("ipl_wickets",0)),
        ("Economy", round(prof1.get("ipl_economy",0),2), round(prof2.get("ipl_economy",0),2)),
        ("Bowling Avg", round(prof1.get("ipl_bowling_avg",0),2), round(prof2.get("ipl_bowling_avg",0),2)),
        ("Bowling SR", round(prof1.get("ipl_bowling_sr",0),2), round(prof2.get("ipl_bowling_sr",0),2))
    ]

    df = pd.DataFrame(table, columns=["Stat", p1, p2])
    st.table(df.set_index("Stat"))
