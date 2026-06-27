"""Keeper Hall — the signature exhibit of A New Dynasty."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.data import (
    load_all, get_keeper_chains, get_keeper_history,
    get_player_market_history, get_champions,
    MANAGER_EMOJI, MANAGER_COLORS, CURRENT_SEASON, FOUNDED,
)
from utils.styles import inject_css, render_nav, render_page_footer, metric_card, html_table

st.set_page_config(
    page_title="Keeper Hall · A New Dynasty",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("keeper_hall")

data     = load_all()
chains   = get_keeper_chains()
keepers  = get_keeper_history()
champions = get_champions()
tnh      = data["team_name_history"]

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-hero">
        <div class="tl-hero-title">KEEPER HALL</div>
        <div class="tl-hero-subtitle">Seven years of loyalty, rising costs, and the players nobody could let go.</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#B8C3B5;
                    margin-top:1.1rem;letter-spacing:1px;font-style:italic;line-height:1.8;">
            In an auction league, every keeper tells a story about trust.
        </div>
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── HERO METRICS ──────────────────────────────────────────────────────────────
total_keepers   = len(keepers)
total_chains    = len(chains)
longest_chain   = int(chains["keeper_seasons"].max()) if not chains.empty else 0
keeper_seasons  = keepers["season"].nunique()
most_loyal_mgr  = (
    keepers.groupby("manager")["player_name"].count().idxmax()
    if not keepers.empty else "—"
)
cheapest_longest = chains.sort_values("keeper_seasons", ascending=False).iloc[0] if not chains.empty else None

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card(str(total_keepers), "Keeper Slots Used"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card(str(keeper_seasons), "Seasons Tracked"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card(str(longest_chain), "Max Seasons Kept"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card(MANAGER_EMOJI.get(most_loyal_mgr,"") + " " + most_loyal_mgr, "Most Keepers Used"), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── HALL OF FAME: LONGEST CHAINS ─────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">The Greatest Keeper Stories</div>'
    '<div class="tl-section-title">Keeper Hall of Fame</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#B8C3B5;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Players kept for the most consecutive seasons — the ultimate test of loyalty and value.</p>',
    unsafe_allow_html=True,
)

def _chain_card(chain_row, rank: int):
    player   = chain_row["player_name"]
    mgr      = chain_row["manager"]
    pos      = chain_row["position"]
    seasons  = chain_row["seasons"]
    prices   = chain_row["prices"]
    n_kept   = chain_row["keeper_seasons"]
    orig_yr  = chain_row["original_season"]
    orig_p   = chain_row["original_price"]
    total_sp = chain_row["total_spend"]
    color    = MANAGER_COLORS.get(mgr, "#6B7280")
    emoji    = MANAGER_EMOJI.get(mgr, "👤")
    border   = "2px solid #D4AF37" if rank == 1 else f"1px solid {color}40"

    # Build the price timeline
    timeline_html = ""
    for i, (szn, prc) in enumerate(zip(seasons, prices)):
        is_orig = not chain_row["seasons_is_keeper"][i] if "seasons_is_keeper" in chain_row else (i == 0)
        tag = "ORIG" if i == 0 else "KEPT"
        tag_color = "#B8C3B5" if i == 0 else "#D4AF37"
        timeline_html += (
            f'<div style="text-align:center;padding:0 6px;">'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.52rem;color:{tag_color};letter-spacing:2px;">{tag}</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.9rem;color:#F5F3EA;letter-spacing:1px;">{szn}</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;color:#D4AF37;">${prc}</div>'
            f'</div>'
        )
        if i < len(seasons) - 1:
            timeline_html += '<div style="color:#B8C3B5;font-size:0.75rem;padding-top:16px;">→</div>'

    return f"""
    <div style="background:#102418;border:{border};border-radius:8px;padding:20px 24px;margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:14px;">
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:0.55rem;color:#B8C3B5;letter-spacing:3px;text-transform:uppercase;">{"🥇" if rank==1 else f"#{rank}"} Keeper Chain · {pos}</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#F5F3EA;letter-spacing:2px;line-height:1.1;">{player}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.8rem;color:{color};margin-top:2px;">{emoji} {mgr}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2.5rem;color:#D4AF37;letter-spacing:2px;line-height:1;">{n_kept}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.55rem;color:#B8C3B5;letter-spacing:2px;">KEEPER SEASONS</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.7rem;color:#6B7280;margin-top:4px;">Total invested: ${total_sp}</div>
            </div>
        </div>
        <div style="display:flex;align-items:center;flex-wrap:wrap;gap:2px;background:rgba(0,0,0,0.2);border-radius:6px;padding:10px 12px;">
            {timeline_html}
        </div>
    </div>
    """

if not chains.empty:
    top_chains = chains.head(9)
    for rank_i, (_, row) in enumerate(top_chains.iterrows(), 1):
        st.markdown(_chain_card(row, rank_i), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FRANCHISE LOYALTY PROFILES ────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Who Kept the Most</div>'
    '<div class="tl-section-title">Franchise Keeper Profiles</div>',
    unsafe_allow_html=True,
)

if not keepers.empty:
    loyalty = (
        keepers.groupby("manager")
        .agg(
            total_keepers=("player_name", "count"),
            total_keeper_spend=("auction_price", "sum"),
            avg_keeper_cost=("auction_price", "mean"),
            seasons=("season", "nunique"),
        )
        .reset_index()
    )
    loyalty["keepers_per_season"] = (loyalty["total_keepers"] / loyalty["seasons"]).round(1)
    loyalty = loyalty.sort_values("total_keepers", ascending=False)

    # Bar visualization
    max_k = int(loyalty["total_keepers"].max())
    for _, row in loyalty.iterrows():
        mgr   = row["manager"]
        color = MANAGER_COLORS.get(mgr, "#6B7280")
        emoji = MANAGER_EMOJI.get(mgr, "👤")
        total = int(row["total_keepers"])
        spend = int(row["total_keeper_spend"])
        avg_c = round(float(row["avg_keeper_cost"]), 1)
        bar_w = int((total / max_k) * 200)
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
            f'<div style="width:140px;font-family:\'Inter\',sans-serif;font-size:0.78rem;color:#F5F3EA;text-align:right;">'
            f'{emoji} {mgr}</div>'
            f'<div style="height:22px;width:{bar_w}px;background:{color};border-radius:3px;min-width:2px;"></div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#B8C3B5;">'
            f'{total} keepers &nbsp;·&nbsp; ${spend} total &nbsp;·&nbsp; ${avg_c:.1f} avg</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── KEEPER COSTS BY SEASON ────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">League-Wide</div>'
    '<div class="tl-section-title">Keeper Economy Over Time</div>',
    unsafe_allow_html=True,
)

if not keepers.empty:
    draft_data = load_all().get("draft", pd.DataFrame())
    if not draft_data.empty:
        draft_data["auction_price"] = pd.to_numeric(draft_data["auction_price"], errors="coerce").fillna(0)
        szn_totals = draft_data.groupby("season").agg(
            total_spend=("auction_price", "sum"),
            keeper_spend=("auction_price", lambda x: x[draft_data.loc[x.index, "is_keeper"] == True].sum()),
        ).reset_index()

        # Use keepers df for keeper spend (cleaner)
        k_spend_by_yr = keepers.groupby("season")["auction_price"].sum().reset_index(name="keeper_spend")
        t_spend_by_yr = draft_data.groupby("season")["auction_price"].sum().reset_index(name="total_spend")
        econ = k_spend_by_yr.merge(t_spend_by_yr, on="season")
        econ["fresh_spend"] = econ["total_spend"] - econ["keeper_spend"]
        econ["keeper_pct"] = (econ["keeper_spend"] / econ["total_spend"] * 100).round(1)
        econ["avg_keeper"] = (econ["keeper_spend"] / keepers.groupby("season")["player_name"].count().values).round(1)

        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=econ["season"], y=econ["keeper_spend"],
                name="Keeper $", marker_color="#D4AF37",
            ))
            fig.add_trace(go.Bar(
                x=econ["season"], y=econ["fresh_spend"],
                name="Fresh Auction $", marker_color="#1D3A2A",
            ))
            fig.update_layout(
                barmode="stack",
                paper_bgcolor="#07120D", plot_bgcolor="#07120D",
                font=dict(family="Inter", color="#B8C3B5", size=11),
                xaxis=dict(tickmode="array", tickvals=list(econ["season"]), gridcolor="#1A3525", color="#B8C3B5"),
                yaxis=dict(gridcolor="#1A3525", color="#B8C3B5", title="Total League Spend ($)"),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#B8C3B5")),
                margin=dict(l=10, r=10, t=20, b=10),
                height=280,
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            pass

        econ_rows = []
        for _, row in econ.sort_values("season", ascending=False).iterrows():
            k_count = int(keepers[keepers["season"] == row["season"]]["player_name"].count())
            econ_rows.append([
                (str(int(row["season"])), "gold"),
                str(k_count),
                (f"${int(row['keeper_spend']):,}", "gold"),
                f"${int(row['fresh_spend']):,}",
                f"{row['keeper_pct']:.0f}%",
            ])
        st.markdown(html_table(["Season", "# Keepers", "Keeper Spend", "Fresh Spend", "% on Keepers"], econ_rows), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── MOST EXPENSIVE KEEPER CHAINS ─────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">The Price of Loyalty</div>'
    '<div class="tl-section-title">Highest Total Investment in a Single Player</div>',
    unsafe_allow_html=True,
)

if not chains.empty:
    expensive = chains.sort_values("total_spend", ascending=False).head(10)
    exp_rows = []
    for _, row in expensive.iterrows():
        price_str = " → ".join(f"${p}" for p in row["prices"])
        exp_rows.append([
            row["player_name"],
            row["position"],
            f"{MANAGER_EMOJI.get(row['manager'],'')} {row['manager']}",
            (f"${row['total_spend']}", "gold"),
            str(row["original_season"]),
            (f"${row['original_price']}", "muted"),
            str(row["keeper_seasons"]),
            (price_str, "muted"),
        ])
    st.markdown(
        html_table(["Player", "Pos", "Manager", "Total Invested", "Since", "Orig $", "Yrs Kept", "Price Chain"], exp_rows),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── POSITION BREAKDOWN ────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">What Gets Kept</div>'
    '<div class="tl-section-title">Keepers by Position</div>',
    unsafe_allow_html=True,
)

if not keepers.empty:
    pos_breakdown = keepers[keepers["position"].isin(["QB","RB","WR","TE"])].groupby(["position","season"])["player_name"].count().unstack(fill_value=0)
    pos_totals    = keepers[keepers["position"].isin(["QB","RB","WR","TE"])].groupby("position").agg(
        count=("player_name","count"),
        avg_price=("auction_price","mean"),
        total_spend=("auction_price","sum"),
    ).reset_index().sort_values("count", ascending=False)

    p_cols = st.columns(4)
    pos_colors = {"QB": "#D4AF37", "RB": "#3FA66B", "WR": "#EC4899", "TE": "#10B981"}
    for col, (_, prow) in zip(p_cols, pos_totals.iterrows()):
        pc = pos_colors.get(prow["position"], "#6B7280")
        with col:
            st.markdown(
                f'<div style="background:#102418;border:1px solid {pc}40;border-top:3px solid {pc};'
                f'border-radius:6px;padding:14px;text-align:center;">'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:{pc};letter-spacing:2px;">{prow["position"]}</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.5rem;color:#F5F3EA;">{int(prow["count"])}</div>'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#B8C3B5;letter-spacing:2px;text-transform:uppercase;">keepers</div>'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:#B8C3B5;margin-top:6px;">${prow["avg_price"]:.1f} avg · ${int(prow["total_spend"]):,} total</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── MARKET VALUE EXPLORER ─────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Follow Any Player</div>'
    '<div class="tl-section-title">Market Value Explorer</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#B8C3B5;font-size:0.78rem;margin:-0.5rem 0 1.2rem;">'
    'Pick any player to see their complete auction history — who had them, at what price, and every time they changed hands.</p>',
    unsafe_allow_html=True,
)

draft = load_all().get("draft", pd.DataFrame())
all_players = sorted(draft["player_name"].dropna().unique().tolist()) if not draft.empty else []
selected_player = st.selectbox("SELECT PLAYER", options=all_players, index=0)

if selected_player:
    history = get_player_market_history(selected_player)
    if not history.empty:
        # Build the visual journey
        journey_html = '<div style="display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:16px 0;">'
        prev_mgr = None
        for _, hrow in history.iterrows():
            mgr       = hrow["manager"]
            szn       = int(hrow["season"])
            price     = int(hrow["auction_price"])
            is_keeper = bool(hrow["is_keeper"])
            color     = MANAGER_COLORS.get(mgr, "#6B7280")
            emoji     = MANAGER_EMOJI.get(mgr, "👤")
            tag       = "KEPT" if is_keeper else ("TRADED" if (prev_mgr and prev_mgr != mgr) else "DRAFTED")
            tag_color = "#D4AF37" if is_keeper else ("#A78BFA" if tag == "TRADED" else "#3FA66B")

            if prev_mgr and prev_mgr != mgr:
                journey_html += '<div style="color:#B8C3B5;font-size:1.2rem;padding:0 4px;">↔</div>'
            elif prev_mgr:
                journey_html += '<div style="color:#B8C3B5;font-size:0.8rem;padding:0 2px;">→</div>'

            journey_html += (
                f'<div style="background:#102418;border:1px solid {color}60;border-radius:6px;padding:8px 12px;text-align:center;min-width:80px;">'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.5rem;color:{tag_color};letter-spacing:2px;">{tag}</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F5F3EA;">{szn}</div>'
                f'<div style="font-size:0.8rem;">{emoji}</div>'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.65rem;color:{color};">{mgr}</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;color:#D4AF37;">${price}</div>'
                f'</div>'
            )
            prev_mgr = mgr

        journey_html += '</div>'
        st.markdown(journey_html, unsafe_allow_html=True)

        # Summary stats
        player_chain = chains[chains["player_name"] == selected_player]
        if not player_chain.empty:
            c = player_chain.iloc[0]
            st.markdown(
                f'<div style="background:#102418;border:1px solid #1A3525;border-left:4px solid #D4AF37;'
                f'border-radius:6px;padding:12px 16px;max-width:600px;">'
                f'<span style="font-family:\'Inter\',sans-serif;font-size:0.65rem;color:#B8C3B5;">Original acquisition: </span>'
                f'<span style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#F5F3EA;">'
                f'${c["original_price"]} in {c["original_season"]} by {MANAGER_EMOJI.get(c["manager"],"")} {c["manager"]}</span>'
                f'&nbsp; &nbsp; <span style="font-family:\'Inter\',sans-serif;font-size:0.65rem;color:#B8C3B5;">Keeper seasons: </span>'
                f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:0.9rem;color:#D4AF37;">{c["keeper_seasons"]}</span>'
                f'&nbsp; &nbsp; <span style="font-family:\'Inter\',sans-serif;font-size:0.65rem;color:#B8C3B5;">Total invested: </span>'
                f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:0.9rem;color:#D4AF37;">${c["total_spend"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info(f"No auction history found for {selected_player}.")

render_page_footer(
    href="/draft_center",
    cta="EXPLORE DRAFT CENTER",
    tagline="HOW THE MARKET MOVED.<br>HOW OWNERS SPENT.<br>WHO GOT THE STEAL.",
)
