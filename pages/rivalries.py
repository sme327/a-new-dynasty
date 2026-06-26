"""Rivalries — the emotional center of the league."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.data import (
    get_all_rivalries, get_playoff_eliminations, get_champions, load_all,
    MANAGER_COLORS, MANAGER_EMOJI, CURRENT_SEASON, FOUNDED,
)
from utils.styles import inject_css, render_nav, render_page_footer, html_table

st.set_page_config(
    page_title="Rivalries · A New Dynasty",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("rivalries")

all_rivalries = get_all_rivalries()
elim_df       = get_playoff_eliminations()
champs        = get_champions()
data_raw      = load_all()
tnh           = data_raw["team_name_history"]
pg            = data_raw["playoffs"]
mgr_lu        = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

if not pg.empty:
    champ_pg = pg[pg["bracket"] == "championship"].copy()
    finals   = champ_pg[champ_pg["game_type"] == "final"].copy()
    finals["winner_mgr"] = finals.apply(lambda r: mgr_lu.get((r["season"], r["winner"]), r["winner"]), axis=1)
    finals["loser_team"] = finals.apply(lambda r: r["team_2"] if r["winner"] == r["team_1"] else r["team_1"], axis=1)
    finals["loser_mgr"]  = finals.apply(lambda r: mgr_lu.get((r["season"], r["loser_team"]), r["loser_team"]), axis=1)
    finals["margin"]     = (finals["score_1"] - finals["score_2"]).abs()
else:
    champ_pg = pd.DataFrame()
    finals   = pd.DataFrame()

def _color(mgr): return MANAGER_COLORS.get(mgr, "#6B7280")
def _emoji(mgr): return MANAGER_EMOJI.get(mgr, "👤")

all_mgrs = sorted(set(all_rivalries["mgr_a"].tolist() + all_rivalries["mgr_b"].tolist())) if not all_rivalries.empty else []

# ── PAGE TITLE ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-page-title">Rivalries</div>
    <div class="tl-page-subtitle">The matchups that defined seasons. The grudges that outlasted rosters.</div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── TOP RIVALRIES ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Most Played</div>'
    '<div class="tl-section-title">Top Rivalries</div>',
    unsafe_allow_html=True,
)

if not all_rivalries.empty:
    top5 = all_rivalries.head(5)
    for _, row in top5.iterrows():
        a, b   = row["mgr_a"], row["mgr_b"]
        aw, bw = int(row["a_wins"]), int(row["b_wins"])
        games  = int(row["games"])
        avg_m  = float(row["avg_margin"])
        ca, cb = _color(a), _color(b)
        lead   = a if aw > bw else (b if bw > aw else None)
        lead_adv = abs(aw - bw)

        st.markdown(
            f"""
            <div style="background:#0F1B2D;border:1px solid #1E2D40;border-radius:8px;padding:16px 20px;margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                    <div style="display:flex;align-items:center;gap:16px;">
                        <span style="font-size:1.5rem;">{_emoji(a)}</span>
                        <div>
                            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:{ca};letter-spacing:2px;">{a}</div>
                            <div style="font-family:'Inter',sans-serif;font-size:0.7rem;color:#A7B0BC;">leads {aw}–{bw}</div>
                        </div>
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#F5F5F5;letter-spacing:4px;padding:0 8px;">VS</div>
                        <div>
                            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:{cb};letter-spacing:2px;">{b}</div>
                            <div style="font-family:'Inter',sans-serif;font-size:0.7rem;color:#A7B0BC;">{bw}–{aw}</div>
                        </div>
                        <span style="font-size:1.5rem;">{_emoji(b)}</span>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;">{games} games &nbsp;·&nbsp; avg margin {avg_m:.1f} pts</div>
                        {f'<div style="font-family:\'Inter\',sans-serif;font-size:0.65rem;color:#D4AF37;margin-top:3px;">{lead} leads by {lead_adv}</div>' if lead else '<div style="font-size:0.65rem;color:#A7B0BC;">Dead even</div>'}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── RIVALRY EXPLORER ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Pick Any Two</div>'
    '<div class="tl-section-title">Rivalry Explorer</div>',
    unsafe_allow_html=True,
)

col_a, col_b = st.columns(2)
with col_a:
    mgr_a = st.selectbox("Manager A", options=all_mgrs, index=0)
with col_b:
    remaining = [m for m in all_mgrs if m != mgr_a]
    mgr_b = st.selectbox("Manager B", options=remaining, index=0)

