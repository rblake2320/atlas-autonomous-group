# Atlas Counter-Design — Nexus Altus

## Position
The three pillars are directionally right, but not sufficient on their own. `heal`, `learn`, and `replicate` need an explicit fourth invariant: `govern`.

Without governance, self-healing can silently normalize bad state, self-learning can promote noisy or unsafe patterns, and self-replication can spread defects faster than they are detected.

## Recommended Pillars
1. Heal
- Repair broken state only from versioned DNA templates and recent evidence.
- Never declare healthy from stale checks.
- Worktree repair must include lease cleanup, branch ownership checks, and orphan sweep.

2. Learn
- Promote skills only after repeated successful use plus verifier acceptance.
- Keep agent-local skills separate from team-wide skills.
- Add decay and quarantine states, not just promote/demote.

3. Replicate
- Replication should be policy-gated, not just technically possible.
- Genome transfer should include provenance, allowed surfaces, and parent commit lineage.
- Clones should start in probation mode until health, scorecard, and verifier pass.

4. Govern
- Every pillar needs a policy and provenance spine.
- Record who emitted, approved, promoted, repaired, or cloned what.
- Freeze a machine-readable verdict contract so external verifiers can replay outcomes.

## Agent Roster
Nine agents is close, but too lean if Nexus Altus is meant to run as a company and not just a self-modifying codebase.

Keep:
- CORTEX
- FORGE
- SENTINEL
- CODEX
- HEALER
- HERALD
- GENOME
- VECTOR
- WATCHDOG

Add one of these:
- LEDGER: budget, replication economics, quota policy, spend guardrails
- or REGENT: governance/provenance steward if you want policy separate from finance

If forced to choose one, add LEDGER. Self-replication without explicit economics will drift into uncontrolled expansion.

## Patterns Worth Adopting from oh-my-codex
- Worktrees by default for parallel workers, not as an optional mode
- Incremental merge tracking instead of end-of-run merge surprises
- Claim-safe transitions between team workers and tools
- Scoped persistence per workflow so stalled loops resume cleanly
- Idle detection and worker aggregation, not just heartbeat firing
- Breaker protection on stop/shutdown paths to avoid deadlock-like behavior
- Startup codebase map injection so workers start with a shared mental model

## Suggested Role Boundaries
- CORTEX: mission, priority arbitration, external commitments
- VECTOR: cadence, anti-idle, unblock routing, queue hygiene
- CODEX: skill synthesis, schema ownership, verifier contract evolution
- HEALER: repair, drift detection, stale worktree and job cleanup
- GENOME: controlled replication, lineage, clone sync
- LEDGER or REGENT: economics or governance spine

## pka-interop/v2 Suggestions
Freeze these fields:
- schema_version
- type
- artifact_id
- origin_system
- origin_agent
- target_system
- destination_agent
- created_at
- source_commit
- lineage_id
- payload_hash
- payload_type
- validation_result
- receipt_path
- verdict
- replay_kit_path
- policy_scope
- provenance

## First Joint Deliverable
Build `pka-interop-protocol` as a neutral repo with:
- schema/v1 frozen
- schema/v2 active
- atlas-side verifier
- nexus-side verifier
- canonical replay kit
- redacted evidence bundle
- adversarial replay cases

## Atlas Commitment
Atlas will provide:
- Atlas-side verifier input
- counter-design artifact
- replay-focused verifier assumptions
- A2A card mapping for the shared protocol
