# SDK Surface

Atlas treats SDK integrations as first-class wiring surfaces.

Machine-readable files:
- `registry.json` lists the SDK-backed surfaces Atlas expects to be wired
- `contracts.json` defines the minimum contract shape the schema audit enforces

Human-readable files:
- `workflow-patterns.md` describes the operating pattern expected when SDK-backed flows are built

Review ownership:
- `WIRING` owns SDK integration completeness
- `SCHEMA` owns SDK contract integrity
