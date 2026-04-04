from __future__ import annotations

import argparse
from business_lib import dump_json, now, read_tasks, seed_pipeline, write_tasks


def create_task(title: str, owner: str, gates: str) -> dict:
    tasks = read_tasks()
    next_id = f"AT-{len(tasks)+1:04d}"
    task = {
        "id": next_id,
        "title": title,
        "owner": owner,
        "status": "new",
        "depends_on": [],
        "requires_audit": "audit" in gates,
        "requires_board_approval": "board" in gates,
        "evidence_file": f"{next_id}-manual.md",
        "summary": title,
        "created_at": now(),
        "updated_at": now(),
        "history": [{"ts": now(), "event": "manually_created"}],
    }
    tasks.append(task)
    write_tasks(tasks)
    return task


def board() -> None:
    tasks = read_tasks()
    buckets = {}
    for task in tasks:
        buckets.setdefault(task["status"], []).append(task)
    for status in ["new", "classified", "assigned", "in_progress", "under_review", "under_audit", "awaiting_approval", "delivered", "archived"]:
        entries = buckets.get(status, [])
        print(f"== {status.upper()} ({len(entries)}) ==")
        for task in entries:
            print(f"{task['id']} | {task['owner']:<10} | {task['title']}")
        if not entries:
            print("- none")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed")
    create = sub.add_parser("create")
    create.add_argument("title")
    create.add_argument("--owner", default="HELM")
    create.add_argument("--gates", default="none")
    sub.add_parser("list")
    sub.add_parser("board")
    args = parser.parse_args()
    if args.cmd == "seed":
        seeded = seed_pipeline()
        print(f"seeded_tasks={len(seeded['tasks'])}")
    elif args.cmd == "create":
        print(create_task(args.title, args.owner, args.gates))
    elif args.cmd == "board":
        board()
    else:
        for task in read_tasks():
            print(f"{task['id']} | {task['status']:<17} | {task['owner']:<10} | {task['title']}")
