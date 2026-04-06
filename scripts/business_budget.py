from __future__ import annotations

import argparse
from business_lib import now, read_budget, write_budget


def status() -> int:
    budget = read_budget()
    spent = budget["spent"]
    limit = budget["monthly_limit"]
    pct = (spent / limit) if limit else 0
    state = "healthy"
    if pct >= 1:
        state = "exhausted"
    elif pct >= budget["alert_threshold"]:
        state = "warning"
    print({
        "timestamp": now(),
        "state": state,
        "currency": budget["currency"],
        "monthly_limit": limit,
        "spent": spent,
        "remaining": limit - spent,
        "entries": len(budget["ledger"]),
    })
    return 0


def log_spend(amount: int, owner: str, note: str) -> int:
    budget = read_budget()
    next_spent = budget["spent"] + amount
    if next_spent > budget["monthly_limit"]:
        print({"error": "budget_exceeded", "attempted": next_spent, "limit": budget["monthly_limit"]})
        return 1
    budget["spent"] = next_spent
    budget["ledger"].append({"ts": now(), "owner": owner, "amount": amount, "note": note})
    write_budget(budget)
    return status()


def set_limit(amount: int) -> int:
    budget = read_budget()
    budget["monthly_limit"] = amount
    write_budget(budget)
    return status()


def reset() -> int:
    budget = read_budget()
    budget["spent"] = 0
    budget["ledger"] = []
    write_budget(budget)
    return status()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    log = sub.add_parser("log")
    log.add_argument("amount", type=int)
    log.add_argument("--owner", default="LEDGER")
    log.add_argument("--note", default="manual entry")
    limit = sub.add_parser("set-limit")
    limit.add_argument("amount", type=int)
    sub.add_parser("reset")
    args = parser.parse_args()

    if args.cmd == "status":
        raise SystemExit(status())
    if args.cmd == "log":
        raise SystemExit(log_spend(args.amount, args.owner, args.note))
    if args.cmd == "set-limit":
        raise SystemExit(set_limit(args.amount))
    raise SystemExit(reset())
