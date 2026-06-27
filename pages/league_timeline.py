"""League Timeline — the historical spine of A New Dynasty."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.data import (
    load_all, get_timeline_events, get_champions,
    MANAGER_EMOJI, MANAGER_COLORS, FOUNDED, CURRENT_SEASON,
)
from utils.styles import inject_css, render_nav, render_page_footer, metric_card

st.set_page_config(
    page_title="Timeline · A New Dynasty",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("league_timeline")

data     = load_all()
events   = get_timeline_events()
champions = get_champions()
seasons  = sorted(events["season"].unique().tolist(), reverse=True) if not events.empty else []

# ── Category styling ──────────────────────────────────────────────────────────
CAT_COLORS = {
    "championship": "#D4AF37",
    "runner_up":    "#94A3B8",
    "franchise":    "#A78BFA",
    "keeper":       "#10B981",
    "auction":      "#F97316",
    "rivalry":      "#F87171",
    "manual":       "#3FA66B",
}
CAT_LABELS = {
    "championship": "CHAMPION",
    "runner_up":    "RUNNER-UP",
    "franchise":    "FRANCHISE",
    "keeper":       "KEEPER",
    "auction":      "AUCTION",
    "rivalry":      "CLOSE CALL",
    "manual":       "LEAGUE LORE",
}

# ── HERO ──────────────────────────────────────────────────────────────────────
total_seasons = CURRENT_SEASON - FOUNDED + 1
unique_champs = champions["champion_manager"].nunique() if not champions.empty else 0

st.markdown(
    f"""
    <div class="tl-hero">
        <div class="tl-hero-title">THE TIMELINE</div>
        <div class="tl-hero-subtitle">Eight years of championship chases, keeper dynasties, and 0.02-point heartbreaks.</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#B8C3B5;
                    margin-top:1.1rem;letter-spacing:1px;font-style:italic;line-height:1.8;">
            {FOUNDED} – {CURRENT_SEASON} &nbsp;·&nbsp; {total_seasons} Seasons &nbsp;·&nbsp; {unique_champs} Unique Champions
        </div>
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── NAVIGATION BAR ────────────────────────────────────────────────────────────
if seasons:
    jump_links = "".join(
        f'<a href="#season-{s}" style="font-family:\'Inter\',sans-serif;font-size:0.7rem;'
        f'color:#B8C3B5;text-decoration:none;padding:4px 10px;border:1px solid #1A3525;'
        f'border-radius:3px;white-space:nowrap;" target="_self">{s}</a>'
        for s in seasons
    )
    st.markdown(
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:2rem;">'
        f'{jump_links}</div>',
        unsafe_allow_html=True,
    )

# ── YEAR CHAPTERS ─────────────────────────────────────────────────────────────
def champ_card(evt: pd.Series, szn: int) -> str:
    mgr    = evt["title"].replace(f" wins {szn} championship", "").strip()
    color  = MANAGER_COLORS.get(mgr, "#D4AF37")
    emoji  = MANAGER_EMOJI.get(mgr, "🏆")
    desc   = evt["description"]
    detail = evt["detail"]
    szn_num = szn - FOUNDED + 1

    # Count this manager's titles up to this season
    if not champions.empty:
        n_titles = len(champions[(champions["champion_manager"] == mgr) & (champions["season"] <= szn)])
        ordinal  = {1: "1ST", 2: "2ND", 3: "3RD"}.get(n_titles, f"{n_titles}TH")
        title_label = f"{ordinal} TITLE"
    else:
        title_label = "CHAMPION"

    return f"""
    <div id="champ-{szn}" style="background:linear-gradient(135deg,#102418 0%,#0B1B13 100%);
         border:2px solid {color};border-radius:10px;padding:24px 28px;margin-bottom:16px;
         position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;right:0;width:120px;height:120px;
             background:radial-gradient(circle,{color}15 0%,transparent 70%);"></div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;">
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:0.52rem;color:{color};letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">
                    🏆 {szn} CHAMPION &nbsp;·&nbsp; {title_label}
                </div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2.6rem;color:#F5F3EA;
                     letter-spacing:3px;line-height:1;margin-bottom:6px;">
                    {emoji} {mgr}
                </div>
                <div style="font-family:'Inter',sans-serif;font-size:0.78rem;color:#C5D4C0;line-height:1.6;max-width:480px;">
                    {desc}
                </div>
            </div>
            <div style="text-align:center;min-width:80px;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;color:{color};
                     letter-spacing:2px;line-height:1;">{detail.split('–')[0].strip()}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.52rem;color:#B8C3B5;letter-spacing:3px;">FINAL SCORE</div>
            </div>
        </div>
    </div>
    """

