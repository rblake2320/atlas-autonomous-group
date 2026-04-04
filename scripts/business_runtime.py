from __future__ import annotations

import argparse
from business_lib import APP_PENDING, JOBS_ACTIVE, read_tasks

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["summary"])
    parser.parse_args()
    tasks = read_tasks()
    delivered = sum(1 for task in tasks if task["status"] == "delivered")
    print({
        "tasks": len(tasks),
        "delivered": delivered,
        "pending_approvals": len(list(APP_PENDING.glob("*.json"))),
        "active_jobs": len(list(JOBS_ACTIVE.glob("*.json"))),
    })
