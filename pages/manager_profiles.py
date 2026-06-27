"""Manager Profiles page — career history for every manager."""
from __future__ import annotations
import streamlit as st
from utils.data import (
    load_all, get_manager_stats, get_manager_season_history,
    get_manager_h2h, get_champions, get_all_time_manager_stats,
    MANAGER_EMOJI, MANAGER_COLORS, CURRENT_SEASON,
)
from utils.styles import inject_css, render_nav, render_page_footer, avatar_html, metric_card, html_table

st.set_page_config(
    page_title="Managers · A New Dynasty",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("manager_profiles")

data          = load_all()
manager_stats = get_manager_stats()
champions     = get_champions()

_as_champ = champions.groupby("champion_manager").size().rename("champs").reset_index().rename(columns={"champion_manager":"mgr"})
_as_ru    = champions.groupby("runner_up_manager").size().rename("runner_ups").reset_index().rename(columns={"runner_up_manager":"mgr"})
_finals   = _as_champ.merge(_as_ru, on="mgr", how="outer").fillna(0)
_finals["finals_apps"] = (_finals["champs"] + _finals["runner_ups"]).astype(int)
finals_rec = _finals.set_index("mgr")

# ── PAGE TITLE ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-page-title">Manager Profiles</div>
    <div class="tl-page-subtitle">Career records for every competitor in league history.</div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── MANAGER SELECTOR ───────────────────────────────────────────────────────────
active  = manager_stats[manager_stats["active"]]["canonical_name"].tolist()
former  = manager_stats[~manager_stats["active"]]["canonical_name"].tolist()
options = active + ["─── Former Members ───"] + former

selected = st.selectbox("SELECT MANAGER", options=options, index=0, format_func=lambda n: n)
if selected.startswith("───"):
    st.stop()

mgr_name = selected
st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── PROFILE HEADER ──────────────────────────────────────────────────────────────
mgr_row      = manager_stats[manager_stats["canonical_name"] == mgr_name].iloc[0]
emoji        = MANAGER_EMOJI.get(mgr_name, "👤")
is_active    = bool(mgr_row["active"])
status_label = f"Active · {mgr_row['first_season']}–Present" if is_active else f"{mgr_row['first_season']}–{mgr_row['last_season']}"

col_avatar, col_info = st.columns([1, 4])
with col_avatar:
    st.markdown(avatar_html(mgr_name, size=100), unsafe_allow_html=True)
with col_info:
    champ_str = "🏆 " * int(mgr_row["championships"]) if mgr_row["championships"] > 0 else ""
    st.markdown(
        f"""
        <div class="tl-profile-name">{mgr_row['display_name']}{' ' + champ_str if champ_str else ''}</div>
        <div class="tl-profile-meta">{status_label} · {int(mgr_row['seasons_played'])} Seasons</div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── CAREER METRICS ─────────────────────────────────────────────────────────────
w, l, t     = int(mgr_row["wins"]), int(mgr_row["losses"]), int(mgr_row["ties"])
total       = w + l + t
win_pct     = f"{mgr_row['win_pct']:.3f}" if total > 0 else ".000"
record_str  = f"{w}-{l}" + (f"-{t}" if t > 0 else "")
seasons_pld = int(mgr_row["seasons_played"])
plyf_apps   = int(mgr_row["playoff_apps"])
plyf_rate   = f"{plyf_apps/seasons_pld:.0%}" if seasons_pld > 0 else "0%"

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.markdown(metric_card(str(int(mgr_row["championships"])), "Championships"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card(str(int(mgr_row["runner_ups"])), "Runner-Up Finishes"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card(str(plyf_apps), "Playoff Appearances"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card(plyf_rate, "Playoff Rate"), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card(record_str, "RS Record"), unsafe_allow_html=True)
with c6:
    st.markdown(metric_card(win_pct, "Win Pct"), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SEASON-BY-SEASON HISTORY ───────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Career History</div>'
    '<div class="tl-section-title">Season by Season</div>',
    unsafe_allow_html=True,
)

season_hist = get_manager_season_history(mgr_name)
if not season_hist.empty:
    tbl_rows = []
    for _, row in season_hist.iterrows():
        result_str = str(row["Result"])
        result_style = ""
        if "Champion" in result_str:
            result_style = "gold"
        elif "Runner" in result_str:
            result_style = ""
        tbl_rows.append([
            (str(row["Season"]), "gold"),
            str(row["Team Name"]),
            f"{row['W']}-{row['L']}" + (f"-{row['T']}" if row.get("T",0) else ""),
            f"#{row['Rank']}" if row.get("Rank") else "—",
            f"{row['PF']:,.2f}",
            f"{row['PA']:,.2f}",
            (result_str, result_style),
        ])
    st.markdown(
        html_table(["Season", "Team Name", "Record", "Rank", "PF", "PA", "Result"], tbl_rows),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── HEAD-TO-HEAD BREAKDOWN ─────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Regular Season Only</div>'
    '<div class="tl-section-title">Head-to-Head Record</div>',
    unsafe_allow_html=True,
)

h2h = get_manager_h2h(mgr_name)
if not h2h.empty:
    dominated  = h2h[h2h["wins"] > h2h["losses"]].sort_values("win_pct", ascending=False)
    struggles  = h2h[h2h["losses"] > h2h["wins"]].sort_values("win_pct")
    even_games = h2h[h2h["wins"] == h2h["losses"]]

    def _h2h_badge(row):
        opp    = row["opp_manager"]
        emoji  = MANAGER_EMOJI.get(opp, "👤")
        w, l   = int(row["wins"]), int(row["losses"])
        pct    = f"{row['win_pct']:.0%}"
        color  = MANAGER_COLORS.get(opp, "#6B7280")
        return (
            f'<div style="background:#102418;border:1px solid #1A3525;border-left:4px solid {color};'
            f'border-radius:6px;padding:10px 14px;margin-bottom:6px;">'
            f'<span style="font-size:1rem;">{emoji}</span> '
            f'<span style="font-family:\'Inter\',sans-serif;font-size:0.85rem;color:#F5F3EA;font-weight:600;">{opp}</span>'
            f'<span style="float:right;font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#D4AF37;letter-spacing:2px;">'
            f'{w}–{l} &nbsp;<span style="font-size:0.7rem;color:#B8C3B5;">({pct})</span></span>'
            f'</div>'
        )

    col_dom, col_str = st.columns(2)
    with col_dom:
        if len(dominated) > 0:
            st.markdown(
                '<div style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#4ADE80;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Winning Record Against</div>',
                unsafe_allow_html=True,
            )
            for _, row in dominated.iterrows():
                st.markdown(_h2h_badge(row), unsafe_allow_html=True)
    with col_str:
        if len(struggles) > 0:
            st.markdown(
                '<div style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#F87171;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Losing Record Against</div>',
                unsafe_allow_html=True,
            )
            for _, row in struggles.iterrows():
                st.markdown(_h2h_badge(row), unsafe_allow_html=True)

    if len(even_games) > 0:
        st.markdown(
            '<div style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#B8C3B5;letter-spacing:3px;text-transform:uppercase;margin:12px 0 8px;">Even Record</div>',
            unsafe_allow_html=True,
        )
        for _, row in even_games.iterrows():
            st.markdown(_h2h_badge(row), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tbl_rows = []
    for _, row in h2h.iterrows():
        tbl_rows.append([
            row["opp_manager"],
            (f"{int(row['wins'])}–{int(row['losses'])}", "gold" if row["wins"] > row["losses"] else ""),
            f"{row['win_pct']:.0%}",
            f"{row['pf']:.1f}",
            f"{row['pa']:.1f}",
            (f"+{row['biggest_win']:.1f}", "") if row["biggest_win"] > 0 else ("—", "muted"),
        ])
    st.markdown(
        html_table(["Opponent", "Record", "Win%", "PF", "PA", "Biggest Win"], tbl_rows),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── KEEPER PROFILE ────────────────────────────────────────────────────────────
from utils.data import get_keeper_history
keepers = get_keeper_history()
mgr_keepers = keepers[keepers["manager"] == mgr_name] if not keepers.empty else keepers

if not mgr_keepers.empty:
    st.markdown(
        '<div class="tl-section-label">Auction Keeper History</div>'
        '<div class="tl-section-title">Keepers Across Seasons</div>',
        unsafe_allow_html=True,
    )

    total_keepers = len(mgr_keepers)
    seasons_with  = mgr_keepers["season"].nunique()
    avg_price     = round(mgr_keepers["auction_price"].mean(), 1)

    km1, km2, km3 = st.columns(3)
    with km1:
        st.markdown(metric_card(str(total_keepers), "Total Keeper Slots Used"), unsafe_allow_html=True)
    with km2:
        st.markdown(metric_card(str(seasons_with), "Seasons With Keepers"), unsafe_allow_html=True)
    with km3:
        st.markdown(metric_card(f"${avg_price:.0f}", "Avg Keeper Cost"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Multi-year keepers (kept 2+ seasons)
    kept_counts = mgr_keepers.groupby("player_name")["season"].count()
    multi_year  = kept_counts[kept_counts >= 2].index.tolist()

    if multi_year:
        st.markdown(
            '<div style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Multi-Year Keepers</div>',
            unsafe_allow_html=True,
        )
        for player in sorted(multi_year):
            chain = mgr_keepers[mgr_keepers["player_name"] == player].sort_values("season")
            years_str  = " → ".join(f"{int(r['season'])} (${int(r['auction_price'])})" for _, r in chain.iterrows())
            pos        = chain.iloc[0]["position"]
            st.markdown(
                f'<div style="background:#102418;border:1px solid #1A3525;border-left:4px solid #D4AF37;'
                f'border-radius:6px;padding:10px 14px;margin-bottom:6px;">'
                f'<span style="font-family:\'Inter\',sans-serif;font-size:0.85rem;color:#F5F3EA;font-weight:600;">{player}</span>'
                f'<span style="font-family:\'Inter\',sans-serif;font-size:0.65rem;color:#B8C3B5;margin-left:8px;">{pos}</span>'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#B8C3B5;margin-top:4px;">{years_str}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("<br>", unsafe_allow_html=True)

    kpr_rows = []
    for _, row in mgr_keepers.sort_values(["season", "auction_price"], ascending=[False, False]).iterrows():
        kpr_rows.append([
            (str(int(row["season"])), "gold"),
            str(row["player_name"]),
            str(row["position"]),
            (f"${int(row['auction_price'])}", "gold"),
        ])
    st.markdown(html_table(["Season", "Player", "Pos", "Cost"], kpr_rows), unsafe_allow_html=True)

render_page_footer(
    href="/rivalries",
    cta="EXPLORE RIVALRIES",
    tagline="THE MATCHUPS THAT DEFINED SEASONS.",
)
