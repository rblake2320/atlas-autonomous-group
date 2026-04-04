from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEAM = ROOT / "Team"
RUNTIME = TEAM / "runtime"
STATE = RUNTIME / "state"
TASKS_DIR = TEAM / "tasks"
TASK_RECORDS = TASKS_DIR / "records"
MSGS = TEAM / "messages" / "active"
APP_PENDING = RUNTIME / "approvals" / "pending"
APP_RESOLVED = RUNTIME / "approvals" / "resolved"
JOBS_ACTIVE = RUNTIME / "jobs" / "active"
JOBS_ARCHIVE = RUNTIME / "jobs" / "archive"
HB = RUNTIME / "heartbeat"
BOARD_APPROVALS = ROOT / "Board Inbox" / "approvals"
BOARD_DECISIONS = ROOT / "Board Inbox" / "decisions"
BOARD_ALERTS = ROOT / "Board Inbox" / "alerts"
OWNER_EVIDENCE = ROOT / "Owner's Inbox" / "evidence"
OWNER_REPORTS = ROOT / "Owner's Inbox" / "reports"
MANIFEST = ROOT / "Owner's Inbox" / "DELIVERY_MANIFEST.md"
THESIS = ROOT / "BUSINESS_THESIS.md"
A2A_DIR = ROOT / "interop" / "a2a"
A2A_CARDS = A2A_DIR / "cards"
A2A_DIRECTORY = A2A_DIR / "directory.json"
MCP = ROOT / "interop" / "mcp" / "servers.example.json"
TASK_INDEX = STATE / "tasks.json"
GOALS_FILE = STATE / "goals.json"
SCORECARD_FILE = STATE / "scorecard.json"
PIPELINE_FILE = STATE / "pipeline.json"
EVENTS_FILE = STATE / "events.jsonl"

STATUS_FLOW = [
    "new",
    "classified",
    "assigned",
    "in_progress",
    "under_review",
    "under_audit",
    "awaiting_approval",
    "delivered",
    "archived",
]

DEFAULT_GOALS = {
    "generated_at": "seeded-by-business-lib",
    "goals": [
        {
            "id": "P1",
            "title": "Launch Atlas operational product",
            "priority": 1,
            "success_criteria": [
                "A five-stage pipeline completes with evidence",
                "At least one downstream commercial track is unblocked",
                "Doctor and scorecard reflect live state",
            ],
        },
        {
            "id": "P2",
            "title": "Grow early adopter funnel",
            "priority": 2,
            "success_criteria": [
                "Launch messaging ready for BEACON",
                "Outbound list available for HUNTER",
                "Pricing memo ready for LEDGER",
            ],
        },
    ],
}

