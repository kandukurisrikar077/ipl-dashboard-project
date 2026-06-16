# pages/2_player_stats.py
import streamlit as st
from src.features import combined_player_profile
from src.data_loader import load_lifetime

st.set_page_config(layout="wide")
st.title("Player Statistics")

lifetime = load_lifetime()
# pick name column
name_col = None
for c in ["Player_Name","Player","player_name","player"]:
    if c in lifetime.columns:
        name_col = c
        break
players = sorted(lifetime[name_col].dropna().unique()) if name_col else []

player = st.selectbox("Select Player", players, index=0 if players else None)

if player:
    prof = combined_player_profile(player)
    st.subheader(prof["player_name"])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Runs", f"{prof.get('lifetime_runs',0)}")
    col2.metric("Average", f"{round(prof.get('lifetime_avg',0),2)}")
    col3.metric("Strike Rate", f"{round(prof.get('lifetime_sr',0),2)}")
    col4.metric("Centuries", f"{prof.get('lifetime_centuries',0)}")

    st.markdown("---")
    st.subheader("IPL Real Stats")
    b1,b2,b3,b4 = st.columns(4)
    b1.metric("IPL Runs", f"{prof.get('ipl_runs',0)}")
    b2.metric("Balls", f"{prof.get('ipl_balls',0)}")
    b3.metric("4s", f"{prof.get('ipl_4s',0)}")
    b4.metric("6s", f"{prof.get('ipl_6s',0)}")

    st.markdown("---")
    st.subheader("IPL Bowling Stats")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Wickets", f"{prof.get('ipl_wickets',0)}")
    c2.metric("Overs", f"{prof.get('ipl_overs',0)}")
    c3.metric("Economy", f"{round(prof.get('ipl_economy',0),2)}")
    c4.metric("Bowling Avg", f"{round(prof.get('ipl_bowling_avg',0),2)}")
