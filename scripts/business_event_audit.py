from __future__ import annotations

import hashlib
import json

from business_lib import EVENTS_FILE, EVENT_AUDIT_FILE, now


def verify_events(lines: list[dict]) -> list[str]:
    problems = []
    prev_hash = 'GENESIS'
    expected_seq = 1
    for item in lines:
        if item.get('seq') != expected_seq:
            problems.append(f"sequence mismatch at {item.get('seq')} expected {expected_seq}")
            break
        if item.get('prev_hash') != prev_hash:
            problems.append(f"prev_hash mismatch at seq {item.get('seq')}")
            break
        canonical = {k: item[k] for k in ['seq', 'ts', 'type', 'agent', 'payload', 'prev_hash']}
        digest = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
        if item.get('hash') != digest:
            problems.append(f"hash mismatch at seq {item.get('seq')}")
            break
        prev_hash = item['hash']
        expected_seq += 1
    return problems


def main() -> int:
    lines = [json.loads(line) for line in EVENTS_FILE.read_text(encoding='utf-8').splitlines() if line.strip()]
    problems = verify_events(lines)
    audit = {'timestamp': now(), 'status': 'PASS' if not problems else 'FAIL', 'event_count': len(lines), 'last_seq': lines[-1]['seq'] if lines else 0, 'chain_ok': not problems, 'problems': problems, 'rigor_score': min(90, len(lines) * 2) if not problems else 0}
    EVENT_AUDIT_FILE.write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    if problems:
        print('FAIL')
        for problem in problems:
            print(f'- {problem}')
        return 1
    print('PASS')
    print(audit)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
