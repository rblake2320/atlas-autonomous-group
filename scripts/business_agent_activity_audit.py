from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from business_lib import EVENTS_FILE, HB, OWNER_REPORTS, ROOT, TASK_INDEX

REPORT = OWNER_REPORTS / 'ATLAS-AGENT-ACTIVITY.json'
ROSTER = ROOT / 'Team' / 'roster.md'
WINDOW = timedelta(days=7)
CRITICAL = {'HELM', 'VECTOR', 'FORGE', 'SENTINEL', 'WIRING', 'SCHEMA', 'INSPECTOR', 'REGENT', 'VERIFY'}
REPORT_MAP = {
    'WIRING': OWNER_REPORTS / 'ATLAS-WIRING-AUDIT.json',
    'SCHEMA': OWNER_REPORTS / 'ATLAS-SCHEMA-AUDIT.json',
    'INSPECTOR': OWNER_REPORTS / 'ATLAS-CODE-INSPECTOR.json',
    'BENCH': OWNER_REPORTS / 'ATLAS-LEARNING-REVIEW.md',
    'MARKET': OWNER_REPORTS / 'ATLAS-MARKET-REVIEW.md',
    'REGENT': ROOT / 'Team' / 'runtime' / 'state' / 'event_audit.json',
    'STEWARD': ROOT / 'Team' / 'runtime' / 'state' / 'runtime_audit.json',
    'VERIFY': OWNER_REPORTS / 'ATLAS-GAP-METER.md',
    'HELM': ROOT / 'Team' / 'runtime' / 'state' / 'scorecard.json',
    'VECTOR': None,
}


def roster_agents() -> list[str]:
    agents = []
    for line in ROSTER.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| ') or 'Agent | Department' in line or '| --- ' in line:
            continue
        parts = [part.strip() for part in line.strip('|').split('|')]
        if parts and parts[0]:
            agents.append(parts[0])
    return agents


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def latest_task_activity() -> dict[str, datetime]:
    latest = {}
    payload = json.loads(TASK_INDEX.read_text(encoding='utf-8'))
    for task in payload.get('tasks', []):
        owner = task.get('owner')
        ts = parse_ts(task.get('updated_at'))
        if owner and ts and (owner not in latest or ts > latest[owner]):
            latest[owner] = ts
    return latest


def latest_event_activity() -> dict[str, datetime]:
    latest = {}
    for line in EVENTS_FILE.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        ts = parse_ts(event.get('ts'))
        agent = event.get('agent')
        if agent and ts and (agent not in latest or ts > latest[agent]):
            latest[agent] = ts
    return latest


def latest_report_activity() -> dict[str, datetime]:
    latest = {}
    for agent, path in REPORT_MAP.items():
        if path is None:
            hb_files = sorted(HB.glob('heartbeat-*.json'))
            if hb_files:
                latest[agent] = datetime.fromtimestamp(hb_files[-1].stat().st_mtime, tz=timezone.utc)
            continue
        if path.exists():
            latest[agent] = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return latest


def main() -> int:
    now = datetime.now(timezone.utc)
    activity = {}
    for source in [latest_task_activity(), latest_event_activity(), latest_report_activity()]:
        for agent, ts in source.items():
            if agent not in activity or ts > activity[agent]:
                activity[agent] = ts

    rows = []
    problems = []
    for agent in roster_agents():
        ts = activity.get(agent)
        age_hours = None if ts is None else round((now - ts).total_seconds() / 3600, 2)
        active = ts is not None and (now - ts) <= WINDOW
        if agent in CRITICAL and not active:
            problems.append(f'critical agent inactive: {agent}')
        rows.append({'agent': agent, 'last_activity': None if ts is None else ts.replace(microsecond=0).isoformat().replace('+00:00', 'Z'), 'age_hours': age_hours, 'status': 'active' if active else 'inactive', 'critical': agent in CRITICAL})

    result = {'timestamp': now.replace(microsecond=0).isoformat().replace('+00:00', 'Z'), 'status': 'PASS' if not problems else 'FAIL', 'active_agents': sum(1 for row in rows if row['status'] == 'active'), 'inactive_agents': sum(1 for row in rows if row['status'] == 'inactive'), 'agents': rows, 'problems': problems}
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    if problems:
        print('FAIL')
        for problem in problems:
            print(f'- {problem}')
        return 1
    print('PASS')
    print({'active_agents': result['active_agents'], 'inactive_agents': result['inactive_agents']})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
