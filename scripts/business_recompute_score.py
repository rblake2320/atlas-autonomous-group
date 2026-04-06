from __future__ import annotations

import json
from pathlib import Path

from business_lib import SCORECARD_FILE, OWNER_REPORTS, read_tasks, write_scorecard

REPORT = OWNER_REPORTS / 'ATLAS-SCORE-RECOMPUTE.json'


def main() -> int:
    before = json.loads(SCORECARD_FILE.read_text(encoding='utf-8')) if SCORECARD_FILE.exists() else None
    if SCORECARD_FILE.exists():
        SCORECARD_FILE.unlink()
    after = write_scorecard(read_tasks())
    report = {'before': before, 'after': after, 'recomputed': True}
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
