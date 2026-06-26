# A New Dynasty — Project Overview

Dynasty keeper fantasy football league (Yahoo, commissioner: Shawn, league slug `sme327`).
Started 2018. Up to 5 keepers per season. Auction draft. Keeper cost = prior year cost + 10%, rounded up.

This folder contains the data pipeline that scrapes and normalizes historical league data
for use in a Streamlit history app.

---

## League Configuration

| Season | Game Code | League ID |
|--------|-----------|-----------|
| 2018   | f1        | 1332374   |
| 2019   | f1        | 407071    |
| 2020   | f1        | 785513    |
| 2021   | f1        | 69643     |
| 2022   | f1        | 641538    |
| 2023   | f1        | 7167      |
| 2024   | f1        | 37702     |
| 2025   | f1        | 66119     |

---

## Scripts

### `fetch_yahoo_data.py`
Main scraper. Uses Playwright (headless Chrome) + BeautifulSoup to pull data from Yahoo.
Adapted from the FFL History scraper with league IDs pre-configured for this league.

**Usage:**
```
python fetch_yahoo_data.py                        # all years, all sections
python fetch_yahoo_data.py --year 2022            # single year
python fetch_yahoo_data.py --year 2020 2025       # range of years
python fetch_yahoo_data.py --section draft        # specific section only
```

**Sections:** `standings`, `draft`, `matchups`, `playoffs`, `managers`, `transactions`

**Sessions:** Login is handled interactively on first run and saved to `.yahoo_cookies.json`.
Subsequent runs reuse the saved session. Delete the file to force a fresh login.

**Rate limiting:** Yahoo blocks after ~40 rapid page loads. The scraper uses a 3.5s delay
between requests and auto-pauses 5 minutes on "Request denied" responses.

---

### `inspect_yahoo_page.py`
Diagnostic tool for examining Yahoo page structure. Use when debugging the scraper.

**Usage:**
```
python inspect_yahoo_page.py standings 2020
python inspect_yahoo_page.py draftresults 2020
```

---

### `build_player_positions.py`
Builds `data/player_positions.csv` by matching player names against the nflverse players database.
Re-run after adding new draft seasons.

**Usage:**
```
python build_player_positions.py
```

---

## Data Files (`data/`)

Same schema as FFL History. See DATA_GUIDE.md for column documentation.

Key keeper note: Yahoo does not store keeper cost directly. The `is_keeper` flag in `draft_picks.csv`
identifies kept players. Keeper cost (prior year acquisition + 10% rounded up) must be derived
from the draft history across seasons.

---

## Running the App

```
streamlit run app.py
```

---

## Known Data Gaps & Pending Work

| Item | Status |
|------|--------|
| Yahoo scraper | Ready to configure — league IDs are in place |
| `fetch_yahoo_data.py` | Needs to be copied from FFL History and adapted |
| `build_player_positions.py` | Needs to be copied from FFL History |
| `data/ref_nfl_players.csv` | Download from nflverse before running position builder |
| `data/manual_timeline_events.csv` | Create manually after initial scrape |
| `data/league_settings.csv` | Create manually with keeper rules and format info |
