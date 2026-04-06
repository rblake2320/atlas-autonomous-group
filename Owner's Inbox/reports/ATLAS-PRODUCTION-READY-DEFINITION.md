# Atlas `production_ready` Definition

Atlas assigns the status label in `scripts/business_lib.py` inside `compute_scorecard(tasks)`.

## Threshold Logic
- `production_ready` if `score >= 85`
- `developing` if `45 <= score < 85`
- `bootstrapping` if `score < 45`

## What It Means In Atlas
In Atlas, `production_ready` means:
- the score computed from live state is at least 85
- delivered tasks exist and have evidence files
- heartbeat activity exists
- the budget and worktree operating surfaces are configured

It does **not** mean:
- external market proof is complete
- learning proof is complete
- 24h autonomy has been proven
- replay/tamper rigor is fully mature

Those remaining proof surfaces are tracked separately by the gap meter.

## Current State
Atlas is currently `production_ready` because:
- score is `95/100`
- score threshold is exceeded
- delivered evidence exists
- validation surfaces are green

## Separate But Related
The `production_ready` label is a score threshold label.
The stronger operational confidence claim comes from the validation commands:
- `python scripts/business_doctor.py`
- `python scripts/business_full_validation.py run`
- `python scripts/business_code_inspector.py`
- `python scripts/business_wiring_audit.py`
- `python scripts/business_schema_audit.py`
- `python scripts/business_sdk_audit.py`

So the label is simple, and the evidence burden lives in the validators.
