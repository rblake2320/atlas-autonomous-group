from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from business_lib import EVENTS_FILE, OWNER_REPORTS, ROOT

REPORT = OWNER_REPORTS / 'ATLAS-FAILURE-INJECTION.json'
HELM_CARD = ROOT / 'interop' / 'a2a' / 'cards' / 'helm.json'


def verify_chain(lines: list[dict]) -> bool:
    prev_hash = 'GENESIS'
    expected_seq = 1
    for item in lines:
        if item.get('seq') != expected_seq or item.get('prev_hash') != prev_hash:
            return False
        canonical = {k: item[k] for k in ['seq', 'ts', 'type', 'agent', 'payload', 'prev_hash']}
        digest = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
        if item.get('hash') != digest:
            return False
        prev_hash = item['hash']
        expected_seq += 1
    return True


def valid_schema(value: object) -> bool:
    return isinstance(value, dict) and value.get('type') == 'object' and isinstance(value.get('properties'), dict) and bool(value.get('properties')) and isinstance(value.get('required'), list) and bool(value.get('required'))


def claim_is_fresh(path: Path, ttl_hours: int) -> bool:
    age = datetime.now(timezone.utc) - datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return age <= timedelta(hours=ttl_hours)


def main() -> int:
    scenarios = []

    lines = [json.loads(line) for line in EVENTS_FILE.read_text(encoding='utf-8').splitlines() if line.strip()]
    tampered = json.loads(json.dumps(lines))
    tampered[0]['payload']['tampered'] = True
    scenarios.append({'name': 'tampered_event_chain_detected', 'passed': not verify_chain(tampered)})

    card = json.loads(HELM_CARD.read_text(encoding='utf-8'))
    card.pop('input_schema', None)
    scenarios.append({'name': 'missing_input_schema_detected', 'passed': not valid_schema(card.get('input_schema'))})

    with tempfile.TemporaryDirectory() as tmp:
        stale = Path(tmp) / 'stale.json'
        stale.write_text('{}\n', encoding='utf-8')
        old = datetime.now().timestamp() - (48 * 3600)
        os.utime(stale, (old, old))
        scenarios.append({'name': 'stale_claim_detected', 'passed': not claim_is_fresh(stale, 6)})

    problems = [item['name'] for item in scenarios if not item['passed']]
    result = {'timestamp': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'), 'status': 'PASS' if not problems else 'FAIL', 'scenarios': scenarios, 'problems': problems}
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    if problems:
        print('FAIL')
        for problem in problems:
            print(f'- {problem}')
        return 1
    print('PASS')
    print({'scenarios': len(scenarios), 'passed': len(scenarios) - len(problems)})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
