# Runtime Matrix

## Profiles
- `cloud_api`: best for always-on automation, budgeted background work, and external integrations.
- `cli_subscription`: best for supervised high-context sessions through Claude Code, Codex, or similar adapters.
- `local_llm`: best for privacy-sensitive reasoning, offline fallback, and self-hosted experimentation.
- `local_slm`: best for cheap classifiers, guardrails, routing, summarization, and heartbeat prechecks.

## Recommended Hybrid
- HELM and department leads can use cloud or CLI backends for complex work.
- Guardrails, routing checks, and heartbeat triage can run on local SLMs first.
- Sensitive or bulk internal analysis can route to local LLMs when available.
- External delivery still requires the same finance, legal, security, and QA gates regardless of backend.
