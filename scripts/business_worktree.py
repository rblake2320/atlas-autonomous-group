from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from business_lib import ROOT, now, read_worktrees, slug, write_worktrees

REPO_ROOT = ROOT


def _resolve_target(path_str: str) -> Path:
    base = Path(read_worktrees()["root"]).resolve()
    target = Path(path_str)
    if not target.is_absolute():
        target = base / target
    target = target.resolve()
    if base != target and base not in target.parents:
        raise ValueError("worktree path escapes configured root")
    return target


def summary() -> int:
    registry = read_worktrees()
    print({
        "timestamp": now(),
        "enabled": registry.get("enabled", False),
        "root": registry.get("root"),
        "registrations": len(registry.get("registrations", [])),
        "branches": [item["branch"] for item in registry.get("registrations", [])],
    })
    return 0


def register(owner: str, task_id: str, branch: str, path: str) -> int:
    registry = read_worktrees()
    target = _resolve_target(path)
    registry.setdefault("registrations", []).append({
        "ts": now(),
        "owner": owner,
        "task_id": task_id,
        "branch": branch,
        "path": str(target),
        "status": "registered",
    })
    write_worktrees(registry)
    return summary()


def plan(owner: str, task_id: str) -> int:
    branch = f"atlas/{owner.lower()}-{slug(task_id)}"
    rel = slug(f"{owner}-{task_id}")
    target = _resolve_target(rel)
    print({
        "branch": branch,
        "path": str(target),
        "command": ["git", "-C", str(REPO_ROOT), "worktree", "add", str(target), "-b", branch],
    })
    return 0


def create(owner: str, task_id: str, branch: str | None, path: str | None) -> int:
    registry = read_worktrees()
    if not registry.get("enabled", False):
        print({"error": "worktrees_disabled"})
        return 1
    branch = branch or f"atlas/{owner.lower()}-{slug(task_id)}"
    target = _resolve_target(path or slug(f"{owner}-{task_id}"))
    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "-C", str(REPO_ROOT), "worktree", "add", str(target), "-b", branch]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        print({"error": "worktree_create_failed", "stderr": result.stderr.strip()})
        return result.returncode
    registry.setdefault("registrations", []).append({
        "ts": now(),
        "owner": owner,
        "task_id": task_id,
        "branch": branch,
        "path": str(target),
        "status": "created",
    })
    write_worktrees(registry)
    print({"created": True, "branch": branch, "path": str(target)})
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("summary")
    reg = sub.add_parser("register")
    reg.add_argument("owner")
    reg.add_argument("task_id")
    reg.add_argument("branch")
    reg.add_argument("path")
    plan_cmd = sub.add_parser("plan")
    plan_cmd.add_argument("owner")
    plan_cmd.add_argument("task_id")
    create_cmd = sub.add_parser("create")
    create_cmd.add_argument("owner")
    create_cmd.add_argument("task_id")
    create_cmd.add_argument("--branch")
    create_cmd.add_argument("--path")
    args = parser.parse_args()

    if args.cmd == "summary":
        raise SystemExit(summary())
    if args.cmd == "register":
        raise SystemExit(register(args.owner, args.task_id, args.branch, args.path))
    if args.cmd == "plan":
        raise SystemExit(plan(args.owner, args.task_id))
    raise SystemExit(create(args.owner, args.task_id, args.branch, args.path))
