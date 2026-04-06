# Operating Model

Lifecycle: new -> classified -> assigned -> in_progress -> under_review -> under_audit -> awaiting_approval -> delivered -> archived

Heartbeat: HELM reviews inboxes, stale work, blocked tasks, idle agents, and open approvals. VECTOR clears cadence drift and utilization gaps.

This company is issue-driven, not chat-driven.

Budget: LEDGER maintains `Team/runtime/state/budget.json`; every new expensive track should be visible there before execution.

Parallel coding: use `scripts/business_worktree.py` to register or create isolated worktrees for concurrent engineering tasks rather than sharing one checkout.
