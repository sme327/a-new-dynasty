#!/usr/bin/env python3
"""
build_player_positions.py
Builds data/player_positions.csv by matching draft_picks.csv player names
against nflverse players database. Run once; re-run after adding new seasons.

Download ref_nfl_players.csv from:
  https://github.com/nflverse/nflverse-data/releases/latest/download/players.csv
Save as data/ref_nfl_players.csv before running.
"""

import csv, re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

NFL_TEAM_NAMES = {
    '49ers', 'bears', 'bengals', 'bills', 'broncos', 'browns', 'buccaneers',
    'cardinals', 'chargers', 'chiefs', 'colts', 'commanders', 'cowboys',
    'dolphins', 'eagles', 'falcons', 'giants', 'jaguars', 'jets', 'lions',
    'packers', 'panthers', 'patriots', 'raiders', 'rams', 'ravens', 'redskins',
    'saints', 'seahawks', 'steelers', 'texans', 'titans', 'vikings', 'washinton'
}

# Known nicknames/alternate names → nflverse display_name (normalized)
NICKNAME_MAP = {
    'beanie wells':         'chris wells',
    'deebo samuel':         'deebo samuel sr',
    'hollywood brown':      'marquise brown',
    'trenton richardson':   'trent richardson',
    'nyheim miller-hines':  'nyheim hines',
    'stephen hauschka':     'steven hauschka',
}

# Players not in nflverse (retired pre-coverage or very obscure) — add as needed
MANUAL_POSITIONS: dict[str, str] = {
    'joshua palmer':  'WR',
    'kenneth barber': 'RB',
}


def strip_yahoo_suffix(name):
    name = re.sub(r'\s*\([A-Za-z]{2,3}\s*-\s*[A-Z]+\)\s*', ' ', name)
    name = re.sub(r'[-]', '', name)
    return name.strip()


def norm(name):
    name = name.lower().strip()
    name = re.sub(r'[^a-z ]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name


def is_defense(name):
    words = name.lower().split()
    return len(words) <= 2 and any(w in NFL_TEAM_NAMES for w in words)


def build_nfl_lookup():
    lookup = {}
    for r in csv.DictReader(open(DATA_DIR / "ref_nfl_players.csv")):
        dn = r.get('display_name', '').strip()
        pos = r.get('position', '').strip()
        if dn and pos:
            lookup.setdefault(norm(dn), []).append((dn, pos))
    return lookup


def resolve(hits):
    if len(hits) == 1:
        return hits[0][1]
    skill_order = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'DB', 'LB', 'DL', 'OL', 'DT', 'DE', 'CB', 'S', 'FB', 'P']
    positions = [h[1] for h in hits]
    for pos in skill_order:
        if pos in positions:
            return pos
    return positions[0]


def lookup_position(name, nfl_lookup):
    if is_defense(name):
        return 'DEF', 'defense'

    cleaned = strip_yahoo_suffix(name)
    k = norm(cleaned)

    hits = nfl_lookup.get(k)
    if hits:
        return resolve(hits), 'nflverse' if len(hits) == 1 else 'nflverse_ambiguous'

    mapped = {norm(key): val for key, val in NICKNAME_MAP.items()}.get(k)
    if mapped:
        hits = nfl_lookup.get(norm(mapped))
        if hits:
            return resolve(hits), 'nflverse_nickname'

    stripped = re.sub(r'\s+(jr|sr|ii|iii|iv|v)\s*$', '', k).strip()
    if stripped != k:
        hits = nfl_lookup.get(stripped)
        if hits:
            return resolve(hits), 'nflverse_no_suffix'

    manual = {norm(key): val for key, val in MANUAL_POSITIONS.items()}
    if k in manual:
        return manual[k], 'manual'

    return '', 'unmatched'


def main():
    nfl_lookup = build_nfl_lookup()

    draft = list(csv.DictReader(open(DATA_DIR / "draft_picks.csv")))
    unique_players = sorted(set(
        r['player_name'].strip() for r in draft
        if r['player_name'].strip() not in ('--empty--', '')
    ))

    results = []
    tally = {}
    for name in unique_players:
        pos, source = lookup_position(name, nfl_lookup)
        results.append({'player_name': name, 'position': pos, 'match_source': source})
        tally[source] = tally.get(source, 0) + 1

    out_path = DATA_DIR / "player_positions.csv"
    with open(out_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['player_name', 'position', 'match_source'])
        w.writeheader()
        w.writerows(results)

    total = len(results)
    matched = total - tally.get('unmatched', 0)
    print(f"Players: {total}  |  Matched: {matched} ({matched/total*100:.1f}%)")
    print()
    for src, n in sorted(tally.items(), key=lambda x: -x[1]):
        print(f"  {src:<30} {n:>4}")

    unmatched = [r for r in results if r['match_source'] == 'unmatched']
    if unmatched:
        print(f"\nStill unmatched ({len(unmatched)}):")
        for r in unmatched:
            print(f"  {r['player_name']}")


if __name__ == '__main__':
    main()
