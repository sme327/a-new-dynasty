"""Season Archive — drill into any individual season."""
from __future__ import annotations
import streamlit as st
from utils.data import load_all, get_champions, get_playoff_result_for_team, MANAGER_EMOJI, CURRENT_SEASON
from utils.styles import inject_css, render_nav, render_page_footer, html_table

st.set_page_config(
    page_title="Season Archive · A New Dynasty",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("season_archive")

data      = load_all()
champions = get_champions()
standings = data["standings"]
pg        = data["playoffs"]
tnh       = data["team_name_history"]
wm        = data["matchups"]

# ── SEASON SELECTOR ────────────────────────────────────────────────────────────
all_seasons = sorted(standings["season"].unique(), reverse=True)

st.markdown(
    """
    <div class="tl-page-title">Season Archive</div>
    <div class="tl-page-subtitle">Select any season to explore its complete history.</div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

season = st.selectbox("SELECT SEASON", options=all_seasons, index=0, format_func=lambda s: f"{s} Season")
season = int(season)
st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SEASON TITLE ───────────────────────────────────────────────────────────────
champ_row     = champions[champions["season"] == season] if not champions.empty else None
_prev_row     = champions[champions["season"] == season - 1] if not champions.empty else None
_prev_champ   = _prev_row.iloc[0]["champion_manager"] if (_prev_row is not None and len(_prev_row) > 0) else None

def _season_title(szn, c_mgr, margin, is_repeat, prior_titles):
    if szn == 2018:
        return "The Inaugural Season"
    if is_repeat:
        return "The Repeat"
    if prior_titles == 0:
        return "The Breakthrough" if margin < 30 else "The Coronation"
    if margin < 5:
        return "Down to the Wire"
    if margin > 50:
        return "No Contest"
    return f"The {szn} Championship"

def _season_narrative(szn, c_mgr, c_team, ru_mgr, ru_team, c_score, ru_score):
    margin = c_score - ru_score
    if szn == 2018:
        return f"Year one. The league was new, the rules were fresh, and {c_mgr} claimed the inaugural trophy."
    if _prev_champ == c_mgr:
        return f"Back-to-back. {c_mgr} didn't let go of the trophy — defending the title with {c_team}."
    if margin < 5:
        return (f"{c_mgr} survived a championship game that could have gone either way. "
                f"{c_score:.2f}–{ru_score:.2f} over {ru_team}. A margin of {margin:.2f} points.")
    if margin > 40:
        return (f"There was no suspense. {c_mgr} dominated the championship game, "
                f"outscoring {ru_mgr} by {margin:.2f} points.")
    return (f"{c_mgr} took home the {szn} title, defeating {ru_mgr}'s {ru_team} "
            f"{c_score:.2f}–{ru_score:.2f} in the championship game.")

if champ_row is not None and len(champ_row) > 0:
    cr         = champ_row.iloc[0]
    c_mgr      = cr["champion_manager"]
    c_team     = cr["champion_team"]
    ru_mgr     = cr["runner_up_manager"]
    ru_team    = cr["runner_up_team"]
    c_score    = float(cr["champion_score"])
    ru_score   = float(cr["runner_up_score"])
    margin     = c_score - ru_score
    prior      = int((champions[champions["season"] < season]["champion_manager"] == c_mgr).sum()) if not champions.empty else 0
    is_repeat  = (_prev_champ == c_mgr)
    title      = _season_title(season, c_mgr, margin, is_repeat, prior)
    narrative  = _season_narrative(season, c_mgr, c_team, ru_mgr, ru_team, c_score, ru_score)
    champ_emoji = MANAGER_EMOJI.get(c_mgr, "🏆")

    st.markdown(
        f"""
        <div style="text-align:center;padding:1rem 0 1.5rem;">
            <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#B8C3B5;letter-spacing:5px;text-transform:uppercase;">The {season} Season</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;color:#F5F3EA;letter-spacing:4px;margin:0.3rem 0 0.5rem;">{title}</div>
            <div style="font-size:3rem;">{champ_emoji}</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#D4AF37;letter-spacing:3px;margin-top:0.5rem;">{c_team}</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.85rem;color:#F5F3EA;margin:0.25rem 0;">{c_mgr}</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#B8C3B5;margin-top:0.25rem;">{c_score:.2f} – {ru_score:.2f} over {ru_team}</div>
        </div>
        <div style="background:#102418;border:1px solid #1A3525;border-left:4px solid #D4AF37;border-radius:6px;padding:1rem 1.5rem;max-width:720px;margin:0 auto 1.5rem;">
            <p style="font-family:'Inter',sans-serif;font-size:0.8rem;color:#B8C3B5;line-height:1.7;margin:0;">{narrative}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div style="text-align:center;font-family:\'Bebas Neue\',sans-serif;font-size:2.5rem;color:#F5F3EA;letter-spacing:4px;">THE {season} SEASON</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FINAL STANDINGS ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">End of Season</div>'
    '<div class="tl-section-title">Final Standings</div>',
    unsafe_allow_html=True,
)

szn_std = standings[standings["season"] == season].sort_values("rank")
tnh_szn = tnh[tnh["season"] == season].set_index("team_name")["canonical_name"].to_dict()

if not szn_std.empty:
    std_rows = []
    for _, row in szn_std.iterrows():
        team    = row["team_name"]
        mgr     = tnh_szn.get(team, team)
        emoji   = MANAGER_EMOJI.get(mgr, "👤")
        gp      = int(row["wins"]) + int(row["losses"]) + int(row.get("ties", 0))
        record  = f"{int(row['wins'])}-{int(row['losses'])}" + (f"-{int(row['ties'])}" if row.get("ties", 0) else "")
        playoff = get_playoff_result_for_team(season, team, pg)
        rank_str = f"#{int(row['rank'])}"
        style    = "gold" if "Champion" in playoff else ""
        std_rows.append([
            (rank_str, style),
            f"{emoji} {team}",
            mgr,
            (record, style),
            f"{float(row['points_for']):,.2f}",
            f"{float(row['points_against']):,.2f}",
            (playoff, style),
        ])
    st.markdown(
        html_table(["Rank", "Team", "Manager", "Record", "PF", "PA", "Playoff Result"], std_rows),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── PLAYOFF BRACKET ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Postseason</div>'
    '<div class="tl-section-title">Playoff Results</div>',
    unsafe_allow_html=True,
)

szn_pg    = pg[pg["season"] == season]
champ_pg  = szn_pg[szn_pg["bracket"] == "championship"].sort_values("round")
consol_pg = szn_pg[szn_pg["bracket"] == "consolation"].sort_values("round") if "consolation" in szn_pg["bracket"].values else None

def _game_html(row):
    t1, s1 = row["team_1"], float(row["score_1"])
    t2, s2 = row["team_2"], float(row["score_2"])
    w      = row["winner"]
    m1_cls = "color:#D4AF37;font-weight:700;" if w == t1 else "color:#6B7280;"
    m2_cls = "color:#D4AF37;font-weight:700;" if w == t2 else "color:#6B7280;"
    lbl    = row["game_type"].replace("_", " ").title()
    return (
        f'<div style="background:#102418;border:1px solid #1A3525;border-radius:6px;padding:10px 16px;margin-bottom:6px;">'
        f'<div style="font-size:0.55rem;color:#B8C3B5;letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;">{lbl}</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<span style="font-family:\'Inter\',sans-serif;font-size:0.85rem;{m1_cls}">{t1}</span>'
        f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;color:#F5F3EA;letter-spacing:2px;">{s1:.2f} – {s2:.2f}</span>'
        f'<span style="font-family:\'Inter\',sans-serif;font-size:0.85rem;{m2_cls}">{t2}</span>'
        f'</div>'
        f'</div>'
    )

if len(champ_pg) > 0:
    st.markdown('<div style="font-size:0.6rem;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Championship Bracket</div>', unsafe_allow_html=True)
    for _, row in champ_pg.iterrows():
        st.markdown(_game_html(row), unsafe_allow_html=True)

if consol_pg is not None and len(consol_pg) > 0:
    st.markdown('<div style="font-size:0.6rem;color:#B8C3B5;letter-spacing:3px;text-transform:uppercase;margin-top:16px;margin-bottom:8px;">Consolation Bracket</div>', unsafe_allow_html=True)
    for _, row in consol_pg.iterrows():
        st.markdown(_game_html(row), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SEASON SCORING ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">By the Numbers</div>'
    '<div class="tl-section-title">Season Scoring</div>',
    unsafe_allow_html=True,
)

szn_rs = wm[(wm["season"] == season) & ~wm["is_bye"] & ~wm["is_playoff"]]
if not szn_rs.empty:
    avg_score  = float(szn_rs["team_score"].mean())
    high_score = float(szn_rs["team_score"].max())
    low_score  = float(szn_rs[szn_rs["team_score"] > 0]["team_score"].min())
    high_row   = szn_rs.loc[szn_rs["team_score"].idxmax()]
    high_mgr   = tnh_szn.get(high_row["team_name"], high_row["team_name"])

    s1, s2, s3, s4 = st.columns(4)
    from utils.styles import metric_card
    with s1:
        st.markdown(metric_card(f"{avg_score:.1f}", "Avg Weekly Score"), unsafe_allow_html=True)
    with s2:
        st.markdown(metric_card(f"{high_score:.2f}", "Highest Single Score"), unsafe_allow_html=True)
    with s3:
        st.markdown(metric_card(f"{low_score:.2f}", "Lowest Single Score"), unsafe_allow_html=True)
    with s4:
        st.markdown(metric_card(high_mgr, "Top Scorer"), unsafe_allow_html=True)

# ── DRAFT RECAP ────────────────────────────────────────────────────────────────
draft = data.get("draft")
if draft is not None and not draft.empty:
    szn_draft = draft[draft["season"] == season]
    if not szn_draft.empty:
        st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)
        st.markdown(
            '<div class="tl-section-label">Auction Draft</div>'
            '<div class="tl-section-title">Draft Recap</div>',
            unsafe_allow_html=True,
        )

        keepers_this_yr  = szn_draft[szn_draft["is_keeper"] == True]
        freshly_drafted  = szn_draft[szn_draft["is_keeper"] != True]
        total_spend      = szn_draft["auction_price"].sum()
        keeper_spend     = int(keepers_this_yr["auction_price"].sum())
        fresh_spend      = total_spend - keeper_spend

        d1, d2, d3, d4 = st.columns(4)
        from utils.styles import metric_card as mc
        with d1:
            st.markdown(mc(str(len(keepers_this_yr)), "Keepers Rostered"), unsafe_allow_html=True)
        with d2:
            st.markdown(mc(str(len(freshly_drafted)), "Freshly Drafted"), unsafe_allow_html=True)
        with d3:
            st.markdown(mc(f"${int(keeper_spend):,}", "$ Spent on Keepers"), unsafe_allow_html=True)
        with d4:
            st.markdown(mc(f"${int(fresh_spend):,}", "$ Spent on Auction"), unsafe_allow_html=True)

        if season > 2018:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:0.6rem;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Kept Players This Season</div>',
                unsafe_allow_html=True,
            )
            pos = data.get("player_positions")
            pos_map = pos.set_index("player_name")["position"].to_dict() if pos is not None else {}
            k_rows = []
            for _, row in keepers_this_yr.sort_values("auction_price", ascending=False).iterrows():
                mgr = tnh_szn.get(row["team_name"], row["team_name"])
                k_rows.append([
                    str(row["player_name"]),
                    pos_map.get(row["player_name"], "?"),
                    f"{MANAGER_EMOJI.get(mgr, '👤')} {mgr}",
                    (f"${int(row['auction_price'])}", "gold"),
                ])
            if k_rows:
                st.markdown(html_table(["Player", "Pos", "Manager", "Keeper Cost"], k_rows), unsafe_allow_html=True)

render_page_footer(
    href="/champions",
    cta="VIEW ALL CHAMPIONS",
    tagline="EVERY SEASON.<br>EVERY MOMENT.<br>EVERY CHAMPION.",
)
