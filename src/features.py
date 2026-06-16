# src/features.py
import pandas as pd
from src.data_loader import load_lifetime, load_deliveries, load_matches
from functools import lru_cache

@lru_cache(maxsize=1)
def batsman_aggregates(deliveries: pd.DataFrame = None):
    """
    Return aggregated batting stats across all deliveries.
    Useful for IPL runs/4s/6s, etc.
    """
    if deliveries is None:
        deliveries = load_deliveries()
    # total runs by batsman
    agg = deliveries.groupby("batsman", dropna=True).agg(
        ipL_runs=("batsman_runs", "sum"),
        balls=("ball", "count"),  # approximate; depends if ball column present
        fours=("batsman_runs", lambda s: (s==4).sum()),
        sixes=("batsman_runs", lambda s: (s==6).sum())
    ).reset_index().rename(columns={"batsman":"Player"})
    return agg

@lru_cache(maxsize=1)
def bowler_aggregates(deliveries: pd.DataFrame = None, matches: pd.DataFrame = None):
    """
    Return aggregated bowling stats: wickets, runs conceded, overs (approx), economy, avg, strike rate
    """
    if deliveries is None:
        deliveries = load_deliveries()
    # wickets: count of non-null player_dismissed for deliveries (and dismissal_kind not null)
    # Note: some dismissals may be runouts with bowler not credited; we count only where 'player_dismissed' is present
    w = deliveries[deliveries["player_dismissed"].notna() & (deliveries["player_dismissed"] != "")]
    wickets = w.groupby("bowler").size().reset_index(name="wickets")

    runs_conceded = deliveries.groupby("bowler").agg(runs_conceded=("total_runs", "sum"),
                                                      balls_bowled=("ball", "count")).reset_index()
    df = runs_conceded.merge(wickets, left_on="bowler", right_on="bowler", how="left").fillna(0)
    df["overs"] = (df["balls_bowled"] // 6) + (df["balls_bowled"] % 6) / 6.0
    # avoid division by zero
    df["economy"] = df.apply(lambda r: r["runs_conceded"]/ (r["balls_bowled"]/6) if r["balls_bowled"]>0 else 0, axis=1)
    df["bowling_avg"] = df.apply(lambda r: r["runs_conceded"]/r["wickets"] if r["wickets"]>0 else 0, axis=1)
    df["strike_rate"] = df.apply(lambda r: (r["balls_bowled"]/r["wickets"]) if r["wickets"]>0 else 0, axis=1)
    df = df.rename(columns={"bowler":"Player"})
    return df[["Player","wickets","runs_conceded","balls_bowled","overs","economy","bowling_avg","strike_rate"]]

def combined_player_profile(player_name: str):
    """
    Returns a dictionary with combined stats for a single player (batting + IPL stats + bowling if any)
    """
    lifetime = load_lifetime()
    deliveries = load_deliveries()

    out = {"player_name": player_name}
    # standardize lookup: lifetime file may have 'Player_Name' or 'Player' etc. We'll try common names
    lifetime_cols = [c.lower() for c in lifetime.columns]
    # attempt to locate player row in lifetime df
    player_col = None
    for col in ["player_name","player","Player_Name","Player"]:
        if col in lifetime.columns:
            player_col = col
            break

    if player_col:
        p_row = lifetime[lifetime[player_col].str.lower() == player_name.lower()]
        if not p_row.empty:
            r = p_row.iloc[0]
            # pick some common lifetime columns safely
            out["lifetime_runs"] = float(r.get("Runs", r.get("runs", r.get("Total_Runs", r.get("total_runs", 0)))))
            out["lifetime_avg"] = float(r.get("Average", r.get("avg", r.get("Average_Runs", 0))))
            out["lifetime_sr"] = float(r.get("Strike_Rate", r.get("SR", 0)))
            out["lifetime_centuries"] = int(r.get("100s", r.get("centuries", 0)))
        else:
            out["lifetime_runs"] = out["lifetime_avg"] = out["lifetime_sr"] = 0
            out["lifetime_centuries"] = 0
    else:
        out["lifetime_runs"] = out["lifetime_avg"] = out["lifetime_sr"] = 0
        out["lifetime_centuries"] = 0

    # IPL real stats from deliveries
    d = deliveries
    # batting
    bat = d[d["batsman"].str.lower() == player_name.lower()]
    out["ipl_runs"] = int(bat["batsman_runs"].sum())
    out["ipl_balls"] = int(bat.shape[0])
    out["ipl_4s"] = int((bat["batsman_runs"]==4).sum())
    out["ipl_6s"] = int((bat["batsman_runs"]==6).sum())
    out["ipl_strike"] = round((out["ipl_runs"] / out["ipl_balls"] * 100) if out["ipl_balls"]>0 else 0, 2)

    # bowling
    bowl = d[d["bowler"].str.lower() == player_name.lower()]
    wickets = bowl[bowl["player_dismissed"].notna() & (bowl["player_dismissed"]!="")].shape[0]
    balls = bowl.shape[0]
    runs_conceded = bowl["total_runs"].sum() if "total_runs" in bowl.columns else bowl["batsman_runs"].sum()
    overs = (balls // 6) + (balls % 6)/6.0
    economy = round(runs_conceded / (balls/6) ,2) if balls>0 else 0
    bowling_avg = round(runs_conceded / wickets,2) if wickets>0 else 0
    bowling_sr = round(balls / wickets,2) if wickets>0 else 0

    out["ipl_wickets"] = int(wickets)
    out["ipl_balls_bowled"] = int(balls)
    out["ipl_runs_conceded"] = int(runs_conceded)
    out["ipl_overs"] = round(overs,2)
    out["ipl_economy"] = round(economy,2)
    out["ipl_bowling_avg"] = bowling_avg
    out["ipl_bowling_sr"] = bowling_sr

    return out

def top_batsmen_overall(top_n=10):
    deliveries = load_deliveries()
    agg = deliveries.groupby("batsman", dropna=True)["batsman_runs"].sum().reset_index()
    agg = agg.rename(columns={"batsman":"Player", "batsman_runs":"Runs"})
    return agg.sort_values("Runs", ascending=False).head(top_n)

def top_bowlers_overall(top_n=10):
    deliveries = load_deliveries()
    w = deliveries[deliveries["player_dismissed"].notna() & (deliveries["player_dismissed"]!="")]
    agg = w.groupby("bowler").size().reset_index(name="Wickets")
    agg = agg.rename(columns={"bowler":"Player"})
    return agg.sort_values("Wickets", ascending=False).head(top_n)

def season_top_batsmen(season, top_n=10):
    matches = load_matches()
    deliveries = load_deliveries()
    # merge on match_id
    merged = deliveries.merge(matches[["id","season"]].rename(columns={"id":"match_id"}), on="match_id", how="left")
    s = merged[merged["season"]==season]
    agg = s.groupby("batsman")["batsman_runs"].sum().reset_index().rename(columns={"batsman":"Player","batsman_runs":"Runs"})
    return agg.sort_values("Runs", ascending=False).head(top_n)

def season_top_bowlers(season, top_n=10):
    matches = load_matches()
    deliveries = load_deliveries()
    merged = deliveries.merge(matches[["id","season"]].rename(columns={"id":"match_id"}), on="match_id", how="left")
    s = merged[merged["season"]==season]
    w = s[s["player_dismissed"].notna() & (s["player_dismissed"]!="")]
    agg = w.groupby("bowler").size().reset_index(name="Wickets").rename(columns={"bowler":"Player"})
    return agg.sort_values("Wickets", ascending=False).head(top_n)