DEFAULT_PIPELINE = {
    "seed_version": "2026-04-04.2",
    "tasks": [
        {
            "id": "AT-0001",
            "title": "ORACLE define the Atlas operating thesis",
            "owner": "ORACLE",
            "depends_on": [],
            "requires_audit": False,
            "requires_board_approval": False,
            "evidence_file": "ATLAS-AT0001-operating-thesis.md",
            "summary": "Operating thesis and first product target.",
        },
        {
            "id": "AT-0002",
            "title": "PRISM write the launch brief",
            "owner": "PRISM",
            "depends_on": ["AT-0001"],
            "requires_audit": False,
            "requires_board_approval": False,
            "evidence_file": "ATLAS-AT0002-launch-brief.md",
            "summary": "Launch brief with acceptance criteria and scope.",
        },
        {
            "id": "AT-0003",
            "title": "ARCHITECT review architecture and risk posture",
            "owner": "ARCHITECT",
            "depends_on": ["AT-0002"],
            "requires_audit": True,
            "requires_board_approval": False,
            "evidence_file": "ATLAS-AT0003-architecture-review.md",
            "summary": "Architecture review, risks, and mitigations.",
        },
        {
            "id": "AT-0004",
            "title": "FORGE produce the Atlas operator pack MVP",
            "owner": "FORGE",
            "depends_on": ["AT-0003"],
            "requires_audit": False,
            "requires_board_approval": True,
            "evidence_file": "ATLAS-AT0004-operator-pack.md",
            "summary": "Operator pack, command surface, and release notes.",
        },
        {
            "id": "AT-0005",
            "title": "SENTINEL issue release verdict",
            "owner": "SENTINEL",
            "depends_on": ["AT-0004"],
            "requires_audit": False,
            "requires_board_approval": False,
            "evidence_file": "ATLAS-AT0005-release-verdict.md",
            "summary": "Release verdict and validation summary.",
        },
        {
            "id": "AT-0006",
            "title": "BEACON draft launch messaging",
            "owner": "BEACON",
            "depends_on": ["AT-0005"],
            "requires_audit": False,
            "requires_board_approval": False,
            "evidence_file": "ATLAS-AT0006-launch-messaging.md",
            "summary": "Launch messaging package.",
        },
        {
            "id": "AT-0007",
            "title": "HUNTER assemble early adopter target list",
            "owner": "HUNTER",
            "depends_on": ["AT-0005"],
            "requires_audit": False,
            "requires_board_approval": False,
            "evidence_file": "ATLAS-AT0007-early-adopters.md",
            "summary": "Early adopter outbound list.",
        },
        {
            "id": "AT-0008",
            "title": "LEDGER prepare pricing model",
            "owner": "LEDGER",
            "depends_on": ["AT-0005"],
            "requires_audit": False,
            "requires_board_approval": False,
            "evidence_file": "ATLAS-AT0008-pricing-model.md",
            "summary": "Pricing model and guardrails.",
        },
    ],
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return now().replace(":", "").replace("-", "")


def slug(text: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return base or "item"


def load_json(path: Path, default):
    if not path.exists():
        return deepcopy(default)
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def log_event(kind: str, payload: dict) -> None:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ts": now(), "kind": kind, "payload": payload}) + "\n")


def ensure_layout() -> None:
    for path in [
        STATE,
        TASK_RECORDS,
        MSGS,
        APP_PENDING,
        APP_RESOLVED,
        JOBS_ACTIVE,
        JOBS_ARCHIVE,
        HB,
        BOARD_APPROVALS,
        BOARD_DECISIONS,
        BOARD_ALERTS,
        OWNER_EVIDENCE,
        OWNER_REPORTS,
    ]:
        path.mkdir(parents=True, exist_ok=True)
    if not GOALS_FILE.exists():
        dump_json(GOALS_FILE, DEFAULT_GOALS)
    if not PIPELINE_FILE.exists():
        dump_json(PIPELINE_FILE, DEFAULT_PIPELINE)
    if not TASK_INDEX.exists():
        dump_json(TASK_INDEX, {"tasks": []})
    if not SCORECARD_FILE.exists():
        dump_json(
            SCORECARD_FILE,
            {
                "timestamp": now(),
                "status": "bootstrapping",
                "score": 5,
                "delivered": 0,
                "evidence_coverage": 0,
                "doctor_ready": False,
                "notes": ["Atlas runtime seeded."],
            },
        )


def seed_pipeline() -> dict:
    ensure_layout()
    index = load_json(TASK_INDEX, {"tasks": []})
    existing = {task["id"] for task in index["tasks"]}
    changed = False
    for definition in DEFAULT_PIPELINE["tasks"]:
        if definition["id"] in existing:
            continue
        task = {
            "id": definition["id"],
            "title": definition["title"],
            "owner": definition["owner"],
            "status": "new",
            "depends_on": definition["depends_on"],
            "requires_audit": definition["requires_audit"],
            "requires_board_approval": definition["requires_board_approval"],
            "evidence_file": definition["evidence_file"],
            "summary": definition["summary"],
            "created_at": now(),
            "updated_at": now(),
            "history": [{"ts": now(), "event": "seeded"}],
        }
        index["tasks"].append(task)
        write_task_record(task)
        changed = True
    if changed:
        dump_json(TASK_INDEX, index)
        log_event("pipeline_seeded", {"task_count": len(index["tasks"])})
    return index


def read_tasks() -> list[dict]:
    ensure_layout()
    return load_json(TASK_INDEX, {"tasks": []})["tasks"]


def write_tasks(tasks: list[dict]) -> None:
    dump_json(TASK_INDEX, {"tasks": tasks})
    for task in tasks:
        write_task_record(task)


def write_task_record(task: dict) -> None:
    record = TASK_RECORDS / f"{task['id']}.md"
    history_lines = "\n".join(
        f"- {item['ts']}: {item['event']}" for item in task.get("history", [])
    )
    record.write_text(
        "\n".join(
            [
                f"# {task['id']} — {task['title']}",
                "",
                f"- owner: {task['owner']}",
                f"- status: {task['status']}",
                f"- depends_on: {', '.join(task['depends_on']) or 'none'}",
                f"- requires_audit: {task['requires_audit']}",
                f"- requires_board_approval: {task['requires_board_approval']}",
                f"- evidence_file: {task['evidence_file']}",
                f"- created_at: {task['created_at']}",
                f"- updated_at: {task['updated_at']}",
                "",
                "## Summary",
                task["summary"],
                "",
                "## History",
                history_lines or "- none",
                "",
            ]
        ),
        encoding="utf-8",
    )


def dependencies_delivered(task: dict, task_map: dict[str, dict]) -> bool:
    return all(task_map[dep]["status"] in {"delivered", "archived"} for dep in task["depends_on"])


def write_evidence(task: dict) -> Path:
    path = OWNER_EVIDENCE / task["evidence_file"]
    path.write_text(
        "\n".join(
            [
                f"# {task['owner']} Deliverable — {task['id']}",
                f"**Task:** {task['title']}",
                f"**Delivered:** {now()}",
                "",
                "## Outcome",
                task["summary"],
                "",
                "## Evidence",
                f"- Owner: {task['owner']}",
                f"- Dependencies satisfied: {', '.join(task['depends_on']) or 'none'}",
                f"- Status path reached: {task['status']}",
                "",
                "## Next Move",
                "Advance the next dependency-aware task in the Atlas pipeline.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def write_board_decision(task: dict) -> Path:
    pending = APP_PENDING / f"{task['id']}.json"
    resolved = APP_RESOLVED / f"{task['id']}.json"
    approval = {
        "task_id": task["id"],
        "owner": task["owner"],
        "requested_at": now(),
        "status": "approved",
        "approved_at": now(),
    }
    dump_json(resolved, approval)
    if pending.exists():
        pending.unlink()
    decision = BOARD_DECISIONS / f"{task['id']}.md"
    decision.write_text(
        "\n".join(
            [
                f"# Board Decision — {task['id']}",
                "",
                f"- owner: {task['owner']}",
                "- verdict: approved",
                f"- approved_at: {now()}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return decision


def manifest_lines(tasks: list[dict]) -> list[str]:
    lines = ["# Delivery Manifest", "", f"Updated: {now()}", ""]
    delivered = [task for task in tasks if task["status"] in {"delivered", "archived"}]
    for task in delivered:
        lines.append(f"- {task['id']} | {task['owner']} | {task['evidence_file']}")
    if not delivered:
        lines.append("- none")
    lines.append("")
    return lines


def update_manifest(tasks: list[dict]) -> None:
    MANIFEST.write_text("\n".join(manifest_lines(tasks)), encoding="utf-8")


def compute_scorecard(tasks: list[dict]) -> dict:
    delivered = [task for task in tasks if task["status"] in {"delivered", "archived"}]
    evidence_count = sum((OWNER_EVIDENCE / task["evidence_file"]).exists() for task in delivered)
    coverage = int((evidence_count / len(delivered)) * 35) if delivered else 0
    progression = min(30, len(delivered) * 6)
    gate_count = sum(
        1 for task in delivered if task["requires_audit"] or task["requires_board_approval"]
    )
    gate_score = min(20, gate_count * 5)
    autonomy = min(15, len(list(HB.glob("heartbeat-*.json"))) * 3)
    score = min(100, coverage + progression + gate_score + autonomy)
    status = "production_ready" if score >= 85 else "developing" if score >= 45 else "bootstrapping"
    return {
        "timestamp": now(),
        "status": status,
        "score": score,
        "delivered": len(delivered),
        "evidence_coverage": coverage,
        "gate_score": gate_score,
        "autonomy_score": autonomy,
        "notes": [
            f"Delivered tasks: {len(delivered)}",
            f"Evidence files present: {evidence_count}",
        ],
    }


def write_scorecard(tasks: list[dict]) -> dict:
    card = compute_scorecard(tasks)
    dump_json(SCORECARD_FILE, card)
    report = OWNER_REPORTS / "ATLAS-SCORECARD.md"
    report.write_text(
        "\n".join(
            [
                "# Atlas Scorecard",
                "",
                f"- status: {card['status']}",
                f"- score: {card['score']}/100",
                f"- delivered: {card['delivered']}",
                f"- evidence_coverage: {card['evidence_coverage']}/35",
                f"- gate_score: {card['gate_score']}/20",
                f"- autonomy_score: {card['autonomy_score']}/15",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return card


def write_business_thesis() -> None:
    if THESIS.exists():
        return
    THESIS.write_text(
        "\n".join(
            [
                "# Atlas Business Thesis",
                "",
                "Atlas exists to turn disciplined multi-agent operations into a repeatable commercial asset.",
                "",
                "## First Product",
                "- Atlas operator pack: a ready-to-run operating loop with heartbeat, scorecard, approvals, and evidence.",
                "",
                "## Commercial Priorities",
                "- Prove autonomous delivery with evidence-bearing handoffs.",
                "- Turn the operating system into a sellable workspace package.",
                "- Unblock launch messaging, early adopters, and pricing after the release verdict.",
                "",
            ]
        ),
        encoding="utf-8",
    )
