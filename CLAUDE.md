# Atlas Autonomous Group

## Startup
1. Read README.md
2. Read Team/CORE_RULES.md
3. Read Team/OPERATING_MODEL.md
4. Read Team/roster.md
5. Inspect Team Inbox/, Board Inbox/, Team/runtime/heartbeat/, and Team/runtime/state/

## Hard gates
- LEDGER gates spend and pricing.
- SHIELD gates contracts and public claims.
- WATCHTOWER gates security-sensitive work.
- SENTINEL gates release quality.
- WIRING gates integration completeness.
- SCHEMA gates machine-readable contract integrity.

## Runtime model
Only HELM runs heartbeat cadence. VECTOR ensures no agent stays idle or blocked without escalation. Intake enters Team Inbox. Final delivery exits Owner's Inbox.

## Runtime Flexibility
- Supports cloud APIs, CLI adapters, local LLMs, and local SLMs.
- Use local SLMs for cheap routing and guardrails; use larger cloud or CLI-backed models for high-context work.

## Operations extras
- `scripts/business_budget.py` is the spend/quota surface and should be consulted before any new high-cost track is opened.
- `scripts/business_worktree.py` is optional and should be used for parallel coding tracks rather than editing the same checkout concurrently.
- `scripts/business_wiring_audit.py` and `scripts/business_schema_audit.py` are the integration truth sources and should stay green.
