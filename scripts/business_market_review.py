from __future__ import annotations

import json

from business_lib import MARKET_FILE, OWNER_REPORTS, now, read_market

REPORT = OWNER_REPORTS / 'ATLAS-MARKET-REVIEW.md'


def main() -> int:
    data = read_market()
    verified = [win for win in data.get('wins', []) if win.get('verified')]
    report = {'timestamp': now(), 'status': 'PASS', 'wins_total': len(data.get('wins', [])), 'verified_external_wins': len(verified), 'wins': verified, 'source': str(MARKET_FILE)}
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