if mgr_a and mgr_b:
    pair = tuple(sorted([mgr_a, mgr_b]))
    match = all_rivalries[
        (all_rivalries["mgr_a"] == pair[0]) & (all_rivalries["mgr_b"] == pair[1])
    ] if not all_rivalries.empty else pd.DataFrame()

    if len(match) > 0:
        row    = match.iloc[0]
        a_wins = int(row["a_wins"]) if mgr_a == pair[0] else int(row["b_wins"])
        b_wins = int(row["b_wins"]) if mgr_a == pair[0] else int(row["a_wins"])
        games  = int(row["games"])
        avg_m  = float(row["avg_margin"])

        st.markdown(
            f"""
            <div style="text-align:center;padding:1.5rem 0;">
                <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:4px;text-transform:uppercase;margin-bottom:0.5rem;">Head-to-Head Record</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;color:#F5F5F5;letter-spacing:4px;">
                    <span style="color:{_color(mgr_a)};">{mgr_a}</span>
                    &nbsp;{a_wins} – {b_wins}&nbsp;
                    <span style="color:{_color(mgr_b)};">{mgr_b}</span>
                </div>
                <div style="font-family:'Inter',sans-serif;font-size:0.7rem;color:#A7B0BC;margin-top:0.5rem;">
                    {games} regular season matchups &nbsp;·&nbsp; avg margin {avg_m:.1f} pts &nbsp;·&nbsp; {int(row['seasons_met'])} seasons together
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Playoff history between these two
        if not elim_df.empty:
            pl_between = elim_df[
                ((elim_df["winner_mgr"] == mgr_a) & (elim_df["loser_mgr"] == mgr_b)) |
                ((elim_df["winner_mgr"] == mgr_b) & (elim_df["loser_mgr"] == mgr_a))
            ].sort_values("season")
            if len(pl_between) > 0:
                st.markdown(
                    '<div style="font-size:0.6rem;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Playoff Meetings</div>',
                    unsafe_allow_html=True,
                )
                pl_rows = []
                for _, pr in pl_between.iterrows():
                    winner_style = "gold"
                    pl_rows.append([
                        (str(int(pr["season"])), "gold"),
                        pr["game_type"].replace("_", " ").title(),
                        (pr["winner_mgr"], winner_style),
                        pr["loser_mgr"],
                        (f"{pr['margin']:.2f}", ""),
                    ])
                st.markdown(html_table(["Season", "Round", "Winner", "Eliminated", "Margin"], pl_rows), unsafe_allow_html=True)
    else:
        st.info(f"{mgr_a} and {mgr_b} have never faced each other in the regular season.")

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── PLAYOFF ELIMINATIONS ──────────────────────────────────────────────────────
if not elim_df.empty:
    st.markdown(
        '<div class="tl-section-label">Postseason History</div>'
        '<div class="tl-section-title">Playoff Eliminations</div>',
        unsafe_allow_html=True,
    )

    # Who eliminates the most
    eliminator_counts = elim_df.groupby("winner_mgr").size().sort_values(ascending=False).reset_index(name="elims")
    victim_counts     = elim_df.groupby("loser_mgr").size().sort_values(ascending=False).reset_index(name="times_elim")

    ec1, ec2 = st.columns(2)
    with ec1:
        st.markdown(
            '<div style="font-size:0.6rem;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Most Eliminations</div>',
            unsafe_allow_html=True,
        )
        for _, row in eliminator_counts.head(5).iterrows():
            mgr = row["winner_mgr"]
            st.markdown(
                f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid {_color(mgr)};'
                f'border-radius:6px;padding:8px 14px;margin-bottom:5px;">'
                f'<span style="font-size:0.9rem;">{_emoji(mgr)}</span> '
                f'<span style="font-family:\'Inter\',sans-serif;font-size:0.82rem;color:#F5F5F5;">{mgr}</span>'
                f'<span style="float:right;font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#D4AF37;">{row["elims"]} elims</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    with ec2:
        st.markdown(
            '<div style="font-size:0.6rem;color:#F87171;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Most Times Eliminated</div>',
            unsafe_allow_html=True,
        )
        for _, row in victim_counts.head(5).iterrows():
            mgr = row["loser_mgr"]
            st.markdown(
                f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid {_color(mgr)};'
                f'border-radius:6px;padding:8px 14px;margin-bottom:5px;">'
                f'<span style="font-size:0.9rem;">{_emoji(mgr)}</span> '
                f'<span style="font-family:\'Inter\',sans-serif;font-size:0.82rem;color:#F5F5F5;">{mgr}</span>'
                f'<span style="float:right;font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F87171;">{row["times_elim"]}×</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.6rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Full Elimination History</div>',
        unsafe_allow_html=True,
    )
    elim_rows = []
    for _, row in elim_df.sort_values("season", ascending=False).iterrows():
        elim_rows.append([
            (str(int(row["season"])), "gold"),
            row["game_type"].replace("_", " ").title(),
            (f"{_emoji(row['winner_mgr'])} {row['winner_mgr']}", "gold"),
            f"{_emoji(row['loser_mgr'])} {row['loser_mgr']}",
            (f"{row['margin']:.2f}", "muted"),
        ])
    st.markdown(html_table(["Season", "Round", "Winner", "Eliminated", "Margin"], elim_rows), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── COMPLETE H2H GRID ─────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">All-Time Regular Season</div>'
    '<div class="tl-section-title">Full H2H Record Table</div>',
    unsafe_allow_html=True,
)

if not all_rivalries.empty:
    tbl_rows = []
    for _, row in all_rivalries.iterrows():
        a, b   = row["mgr_a"], row["mgr_b"]
        aw, bw = int(row["a_wins"]), int(row["b_wins"])
        lead   = a if aw > bw else (b if bw > aw else "—")
        tbl_rows.append([
            f"{_emoji(a)} {a}",
            f"{_emoji(b)} {b}",
            (f"{aw}–{bw}", "gold" if aw > bw else ""),
            f"{float(row['avg_margin']):.1f} pts",
            (str(int(row["games"])), "muted"),
        ])
    st.markdown(html_table(["Manager A", "Manager B", "Record (A–B)", "Avg Margin", "Games"], tbl_rows), unsafe_allow_html=True)

render_page_footer(
    href="/champions",
    cta="VIEW CHAMPIONS",
    tagline="WHO WON.<br>WHO LOST.<br>WHO STILL HOLDS A GRUDGE.",
)
