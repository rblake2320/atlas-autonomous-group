from __future__ import annotations

import argparse
from business_lib import (
    APP_PENDING,
    HB,
    dependencies_delivered,
    dump_json,
    load_json,
    now,
    read_tasks,
    seed_pipeline,
    stamp,
    update_manifest,
    write_board_decision,
    write_evidence,
    write_scorecard,
    write_tasks,
)


def pulse_once() -> dict:
    seed_pipeline()
    tasks = read_tasks()
    task_map = {task["id"]: task for task in tasks}
    changed = []

    for task in tasks:
        status = task["status"]
        if status in {"delivered", "archived"}:
            continue
        if not dependencies_delivered(task, task_map):
            continue
        if status == "new":
            task["status"] = "classified"
            task["history"].append({"ts": now(), "event": "classified"})
            task["updated_at"] = now()
            changed.append((task["id"], "classified"))
            continue
        if status == "classified":
            task["status"] = "assigned"
            task["history"].append({"ts": now(), "event": f'assigned:{task["owner"]}'})
            task["updated_at"] = now()
            changed.append((task["id"], "assigned"))
            continue
        if status == "assigned":
            task["status"] = "in_progress"
            task["history"].append({"ts": now(), "event": "started"})
            task["updated_at"] = now()
            changed.append((task["id"], "in_progress"))
            continue
        if status == "in_progress":
            write_evidence(task)
            task["status"] = "under_review"
            task["history"].append({"ts": now(), "event": "evidence_created"})
            task["updated_at"] = now()
            changed.append((task["id"], "under_review"))
            continue
        if status == "under_review":
            if task["requires_audit"]:
                task["status"] = "under_audit"
                task["history"].append({"ts": now(), "event": "audit_requested"})
                task["updated_at"] = now()
                changed.append((task["id"], "under_audit"))
            elif task["requires_board_approval"]:
                pending = APP_PENDING / f"{task['id']}.json"
                dump_json(pending, {"task_id": task["id"], "owner": task["owner"], "requested_at": now(), "status": "pending"})
                task["status"] = "awaiting_approval"
                task["history"].append({"ts": now(), "event": "approval_requested"})
                task["updated_at"] = now()
                changed.append((task["id"], "awaiting_approval"))
            else:
                task["status"] = "delivered"
                task["history"].append({"ts": now(), "event": "delivered"})
                task["updated_at"] = now()
                changed.append((task["id"], "delivered"))
            continue
        if status == "under_audit":
            if task["requires_board_approval"]:
                pending = APP_PENDING / f"{task['id']}.json"
                dump_json(pending, {"task_id": task["id"], "owner": task["owner"], "requested_at": now(), "status": "pending"})
                task["status"] = "awaiting_approval"
                task["history"].append({"ts": now(), "event": "audit_passed"})
                task["updated_at"] = now()
                changed.append((task["id"], "awaiting_approval"))
            else:
                task["status"] = "delivered"
                task["history"].append({"ts": now(), "event": "audit_passed"})
                task["updated_at"] = now()
                changed.append((task["id"], "delivered"))
            continue
        if status == "awaiting_approval":
            write_board_decision(task)
            task["status"] = "delivered"
            task["history"].append({"ts": now(), "event": "board_approved"})
            task["updated_at"] = now()
            changed.append((task["id"], "delivered"))

    write_tasks(tasks)
    update_manifest(tasks)
    scorecard = write_scorecard(tasks)
    summary = {
        "timestamp": now(),
        "changed": changed,
        "counts": {state: sum(1 for task in tasks if task["status"] == state) for state in sorted({task["status"] for task in tasks})},
        "scorecard": scorecard,
    }
    path = HB / f"heartbeat-{stamp()}.json"
    dump_json(path, summary)
    return {"path": str(path), "summary": summary}


def heartbeat_summary() -> dict:
    files = sorted(HB.glob("heartbeat-*.json"))
    latest = load_json(files[-1], {}) if files else {}
    return {"heartbeat_records": len(files), "latest": files[-1].name if files else None, "score": latest.get("scorecard", {})}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["run", "summary"])
    args = parser.parse_args()
    if args.cmd == "run":
        out = pulse_once()
        print(out["path"])
        print(out["summary"])
    else:
        print(heartbeat_summary())
