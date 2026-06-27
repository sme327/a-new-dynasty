"""Central data loading and derived metrics for A New Dynasty."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

LEAGUE_NAME     = "A New Dynasty"
LEAGUE_SUBTITLE = "A Keeper League Built to Last"
FOUNDED         = 2018
CURRENT_SEASON  = 2025

MANAGER_COLORS: dict[str, str] = {
    "Shawn":          "#D4AF37",
    "Fadi":           "#F97316",
    "Evan":           "#EC4899",
    "Eric":           "#06B6D4",
    "Nick Blaettler": "#FB923C",
    "Bryan Kearney":  "#60A5FA",
    "Kevin O'Boyle":  "#10B981",
    "Kevin Swanson":  "#F59E0B",
    "Matt Riebel":    "#6D28D9",
    "Tom Urbanczyk":  "#14B8A6",
    "Roger Dillman":  "#4ADE80",
    "Dave Holmes":    "#D97706",
    "Al Anastos":     "#6366F1",
    "Jamie Patno":    "#94A3B8",
    "Karl":           "#84CC16",
    "Nate":           "#C084FC",
}

MANAGER_EMOJI: dict[str, str] = {
    "Shawn":          "🐝",
    "Fadi":           "👑",
    "Evan":           "🎉",
    "Eric":           "⛳",
    "Nick Blaettler": "🐱",
    "Bryan Kearney":  "💪",
    "Kevin O'Boyle":  "🍺",
    "Kevin Swanson":  "🧔",
    "Matt Riebel":    "🐦‍⬛",
    "Tom Urbanczyk":  "🦲",
    "Roger Dillman":  "🐕",
    "Dave Holmes":    "🥃",
    "Al Anastos":     "🎩",
    "Jamie Patno":    "⚽",
    "Karl":           "💎",
    "Nate":           "🎯",
}


@st.cache_data
def load_all() -> dict[str, pd.DataFrame]:
    _cache_bust = 1
    files = {
        "standings":         "season_standings.csv",
        "matchups":          "weekly_matchups.csv",
        "playoffs":          "playoff_games.csv",
        "draft":             "draft_picks.csv",
        "managers":          "managers.csv",
        "manager_lookup":    "manager_lookup.csv",
        "season_managers":   "season_managers.csv",
        "team_name_history": "team_name_history.csv",
        "franchise_history": "franchise_history.csv",
        "trades":            "season_trades.csv",
        "player_positions":  "player_positions.csv",
        "timeline_events":   "manual_timeline_events.csv",
        "league_settings":   "league_settings.csv",
    }
    result = {}
    for key, fname in files.items():
        path = DATA_DIR / fname
        if path.exists():
            result[key] = pd.read_csv(path)

    # Derive winner from scores (scraper leaves the column blank)
    if "playoffs" in result:
        pg = result["playoffs"].copy()
        pg["score_1"] = pd.to_numeric(pg["score_1"], errors="coerce")
        pg["score_2"] = pd.to_numeric(pg["score_2"], errors="coerce")
        pg["winner"] = pg.apply(
            lambda r: r["team_1"] if r["score_1"] > r["score_2"] else r["team_2"],
            axis=1,
        )
        result["playoffs"] = pg

    # Tag matchups with is_playoff using playoff week presence per season
    if "playoffs" in result and "matchups" in result:
        pg = result["playoffs"]
        playoff_weeks = set(zip(pg["season"].astype(int), pg["week"].astype(int)))
        wm = result["matchups"].copy()
        wm["is_bye"] = wm["is_bye"].fillna(False).astype(bool)
        wm["is_playoff"] = wm.apply(
            lambda r: (int(r["season"]), int(r["week"])) in playoff_weeks, axis=1
        )
        result["matchups"] = wm

    return result


@st.cache_data
def get_champions() -> pd.DataFrame:
    data = load_all()
    pg  = data.get("playoffs", pd.DataFrame())
    tnh = data.get("team_name_history", pd.DataFrame())
    if pg.empty:
        return pd.DataFrame()

    tnh_map = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

    finals = pg[
        (pg["game_type"] == "final") & (pg["bracket"] == "championship")
    ].copy()
    if finals.empty:
        return pd.DataFrame()

    def resolve(season, team):
        return tnh_map.get((int(season), team), team)

    finals["champion_team"]     = finals["winner"]
    finals["champion_manager"]  = finals.apply(lambda r: resolve(r["season"], r["winner"]), axis=1)
    finals["champion_score"]    = finals.apply(
        lambda r: float(r["score_1"]) if r["winner"] == r["team_1"] else float(r["score_2"]), axis=1
    )
    finals["runner_up_team"]    = finals.apply(
        lambda r: r["team_2"] if r["winner"] == r["team_1"] else r["team_1"], axis=1
    )
    finals["runner_up_manager"] = finals.apply(
        lambda r: resolve(r["season"], r["team_2"] if r["winner"] == r["team_1"] else r["team_1"]), axis=1
    )
    finals["runner_up_score"]   = finals.apply(
        lambda r: float(r["score_2"]) if r["winner"] == r["team_1"] else float(r["score_1"]), axis=1
    )

    return finals[[
        "season", "champion_team", "champion_manager", "champion_score",
        "runner_up_team", "runner_up_manager", "runner_up_score",
    ]].sort_values("season").reset_index(drop=True)


@st.cache_data
def get_manager_stats() -> pd.DataFrame:
    data        = load_all()
    std         = data.get("standings", pd.DataFrame())
    tnh         = data.get("team_name_history", pd.DataFrame())
    managers_df = data.get("managers", pd.DataFrame())
    pg          = data.get("playoffs", pd.DataFrame())
    if std.empty or managers_df.empty:
        return pd.DataFrame()

    champions = get_champions()

    # RS record from standings (already regular-season only from Yahoo)
    std_with_mgr = tnh.merge(std, on=["season", "team_name"], how="inner")
    record = (
        std_with_mgr.groupby("canonical_name")
        .apply(lambda g: pd.Series({
            "wins":       int(g["wins"].sum()),
            "losses":     int(g["losses"].sum()),
            "ties":       int(g["ties"].sum()),
            "points_for": round(g["points_for"].sum(), 2),
        }))
        .reset_index()
    )

    # Playoff appearances (distinct seasons in championship bracket)
    if not pg.empty:
        champ_pg = pg[pg["bracket"] == "championship"]
        team_playoff = pd.concat([
            champ_pg[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
            champ_pg[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
        ]).drop_duplicates()
        playoff_merged = tnh.merge(team_playoff, on=["season", "team_name"], how="inner")
        playoff_apps = (
            playoff_merged.groupby("canonical_name")["season"]
            .nunique().reset_index(name="playoff_apps")
        )
    else:
        playoff_apps = pd.DataFrame(columns=["canonical_name", "playoff_apps"])

    champ_counts = (
        champions.groupby("champion_manager").size()
        .reset_index(name="championships")
        .rename(columns={"champion_manager": "canonical_name"})
    ) if not champions.empty else pd.DataFrame(columns=["canonical_name", "championships"])

    ru_counts = (
        champions.groupby("runner_up_manager").size()
        .reset_index(name="runner_ups")
        .rename(columns={"runner_up_manager": "canonical_name"})
    ) if not champions.empty else pd.DataFrame(columns=["canonical_name", "runner_ups"])

    stats = managers_df[["canonical_name", "display_name", "first_season", "last_season", "seasons_played"]].copy()
    stats = stats.merge(record,       on="canonical_name", how="left")
    stats = stats.merge(playoff_apps, on="canonical_name", how="left")
    stats = stats.merge(champ_counts, on="canonical_name", how="left")
    stats = stats.merge(ru_counts,    on="canonical_name", how="left")

    for col in ["wins", "losses", "ties", "playoff_apps", "championships", "runner_ups"]:
        stats[col] = stats[col].fillna(0).astype(int)
    stats["points_for"] = stats["points_for"].fillna(0.0)

    total = stats["wins"] + stats["losses"] + stats["ties"]
    stats["win_pct"] = (stats["wins"] / total.replace(0, pd.NA)).round(3)
    stats["active"]  = stats["last_season"] == CURRENT_SEASON

    return stats.sort_values(["championships", "playoff_apps", "wins"], ascending=False).reset_index(drop=True)


def _playoff_result(season: int, team: str, pg: pd.DataFrame) -> str:
    games = pg[
        (pg["season"] == season) & (pg["bracket"] == "championship")
        & ((pg["team_1"] == team) | (pg["team_2"] == team))
    ]
    if len(games) == 0:
        return "—"
    if len(games[(games["game_type"] == "final") & (games["winner"] == team)]):
        return "🏆 Champion"
    if len(games[(games["game_type"] == "final") & (games["winner"] != team)]):
        return "🥈 Runner-Up"
    if len(games[(games["game_type"] == "3rd_place") & (games["winner"] == team)]):
        return "🥉 3rd Place"
    if len(games[(games["game_type"] == "3rd_place") & (games["winner"] != team)]):
        return "4th Place"
    if len(games[games["game_type"] == "semifinal"]):
        return "Semifinals"
    return "Playoffs"


def get_playoff_result_for_team(season: int, team: str, pg: pd.DataFrame) -> str:
    return _playoff_result(season, team, pg)


@st.cache_data
def get_manager_season_history(canonical_name: str) -> pd.DataFrame:
    data = load_all()
    tnh  = data.get("team_name_history", pd.DataFrame())
    std  = data.get("standings", pd.DataFrame())
    pg   = data.get("playoffs", pd.DataFrame())

    mgr_seasons = tnh[tnh["canonical_name"] == canonical_name].copy()
    results = []

    for _, row in mgr_seasons.iterrows():
        season = int(row["season"])
        team   = row["team_name"]

        szn_std = std[(std["season"] == season) & (std["team_name"] == team)]
        wins    = int(szn_std.iloc[0]["wins"])    if len(szn_std) > 0 else 0
        losses  = int(szn_std.iloc[0]["losses"])  if len(szn_std) > 0 else 0
        ties    = int(szn_std.iloc[0]["ties"])    if len(szn_std) > 0 else 0
        pf      = round(float(szn_std.iloc[0]["points_for"]),    2) if len(szn_std) > 0 else 0.0
        pa      = round(float(szn_std.iloc[0]["points_against"]),2) if len(szn_std) > 0 else 0.0
        rank    = int(szn_std.iloc[0]["rank"])    if len(szn_std) > 0 else None

        playoff_res = _playoff_result(season, team, pg) if not pg.empty else "—"

        results.append({
            "Season": season, "Team Name": team,
            "W": wins, "L": losses, "T": ties,
            "PF": pf, "PA": pa,
            "Rank": rank, "Result": playoff_res,
        })

    return pd.DataFrame(results).sort_values("Season", ascending=False).reset_index(drop=True)


@st.cache_data
def get_franchise_steward_periods() -> pd.DataFrame:
    data = load_all()
    fh   = data.get("franchise_history", pd.DataFrame())
    if fh.empty:
        return pd.DataFrame()
    fh = fh.sort_values(["franchise_id", "season"])

    periods = []
    for fid, group in fh.groupby("franchise_id"):
        current_mgr = start = prev_season = None
        for _, row in group.iterrows():
            mgr    = row["manager_name"]
            season = int(row["season"])
            if mgr != current_mgr:
                if current_mgr is not None:
                    periods.append({
                        "franchise_id": fid, "manager_name": current_mgr,
                        "start_season": start, "end_season": prev_season,
                        "years": prev_season - start + 1,
                    })
                current_mgr, start = mgr, season
            prev_season = season
        if current_mgr:
            periods.append({
                "franchise_id": fid, "manager_name": current_mgr,
                "start_season": start, "end_season": prev_season,
                "years": prev_season - start + 1,
            })

    return pd.DataFrame(periods)


@st.cache_data
def get_franchise_stats() -> pd.DataFrame:
    data      = load_all()
    fh        = data.get("franchise_history", pd.DataFrame())
    tnh       = data.get("team_name_history", pd.DataFrame())
    std       = data.get("standings", pd.DataFrame())
    pg        = data.get("playoffs", pd.DataFrame())
    champions = get_champions()
    if fh.empty:
        return pd.DataFrame()

    fh_tnh = fh.merge(
        tnh.rename(columns={"canonical_name": "manager_name"}),
        on=["season", "manager_name"], how="left",
    )

    std_merged = fh_tnh.merge(std, on=["season", "team_name"], how="inner")
    record = (
        std_merged.groupby("franchise_id")
        .apply(lambda g: pd.Series({
            "wins":   int(g["wins"].sum()),
            "losses": int(g["losses"].sum()),
            "ties":   int(g["ties"].sum()),
        }))
        .reset_index()
    )

    if not champions.empty:
        champ_teams = champions[["season", "champion_team"]].rename(columns={"champion_team": "team_name"})
        fh_champs   = fh_tnh.merge(champ_teams, on=["season", "team_name"], how="inner")
        champ_count = fh_champs.groupby("franchise_id").size().reset_index(name="championships")
    else:
        champ_count = pd.DataFrame(columns=["franchise_id", "championships"])

    if not pg.empty:
        champ_pg = pg[pg["bracket"] == "championship"]
        team_playoff = pd.concat([
            champ_pg[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
            champ_pg[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
        ]).drop_duplicates()
        playoff_merged = fh_tnh.merge(team_playoff, on=["season", "team_name"], how="inner")
        playoff_apps   = playoff_merged.groupby("franchise_id")["season"].nunique().reset_index(name="playoff_apps")
    else:
        playoff_apps = pd.DataFrame(columns=["franchise_id", "playoff_apps"])

    established = fh.groupby("franchise_id")["season"].min().reset_index(name="established")
    current_mgr = (
        fh[fh["season"] == CURRENT_SEASON][["franchise_id", "manager_name"]]
        .rename(columns={"manager_name": "current_manager"})
    )

    stats = established.merge(current_mgr, on="franchise_id", how="left")
    for df in [record, champ_count, playoff_apps]:
        stats = stats.merge(df, on="franchise_id", how="left")

    for col in ["wins", "losses", "ties", "championships", "playoff_apps"]:
        stats[col] = stats[col].fillna(0).astype(int)

    total = stats["wins"] + stats["losses"] + stats["ties"]
    stats["win_pct"] = (stats["wins"] / total.replace(0, pd.NA)).round(3)
    stats["seasons"] = CURRENT_SEASON - stats["established"].astype(int) + 1

    return stats.sort_values("franchise_id").reset_index(drop=True)


@st.cache_data
def get_all_time_manager_stats() -> pd.DataFrame:
    data        = load_all()
    std         = data.get("standings", pd.DataFrame())
    tnh         = data.get("team_name_history", pd.DataFrame())
    pg          = data.get("playoffs", pd.DataFrame())
    managers_df = data.get("managers", pd.DataFrame())
    champions   = get_champions()
    if std.empty or managers_df.empty:
        return pd.DataFrame()

    std_mgr = tnh.merge(std, on=["season", "team_name"], how="inner")
    rs_stats = (
        std_mgr.groupby("canonical_name")
        .apply(lambda g: pd.Series({
            "rs_wins":   int(g["wins"].sum()),
            "rs_losses": int(g["losses"].sum()),
            "rs_pf":     round(g["points_for"].sum(), 1),
            "rs_pa":     round(g["points_against"].sum(), 1),
        }))
        .reset_index()
    )

    if not pg.empty:
        champ_pg = pg[pg["bracket"] == "championship"].copy()
        pl_games = pd.concat([
            champ_pg[["season", "team_1", "score_1", "score_2", "winner"]].rename(
                columns={"team_1": "team_name", "score_1": "team_score", "score_2": "opp_score"}
            ),
            champ_pg[["season", "team_2", "score_2", "score_1", "winner"]].rename(
                columns={"team_2": "team_name", "score_2": "team_score", "score_1": "opp_score"}
            ),
        ])
        pl_games["result"] = pl_games.apply(
            lambda r: "Win" if r["winner"] == r["team_name"] else "Loss", axis=1
        )
        pl_merged = tnh.merge(pl_games, on=["season", "team_name"], how="inner")
        pl_stats  = (
            pl_merged.groupby("canonical_name")
            .apply(lambda g: pd.Series({
                "pl_wins":   int((g["result"] == "Win").sum()),
                "pl_losses": int((g["result"] == "Loss").sum()),
            }))
            .reset_index()
        )
        all_pl_teams = pd.concat([
            champ_pg[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
            champ_pg[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
        ]).drop_duplicates()
        pl_apps = (
            tnh.merge(all_pl_teams, on=["season", "team_name"], how="inner")
            .groupby("canonical_name")["season"].nunique()
            .reset_index(name="playoff_apps")
        )
        finals = champ_pg[champ_pg["game_type"] == "final"]
        finals_teams = pd.concat([
            finals[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
            finals[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
        ])
        finals_apps = (
            tnh.merge(finals_teams, on=["season", "team_name"], how="inner")
            .groupby("canonical_name")["season"].nunique()
            .reset_index(name="finals_apps")
        )
    else:
        pl_stats    = pd.DataFrame(columns=["canonical_name", "pl_wins", "pl_losses"])
        pl_apps     = pd.DataFrame(columns=["canonical_name", "playoff_apps"])
        finals_apps = pd.DataFrame(columns=["canonical_name", "finals_apps"])

    champ_counts = (
        champions.groupby("champion_manager").size()
        .reset_index(name="championships")
        .rename(columns={"champion_manager": "canonical_name"})
    ) if not champions.empty else pd.DataFrame(columns=["canonical_name", "championships"])

    best_worst   = std_mgr.groupby("canonical_name")["rank"].agg(best_finish="min", worst_finish="max").reset_index()
    seasons_plyd = tnh.groupby("canonical_name")["season"].nunique().reset_index(name="seasons")

    stats = managers_df[["canonical_name", "display_name"]].copy()
    for df in [seasons_plyd, rs_stats, pl_stats, pl_apps, finals_apps, champ_counts, best_worst]:
        stats = stats.merge(df, on="canonical_name", how="left")

    for col in ["rs_wins", "rs_losses", "pl_wins", "pl_losses", "playoff_apps", "finals_apps", "championships", "seasons"]:
        stats[col] = stats[col].fillna(0).astype(int)
    for col in ["rs_pf", "rs_pa"]:
        stats[col] = stats[col].fillna(0.0)

    stats = stats[stats["seasons"] > 0].copy()
    return stats.sort_values(
        ["championships", "finals_apps", "playoff_apps", "rs_wins"], ascending=False
    ).reset_index(drop=True)


@st.cache_data
def get_manager_h2h(canonical_name: str) -> pd.DataFrame:
    data = load_all()
    wm   = data.get("matchups", pd.DataFrame())
    tnh  = data.get("team_name_history", pd.DataFrame())
    if wm.empty:
        return pd.DataFrame()

    rs        = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy()
    mgr_teams = tnh[tnh["canonical_name"] == canonical_name][["season", "team_name"]]
    mgr_games = mgr_teams.merge(rs, on=["season", "team_name"], how="inner")

    opp_lookup = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
    mgr_games  = mgr_games.copy()
    mgr_games["opp_manager"] = mgr_games.apply(
        lambda r: opp_lookup.get((int(r["season"]), r["opponent"]), None), axis=1
    )
    mgr_games = mgr_games.dropna(subset=["opp_manager"])
    mgr_games = mgr_games[mgr_games["opp_manager"] != canonical_name]
    mgr_games["margin"] = mgr_games["team_score"] - mgr_games["opponent_score"]

    def summarize(g):
        wins   = g[g["result"] == "Win"]
        losses = g[g["result"] == "Loss"]
        return pd.Series({
            "games":        len(g),
            "wins":         int((g["result"] == "Win").sum()),
            "losses":       int((g["result"] == "Loss").sum()),
            "ties":         int((g["result"] == "Tie").sum()),
            "pf":           round(g["team_score"].sum(), 1),
            "pa":           round(g["opponent_score"].sum(), 1),
            "biggest_win":  round(wins["margin"].max(), 1)   if len(wins)   > 0 else 0.0,
            "biggest_loss": round(losses["margin"].min(), 1) if len(losses) > 0 else 0.0,
        })

    h2h = mgr_games.groupby("opp_manager").apply(summarize).reset_index()
    h2h["win_pct"] = (h2h["wins"] / h2h["games"]).round(3)
    return h2h.sort_values("wins", ascending=False).reset_index(drop=True)


@st.cache_data
def get_all_rivalries() -> pd.DataFrame:
    """Pairwise H2H stats for every manager pair (regular season)."""
    data = load_all()
    wm   = data.get("matchups", pd.DataFrame())
    tnh  = data.get("team_name_history", pd.DataFrame())
    if wm.empty:
        return pd.DataFrame()

    rs = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy()
    lookup = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

    rs["mgr_a"] = rs.apply(lambda r: lookup.get((int(r["season"]), r["team_name"]), None), axis=1)
    rs["mgr_b"] = rs.apply(lambda r: lookup.get((int(r["season"]), r["opponent"]),  None), axis=1)
    rs = rs.dropna(subset=["mgr_a", "mgr_b"])
    rs = rs[rs["mgr_a"] != rs["mgr_b"]].copy()

    # Normalise pair order so (A,B) and (B,A) both map to (min,max)
    rs["pair"] = rs.apply(lambda r: tuple(sorted([r["mgr_a"], r["mgr_b"]])), axis=1)
    rs["a_win"] = rs.apply(lambda r: int(r["result"] == "Win" and r["mgr_a"] == r["pair"][0]), axis=1)
    rs["b_win"] = rs.apply(lambda r: int(r["result"] == "Win" and r["mgr_a"] == r["pair"][1]), axis=1)
    rs["margin"] = (rs["team_score"] - rs["opponent_score"]).abs()

    grouped = rs.groupby("pair").apply(lambda g: pd.Series({
        "mgr_a":       g.name[0],
        "mgr_b":       g.name[1],
        "games":       len(g) // 2,
        "a_wins":      int(g["a_win"].sum()),
        "b_wins":      int(g["b_win"].sum()),
        "ties":        int((g["result"] == "Tie").sum()) // 2,
        "avg_margin":  round(g["margin"].mean(), 1),
        "seasons_met": g["season"].nunique(),
    })).reset_index(drop=True)

    grouped["rivalry_score"] = grouped["games"] + grouped["avg_margin"].apply(
        lambda m: max(0, 10 - m)
    )
    return grouped.sort_values("games", ascending=False).reset_index(drop=True)


@st.cache_data
def get_playoff_eliminations() -> pd.DataFrame:
    """Who eliminated whom in the championship bracket."""
    data = load_all()
    pg   = data.get("playoffs", pd.DataFrame())
    tnh  = data.get("team_name_history", pd.DataFrame())
    if pg.empty:
        return pd.DataFrame()

    champ_pg = pg[
        (pg["bracket"] == "championship") & (pg["game_type"] != "3rd_place")
    ].copy()
    tnh_map = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

    rows = []
    for _, r in champ_pg.iterrows():
        winner_mgr = tnh_map.get((int(r["season"]), r["winner"]), r["winner"])
        loser_team = r["team_2"] if r["winner"] == r["team_1"] else r["team_1"]
        loser_mgr  = tnh_map.get((int(r["season"]), loser_team), loser_team)
        rows.append({
            "season":      int(r["season"]),
            "game_type":   r["game_type"],
            "winner_mgr":  winner_mgr,
            "winner_team": r["winner"],
            "loser_mgr":   loser_mgr,
            "loser_team":  loser_team,
            "margin":      round(abs(float(r["score_1"]) - float(r["score_2"])), 2),
        })

    return pd.DataFrame(rows)


@st.cache_data
def get_auction_data() -> pd.DataFrame:
    """Full draft_picks enriched with manager canonical name and player position."""
    data  = load_all()
    draft = data.get("draft", pd.DataFrame())
    tnh   = data.get("team_name_history", pd.DataFrame())
    pos   = data.get("player_positions", pd.DataFrame())
    if draft.empty:
        return pd.DataFrame()

    draft = draft.copy()
    tnh_map = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
    draft["manager"] = draft.apply(
        lambda r: tnh_map.get((int(r["season"]), r["team_name"]), r["team_name"]), axis=1
    )
    pos_map = pos.set_index("player_name")["position"].to_dict() if not pos.empty else {}
    draft["position"] = draft["player_name"].map(pos_map).fillna("?")
    draft["auction_price"] = pd.to_numeric(draft["auction_price"], errors="coerce").fillna(0).astype(int)
    return draft


@st.cache_data
def get_player_market_history(player_name: str) -> pd.DataFrame:
    """Full auction + keeper history for a single player across all seasons."""
    d   = get_auction_data()
    tnh = load_all().get("team_name_history", pd.DataFrame())
    rows = d[d["player_name"] == player_name].copy()
    if rows.empty:
        return pd.DataFrame()
    return rows[["season", "team_name", "manager", "is_keeper", "auction_price"]].sort_values("season").reset_index(drop=True)


@st.cache_data
def get_keeper_chains() -> pd.DataFrame:
    """All multi-season keeper chains with original acquisition included."""
    d = get_auction_data()
    if d.empty:
        return pd.DataFrame()

    rows = []
    for player, grp in d.groupby("player_name"):
        grp = grp.sort_values("season")
        # Find contiguous keeper runs by the same manager
        grp = grp.reset_index(drop=True)
        i = 0
        while i < len(grp):
            row = grp.iloc[i]
            if not row["is_keeper"]:
                # Potential start of a chain
                orig_season = int(row["season"])
                orig_price  = int(row["auction_price"])
                orig_mgr    = row["manager"]
                chain_seasons = [orig_season]
                chain_prices  = [orig_price]
                chain_is_keeper = [False]
                j = i + 1
                while j < len(grp):
                    nxt = grp.iloc[j]
                    if nxt["is_keeper"] and nxt["manager"] == orig_mgr and int(nxt["season"]) == chain_seasons[-1] + 1:
                        chain_seasons.append(int(nxt["season"]))
                        chain_prices.append(int(nxt["auction_price"]))
                        chain_is_keeper.append(True)
                        j += 1
                    else:
                        break
                if len(chain_seasons) > 1:  # at least 1 keeper season
                    rows.append({
                        "player_name":      player,
                        "manager":          orig_mgr,
                        "position":         row["position"],
                        "original_season":  orig_season,
                        "original_price":   orig_price,
                        "seasons":          chain_seasons,
                        "prices":           chain_prices,
                        "keeper_seasons":   len(chain_seasons) - 1,
                        "total_spend":      sum(chain_prices),
                        "final_price":      chain_prices[-1],
                        "final_season":     chain_seasons[-1],
                    })
                i = j
            else:
                i += 1

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("keeper_seasons", ascending=False).reset_index(drop=True)


@st.cache_data
def get_keeper_history() -> pd.DataFrame:
    """All keeper picks with manager name and position resolved."""
    data  = load_all()
    draft = data.get("draft", pd.DataFrame())
    tnh   = data.get("team_name_history", pd.DataFrame())
    pos   = data.get("player_positions", pd.DataFrame())
    if draft.empty:
        return pd.DataFrame()

    keepers = draft[draft["is_keeper"] == True].copy()
    if keepers.empty:
        return pd.DataFrame()

    tnh_map  = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
    keepers["manager"] = keepers.apply(
        lambda r: tnh_map.get((int(r["season"]), r["team_name"]), r["team_name"]), axis=1
    )

    if not pos.empty:
        pos_map = pos.set_index("player_name")["position"].to_dict()
        keepers["position"] = keepers["player_name"].map(pos_map).fillna("?")
    else:
        keepers["position"] = "?"

    keepers["auction_price"] = pd.to_numeric(keepers["auction_price"], errors="coerce").fillna(0).astype(int)

    return keepers[["season", "team_name", "manager", "player_name", "position", "auction_price"]].sort_values(
        ["player_name", "season"]
    ).reset_index(drop=True)


@st.cache_data
def get_timeline_events() -> pd.DataFrame:
    """Auto-generate timeline events from all data sources."""
    import math

    data    = load_all()
    pg      = data.get("playoffs", pd.DataFrame())
    wm      = data.get("matchups", pd.DataFrame())
    fh      = data.get("franchise_history", pd.DataFrame())
    tnh     = data.get("team_name_history", pd.DataFrame())
    manual  = data.get("manual_timeline", pd.DataFrame())
    tnh_map = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict() if not tnh.empty else {}

    events = []

    # ── 1. CHAMPIONSHIPS ───────────────────────────────────────────────────────
    if not pg.empty:
        finals = pg[pg["game_type"] == "final"].sort_values("season")
        title_counts: dict[str, int] = {}
        for _, row in finals.iterrows():
            szn     = int(row["season"])
            winner  = tnh_map.get((szn, row["winner"]), row["winner"])
            l_team  = row["team_2"] if row["winner"] == row["team_1"] else row["team_1"]
            loser   = tnh_map.get((szn, l_team), l_team)
            w_score = float(row["score_1"]) if row["winner"] == row["team_1"] else float(row["score_2"])
            l_score = float(row["score_2"]) if row["winner"] == row["team_1"] else float(row["score_1"])
            margin  = abs(w_score - l_score)
            title_counts[winner] = title_counts.get(winner, 0) + 1
            n = title_counts[winner]
            szn_num = szn - FOUNDED + 1

            if szn == FOUNDED:
                flavor = (
                    f"{winner} won the inaugural championship, "
                    f"defeating {loser} {w_score:.2f}–{l_score:.2f}."
                )
            elif n == 2:
                flavor = (
                    f"{winner} claimed a second title, "
                    f"defeating {loser} {w_score:.2f}–{l_score:.2f} by {margin:.2f}."
                )
            elif n == 3:
                flavor = (
                    f"{winner}'s third championship in {szn - FOUNDED + 1} seasons "
                    f"confirmed a dynasty. {loser} fell {w_score:.2f}–{l_score:.2f}."
                )
            elif margin <= 5:
                flavor = (
                    f"{winner} survived a championship thriller, "
                    f"edging {loser} {w_score:.2f}–{l_score:.2f} by just {margin:.2f}."
                )
            elif margin >= 80:
                flavor = (
                    f"{winner} dominated the final, beating {loser} "
                    f"{w_score:.2f}–{l_score:.2f} by {margin:.0f} points."
                )
            else:
                ordinal = {1:"first",2:"second",3:"third"}.get(n, f"{n}th")
                flavor = (
                    f"{winner} won their {ordinal} championship, "
                    f"defeating {loser} {w_score:.2f}–{l_score:.2f}."
                )

            events.append({
                "season": szn, "category": "championship",
                "emoji": "🏆", "importance": 1,
                "title": f"{winner} wins {szn} championship",
                "description": flavor,
                "detail": f"{w_score:.2f}–{l_score:.2f} over {loser} · margin {margin:.2f}",
            })
            events.append({
                "season": szn, "category": "runner_up",
                "emoji": "🥈", "importance": 2,
                "title": f"{loser} — runner-up",
                "description": f"{loser} reached the {szn} championship final, losing to {winner} {l_score:.2f}–{w_score:.2f}.",
                "detail": f"Final score: {l_score:.2f}",
            })

    # ── 2. FRANCHISE CHANGES ───────────────────────────────────────────────────
    if not fh.empty:
        fh_s = fh.sort_values(["franchise_id", "season"])
        for fid, grp in fh_s.groupby("franchise_id"):
            mgrs = grp["manager_name"].tolist()
            szns = grp["season"].tolist()
            for i in range(1, len(mgrs)):
                if mgrs[i] != mgrs[i - 1]:
                    old_m, new_m, szn = mgrs[i - 1], mgrs[i], int(szns[i])
                    events.append({
                        "season": szn, "category": "franchise",
                        "emoji": "🏠", "importance": 2,
                        "title": f"{new_m} joins the league",
                        "description": (
                            f"{new_m} took over {fid} from {old_m}, "
                            f"inheriting the franchise seat for the {szn} season."
                        ),
                        "detail": f"{fid}: {old_m} → {new_m}",
                    })

    # ── 3. KEEPER MILESTONES ───────────────────────────────────────────────────
    chains = get_keeper_chains()
    if not chains.empty:
        draft = get_auction_data()
        for _, chain in chains.iterrows():
            seasons_list = chain["seasons"]
            prices_list  = chain["prices"]
            player       = chain["player_name"]
            mgr          = chain["manager"]
            n_kept       = chain["keeper_seasons"]

            # Only milestone-worthy chains (3+ keeper seasons)
            if n_kept < 3:
                continue

            # Event for first keeper year
            if len(seasons_list) >= 2:
                first_keeper_szn = int(seasons_list[1])
                orig_price       = int(prices_list[0])
                first_k_price    = int(prices_list[1])
                events.append({
                    "season": first_keeper_szn, "category": "keeper",
                    "emoji": "🔑", "importance": 3,
                    "title": f"{mgr} begins keeping {player}",
                    "description": (
                        f"{mgr} kept {player} for the first time "
                        f"(${first_k_price}, up from ${orig_price} acquisition). "
                        f"A chain that would last {n_kept} seasons."
                    ),
                    "detail": f"Original ${orig_price} → ${first_k_price} · chain total ${chain['total_spend']}",
                })

            # Event for final keeper year (if chain ended before current season)
            final_szn = int(chain["final_season"])
            if final_szn < CURRENT_SEASON:
                final_price = int(chain["final_price"])
                events.append({
                    "season": final_szn, "category": "keeper",
                    "emoji": "🔑", "importance": 3,
                    "title": f"{player} era ends for {mgr}",
                    "description": (
                        f"After {n_kept} seasons, {mgr}'s {player} keeper chain ended. "
                        f"Final price ${final_price}, total invested ${chain['total_spend']}."
                    ),
                    "detail": f"{n_kept} keeper seasons · ${chain['original_price']} → ${final_price}",
                })

    # ── 4. AUCTION RECORDS ─────────────────────────────────────────────────────
    if not chains.empty or True:
        draft = get_auction_data()
        if not draft.empty:
            fresh = draft[draft["is_keeper"] != True].copy()
            running_record = 0
            for szn in sorted(fresh["season"].unique()):
                szn_fresh = fresh[fresh["season"] == szn]
                if szn_fresh.empty:
                    continue
                top_row = szn_fresh.loc[szn_fresh["auction_price"].idxmax()]
                price   = int(top_row["auction_price"])
                player  = top_row["player_name"]
                mgr     = top_row["manager"]
                is_record = price > running_record
                running_record = max(running_record, price)
                importance = 2 if is_record else 3
                record_tag = " — a new league record" if is_record else ""
                events.append({
                    "season": int(szn), "category": "auction",
                    "emoji": "💰", "importance": importance,
                    "title": f"${price} on {player}",
                    "description": (
                        f"{mgr} bid ${price} on {player}{record_tag}, "
                        f"the highest bid of the {int(szn)} draft."
                    ),
                    "detail": f"${price} · {player} · {mgr}",
                })

    # ── 5. CLOSE REGULAR-SEASON GAMES ─────────────────────────────────────────
    if not wm.empty:
        rs = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy()
        rs["manager"]  = rs.apply(lambda r: tnh_map.get((int(r["season"]), r["team_name"]), r["team_name"]), axis=1)
        rs["opp_mgr"]  = rs.apply(lambda r: tnh_map.get((int(r["season"]), r["opponent"]), r["opponent"]), axis=1)
        rs["margin"]   = (rs["team_score"] - rs["opponent_score"]).abs()
        # Only wins (avoid duplicates)
        close_wins = rs[(rs["result"] == "Win") & (rs["margin"] < 0.5)].sort_values("margin")
        for _, row in close_wins.iterrows():
            m   = float(row["margin"])
            mgr = row["manager"]
            opp = row["opp_mgr"]
            szn = int(row["season"])
            wk  = int(row["week"])
            ts  = float(row["team_score"])
            os  = float(row["opponent_score"])
            events.append({
                "season": szn, "category": "rivalry",
                "emoji": "⚔️", "importance": 2,
                "title": f"{mgr} wins by {m:.2f} pts (Week {wk})",
                "description": (
                    f"{mgr} survived a {szn} Week {wk} showdown with {opp}, "
                    f"winning {ts:.2f}–{os:.2f} by just {m:.2f} points."
                ),
                "detail": f"{ts:.2f}–{os:.2f} · margin {m:.2f}",
            })

    # ── 6. MANUAL EVENTS ───────────────────────────────────────────────────────
    if not manual.empty and "season" in manual.columns:
        for _, row in manual.iterrows():
            if not row.get("show_on_league_timeline", True):
                continue
            events.append({
                "season":      int(row.get("season", 0)),
                "category":    row.get("event_type", "manual"),
                "emoji":       "📌",
                "importance":  int(row.get("importance", 2)),
                "title":       str(row.get("title", "")),
                "description": str(row.get("description", "")),
                "detail":      "",
            })

    if not events:
        return pd.DataFrame()

    df = pd.DataFrame(events)
    df["season"]     = df["season"].astype(int)
    df["importance"] = df["importance"].astype(int)
    return df.sort_values(["season", "importance"]).reset_index(drop=True)
