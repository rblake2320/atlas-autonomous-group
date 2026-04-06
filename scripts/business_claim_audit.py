from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from business_lib import OWNER_REPORTS, ROOT

PLAN = ROOT / 'Team' / 'runtime' / 'state' / 'validation_plan.json'
REPORT = OWNER_REPORTS / 'ATLAS-CLAIMS.json'

DEFAULT_PLAN = {
    'claims': [
        {'id': 'scorecard_fresh', 'ttl_hours': 6, 'evidence': 'Team/runtime/state/scorecard.json', 'must_equal': {'status': 'production_ready'}},
        {'id': 'doctor_pass', 'ttl_hours': 6, 'evidence': "Owner's Inbox/reports/ATLAS-DOCTOR.json", 'must_equal': {'status': 'PASS'}},
        {'id': 'full_validation_pass', 'ttl_hours': 6, 'evidence': "Owner's Inbox/reports/ATLAS-FULL-VALIDATION.json", 'must_equal': {'status': 'PASS'}},
        {'id': 'runtime_rigor_current', 'ttl_hours': 24, 'evidence': 'Team/runtime/state/event_audit.json', 'must_equal': {'status': 'PASS'}},
        {'id': 'runtime_uptime_current', 'ttl_hours': 6, 'evidence': 'Team/runtime/state/runtime_audit.json', 'min_numeric': {'continuous_hours': 0}},
        {'id': 'gap_meter_current', 'ttl_hours': 24, 'evidence': "Owner's Inbox/reports/ATLAS-GAP-METER.md"},
    ]
}


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def ensure_plan() -> dict:
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    PLAN.write_text(json.dumps(DEFAULT_PLAN, indent=2) + '\n', encoding='utf-8')
    return DEFAULT_PLAN


def load_evidence(path: Path) -> tuple[dict, datetime | None]:
    if not path.exists():
        return {}, None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        data = {}
    ts = parse_timestamp(data.get('timestamp')) if isinstance(data, dict) else None
    if ts is None:
        ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return data if isinstance(data, dict) else {}, ts


def main() -> int:
    plan = ensure_plan()
    now = datetime.now(timezone.utc)
    rows = []
    problems = []
    for claim in plan.get('claims', []):
        evidence_path = ROOT / claim['evidence']
        evidence, ts = load_evidence(evidence_path)
        ttl = timedelta(hours=claim['ttl_hours'])
        age_hours = None if ts is None else round((now - ts).total_seconds() / 3600, 2)
        fresh = ts is not None and (now - ts) <= ttl
        ok = evidence_path.exists() and fresh
        if ok and 'must_equal' in claim:
            for key, expected in claim['must_equal'].items():
                if evidence.get(key) != expected:
                    ok = False
                    problems.append(f"{claim['id']} expected {key}={expected}, got {evidence.get(key)}")
        if ok and 'min_numeric' in claim:
            for key, minimum in claim['min_numeric'].items():
                if float(evidence.get(key, -1)) < minimum:
                    ok = False
                    problems.append(f"{claim['id']} expected {key}>={minimum}, got {evidence.get(key)}")
        if not evidence_path.exists():
            problems.append(f"{claim['id']} missing evidence {claim['evidence']}")
        elif not fresh:
            problems.append(f"{claim['id']} stale: {age_hours}h old")
        rows.append({'id': claim['id'], 'evidence': claim['evidence'], 'ttl_hours': claim['ttl_hours'], 'age_hours': age_hours, 'fresh': fresh, 'status': 'verified' if ok else 'stale'})
    result = {'timestamp': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'), 'status': 'PASS' if not problems else 'FAIL', 'claims': rows, 'problems': problems}
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    if problems:
        print('FAIL')
        for problem in problems:
            print(f'- {problem}')
        return 1
    print('PASS')
    print({'claims': len(rows), 'status': 'current'})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
