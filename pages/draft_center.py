"""Draft Center — Auction Economics of A New Dynasty."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.data import (
    load_all, get_auction_data, get_keeper_chains, get_keeper_history,
    MANAGER_EMOJI, MANAGER_COLORS, CURRENT_SEASON, FOUNDED,
)
from utils.styles import inject_css, render_nav, render_page_footer, metric_card, html_table

st.set_page_config(
    page_title="Draft Center · A New Dynasty",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("draft_center")

data    = load_all()
draft   = get_auction_data()
keepers = get_keeper_history()
chains  = get_keeper_chains()

POSITIONS = ["QB", "RB", "WR", "TE"]
POS_COLORS = {"QB": "#D4AF37", "RB": "#60A5FA", "WR": "#EC4899", "TE": "#10B981", "K": "#6B7280", "DEF": "#6B7280"}
seasons_played = sorted(draft["season"].unique().tolist()) if not draft.empty else []

# Pre-compute fresh (non-keeper) picks
fresh = draft[draft["is_keeper"] != True].copy() if not draft.empty else pd.DataFrame()

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-hero">
        <div class="tl-hero-title">DRAFT CENTER</div>
        <div class="tl-hero-subtitle">Snake drafts tell you who was available. Auction drafts tell you what people actually believe.</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#A7B0BC;
                    margin-top:1.1rem;letter-spacing:1px;font-style:italic;line-height:1.8;">
            Seven years of bids, budgets, and the economics of belief.
        </div>
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── HERO METRICS ──────────────────────────────────────────────────────────────
total_picks     = len(draft) if not draft.empty else 0
total_spent     = int(draft["auction_price"].sum()) if not draft.empty else 0
fresh_picks     = len(fresh)
avg_pick_price  = round(float(draft["auction_price"].mean()), 1) if not draft.empty else 0
highest_bid_row = draft.loc[draft["auction_price"].idxmax()] if not draft.empty else None
highest_bid_str = (
    f"${int(highest_bid_row['auction_price'])} — {highest_bid_row['player_name']}"
    if highest_bid_row is not None else "—"
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card(f"${total_spent:,}", "Total Auction Spend"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card(str(total_picks), "Total Picks Made"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card(f"${avg_pick_price}", "Average Pick Price"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card(highest_bid_str, "Highest Single Bid"), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 1 — LEAGUE ECONOMICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">Chapter 1</div>'
    '<div class="tl-section-title">League Economics</div>'
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'How has the auction market evolved? Where does the league\'s money actually go?</p>',
    unsafe_allow_html=True,
)

if not draft.empty:
    try:
        import plotly.graph_objects as go

        # Position spending by season (stacked bar)
        pos_spend = (
            draft[draft["position"].isin(POSITIONS)]
            .groupby(["season", "position"])["auction_price"]
            .sum()
            .reset_index()
        )

        fig1 = go.Figure()
        for pos in POSITIONS:
            pdata = pos_spend[pos_spend["position"] == pos]
            fig1.add_trace(go.Bar(
                x=pdata["season"], y=pdata["auction_price"],
                name=pos, marker_color=POS_COLORS.get(pos, "#6B7280"),
            ))
        fig1.update_layout(
            barmode="stack",
            paper_bgcolor="#081120", plot_bgcolor="#081120",
            font=dict(family="Inter", color="#A7B0BC", size=11),
            xaxis=dict(tickmode="array", tickvals=seasons_played, gridcolor="#1E2D40", color="#A7B0BC"),
            yaxis=dict(gridcolor="#1E2D40", color="#A7B0BC", title="Total Spend ($)"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#A7B0BC"), orientation="h", y=1.05),
            margin=dict(l=10, r=10, t=30, b=10),
            height=300,
            title=dict(text="Where the Money Goes — Spend by Position", font=dict(color="#A7B0BC", size=12), x=0),
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Average price by position per season
        pos_avg = (
            draft[draft["position"].isin(POSITIONS)]
            .groupby(["season", "position"])["auction_price"]
            .mean()
            .reset_index()
        )

        fig2 = go.Figure()
        for pos in POSITIONS:
            pdata = pos_avg[pos_avg["position"] == pos]
            fig2.add_trace(go.Scatter(
                x=pdata["season"], y=pdata["auction_price"].round(1),
                name=pos, mode="lines+markers",
                line=dict(color=POS_COLORS.get(pos, "#6B7280"), width=2),
                marker=dict(size=6),
            ))
        fig2.update_layout(
            paper_bgcolor="#081120", plot_bgcolor="#081120",
            font=dict(family="Inter", color="#A7B0BC", size=11),
            xaxis=dict(tickmode="array", tickvals=seasons_played, gridcolor="#1E2D40", color="#A7B0BC"),
            yaxis=dict(gridcolor="#1E2D40", color="#A7B0BC", title="Average Price ($)"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#A7B0BC"), orientation="h", y=1.05),
            margin=dict(l=10, r=10, t=30, b=10),
            height=300,
            title=dict(text="Position Inflation — Average Price Per Season", font=dict(color="#A7B0BC", size=12), x=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    except ImportError:
        st.info("Install plotly for auction charts.")

    # Spend summary table
    pos_summary = (
        draft[draft["position"].isin(POSITIONS)]
        .groupby("position")
        .agg(
            picks=("player_name", "count"),
            total=("auction_price", "sum"),
            avg=("auction_price", "mean"),
            max=("auction_price", "max"),
        )
        .reset_index()
        .sort_values("total", ascending=False)
    )
    total_known = pos_summary["total"].sum()
    sum_rows = []
    for _, row in pos_summary.iterrows():
        pct = row["total"] / total_known * 100
        bar = "█" * int(pct / 4)
        sum_rows.append([
            (row["position"], "gold"),
            f"{int(row['picks'])}",
            (f"${int(row['total']):,}", "gold"),
            f"${row['avg']:.1f}",
            f"${int(row['max'])}",
            f"{pct:.1f}%  {bar}",
        ])
    st.markdown(
        html_table(["Position", "Picks", "Total Spend", "Avg Bid", "Top Bid", "Share of Spend"], sum_rows),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 2 — OWNER PERSONALITIES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">Chapter 2</div>'
    '<div class="tl-section-title">Owner Personalities</div>'
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Everyone has a draft philosophy. This is where it shows.</p>',
    unsafe_allow_html=True,
)

if not fresh.empty:
    # Stars & Scrubs vs Balanced: compare top-3 spend to rest
    mgr_spending = []
    for mgr in fresh["manager"].unique():
        mgr_picks = fresh[fresh["manager"] == mgr].sort_values("auction_price", ascending=False)
        seasons   = mgr_picks["season"].nunique()
        top3_avg  = mgr_picks.groupby("season")["auction_price"].nlargest(3).groupby(level=0).sum().mean()
        all_avg   = mgr_picks.groupby("season")["auction_price"].sum().mean()
        leftover  = 200 - all_avg  # approximate
        picks_at_1 = (mgr_picks["auction_price"] == 1).sum()
        pct_at_1  = picks_at_1 / len(mgr_picks) * 100
        mgr_spending.append({
            "manager": mgr,
            "seasons": seasons,
            "avg_top3_spend": round(float(top3_avg), 1),
            "avg_total_spend": round(float(all_avg), 1),
            "avg_leftover": round(float(leftover), 1),
            "picks_at_$1": int(picks_at_1),
            "pct_$1": round(float(pct_at_1), 1),
            "top3_pct_of_budget": round(float(top3_avg) / 200 * 100, 1),
        })
    mgr_df = pd.DataFrame(mgr_spending).sort_values("avg_top3_spend", ascending=False)

    # Personality label
    def draft_archetype(row) -> str:
        if row["top3_pct_of_budget"] >= 60:
            return "Stars & Scrubs"
        elif row["top3_pct_of_budget"] <= 40:
            return "Balanced Builder"
        elif row["pct_$1"] >= 40:
            return "Thrifty Strategist"
        else:
            return "The Pragmatist"

    mgr_df["archetype"] = mgr_df.apply(draft_archetype, axis=1)

    try:
        import plotly.graph_objects as go

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=mgr_df["manager"],
            y=mgr_df["avg_top3_spend"],
            name="Top-3 Star Spend",
            marker_color=[MANAGER_COLORS.get(m, "#6B7280") for m in mgr_df["manager"]],
        ))
        fig3.add_trace(go.Bar(
            x=mgr_df["manager"],
            y=mgr_df["avg_total_spend"] - mgr_df["avg_top3_spend"],
            name="Rest of Roster",
            marker_color=["rgba(107,114,128,0.35)"] * len(mgr_df),
        ))
        fig3.update_layout(
            barmode="stack",
            paper_bgcolor="#081120", plot_bgcolor="#081120",
            font=dict(family="Inter", color="#A7B0BC", size=11),
            xaxis=dict(gridcolor="#1E2D40", color="#A7B0BC"),
            yaxis=dict(gridcolor="#1E2D40", color="#A7B0BC", title="Avg Auction Spend Per Season ($)"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#A7B0BC"), orientation="h", y=1.05),
            margin=dict(l=10, r=10, t=30, b=80),
            height=320,
            title=dict(text="Stars & Scrubs vs Balanced — Average Fresh Auction Spend (Per Season)", font=dict(color="#A7B0BC", size=12), x=0),
        )
        fig3.update_xaxes(tickangle=25)
        st.plotly_chart(fig3, use_container_width=True)
    except ImportError:
        pass

    archetype_colors = {
        "Stars & Scrubs": "#D4AF37",
        "Balanced Builder": "#60A5FA",
        "Thrifty Strategist": "#10B981",
        "The Pragmatist": "#A7B0BC",
    }

    arch_rows = []
    for _, row in mgr_df.iterrows():
        a_color = archetype_colors.get(row["archetype"], "#6B7280")
        arch_rows.append([
            f'{MANAGER_EMOJI.get(row["manager"], "")} {row["manager"]}',
            (row["archetype"], "gold" if "Stars" in row["archetype"] else ""),
            f'${row["avg_top3_spend"]:.0f} ({row["top3_pct_of_budget"]:.0f}% of budget)',
            f'${row["avg_leftover"]:.0f} avg unused',
            f'{row["picks_at_$1"]} picks ({row["pct_$1"]:.0f}%)',
        ])
    st.markdown(
        html_table(["Manager", "Draft Style", "Star Spend (Top 3)", "Budget Left", "$1 Pickups"], arch_rows),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 3 — KEEPER LEGENDS (summary; full detail in Keeper Hall)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">Chapter 3</div>'
    '<div class="tl-section-title">Keeper Legends</div>'
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'The longest relationships in the league. Players someone refused to let go.</p>',
    unsafe_allow_html=True,
)

if not chains.empty:
    # Top chains by years kept
    showcase = chains.head(6)
    cols = st.columns(3)
    for i, (_, row) in enumerate(showcase.iterrows()):
        mgr     = row["manager"]
        player  = row["player_name"]
        n_kept  = row["keeper_seasons"]
        orig_p  = row["original_price"]
        final_p = row["final_price"]
        total   = row["total_spend"]
        color   = MANAGER_COLORS.get(mgr, "#6B7280")
        emoji   = MANAGER_EMOJI.get(mgr, "👤")
        seasons_list = row["seasons"]
        prices_list  = row["prices"]
        chain_str = " → ".join(f"${p}" for p in prices_list)
        with cols[i % 3]:
            st.markdown(
                f'<div style="background:#0F1B2D;border:1px solid {color}40;border-top:2px solid {color};'
                f'border-radius:6px;padding:14px;margin-bottom:10px;height:165px;">'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.52rem;color:#A7B0BC;letter-spacing:2px;text-transform:uppercase;">Kept {n_kept} years</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.3rem;color:#F5F5F5;letter-spacing:2px;line-height:1.2;margin:3px 0;">{player}</div>'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.7rem;color:{color};margin-bottom:8px;">{emoji} {mgr}</div>'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#A7B0BC;">${orig_p} original → ${final_p} final</div>'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#D4AF37;margin-top:3px;">{chain_str}</div>'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#6B7280;margin-top:5px;">${total} total invested</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

st.markdown(
    '<div style="text-align:center;padding:12px 0;">'
    '<a href="/keeper_hall" style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#D4AF37;'
    'letter-spacing:2px;text-decoration:none;border:1px solid #D4AF37;padding:8px 20px;border-radius:4px;">'
    '→ FULL KEEPER HALL OF FAME</a></div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 4 — BIGGEST BIDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">Chapter 4</div>'
    '<div class="tl-section-title">The Biggest Bids</div>'
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'The moments when someone said: this player is worth everything.</p>',
    unsafe_allow_html=True,
)

if not fresh.empty:
    top_bids = fresh.sort_values("auction_price", ascending=False).head(20)
    bid_rows = []
    for _, row in top_bids.iterrows():
        mgr = row.get("manager", "—")
        pos = row.get("position", "—")
        bid_rows.append([
            (f"${int(row['auction_price'])}", "gold"),
            row["player_name"],
            pos,
            f'{MANAGER_EMOJI.get(mgr, "")} {mgr}',
            str(int(row["season"])),
        ])
    st.markdown(
        html_table(["Bid", "Player", "Pos", "Manager", "Season"], bid_rows),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 5 — AUCTION ECONOMICS BY MANAGER (per-season budget allocation)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">Chapter 5</div>'
    '<div class="tl-section-title">Owner Spending by Season</div>'
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'How much each manager spent — on keepers vs. fresh auction picks — across every draft.</p>',
    unsafe_allow_html=True,
)

if not draft.empty:
    mgr_szn = (
        draft.groupby(["manager", "season", "is_keeper"])["auction_price"]
        .sum()
        .reset_index()
    )

    try:
        import plotly.graph_objects as go

        # Pivot so we can plot keeper vs fresh per manager per season
        # Use a faceted chart — but that's complex in plotly without express.
        # Instead: dropdown selector per manager.
        all_mgrs_sorted = sorted(draft["manager"].unique().tolist())
        selected_mgr = st.selectbox("SELECT MANAGER", options=all_mgrs_sorted, key="owner_spending_mgr")

        mgr_data = draft[draft["manager"] == selected_mgr].copy()
        mgr_szn_pivot = mgr_data.groupby(["season", "is_keeper"])["auction_price"].sum().unstack(fill_value=0)
        keeper_col = True if True in mgr_szn_pivot.columns else None
        fresh_col  = False if False in mgr_szn_pivot.columns else None

        fig4 = go.Figure()
        if keeper_col is not None:
            fig4.add_trace(go.Bar(
                x=mgr_szn_pivot.index, y=mgr_szn_pivot[True],
                name="Keepers", marker_color="#D4AF37",
            ))
        if fresh_col is not None:
            fig4.add_trace(go.Bar(
                x=mgr_szn_pivot.index, y=mgr_szn_pivot[False],
                name="Fresh Auction", marker_color=MANAGER_COLORS.get(selected_mgr, "#1E3A5F"),
            ))
        fig4.update_layout(
            barmode="stack",
            paper_bgcolor="#081120", plot_bgcolor="#081120",
            font=dict(family="Inter", color="#A7B0BC", size=11),
            xaxis=dict(tickmode="array", tickvals=seasons_played, gridcolor="#1E2D40", color="#A7B0BC"),
            yaxis=dict(gridcolor="#1E2D40", color="#A7B0BC", title="$ Spent"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#A7B0BC"), orientation="h", y=1.05),
            margin=dict(l=10, r=10, t=30, b=10),
            height=260,
        )
        st.plotly_chart(fig4, use_container_width=True)

        # Manager summary stats
        mgr_szn_by_yr = mgr_data.groupby("season").agg(
            total=("auction_price", "sum"),
            picks=("player_name", "count"),
            top_pick=("auction_price", "max"),
            top_player=("player_name", lambda x: x.loc[mgr_data.loc[x.index, "auction_price"].idxmax()]),
            keepers=("is_keeper", "sum"),
        ).reset_index().sort_values("season", ascending=False)

        detail_rows = []
        for _, row in mgr_szn_by_yr.iterrows():
            ks = int(row["keepers"])
            detail_rows.append([
                (str(int(row["season"])), "gold"),
                f"${int(row['total'])}",
                str(int(row["picks"])),
                (f"${int(row['top_pick'])} — {row['top_player']}", "gold"),
                str(ks),
            ])
        st.markdown(
            html_table(["Season", "Total Spent", "Total Picks", "Top Bid", "Keepers"], detail_rows),
            unsafe_allow_html=True,
        )

    except ImportError:
        st.info("Install plotly for spending charts.")

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 6 — HISTORICAL TRENDS / MARKET VALUE EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">Chapter 6</div>'
    '<div class="tl-section-title">Market Value Explorer</div>'
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Pick any player. See how the league valued them — every bid, every keeper, every time they changed hands.</p>',
    unsafe_allow_html=True,
)

from utils.data import get_player_market_history

if not draft.empty:
    all_players = sorted(draft["player_name"].dropna().unique().tolist())
    selected_player = st.selectbox("SELECT PLAYER", options=all_players, key="market_explorer")

    if selected_player:
        history = get_player_market_history(selected_player)
        if not history.empty:
            try:
                import plotly.graph_objects as go

                fig5 = go.Figure()
                keeper_rows = history[history["is_keeper"] == True]
                fresh_rows  = history[history["is_keeper"] != True]

                if not fresh_rows.empty:
                    fig5.add_trace(go.Scatter(
                        x=fresh_rows["season"], y=fresh_rows["auction_price"],
                        mode="markers",
                        name="Auction Bid",
                        marker=dict(color="#60A5FA", size=14, symbol="circle"),
                        text=[f'{MANAGER_EMOJI.get(m,"")} {m}' for m in fresh_rows["manager"]],
                        hovertemplate="<b>%{text}</b><br>%{x}: $%{y}<extra></extra>",
                    ))
                if not keeper_rows.empty:
                    fig5.add_trace(go.Scatter(
                        x=keeper_rows["season"], y=keeper_rows["auction_price"],
                        mode="markers",
                        name="Keeper Cost",
                        marker=dict(color="#D4AF37", size=14, symbol="diamond"),
                        text=[f'{MANAGER_EMOJI.get(m,"")} {m}' for m in keeper_rows["manager"]],
                        hovertemplate="<b>%{text}</b><br>%{x} (keeper): $%{y}<extra></extra>",
                    ))
                # Connect same-manager chains
                for mgr in history["manager"].unique():
                    mgr_h = history[history["manager"] == mgr].sort_values("season")
                    if len(mgr_h) > 1:
                        fig5.add_trace(go.Scatter(
                            x=mgr_h["season"], y=mgr_h["auction_price"],
                            mode="lines",
                            line=dict(color=MANAGER_COLORS.get(mgr, "#6B7280"), width=1.5, dash="dot"),
                            showlegend=False,
                        ))

                fig5.update_layout(
                    paper_bgcolor="#081120", plot_bgcolor="#081120",
                    font=dict(family="Inter", color="#A7B0BC", size=11),
                    xaxis=dict(tickmode="array", tickvals=seasons_played, gridcolor="#1E2D40", color="#A7B0BC", title="Season"),
                    yaxis=dict(gridcolor="#1E2D40", color="#A7B0BC", title="Price ($)"),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#A7B0BC")),
                    margin=dict(l=10, r=10, t=20, b=10),
                    height=280,
                )
                st.plotly_chart(fig5, use_container_width=True)
            except ImportError:
                pass

            # Timeline cards
            journey_html = '<div style="display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:12px 0;">'
            prev_mgr = None
            for _, hrow in history.iterrows():
                mgr       = hrow["manager"]
                szn       = int(hrow["season"])
                price     = int(hrow["auction_price"])
                is_keeper = bool(hrow["is_keeper"])
                color     = MANAGER_COLORS.get(mgr, "#6B7280")
                emoji     = MANAGER_EMOJI.get(mgr, "👤")
                tag       = "KEPT" if is_keeper else ("TRADED" if (prev_mgr and prev_mgr != mgr) else "DRAFTED")
                tag_color = "#D4AF37" if is_keeper else ("#A78BFA" if tag == "TRADED" else "#60A5FA")

                if prev_mgr is not None:
                    arrow = "↔" if prev_mgr != mgr else "→"
                    journey_html += f'<div style="color:#A7B0BC;font-size:{1.2 if arrow=="↔" else 0.8}rem;padding:0 2px;">{arrow}</div>'

                journey_html += (
                    f'<div style="background:#0F1B2D;border:1px solid {color}60;border-radius:6px;padding:8px 12px;text-align:center;min-width:80px;">'
                    f'<div style="font-family:\'Inter\',sans-serif;font-size:0.5rem;color:{tag_color};letter-spacing:2px;">{tag}</div>'
                    f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F5F5F5;">{szn}</div>'
                    f'<div style="font-size:0.8rem;">{emoji}</div>'
                    f'<div style="font-family:\'Inter\',sans-serif;font-size:0.65rem;color:{color};">{mgr}</div>'
                    f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;color:#D4AF37;">${price}</div>'
                    f'</div>'
                )
                prev_mgr = mgr

            journey_html += '</div>'
            st.markdown(journey_html, unsafe_allow_html=True)
        else:
            st.info(f"No auction history found for {selected_player}.")

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FULL DRAFT LOG
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="tl-section-label">The Archive</div>'
    '<div class="tl-section-title">Full Draft Log</div>',
    unsafe_allow_html=True,
)

if not draft.empty:
    season_opts = ["All Seasons"] + [str(int(s)) for s in sorted(draft["season"].unique(), reverse=True)]
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        szn_filter = st.selectbox("Season", options=season_opts, key="draft_log_season")
    with col_f2:
        mgr_opts = ["All Managers"] + sorted(draft["manager"].unique().tolist())
        mgr_filter = st.selectbox("Manager", options=mgr_opts, key="draft_log_mgr")

    filtered = draft.copy()
    if szn_filter != "All Seasons":
        filtered = filtered[filtered["season"] == int(szn_filter)]
    if mgr_filter != "All Managers":
        filtered = filtered[filtered["manager"] == mgr_filter]

    filtered = filtered.sort_values(["season", "auction_price"], ascending=[False, False])

    log_rows = []
    for _, row in filtered.head(100).iterrows():
        mgr = row.get("manager", "—")
        pos = row.get("position", "—")
        k_tag = "🔑" if row["is_keeper"] else ""
        log_rows.append([
            (str(int(row["season"])), "gold"),
            row["player_name"] + (" 🔑" if row["is_keeper"] else ""),
            pos,
            f'{MANAGER_EMOJI.get(mgr, "")} {mgr}',
            (f'${int(row["auction_price"])}', "gold"),
        ])
    st.markdown(html_table(["Season", "Player", "Pos", "Manager", "Price"], log_rows), unsafe_allow_html=True)
    if len(filtered) > 100:
        st.markdown(
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.7rem;color:#A7B0BC;text-align:center;padding:8px;">Showing first 100 of {len(filtered)} picks. Use filters above to narrow results.</div>',
            unsafe_allow_html=True,
        )

render_page_footer(
    href="/keeper_hall",
    cta="EXPLORE KEEPER HALL",
    tagline="THE PLAYERS THEY COULDN'T LET GO.<br>THE CHAINS THAT BUILT DYNASTIES.",
)
