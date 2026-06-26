"""Home page — A New Dynasty."""
import streamlit as st
from utils.data import (
    load_all, get_champions, get_manager_stats,
    LEAGUE_NAME, LEAGUE_SUBTITLE, CURRENT_SEASON, FOUNDED, MANAGER_EMOJI,
)
from utils.styles import inject_css, render_nav, metric_card

st.set_page_config(
    page_title="A New Dynasty",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("home")

data          = load_all()
champions     = get_champions()
manager_stats = get_manager_stats()
tnh           = data["team_name_history"]
std           = data["standings"]

# ── DERIVED ───────────────────────────────────────────────────────────────────
total_seasons    = CURRENT_SEASON - FOUNDED + 1
unique_champions = int(champions["champion_manager"].nunique()) if not champions.empty else 0
active_managers  = int((manager_stats["last_season"] == CURRENT_SEASON).sum())

legend_counts = (
    champions.groupby("champion_manager")
    .agg(
        titles=("season", "count"),
        years=("season", lambda x: ", ".join(str(y) for y in sorted(x))),
    )
    .sort_values("titles", ascending=False)
    .reset_index()
) if not champions.empty else None

tnh_lookup = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

_std = std.copy()
_std["gp"]  = _std["wins"] + _std["losses"] + _std["ties"]
_std["wpc"] = _std["wins"] / _std["gp"].replace(0, float("nan"))
_best_szns  = _std[_std["wpc"] == _std["wpc"].max()].copy()
_best_szns["manager"] = _best_szns.apply(
    lambda r: tnh_lookup.get((int(r["season"]), r["team_name"]), r["team_name"]), axis=1
)
_best_szn       = _best_szns.iloc[0]
best_szn_record = f"{int(_best_szn['wins'])}-{int(_best_szn['losses'])}"
_best_szn_years = sorted(_best_szns["season"].astype(int).tolist())
_best_szn_mgrs  = _best_szns["manager"].tolist()
if len(_best_szns) == 1:
    best_szn_mgr  = _best_szn_mgrs[0]
    best_szn_year = _best_szn_years[0]
    _best_szn_desc = f"{best_szn_mgr} ({best_szn_year}) — the most dominant regular season in league history."
else:
    _yr_str        = " & ".join(str(y) for y in _best_szn_years)
    _mgr_str       = " & ".join(_best_szn_mgrs)
    best_szn_year  = _best_szn_years[0]
    best_szn_mgr   = _mgr_str
    _best_szn_desc = f"{_mgr_str} — both went {best_szn_record} in {_yr_str}."

no_title_active = (
    manager_stats[(manager_stats["championships"] == 0) & (manager_stats["active"])]
    .sort_values("playoff_apps", ascending=False)
)
drought_row     = no_title_active.iloc[0] if len(no_title_active) > 0 else None
has_heartbreak  = drought_row is not None and int(drought_row["playoff_apps"]) >= 2
top_scorer      = manager_stats.sort_values("points_for", ascending=False).iloc[0]

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="tl-hero">
        <div class="tl-hero-title">A NEW DYNASTY</div>
        <div class="tl-hero-subtitle">{LEAGUE_SUBTITLE}</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#A7B0BC;
                    margin-top:1.1rem;letter-spacing:1px;font-style:italic;line-height:1.8;">
            Built to last.&nbsp; Paid to keep.&nbsp; Hard to win.
        </div>
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── CURRENT CHAMPION ──────────────────────────────────────────────────────────
if not champions.empty:
    current_row  = champions[champions["season"] == CURRENT_SEASON]
    if len(current_row) > 0:
        current     = current_row.iloc[0]
        champ_emoji = MANAGER_EMOJI.get(current["champion_manager"], "🏆")
        all_titles  = int((champions["champion_manager"] == current["champion_manager"]).sum())
        title_badge = f" &nbsp;·&nbsp; {all_titles}× Champion" if all_titles > 1 else ""

        st.markdown(
            '<div style="text-align:center;" class="tl-section-label">Reigning Champion</div>',
            unsafe_allow_html=True,
        )
        _, col, _ = st.columns([1, 3, 1])
        with col:
            st.markdown(
                f"""
                <div class="tl-champion-card" style="padding:3rem 2.5rem;box-shadow:0 0 80px rgba(212,175,55,0.22);">
                    <div style="font-size:4rem;margin-bottom:0.5rem;">{champ_emoji}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.6rem;color:#A7B0BC;letter-spacing:6px;text-transform:uppercase;">🏆 {CURRENT_SEASON} League Champion 🏆</div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:4.5rem;color:#D4AF37;letter-spacing:5px;line-height:1;margin:0.3rem 0 0.25rem;">{current['champion_team']}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:1.05rem;color:#F5F5F5;font-weight:500;">{current['champion_manager']}{title_badge}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.8rem;color:#A7B0BC;margin-top:0.75rem;">{current['champion_score']:.2f} – {current['runner_up_score']:.2f} over {current['runner_up_team']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── LEAGUE METRICS ────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card(str(total_seasons), "Seasons"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card(str(active_managers), "Active Members"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card(str(unique_champions), "Different Champions"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("5", "Max Keepers Per Team"), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── RECENT CHAMPIONS ──────────────────────────────────────────────────────────
if not champions.empty:
    st.markdown(
        '<div style="text-align:center;" class="tl-section-label">Recent Champions</div>',
        unsafe_allow_html=True,
    )
    recent = champions[champions["season"] < CURRENT_SEASON].tail(5).iloc[::-1]
    cols   = st.columns(min(5, len(recent)))
    for col, (_, row) in zip(cols, recent.iterrows()):
        mgr_emoji   = MANAGER_EMOJI.get(row["champion_manager"], "🏆")
        title_count = int((
            (champions["champion_manager"] == row["champion_manager"]) &
            (champions["season"] <= row["season"])
        ).sum())
        trophy_html = (
            f'<div class="tl-mini-champ-mgr" style="color:#D4AF37;font-size:0.7rem;">{"🏆" * title_count}</div>'
            if title_count > 1 else ""
        )
        with col:
            st.markdown(
                f"""
                <div class="tl-mini-champ">
                    <div style="font-size:1.5rem;">{mgr_emoji}</div>
                    <div class="tl-mini-champ-year">{row['season']}</div>
                    <div class="tl-mini-champ-team">{row['champion_team']}</div>
                    <div class="tl-mini-champ-mgr">{row['champion_manager']}</div>
                    {trophy_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── LEAGUE LEGENDS ────────────────────────────────────────────────────────────
if legend_counts is not None:
    st.markdown(
        '<div class="tl-section-label" style="text-align:center;">All-Time</div>'
        '<div style="text-align:center;font-family:\'Bebas Neue\',sans-serif;font-size:2rem;'
        'color:#F5F5F5;letter-spacing:4px;margin-bottom:1.25rem;">League Legends</div>',
        unsafe_allow_html=True,
    )

    top_legends = legend_counts.head(4).to_dict("records")
    n_legend    = len(top_legends) + (1 if has_heartbreak else 0)
    leg_cols    = st.columns(max(n_legend, 1))

    for col, leg in zip(leg_cols, top_legends):
        leg_emoji = MANAGER_EMOJI.get(leg["champion_manager"], "👤")
        plural    = "s" if leg["titles"] != 1 else ""
        with col:
            st.markdown(
                f"""<div class="tl-card" style="text-align:center;padding:1.5rem 1rem;">
                    <div style="font-size:2.2rem;margin-bottom:0.4rem;">{leg_emoji}</div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:2.6rem;color:#D4AF37;letter-spacing:2px;line-height:1;">{leg["titles"]}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.6rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;margin:0.1rem 0 0.4rem;">Championship{plural}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#F5F5F5;font-weight:600;">{leg["champion_manager"]}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.64rem;color:#A7B0BC;margin-top:0.15rem;">{leg["years"]}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    if has_heartbreak:
        hb       = no_title_active.iloc[0]
        hb_emoji = MANAGER_EMOJI.get(hb["canonical_name"], "👤")
        with leg_cols[len(top_legends)]:
            st.markdown(
                f"""<div class="tl-card" style="text-align:center;padding:1.5rem 1rem;border-color:rgba(184,144,46,0.4);">
                    <div style="font-size:2.2rem;margin-bottom:0.4rem;">{hb_emoji}</div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:2.6rem;color:#A7B0BC;letter-spacing:2px;line-height:1;">{int(hb['playoff_apps'])}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.6rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;margin:0.1rem 0 0.4rem;">Playoff Trips &nbsp;·&nbsp; 0 Titles</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#F5F5F5;font-weight:600;">{hb['canonical_name']}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.64rem;color:#A7B0BC;margin-top:0.15rem;">Still waiting...</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── LEAGUE STORYLINES ─────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label" style="text-align:center;">The Numbers Behind the Legend</div>'
    '<div style="text-align:center;font-family:\'Bebas Neue\',sans-serif;font-size:2rem;'
    'color:#F5F5F5;letter-spacing:4px;margin-bottom:1.25rem;">League Storylines</div>',
    unsafe_allow_html=True,
)

def _story(label, headline, sub):
    return (
        f'<div class="tl-card">'
        f'<div class="tl-section-label">{label}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:#D4AF37;'
        f'letter-spacing:2px;line-height:1.1;margin:0.2rem 0;">{headline}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
        f'margin-top:0.35rem;line-height:1.5;">{sub}</div>'
        f'</div>'
    )

sc1, sc2, sc3, sc4 = st.columns(4)

with sc1:
    if legend_counts is not None:
        top_leg = legend_counts.iloc[0]
        st.markdown(_story(
            "Most Championships",
            f"{top_leg['titles']}× — {top_leg['champion_manager']}",
            f"Won in {top_leg['years']}. The benchmark everyone is chasing.",
        ), unsafe_allow_html=True)

with sc2:
    _best_szn_value = (
        f"{best_szn_record} ({' & '.join(str(y) for y in _best_szn_years)})"
        if len(_best_szns) > 1 else f"{best_szn_record} in {_best_szn_years[0]}"
    )
    st.markdown(_story("Best Regular Season", _best_szn_value, _best_szn_desc), unsafe_allow_html=True)

with sc3:
    if drought_row is not None:
        st.markdown(_story(
            "Most Trips Without a Title",
            f"{int(drought_row['playoff_apps'])} Appearances",
            f"{drought_row['canonical_name']} — the playoffs keep calling. The trophy doesn't.",
        ), unsafe_allow_html=True)

with sc4:
    st.markdown(_story(
        "All-Time Scoring Leader",
        f"{top_scorer['points_for']:,.0f} pts",
        f"{top_scorer['canonical_name']} — more fantasy points than anyone in league history.",
    ), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── MUSEUM DESTINATIONS ───────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label" style="text-align:center;">Museum Destinations</div>'
    '<div style="text-align:center;font-family:\'Bebas Neue\',sans-serif;font-size:2rem;'
    'color:#F5F5F5;letter-spacing:4px;margin-bottom:0.4rem;">Explore the Exhibits</div>'
    '<div style="text-align:center;font-family:\'Inter\',sans-serif;font-size:0.75rem;'
    'color:#6B7280;margin-bottom:1.5rem;">Every section is a destination. Start anywhere.</div>',
    unsafe_allow_html=True,
)

exhibits_row1 = [
    ("🏆", "Trophy Room",   "Every champion. Every dynasty. The immortal record of who won and how.",         "/champions"),
    ("🔑", "Keeper Hall",   "The signature exhibit. Seven years of loyalty, cost escalation, and attachment.", "/keeper_hall"),
    ("📋", "Draft Legends", "Auction behavior, spending patterns, and the players everyone had to have.",      "/draft_center"),
]
exhibits_row2 = [
    ("👤", "Manager Files",    "Career plaques and records for every competitor in league history.",            "/manager_profiles"),
    ("🏟️", "Franchise Files", "Ten franchises, their stewards, and the lineages that shaped the league.",     "/franchise_profiles"),
    ("⚔️", "Rivalries",       "The matchups that defined seasons. Head-to-head records and playoff grudges.",  "/rivalries"),
]

for row in [exhibits_row1, exhibits_row2]:
    ex_cols = st.columns(3)
    for col, (icon, title, desc, href) in zip(ex_cols, row):
        with col:
            st.markdown(
                f"""<a href="{href}" class="tl-nav-card" target="_self">
                    <div style="font-size:0.55rem;color:#A7B0BC;letter-spacing:4px;text-transform:uppercase;margin-bottom:0.5rem;">EXHIBIT</div>
                    <div class="tl-nav-card-icon">{icon}</div>
                    <div class="tl-nav-card-title">{title}</div>
                    <div class="tl-nav-card-desc">{desc}</div>
                </a>""",
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

# ── FOOTER TAGLINE ────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="text-align:center;padding:3rem 0 2rem;">
        <div style="height:1px;background:linear-gradient(to right,transparent,#D4AF37,transparent);margin:0 auto 2rem;max-width:400px;"></div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:#F5F5F5;letter-spacing:4px;line-height:1.8;">
            {total_seasons} SEASONS.<br>{unique_champions} DIFFERENT CHAMPIONS.<br>ONE KEEPER LEAGUE THAT NEVER QUIT.
        </div>
        <div style="margin-top:1.75rem;">
            <a href="/champions" target="_self"
               style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#D4AF37;
                      letter-spacing:4px;text-transform:uppercase;text-decoration:none;
                      border-bottom:1px solid rgba(212,175,55,0.6);padding-bottom:3px;">
                ENTER THE TROPHY ROOM &nbsp;&rarr;
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
