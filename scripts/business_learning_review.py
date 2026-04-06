from __future__ import annotations

import json

from business_lib import LEARNING_FILE, OWNER_REPORTS, now, read_benchmarks

REPORT = OWNER_REPORTS / 'ATLAS-LEARNING-REVIEW.md'


def main() -> int:
    data = read_benchmarks()
    deltas = []
    for bench in data.get('benchmarks', []):
        baseline = bench.get('baseline', 0)
        current = bench.get('current', 0)
        if current > baseline and bench.get('verified', True):
            deltas.append({'name': bench['name'], 'delta': round(current - baseline, 4)})
    report = {'timestamp': now(), 'status': 'PASS', 'benchmarks': len(data.get('benchmarks', [])), 'verified_learning_deltas': len(deltas), 'deltas': deltas, 'source': str(LEARNING_FILE)}
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
