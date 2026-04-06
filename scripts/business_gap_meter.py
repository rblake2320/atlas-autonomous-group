from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_lib import (
    EVENT_AUDIT_FILE,
    GAPS_FILE,
    MARKET_FILE,
    OWNER_REPORTS,
    RUNTIME_AUDIT_FILE,
    SCORECARD_FILE,
    now,
    read_gaps,
    write_gaps,
)

REPORT = OWNER_REPORTS / 'ATLAS-GAP-METER.md'
LEARNING_REPORT = OWNER_REPORTS / 'ATLAS-LEARNING-REVIEW.md'
MARKET_REPORT = OWNER_REPORTS / 'ATLAS-MARKET-REVIEW.md'


def _ratio(current: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return max(0.0, min(1.0, current / target))


def sync() -> dict:
    data = read_gaps()
    event_audit = json.loads(EVENT_AUDIT_FILE.read_text(encoding='utf-8')) if EVENT_AUDIT_FILE.exists() else {}
    runtime_audit = json.loads(RUNTIME_AUDIT_FILE.read_text(encoding='utf-8')) if RUNTIME_AUDIT_FILE.exists() else {}
    learning_review = json.loads(LEARNING_REPORT.read_text(encoding='utf-8')) if LEARNING_REPORT.exists() else {'verified_learning_deltas': 0}
    market_review = json.loads(MARKET_REPORT.read_text(encoding='utf-8')) if MARKET_REPORT.exists() else {'verified_external_wins': 0}
    for gap in data['gaps']:
        if gap['id'] == 'runtime_rigor':
            gap['current'] = event_audit.get('rigor_score', gap['current'])
            gap['status'] = 'verified' if gap['current'] >= gap['target'] else 'active'
            gap['evidence_path'] = 'Team/runtime/state/event_audit.json'
        elif gap['id'] == 'autonomy_hours':
            gap['current'] = runtime_audit.get('continuous_hours', gap['current'])
            gap['status'] = 'verified' if gap['current'] >= gap['target'] else 'active'
            gap['evidence_path'] = 'Team/runtime/state/runtime_audit.json'
        elif gap['id'] == 'learning_proof':
            gap['current'] = learning_review.get('verified_learning_deltas', gap['current'])
            gap['status'] = 'verified' if gap['current'] >= gap['target'] else 'active'
            gap['evidence_path'] = "Owner's Inbox/reports/ATLAS-LEARNING-REVIEW.md"
        elif gap['id'] == 'external_value':
            gap['current'] = market_review.get('verified_external_wins', gap['current'])
            gap['status'] = 'verified' if gap['current'] >= gap['target'] else 'active'
            gap['evidence_path'] = "Owner's Inbox/reports/ATLAS-MARKET-REVIEW.md"
        elif gap['id'] == 'interop_replay':
            receipt = Path(gap['evidence_path'])
            gap['status'] = 'verified' if gap['current'] >= gap['target'] else 'active'
    write_gaps(data)
    return data


def _render(data: dict) -> str:
    gaps = data['gaps']
    total = sum(_ratio(g['current'], g['target']) for g in gaps)
    score = round((total / len(gaps)) * 100, 1) if gaps else 0.0
    lines = [
        '# Atlas Gap Meter',
        '',
        f'Updated: {now()}',
        f'Overall progress: {score}%',
        '',
        '| Gap | Owner | Current | Target | Status | Verifier | Evidence |',
        '| --- | --- | --- | --- | --- | --- | --- |',
    ]
    for gap in gaps:
        lines.append(f"| {gap['id']} | {gap['owner']} | {gap['current']} {gap['metric']} | {gap['target']} | {gap['status']} | `{gap['verifier_cmd']}` | `{gap['evidence_path']}` |")
    lines.append('')
    return '\n'.join(lines)


def status() -> int:
    data = sync()
    REPORT.write_text(_render(data), encoding='utf-8')
    gaps = data['gaps']
    total = sum(_ratio(g['current'], g['target']) for g in gaps)
    score = round((total / len(gaps)) * 100, 1) if gaps else 0.0
    print({'timestamp': now(), 'gap_count': len(gaps), 'overall_progress_pct': score, 'active': sum(1 for g in gaps if g['status'] == 'active'), 'verified': sum(1 for g in gaps if g['status'] == 'verified'), 'report': str(REPORT)})
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', choices=['status'])
    parser.parse_args()
    raise SystemExit(status())
