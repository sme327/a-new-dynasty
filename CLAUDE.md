CLAUDE.md

A New Dynasty

Project Mission

A New Dynasty is a digital museum preserving the history of a dynasty keeper fantasy football league that has been active since 2018.

This is not a fantasy football analytics site.

This is not a Yahoo replacement.

This is not a statistics dashboard.

The purpose of the project is to preserve the memory and identity of a dynasty league built around keeper loyalty, auction strategy, and long-term team building.

Championships, drafts, keepers, trades, standings, rivalries, and franchise evolution are all artifacts that help tell the story.

The stories themselves are the product.

⸻

League Format

Platform: Yahoo Fantasy Football
Commissioner: Shawn (Yahoo slug: sme327)
Format: Dynasty keeper league
Seasons: 2018–present
Draft style: Auction draft
Keepers per season: Up to 5
Keeper cost formula: Prior year acquisition cost + 10%, rounded up to the nearest whole dollar

The keeper cost formula is central to this league's identity. Rising costs create hard decisions: when does a dynasty player become too expensive to keep? This tension between loyalty and value is one of the league's defining stories.

⸻

Core Design Philosophy

When building new features, prioritize:

1. Story
2. Legacy
3. Identity
4. Rivalry
5. Statistics

Statistics support stories.

Statistics should rarely be the final destination.

⸻

Desired User Experience

A league member should spend time exploring the site and repeatedly say:

"Oh wow, I forgot about that."

Examples:

* A dynasty player kept so long the cost became painful
* A championship run built around a single auction target
* A keeper that was finally let go after years of loyalty
* A rivalry that defined multiple seasons
* A sleeper pickup that became a multi-year cornerstone
* The moment someone paid too much to keep the wrong player

The site succeeds when it creates nostalgia and rediscovery.

⸻

Visual Identity

A New Dynasty should feel like:

* A Hall of Fame
* A Sports Museum
* A Franchise Documentary
* A Trophy Room

The site should NOT feel like:

* Yahoo Fantasy
* A betting application
* A generic analytics dashboard

⸻

Page Philosophy

Every page should follow a similar structure:

Hero

↓

Story

↓

Records

↓

Deep Dive

↓

Raw Data

Raw data should support the story, not dominate it.

⸻

Page Ownership

Home

Question:

"What is this place?"

Purpose:

Introduce the league and invite exploration.

⸻

Champions

Question:

"Who won?"

Purpose:

Celebrate champions, title runs, and championship heartbreak.

⸻

Timeline

Question:

"What happened?"

Purpose:

The historical spine of the league.

All major pages should eventually contribute notable events to Timeline.

⸻

League History

Question:

"How did the league evolve?"

Purpose:

League eras, rule changes, competitive balance, and historical trends.

⸻

Season Archive

Question:

"What happened in a specific year?"

Purpose:

Documentary-style season histories. Each season should feel like its own chapter.

⸻

Managers

Question:

"Who are these people?"

Purpose:

Manager identities, accomplishments, failures, rivalries, and mythology.

Managers should feel like characters, not records.

⸻

Franchises

Question:

"What happened to this seat over time?"

Purpose:

Franchise lineage, stewardship, continuity, identity, and legacy.

⸻

Draft Center

Question:

"How were contenders built?"

Purpose:

Auction draft behavior, bidding tendencies, player targets, and draft history.

⸻

Keeper Hall

Question:

"Who couldn't let go — and at what cost?"

Purpose:

This is one of the defining pages of A New Dynasty.

Keeper dynasties, keeper lore, cost escalation stories, and the players nobody could release.

Key stories to surface:
- Players kept the maximum number of years
- Highest keeper costs paid
- Players whose cost finally forced a release
- The keeper that won a championship

⸻

Rivalries

Question:

"Who still hates each other?"

Purpose:

The emotional center of competition.

Manager rivalries, playoff rivalries, streaks, and heartbreak.

⸻

Narrative Layer Requirement

Every significant entity should eventually have a narrative summary.

Not just: Record: 62-42

But: "One of the most aggressive auction drafters in league history, known for..."

⸻

Future Priorities

Highest future priorities:

1. Keeper Hall
2. Champions
3. Season Archive
4. Rivalries
5. Manager Profiles

Second-tier priorities:

1. Draft Center
2. Franchise Timelines
3. League History

⸻

Data Notes

- Keeper cost is NOT stored directly by Yahoo. It must be inferred from draft data (the round a keeper is taken reflects their cost tier) combined with the formula: prior year acquisition price + 10%, rounded up.
- All seasons are on Yahoo (game code f1, 2018–2025).
- Yahoo league IDs per season:
  - 2018: 1332374
  - 2019: 407071
  - 2020: 785513
  - 2021: 69643
  - 2022: 641538
  - 2023: 7167
  - 2024: 37702
  - 2025: 66119

⸻

Product Test

Before adding any feature, ask:

Does this help preserve the memory of the league?

If not, it probably does not belong.

A New Dynasty is a museum.

Always build toward that vision.
