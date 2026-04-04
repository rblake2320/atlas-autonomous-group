from __future__ import annotations

import shutil
from pathlib import Path

from business_lib import (
    APP_PENDING,
    APP_RESOLVED,
    BOARD_DECISIONS,
    EVENTS_FILE,
    HB,
    JOBS_ACTIVE,
    JOBS_ARCHIVE,
    MANIFEST,
    OWNER_EVIDENCE,
    OWNER_REPORTS,
    SCORECARD_FILE,
    TASK_INDEX,
    TASK_RECORDS,
    dump_json,
    ensure_layout,
    now,
)


def clear_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


if __name__ == '__main__':
    ensure_layout()
    for path in [
        TASK_RECORDS,
        APP_PENDING,
        APP_RESOLVED,
        JOBS_ACTIVE,
        JOBS_ARCHIVE,
        HB,
        OWNER_EVIDENCE,
        OWNER_REPORTS,
        BOARD_DECISIONS,
    ]:
        clear_dir(path)
    if EVENTS_FILE.exists():
        EVENTS_FILE.unlink()
    dump_json(TASK_INDEX, {"tasks": []})
    dump_json(
        SCORECARD_FILE,
        {
            "timestamp": now(),
            "status": "bootstrapping",
            "score": 5,
            "delivered": 0,
            "evidence_coverage": 0,
            "doctor_ready": False,
            "notes": ["Atlas runtime reset."],
        },
    )
    MANIFEST.write_text('# Delivery Manifest\n\n- none\n', encoding='utf-8')
    print('RESET COMPLETE')
