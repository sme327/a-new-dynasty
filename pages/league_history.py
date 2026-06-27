"""League History — The Evolution of A New Dynasty."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.data import (
    load_all, get_champions, get_all_time_manager_stats,
    MANAGER_EMOJI, MANAGER_COLORS, FOUNDED, CURRENT_SEASON,
)
from utils.styles import inject_css, render_nav, render_page_footer, html_table

st.set_page_config(
    page_title="League History · A New Dynasty",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("league_history")

data       = load_all()
champions  = get_champions()
standings  = data["standings"]
wm         = data["matchups"]
tnh        = data["team_name_history"]
_tnh_lkp   = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

# ── PRE-COMPUTE ────────────────────────────────────────────────────────────────
season_scoring = (
    standings.groupby("season")["points_for"]
    .agg(avg="mean", high="max", low="min")
    .reset_index().sort_values("season")
)

_rs_all  = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy() if not wm.empty else pd.DataFrame()
_std_all = standings.copy()
_std_all["gp"]  = _std_all["wins"] + _std_all["losses"] + _std_all["ties"]
_std_all["wpc"] = _std_all["wins"] / _std_all["gp"].replace(0, float("nan"))

total_seasons = CURRENT_SEASON - FOUNDED + 1

# ── PAGE HEADER ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="tl-page-title">The Evolution of the League</div>
    <div class="tl-page-subtitle">
        {FOUNDED}–{CURRENT_SEASON} &nbsp;·&nbsp; {total_seasons} Seasons &nbsp;·&nbsp;
        One keeper league. Built to last.
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── LEAGUE SUMMARY ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">At a Glance</div>'
    '<div class="tl-section-title">The League in Numbers</div>',
    unsafe_allow_html=True,
)

unique_champs  = int(champions["champion_manager"].nunique()) if not champions.empty else 0
total_managers = tnh["canonical_name"].nunique()
active_mgrs    = int((data["managers"]["last_season"] == CURRENT_SEASON).sum())

n1, n2, n3, n4 = st.columns(4)
from utils.styles import metric_card
with n1:
    st.markdown(metric_card(str(total_seasons), "Seasons Played"), unsafe_allow_html=True)
with n2:
    st.markdown(metric_card(str(total_managers), "Total Managers"), unsafe_allow_html=True)
with n3:
    st.markdown(metric_card(str(unique_champs), "Unique Champions"), unsafe_allow_html=True)
with n4:
    st.markdown(metric_card(str(active_mgrs), "Active Members"), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── YEAR-BY-YEAR SNAPSHOT ──────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Season by Season</div>'
    '<div class="tl-section-title">Year-by-Year Snapshot</div>',
    unsafe_allow_html=True,
)

szn_rows = []
for _, szn_row in season_scoring.sort_values("season", ascending=False).iterrows():
    szn = int(szn_row["season"])
    champ_row = champions[champions["season"] == szn] if not champions.empty else pd.DataFrame()
    champ_str = champ_row.iloc[0]["champion_manager"] if len(champ_row) > 0 else "—"
    champ_e   = MANAGER_EMOJI.get(champ_str, "🏆")
    high_std  = _std_all[_std_all["season"] == szn].sort_values("wins", ascending=False)
    best_rec  = f"{int(high_std.iloc[0]['wins'])}-{int(high_std.iloc[0]['losses'])}" if len(high_std) > 0 else "—"
    best_mgr  = _tnh_lkp.get((szn, high_std.iloc[0]["team_name"]), "—") if len(high_std) > 0 else "—"
    szn_rows.append([
        (str(szn), "gold"),
        f"{champ_e} {champ_str}",
        f"{float(szn_row['avg']):.1f}",
        f"{float(szn_row['high']):.1f}",
        f"{best_mgr} ({best_rec})",
    ])

st.markdown(
    html_table(["Season", "Champion", "Avg Score", "High Score", "Best Record"], szn_rows),
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SCORING TRENDS ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">How the League Has Changed</div>'
    '<div class="tl-section-title">Scoring Trends</div>',
    unsafe_allow_html=True,
)

try:
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=season_scoring["season"], y=season_scoring["high"],
        name="Season High", mode="lines+markers",
        line=dict(color="#D4AF37", width=2),
        marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=season_scoring["season"], y=season_scoring["avg"],
        name="League Avg", mode="lines+markers",
        line=dict(color="#3FA66B", width=2, dash="dot"),
        marker=dict(size=5),
    ))
    fig.add_trace(go.Scatter(
        x=season_scoring["season"], y=season_scoring["low"],
        name="Season Low", mode="lines+markers",
        line=dict(color="#F87171", width=1, dash="dash"),
        marker=dict(size=4),
    ))
    fig.update_layout(
        paper_bgcolor="#07120D", plot_bgcolor="#07120D",
        font=dict(family="Inter", color="#B8C3B5", size=11),
        xaxis=dict(tickmode="array", tickvals=list(season_scoring["season"]), gridcolor="#1A3525", color="#B8C3B5"),
        yaxis=dict(gridcolor="#1A3525", color="#B8C3B5"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#B8C3B5")),
        margin=dict(l=10, r=10, t=20, b=10),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)
except ImportError:
    st.info("Install plotly to see scoring trend charts.")

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── KEEPER COST TRENDS ────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">The Keeper Economy</div>'
    '<div class="tl-section-title">Keeper Spending Over Time</div>',
    unsafe_allow_html=True,
)

draft = data.get("draft")
if draft is not None and not draft.empty:
    keepers_by_yr = (
        draft[draft["is_keeper"] == True]
        .groupby("season")
        .agg(
            count=("player_name", "count"),
            total_spend=("auction_price", "sum"),
            avg_cost=("auction_price", "mean"),
            max_cost=("auction_price", "max"),
        )
        .reset_index()
        .sort_values("season")
    )

    if not keepers_by_yr.empty:
        k_rows = []
        for _, row in keepers_by_yr.sort_values("season", ascending=False).iterrows():
            k_rows.append([
                (str(int(row["season"])), "gold"),
                str(int(row["count"])),
                (f"${int(row['total_spend']):,}", "gold"),
                f"${float(row['avg_cost']):.1f}",
                (f"${int(row['max_cost'])}", ""),
            ])
        st.markdown(
            html_table(["Season", "Keepers", "Total Spend", "Avg Cost", "Most Expensive"], k_rows),
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── MANAGER LEADERBOARD ───────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">All-Time</div>'
    '<div class="tl-section-title">Manager Leaderboard</div>',
    unsafe_allow_html=True,
)

stats = get_all_time_manager_stats()
if not stats.empty:
    lb_rows = []
    for rank_i, (_, row) in enumerate(stats.iterrows(), 1):
        mgr   = row["canonical_name"]
        emoji = MANAGER_EMOJI.get(mgr, "👤")
        champs_str = "🏆" * int(row["championships"]) if row["championships"] > 0 else "—"
        lb_rows.append([
            (f"#{rank_i}", "gold" if rank_i <= 3 else "muted"),
            f"{emoji} {mgr}",
            (champs_str, "gold"),
            str(int(row["seasons"])),
            str(int(row["playoff_apps"])),
            f"{int(row['rs_wins'])}-{int(row['rs_losses'])}",
            f"{float(row['rs_pf']):,.1f}",
        ])
    st.markdown(
        html_table(["Rank", "Manager", "Titles", "Seasons", "Playoffs", "RS Record", "RS Points"], lb_rows),
        unsafe_allow_html=True,
    )

render_page_footer(
    href="/manager_profiles",
    cta="EXPLORE MANAGER PROFILES",
    tagline="THE HISTORY.<br>THE DATA.<br>THE LEGACY.",
)
