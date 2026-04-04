from __future__ import annotations

import json
from business_lib import (
    A2A_CARDS,
    A2A_DIRECTORY,
    GOALS_FILE,
    HB,
    MCP,
    OWNER_EVIDENCE,
    PIPELINE_FILE,
    SCORECARD_FILE,
    TASK_INDEX,
    THESIS,
    ensure_layout,
    read_tasks,
)

ensure_layout()
problems = []
checks = 0

def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        problems.append(message)

for path in [THESIS, GOALS_FILE, PIPELINE_FILE, TASK_INDEX, SCORECARD_FILE, A2A_DIRECTORY, MCP]:
    check(path.exists(), f"missing {path.name}")

for path in [GOALS_FILE, PIPELINE_FILE, TASK_INDEX, SCORECARD_FILE, A2A_DIRECTORY, MCP]:
    if path.exists():
        try:
            json.loads(path.read_text(encoding="utf-8"))
            check(True, "")
        except Exception as exc:
            check(False, f"invalid json {path.name}: {exc}")

tasks = read_tasks()
cards = list(A2A_CARDS.glob("*.json"))
check(len(tasks) >= 8, "expected seeded pipeline with at least 8 tasks")
check(len(cards) >= 15, "expected A2A cards for all agents")

ids = set()
for task in tasks:
    check(task["id"] not in ids, f"duplicate task id {task['id']}")
    ids.add(task["id"])
    check(task["status"] in {"new", "classified", "assigned", "in_progress", "under_review", "under_audit", "awaiting_approval", "delivered", "archived"}, f"invalid status for {task['id']}")
    if task["status"] == "delivered":
        check((OWNER_EVIDENCE / task["evidence_file"]).exists(), f"missing evidence for delivered task {task['id']}")

heartbeats = list(HB.glob("heartbeat-*.json"))
check(len(heartbeats) >= 1, "expected at least one heartbeat record")

score = json.loads(SCORECARD_FILE.read_text(encoding="utf-8")) if SCORECARD_FILE.exists() else {}
check("score" in score and score.get("score", 0) >= 0, "scorecard missing score")
check(score.get("status") in {"bootstrapping", "developing", "production_ready"}, "scorecard missing valid status")

if problems:
    print("FAIL")
    print(f"checks={checks}")
    for problem in problems:
        print(f"- {problem}")
    raise SystemExit(1)

print("PASS")
print(f"checks={checks}")
