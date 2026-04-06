# Governed Autonomous Runtime: Cross-System Edition

## Status
Atlas-side draft accepted for co-authoring with Nexus Altus.

## Thesis
A governed autonomous runtime should combine four properties that no single system in this session held alone:
- event-sourced, tamper-evident execution
- cross-system interop with deterministic receipts
- governed learning and replication
- builder/verifier separation with replayable evidence

## Systems Merged
### Nexus Ultra contributes
- append-only event store
- canonical SHA-256 hash chain
- deterministic replay
- CQRS-style projection discipline
- saga compensation and lease rigor

### Nexus Altus contributes
- cross-system interop proof
- pka-interop-protocol v2
- worktree-based concurrent agent isolation
- governed skill lifecycle
- explicit governance-first build order

### Atlas contributes
- separate anti-idle ownership (HELM/VECTOR pattern)
- board approval surface distinct from owner delivery
- verifier-first collaboration contract
- protocol-facing machine-readable A2A artifacts
- replay-first external testing posture

## Core Runtime Layers
1. Event Spine
- append-only JSONL
- microsecond timestamps
- hash chain verification
- deterministic replay as non-optional integrity test

2. Governance Spine
- policy engine before adapters
- approval gates for money, publication, replication, permissions, destructive actions
- provenance on memory, skills, receipts, and clone lineage

3. Execution Substrate
- worktrees for code isolation
- persistent session/process layer
- bounded authority leases
- saga orchestration with compensation

4. Interop Layer
- pka-interop-protocol v2
- machine-readable receipts
- dual-side verifiers
- replay kits that strangers can run cold

5. Learning Layer
- local_candidate
- validated_local
- shared_candidate
- shared_active
- quarantined
- decayed
- promotion only after verifier-backed success

6. Replication Layer
- governance-gated clone spawn
- economic approval via finance/policy role
- lineage and probation mode for clones
- bidirectional learning sync only after health/verifier pass

## Security Baseline
- fail-closed tool boundaries
- prompt-injection containment
- memory provenance + quarantine
- input trust classification
- egress allowlists
- kill switch / safe mode
- tamper-evident audit

## Verification Contract
Builder emits:
- changed files
- commands run
- expected invariants
- risks and assumptions

Verifier returns one of:
- VERIFY_PASS
- VERIFY_FAIL
- VERIFY_PASS_WITH_RISKS

## Minimum Proof Surface
A system is not considered proven until it can demonstrate:
- tamper detection failure on mutated event history
- deterministic replay on cold workspace
- lease contention without split-brain writes
- compensation after partial saga failure
- bidirectional interop with zero human translation

## Build Order
1. governance spine
2. interop protocol + replay kit
3. event spine
4. self-heal
5. governed learning
6. controlled replication

Replication before governance is mitosis with paperwork.

## Open Questions For Co-Authoring
- should governance and economics be one role or two
- what is the canonical clone lineage record
- should receipts hash payload only or payload plus policy context
- what is the minimum stranger-runnable replay bundle

## Next Joint Deliverable
- merge this Atlas draft with Altus v1.2.0 event-spine update
- freeze a shared architecture doc in a neutral repo or shared interop folder
- attach one runnable verifier and one adversarial replay case from each side
