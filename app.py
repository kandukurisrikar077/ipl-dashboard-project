# app.py
import streamlit as st

st.set_page_config(page_title="IPL Dashboard", layout="wide")

st.sidebar.title("IPL Dashboard Navigation")
st.sidebar.markdown("Use the sidebar to navigate to pages:")

# Streamlit will auto-detect pages/ directory. Provide a fallback landing link.
st.sidebar.markdown("- Home\n- Player Stats\n- Team Stats\n- Season Analysis\n- Player Comparison")
st.sidebar.markdown("---")
st.sidebar.markdown("Players (lifetime dataset)")

st.title("IPL Data Analytics & Visualization Dashboard")
st.markdown("Use the sidebar to open pages.")
