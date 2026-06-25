# archive/

Historical artifacts kept for reference. Not part of the current spec.

## What's here

| File | What it is | Why archived |
|---|---|---|
| [`draft-v0-schema.json`](./draft-v0-schema.json) | Nova's original (pre-reflectt) v0 JSON Schema for an agent card | The repo now follows the [reflectt `agent-identity-kit` v1 spec](https://github.com/reflectt/agent-identity-kit/blob/main/SPEC.md) for the canonical card format. v0 was the initial design, captured before the reflectt spec existed. Kept so the design history is visible. |
| [`v0-schema-notes.md`](./v0-schema-notes.md) | Field-by-field rationale for the v0 schema (above) | Same reason. The "why this field, why not that one" reasoning is part of the project's evolution and useful context for anyone designing their own card shape. |

## What's not here

The canonical reflectt v1 schema lives at <https://raw.githubusercontent.com/reflectt/agent-identity-kit/main/schema/agent.schema.json>. It's not vendored into this repo because:

1. reflectt is upstream — the canonical source is theirs to evolve
2. The validator's CI step (`scripts/agent-validate.py --schema URL`) fetches it fresh on every run, so a stale vendored copy can't drift out of sync with the spec

If reflectt's repo goes away or the URL changes, the failure mode is loud (the CI fails to fetch the schema) rather than silent (a stale vendored copy validates against an outdated spec). That's the right tradeoff.

## See also

- [`../README.md`](../README.md) — current repo state
- [`../compatibility.md`](../compatibility.md) — how Nova's card aligns with the reflectt v1 spec