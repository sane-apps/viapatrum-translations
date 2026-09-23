# Work lanes

Two lane systems exist. Do not confuse them:

- **Compute lanes** (`docs/LLM_LANE_CONFIG.json`): which models do the work
  (cf / nv / gemini). Machine concern.
- **Work lanes** (this file + `docs/work-lanes.json`): what gets translated,
  in what order, on whose budget. Charter concern.

## The lanes

| Lane | Status | Budget share | Scope |
|------|--------|--------------|-------|
| rank1 | **paused** since 2026-09-13 | 0% | Greek first-English wave, oldest first within lane. Default for unassigned books. |
| reformed | active | 60% | Reformed retrieval (`docs/REFORMED_RETRIEVAL.md`), 6 books. |
| densify | active | 25% | Refresh over dated PD English (NOT OET), disclosed base. |
| topics | active | 15% | Site topics layer (`ante-nicene-topics`). |
| latin | unopened | 0% | Latin Fathers oldest-first. No books yet. |

Shares split fathers CF-neuron spend per overnight run. In-flight rows
(resume: claimed/checking/review) are exempt from pause skips and share caps:
we finish what we started.

## Priority rule (charter enforcement)

Oldest first governs **within** every lane and **across** lanes for new work:
the overnight queue sorts free rows by lane priority, then by book year from
`docs/corpus-catalog.json`. Paused/unopened lanes contribute no new rows;
their in-flight rows still complete.

## Paused lane behavior

- `scripts/claims.py start` skips free rows in paused lanes
  (`--include-paused` overrides and logs the choice).
- `scripts/claims.py take <id>` on a paused-lane row prints a warning but
  proceeds (deliberate human/agent choice).
- `scripts/overnight_quota.py` skips paused-lane free rows, processes resume
  rows, and records skips in the dual summary.

## Rank-1 resume criteria (quality pause of 2026-09-13)

The owner paused new Rank-1 for quality review
(`SESSION_HANDOFF.md` 2026-09-13 wrap). Resume requires all three:

1. Owner completes the quality review of tipped Rank-1 work.
2. Symeon Junior Theologica decision recorded (tip or defer).
3. Owner sets `rank1.status` back to `active` in `docs/work-lanes.json`
   with a budget share.

No lane, agent, or script lifts the pause on its own.

## Assigning books to lanes

Precedence: `lane:` field in `books/<slug>/book.yml`, then the explicit
lists in `docs/work-lanes.json`, then catalog lineage `refresh` -> densify,
then the default lane (rank1). New books land in rank1 (paused) until
consciously assigned: no unowned work. To open the Latin lane, assign the
first locked Latin book `lane: latin` and set the lane active with a share.

## Changing shares or statuses

Edit `docs/work-lanes.json` (owner or lane owner). Shares should total 100
across active lanes; the runner normalizes regardless. Record the reason in
`docs/WORKS_QUEUE.md`.

Owners and collision rules: docs/OWNERSHIP.md.
