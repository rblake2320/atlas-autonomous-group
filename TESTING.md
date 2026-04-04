# Testing Atlas Autonomous Group

## Requirements
- Python 3.11+
- Windows, macOS, or Linux with a writable clone of this repo

## Quick Repro
From repo root:

```powershell
python scripts/business_reset_demo.py
python scripts/business_task_cli.py seed
1..28 | ForEach-Object { python scripts/business_heartbeat.py run | Out-Null }
python scripts/business_task_cli.py board
python scripts/business_scorecard.py
python scripts/business_doctor.py
python scripts/business_full_validation.py
```

Expected outcome:
- all seeded tasks end in `delivered`
- scorecard reaches `production_ready`
- doctor returns `PASS`
- full validation returns `FULL VALIDATION PASS`

## One-command Replay
```powershell
python scripts/business_replay_demo.py
```

## Interop Artifacts
The repo includes an interop receipt at:
- `Owner's Inbox/evidence/ATLAS-INTEROP-RECEIPT.md`

The received A2A artifact copied from the generated workspace is at:
- `interop/received/atlas-workspace-a2a-directory.json`