def event_card(evt: pd.Series) -> str:
    cat    = evt["category"]
    color  = CAT_COLORS.get(cat, "#6B7280")
    label  = CAT_LABELS.get(cat, cat.upper())
    emoji  = evt["emoji"]
    title  = evt["title"]
    desc   = evt["description"]

    return f"""
    <div style="background:#102418;border:1px solid #1A3525;border-left:3px solid {color};
         border-radius:6px;padding:12px 14px;margin-bottom:8px;height:100%;">
        <div style="font-family:'Inter',sans-serif;font-size:0.48rem;color:{color};
             letter-spacing:3px;text-transform:uppercase;margin-bottom:4px;">{emoji} {label}</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.78rem;color:#F5F3EA;
             font-weight:600;margin-bottom:5px;line-height:1.3;">{title}</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.68rem;color:#B8C3B5;line-height:1.5;">{desc}</div>
    </div>
    """

for szn in seasons:
    szn_events = events[events["season"] == szn].copy()
    szn_num    = szn - FOUNDED + 1

    # Build champion info for the year header
    champ_evt = szn_events[szn_events["category"] == "championship"]
    champ_mgr = ""
    if not champ_evt.empty:
        champ_mgr = champ_evt.iloc[0]["title"].replace(f" wins {szn} championship", "").strip()

    champ_color = MANAGER_COLORS.get(champ_mgr, "#D4AF37")
    champ_emoji = MANAGER_EMOJI.get(champ_mgr, "🏆")

    # ── Season header ─────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div id="season-{szn}" style="display:flex;align-items:center;gap:16px;
             margin:2.5rem 0 1.2rem;padding-bottom:10px;border-bottom:1px solid {champ_color}30;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:3.2rem;color:{champ_color};
                 letter-spacing:4px;line-height:1;">{szn}</div>
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:0.52rem;color:#B8C3B5;
                     letter-spacing:3px;text-transform:uppercase;">Season {szn_num} of {total_seasons}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.85rem;color:#C5D4C0;">
                    {champ_emoji} {champ_mgr} won the championship
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Championship card (full width) ────────────────────────────────────────
    if not champ_evt.empty:
        st.markdown(champ_card(champ_evt.iloc[0], szn), unsafe_allow_html=True)

    # ── Other events (3-column grid) ──────────────────────────────────────────
    other = szn_events[szn_events["category"] != "championship"].sort_values("importance")

    if not other.empty:
        # Prioritize: runner_up → rivalry → franchise → auction → keeper
        priority = {"runner_up": 0, "rivalry": 1, "franchise": 2, "auction": 3, "keeper": 4}
        other = other.copy()
        other["_sort"] = other["category"].map(priority).fillna(5)
        other = other.sort_values(["importance", "_sort"]).drop(columns="_sort")

        rows = [other.iloc[i:i+3] for i in range(0, len(other), 3)]
        for row_df in rows:
            cols = st.columns(3)
            for ci, (_, evt) in enumerate(row_df.iterrows()):
                with cols[ci]:
                    st.markdown(event_card(evt), unsafe_allow_html=True)

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

# ── BOTTOM DIVIDER + NAV ──────────────────────────────────────────────────────
st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# Back to top
st.markdown(
    '<div style="text-align:center;padding:12px 0;">'
    '<a href="#" style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#B8C3B5;'
    'letter-spacing:2px;text-decoration:none;border:1px solid #1A3525;padding:8px 20px;border-radius:4px;">'
    '↑ BACK TO TOP</a></div>',
    unsafe_allow_html=True,
)

render_page_footer(
    href="/season_archive",
    cta="EXPLORE SEASON ARCHIVE",
    tagline="EVERY SEASON.<br>EVERY GAME.<br>EVERY CHAPTER.",
)
