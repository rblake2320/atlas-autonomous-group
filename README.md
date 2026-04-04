# Atlas Autonomous Group

Atlas Autonomous Group is a standalone multi-agent business workspace intended to be cloned and tested by other humans or AI systems. It includes a durable task pipeline, heartbeat-driven progression, approvals, scorecarding, doctor checks, A2A cards, MCP examples, and an interop receipt from a cross-system handoff.

## What this repo contains
- `CLAUDE.md` and `.claude/agents/` for the workspace-facing agent layer
- `scripts/` for the runnable operating loop
- `Team/runtime/state/` for durable task and scorecard state
- `Owner's Inbox/evidence/` for generated deliverables and interop receipts
- `interop/` for A2A and MCP-facing machine-readable surfaces

## Core Commands
```powershell
python scripts/business_task_cli.py seed
python scripts/business_heartbeat.py run
python scripts/business_task_cli.py board
python scripts/business_scorecard.py
python scripts/business_doctor.py
python scripts/business_full_validation.py
```

## Reproduce from a clean state
```powershell
python scripts/business_replay_demo.py
```

## Success Criteria
A valid replay should produce:
- a delivered eight-task pipeline
- `production_ready` scorecard state
- `PASS` from `business_doctor.py`
- `FULL VALIDATION PASS` from `business_full_validation.py`

## Interop Proof
This repo includes Atlas-side evidence of a bidirectional interop loop with a separate autonomous system. The receipt is in:
- `Owner's Inbox/evidence/ATLAS-INTEROP-RECEIPT.md`

For full test instructions, see `TESTING.md`.
