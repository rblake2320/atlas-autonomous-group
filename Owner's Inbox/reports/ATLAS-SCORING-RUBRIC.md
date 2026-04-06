# Atlas Scoring Rubric

This file explains the exact `95/100` score Atlas currently reports.

## Formula
Atlas score is computed in `scripts/business_lib.py` by `compute_scorecard(tasks)`.

Components:
- `evidence_coverage` = up to 35 points
  - Formula: `(delivered tasks with evidence / delivered tasks) * 35`
- `progression` = up to 25 points
  - Formula: `min(25, delivered_tasks * 4)`
- `gate_score` = up to 15 points
  - Formula: `min(15, delivered_tasks_with_audit_or_board_gate * 5)`
- `autonomy_score` = up to 15 points
  - Formula: `min(15, heartbeat_records * 3)`
- `operations_score` = up to 10 points
  - 4 points if `budget.json.monthly_limit > 0`
  - 3 points if `budget.json.spent <= budget.json.monthly_limit`
  - 3 points if `worktrees.json.enabled == true`

Maximum total: 100.

## Current Breakdown
Current state:
- delivered tasks: 8
- delivered tasks with evidence: 8
- delivered tasks with gate requirements: 2 (`AT-0003`, `AT-0004`)
- heartbeat records: 29+
- budget configured and healthy: yes
- worktrees enabled: yes

Current score:
- `evidence_coverage = 35/35`
- `progression = 25/25`
- `gate_score = 10/15`
- `autonomy_score = 15/15`
- `operations_score = 10/10`
- `total = 95/100`

## The Missing 5 Points
The missing 5 points are entirely in `gate_score`.

Why:
- Atlas currently has two delivered tasks with a gate requirement.
- Gate score formula is `min(15, gate_count * 5)`.
- Two gated delivered tasks gives `10/15`.

To reach `100/100` under the current rubric:
- one more delivered task must require either:
  - audit, or
  - board approval
- that would raise `gate_count` from `2` to `3`
- `min(15, 3 * 5) = 15`

So the exact remaining 5 points require:
- one additional delivered gated task
- with evidence present
- and reflected in `tasks.json`

## Recompute Rule
If `scorecard.json` is deleted, the score can be recomputed from:
- `Team/runtime/state/tasks.json`
- `Owner's Inbox/evidence/`
- `Team/runtime/heartbeat/`
- `Team/runtime/state/budget.json`
- `Team/runtime/state/worktrees.json`

Use:
- `python scripts/business_recompute_score.py`
