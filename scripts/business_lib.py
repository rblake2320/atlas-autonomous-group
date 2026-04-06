from __future__ import annotations

import hashlib
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
EVENT_AUDIT_FILE = STATE / "event_audit.json"
BUDGET_FILE = STATE / "budget.json"
WORKTREE_FILE = STATE / "worktrees.json"
GAPS_FILE = STATE / "gaps.json"
RUNTIME_AUDIT_FILE = STATE / "runtime_audit.json"
LEARNING_FILE = STATE / "benchmarks.json"
MARKET_FILE = STATE / "market.json"

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
        {"id": "AT-0001", "title": "ORACLE define the Atlas operating thesis", "owner": "ORACLE", "depends_on": [], "requires_audit": False, "requires_board_approval": False, "evidence_file": "ATLAS-AT0001-operating-thesis.md", "summary": "Operating thesis and first product target."},
        {"id": "AT-0002", "title": "PRISM write the launch brief", "owner": "PRISM", "depends_on": ["AT-0001"], "requires_audit": False, "requires_board_approval": False, "evidence_file": "ATLAS-AT0002-launch-brief.md", "summary": "Launch brief with acceptance criteria and scope."},
        {"id": "AT-0003", "title": "ARCHITECT review architecture and risk posture", "owner": "ARCHITECT", "depends_on": ["AT-0002"], "requires_audit": True, "requires_board_approval": False, "evidence_file": "ATLAS-AT0003-architecture-review.md", "summary": "Architecture review, risks, and mitigations."},
        {"id": "AT-0004", "title": "FORGE produce the Atlas operator pack MVP", "owner": "FORGE", "depends_on": ["AT-0003"], "requires_audit": False, "requires_board_approval": True, "evidence_file": "ATLAS-AT0004-operator-pack.md", "summary": "Operator pack, command surface, and release notes."},
        {"id": "AT-0005", "title": "SENTINEL issue release verdict", "owner": "SENTINEL", "depends_on": ["AT-0004"], "requires_audit": False, "requires_board_approval": False, "evidence_file": "ATLAS-AT0005-release-verdict.md", "summary": "Release verdict and validation summary."},
        {"id": "AT-0006", "title": "BEACON draft launch messaging", "owner": "BEACON", "depends_on": ["AT-0005"], "requires_audit": False, "requires_board_approval": False, "evidence_file": "ATLAS-AT0006-launch-messaging.md", "summary": "Launch messaging package."},
        {"id": "AT-0007", "title": "HUNTER assemble early adopter target list", "owner": "HUNTER", "depends_on": ["AT-0005"], "requires_audit": False, "requires_board_approval": False, "evidence_file": "ATLAS-AT0007-early-adopters.md", "summary": "Early adopter outbound list."},
        {"id": "AT-0008", "title": "LEDGER prepare pricing model", "owner": "LEDGER", "depends_on": ["AT-0005"], "requires_audit": False, "requires_board_approval": False, "evidence_file": "ATLAS-AT0008-pricing-model.md", "summary": "Pricing model and guardrails."},
    ],
}

