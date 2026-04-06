from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
REPORT = ROOT / "Owner's Inbox" / 'reports' / 'ATLAS-FULL-VALIDATION.json'

PRECHECKS = [
    [sys.executable, str(SCRIPT_DIR / 'business_doctor.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_adapter_check.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_budget.py'), 'status'],
    [sys.executable, str(SCRIPT_DIR / 'business_worktree.py'), 'summary'],
    [sys.executable, str(SCRIPT_DIR / 'business_event_audit.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_runtime.py'), 'summary'],
    [sys.executable, str(SCRIPT_DIR / 'business_learning_review.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_market_review.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_gap_meter.py'), 'status'],
    [sys.executable, str(SCRIPT_DIR / 'business_wiring_audit.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_schema_audit.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_sdk_audit.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_code_inspector.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_agent_activity_audit.py')],
    [sys.executable, str(SCRIPT_DIR / 'business_failure_injection.py')],
]
POSTCHECKS = [[sys.executable, str(SCRIPT_DIR / 'business_claim_audit.py')]]


def run_command(command: list[str]) -> dict:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    return {'command': command, 'returncode': result.returncode, 'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', nargs='?', default='run', choices=['run'])
    parser.parse_args()

    results = [run_command(command) for command in PRECHECKS]
    rc = 0
    for item in results:
        rc = rc or item['returncode']

    report = {'status': 'PASS' if rc == 0 else 'FAIL', 'commands': results}
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    post_results = [run_command(command) for command in POSTCHECKS]
    for item in post_results:
        rc = rc or item['returncode']
    report = {'status': 'PASS' if rc == 0 else 'FAIL', 'commands': results + post_results}
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    print('FULL VALIDATION PASS' if rc == 0 else 'FULL VALIDATION FAIL')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