DEFAULT_BUDGET = {"currency": "USD", "monthly_limit": 1200, "alert_threshold": 0.8, "spent": 0, "ledger": []}
DEFAULT_WORKTREES = {"enabled": True, "root": str(ROOT / ".worktrees"), "registrations": []}
DEFAULT_BENCHMARKS = {"benchmarks": []}
DEFAULT_MARKET = {"wins": []}
DEFAULT_GAPS = {
    "generated_at": "seeded-by-business-lib",
    "gaps": [
        {"id": "runtime_rigor", "title": "Replay and tamper-proof runtime rigor", "owner": "REGENT", "metric": "rigor_score", "baseline": 0, "current": 0, "target": 90, "status": "active", "verifier_cmd": "python scripts/business_event_audit.py", "evidence_path": "Team/runtime/state/event_audit.json"},
        {"id": "autonomy_hours", "title": "Long-horizon autonomous runtime", "owner": "STEWARD", "metric": "continuous_hours", "baseline": 0, "current": 0, "target": 24, "status": "active", "verifier_cmd": "python scripts/business_runtime.py summary", "evidence_path": "Team/runtime/state/runtime_audit.json"},
        {"id": "learning_proof", "title": "Measured before/after learning improvement", "owner": "BENCH", "metric": "verified_learning_deltas", "baseline": 0, "current": 0, "target": 5, "status": "active", "verifier_cmd": "python scripts/business_learning_review.py", "evidence_path": "Team/runtime/state/benchmarks.json"},
        {"id": "external_value", "title": "Real external economic value", "owner": "MARKET", "metric": "verified_external_wins", "baseline": 0, "current": 0, "target": 3, "status": "active", "verifier_cmd": "python scripts/business_market_review.py", "evidence_path": "Team/runtime/state/market.json"},
        {"id": "interop_replay", "title": "Third-party replayable interop proof", "owner": "VERIFY", "metric": "bidirectional_verified_receipts", "baseline": 1, "current": 1, "target": 3, "status": "active", "verifier_cmd": "python scripts/business_full_validation.py run", "evidence_path": "Owner's Inbox/evidence/ATLAS-INTEROP-RECEIPT.md"},
    ],
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")


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


def canonical_event(seq: int, ts: str, kind: str, agent: str, payload: dict, prev_hash: str) -> dict:
    canonical = {"seq": seq, "ts": ts, "type": kind, "agent": agent, "payload": payload, "prev_hash": prev_hash}
    digest = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    canonical["hash"] = digest
    return canonical


def build_chain_from_tasks() -> list[dict]:
    tasks = load_json(TASK_INDEX, {"tasks": []}).get("tasks", [])
    rows: list[tuple[str, str, str, dict]] = []
    rows.append((now(), "system.init", "HELM", {"reason": "atlas_chain_migration"}))
    for task in tasks:
        rows.append((task.get("created_at", now()), "task.seeded", task["owner"], {"task_id": task["id"], "title": task["title"]}))
        for item in task.get("history", []):
            rows.append((item["ts"], f"task.{item['event']}", task["owner"], {"task_id": task["id"]}))
    rows.sort(key=lambda item: (item[0], item[1], item[2]))
    chain = []
    prev_hash = "GENESIS"
    for idx, (ts, kind, agent, payload) in enumerate(rows, start=1):
        event = canonical_event(idx, ts, kind, agent, payload, prev_hash)
        chain.append(event)
        prev_hash = event["hash"]
    return chain


def ensure_event_chain() -> None:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not EVENTS_FILE.exists() or EVENTS_FILE.read_text(encoding="utf-8").strip() == "":
        chain = build_chain_from_tasks()
        EVENTS_FILE.write_text("\n".join(json.dumps(item) for item in chain) + ("\n" if chain else ""), encoding="utf-8")
        return
    lines = [json.loads(line) for line in EVENTS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if lines and "seq" in lines[0] and "hash" in lines[0]:
        return
    chain = build_chain_from_tasks()
    EVENTS_FILE.write_text("\n".join(json.dumps(item) for item in chain) + ("\n" if chain else ""), encoding="utf-8")


def log_event(kind: str, payload: dict, agent: str = "HELM") -> None:
    ensure_event_chain()
    lines = [json.loads(line) for line in EVENTS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    prev_hash = lines[-1]["hash"] if lines else "GENESIS"
    seq = (lines[-1]["seq"] + 1) if lines else 1
    event = canonical_event(seq, now(), kind, agent, payload, prev_hash)
    with EVENTS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def ensure_layout() -> None:
    for path in [STATE, TASK_RECORDS, MSGS, APP_PENDING, APP_RESOLVED, JOBS_ACTIVE, JOBS_ARCHIVE, HB, BOARD_APPROVALS, BOARD_DECISIONS, BOARD_ALERTS, OWNER_EVIDENCE, OWNER_REPORTS]:
        path.mkdir(parents=True, exist_ok=True)
    if not GOALS_FILE.exists():
        dump_json(GOALS_FILE, DEFAULT_GOALS)
    if not PIPELINE_FILE.exists():
        dump_json(PIPELINE_FILE, DEFAULT_PIPELINE)
    if not TASK_INDEX.exists():
        dump_json(TASK_INDEX, {"tasks": []})
    if not BUDGET_FILE.exists():
        dump_json(BUDGET_FILE, DEFAULT_BUDGET)
    if not WORKTREE_FILE.exists():
        dump_json(WORKTREE_FILE, DEFAULT_WORKTREES)
    if not LEARNING_FILE.exists():
        dump_json(LEARNING_FILE, DEFAULT_BENCHMARKS)
    if not MARKET_FILE.exists():
        dump_json(MARKET_FILE, DEFAULT_MARKET)
    if not GAPS_FILE.exists():
        dump_json(GAPS_FILE, DEFAULT_GAPS)
    if not SCORECARD_FILE.exists():
        dump_json(SCORECARD_FILE, {"timestamp": now(), "status": "bootstrapping", "score": 5, "delivered": 0, "evidence_coverage": 0, "doctor_ready": False, "notes": ["Atlas runtime seeded."]})
    ensure_event_chain()


def seed_pipeline() -> dict:
    ensure_layout()
    index = load_json(TASK_INDEX, {"tasks": []})
    existing = {task["id"] for task in index["tasks"]}
    changed = False
    for definition in DEFAULT_PIPELINE["tasks"]:
        if definition["id"] in existing:
            continue
        task = {"id": definition["id"], "title": definition["title"], "owner": definition["owner"], "status": "new", "depends_on": definition["depends_on"], "requires_audit": definition["requires_audit"], "requires_board_approval": definition["requires_board_approval"], "evidence_file": definition["evidence_file"], "summary": definition["summary"], "created_at": now(), "updated_at": now(), "history": [{"ts": now(), "event": "seeded"}]}
        index["tasks"].append(task)
        write_task_record(task)
        changed = True
    if changed:
        dump_json(TASK_INDEX, index)
        ensure_event_chain()
        log_event("pipeline.seeded", {"task_count": len(index["tasks"])}, "HELM")
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
    history_lines = "\n".join(f"- {item['ts']}: {item['event']}" for item in task.get("history", []))
    record.write_text("\n".join([f"# {task['id']} — {task['title']}", "", f"- owner: {task['owner']}", f"- status: {task['status']}", f"- depends_on: {', '.join(task['depends_on']) or 'none'}", f"- requires_audit: {task['requires_audit']}", f"- requires_board_approval: {task['requires_board_approval']}", f"- evidence_file: {task['evidence_file']}", f"- created_at: {task['created_at']}", f"- updated_at: {task['updated_at']}", "", "## Summary", task["summary"], "", "## History", history_lines or "- none", ""]), encoding="utf-8")


def dependencies_delivered(task: dict, task_map: dict[str, dict]) -> bool:
    return all(task_map[dep]["status"] in {"delivered", "archived"} for dep in task["depends_on"])


def write_evidence(task: dict) -> Path:
    budget = load_json(BUDGET_FILE, DEFAULT_BUDGET)
    score = load_json(SCORECARD_FILE, {"score": 0, "status": "bootstrapping"})
    deps = ", ".join(task["depends_on"]) or "none"
    remaining = budget["monthly_limit"] - budget["spent"]
    path = OWNER_EVIDENCE / task["evidence_file"]
    path.write_text("\n".join([f"# {task['owner']} Deliverable — {task['id']}", f"**Task:** {task['title']}", f"**Delivered:** {now()}", "", "## Outcome", task["summary"], "", "## Delivery Evidence", f"- Owner: {task['owner']}", f"- Dependencies satisfied: {deps}", f"- Status path reached: {task['status']}", f"- Audit gate required: {task['requires_audit']}", f"- Board approval required: {task['requires_board_approval']}", f"- Current score snapshot: {score.get('score', 0)}/100 ({score.get('status', 'unknown')})", "", "## Runtime Context", f"- Thesis file: {THESIS.relative_to(ROOT)}", f"- Manifest file: {MANIFEST.relative_to(ROOT)}", f"- MCP registry: {MCP.relative_to(ROOT)}", f"- A2A directory: {A2A_DIRECTORY.relative_to(ROOT)}", "", "## Budget Context", f"- Monthly limit: {budget['currency']} {budget['monthly_limit']}", f"- Spent so far: {budget['currency']} {budget['spent']}", f"- Remaining headroom: {budget['currency']} {remaining}", "", "## Next Move", "Advance the next dependency-aware task in the Atlas pipeline.", ""]), encoding="utf-8")
    return path


def write_board_decision(task: dict) -> Path:
    pending = APP_PENDING / f"{task['id']}.json"
    resolved = APP_RESOLVED / f"{task['id']}.json"
    approval = {"task_id": task["id"], "owner": task["owner"], "requested_at": now(), "status": "approved", "approved_at": now()}
    dump_json(resolved, approval)
    if pending.exists():
        pending.unlink()
    decision = BOARD_DECISIONS / f"{task['id']}.md"
    decision.write_text("\n".join([f"# Board Decision — {task['id']}", "", f"- owner: {task['owner']}", "- verdict: approved", f"- approved_at: {now()}", ""]), encoding="utf-8")
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
    progression = min(25, len(delivered) * 4)
    gate_count = sum(1 for task in delivered if task["requires_audit"] or task["requires_board_approval"])
    gate_score = min(15, gate_count * 5)
    autonomy = min(15, len(list(HB.glob("heartbeat-*.json"))) * 3)
    budget = load_json(BUDGET_FILE, DEFAULT_BUDGET)
    worktrees = load_json(WORKTREE_FILE, DEFAULT_WORKTREES)
    operations = 0
    if budget.get("monthly_limit", 0) > 0:
        operations += 4
    if budget.get("spent", 0) <= budget.get("monthly_limit", 0):
        operations += 3
    if worktrees.get("enabled"):
        operations += 3
    score = min(100, coverage + progression + gate_score + autonomy + operations)
    status = "production_ready" if score >= 85 else "developing" if score >= 45 else "bootstrapping"
    return {"timestamp": now(), "status": status, "score": score, "delivered": len(delivered), "evidence_coverage": coverage, "gate_score": gate_score, "autonomy_score": autonomy, "operations_score": operations, "notes": [f"Delivered tasks: {len(delivered)}", f"Evidence files present: {evidence_count}", f"Budget headroom: {budget.get('monthly_limit', 0) - budget.get('spent', 0)}"]}


def write_scorecard(tasks: list[dict]) -> dict:
    card = compute_scorecard(tasks)
    dump_json(SCORECARD_FILE, card)
    report = OWNER_REPORTS / "ATLAS-SCORECARD.md"
    report.write_text("\n".join(["# Atlas Scorecard", "", f"- status: {card['status']}", f"- score: {card['score']}/100", f"- delivered: {card['delivered']}", f"- evidence_coverage: {card['evidence_coverage']}/35", f"- gate_score: {card['gate_score']}/15", f"- autonomy_score: {card['autonomy_score']}/15", f"- operations_score: {card['operations_score']}/10", ""]), encoding="utf-8")
    return card


def write_business_thesis() -> None:
    if THESIS.exists():
        return
    THESIS.write_text("\n".join(["# Atlas Business Thesis", "", "Atlas exists to turn disciplined multi-agent operations into a repeatable commercial asset.", "", "## First Product", "- Atlas operator pack: a ready-to-run operating loop with heartbeat, scorecard, approvals, evidence, budget discipline, and optional worktree isolation.", "", "## Commercial Priorities", "- Prove autonomous delivery with evidence-bearing handoffs.", "- Turn the operating system into a sellable workspace package.", "- Unblock launch messaging, early adopters, and pricing after the release verdict.", ""]), encoding="utf-8")


def read_budget() -> dict:
    ensure_layout()
    return load_json(BUDGET_FILE, DEFAULT_BUDGET)


def write_budget(data: dict) -> None:
    dump_json(BUDGET_FILE, data)


def read_worktrees() -> dict:
    ensure_layout()
    return load_json(WORKTREE_FILE, DEFAULT_WORKTREES)


def write_worktrees(data: dict) -> None:
    dump_json(WORKTREE_FILE, data)


def read_gaps() -> dict:
    ensure_layout()
    return load_json(GAPS_FILE, DEFAULT_GAPS)


def write_gaps(data: dict) -> None:
    dump_json(GAPS_FILE, data)


def read_benchmarks() -> dict:
    ensure_layout()
    return load_json(LEARNING_FILE, DEFAULT_BENCHMARKS)


def write_benchmarks(data: dict) -> None:
    dump_json(LEARNING_FILE, data)


def read_market() -> dict:
    ensure_layout()
    return load_json(MARKET_FILE, DEFAULT_MARKET)


def write_market(data: dict) -> None:
    dump_json(MARKET_FILE, data)
