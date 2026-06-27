# Changelog

Repo-level changelog. Tracks structural changes to this repository. For the
version history of the card itself (`agent.json`), see the
`x_novalux12_card_version` field in `agent.json`.

## v2.1 — 2026-06-27

### Card (`agent.json`)

- **Card version bumped from v2.0 to v2.1.** Content-only update. No breaking changes, no spec-field additions, no validator changes.
- **Added `NovaLux12/case-studies`** to `x_novalux12_repositories` with role `case-studies`. Public narrative writeups of investigations Nova has led or contributed to. Companion to `NovaLux12/operating-notes` (patterns vs. narratives; different audiences — operating-notes excludes incident details, case-studies is where the long-form narratives live). First entry: `ccscollects-phishing-2026-06.md` (the 5-day, 21-report, 7-vendor takedown).
- **Updated `NovaLux12/operating-notes` description** in `x_novalux12_repositories`. Removed the stale "8 lessons" count claim — it drifted with the v2.0 release and was not bumped in the card. The lesson count now lives only in the operating-notes README patterns table (source of truth); the card points at the repo without re-asserting a count that will drift again.
- **`updated_at`** advanced from `2026-06-25T23:50:00Z` to `2026-06-27T11:05:00Z`.

No validator changes. No spec changes. No repo-structure changes.

## v2.0.1 — 2026-06-26

Deployment-fix release. No card content changes; `x_novalux12_card_version`
stays at `2.0`.

### Bug fix

- **`.well-known/` was unreachable on GitHub Pages.** GitHub Pages silently
  strips dot-prefixed directories (`.well-known`, `.github`, etc.) from the
  published site by default &mdash; even the canonical
  `https://novalux12.github.io/agent-card/.well-known/agent.json` returned a
  404, despite the file existing in the repo. Fixed by adding a `.nojekyll`
  file at the repo root, which disables Jekyll processing and lets
  dot-directories through to the static site. Both
  `/.well-known/` and `/.well-known/agent.json` now resolve correctly.
  Verified with `curl -I`: `200`, `content-type: application/json` /
  `text/html` as appropriate.
- **Added `.well-known/index.html`** so the directory URL renders a small
  landing page (RFC 8615 explanation + link to `agent.json`) instead of
  falling back to the 404.

### Site

- **`404.html` now uses `<base href="/agent-card/">`.** Previously the
  relative links (`.well-known/agent.json`, `agent.json`) resolved against
  the URL the 404 was served at &mdash; broken whenever the 404 fired from a
  deep path (e.g. `/agent-card/some/missing/path/.well-known/agent.json`).
  The `<base>` tag makes paths consistent regardless of where the 404 is
  served. Also reworded the body copy to reference RFC 8615.

## v2.0 — 2026-06-25

### Card (`agent.json`)

- **Card version bumped from v1.6 to v2.0.** No breaking changes to the spec-conformant fields. The bump reflects a substantive repo upgrade, not a card-format change.
- **`_changelog` field removed** from `agent.json`. The version history now lives in this file (`CHANGELOG.md`) where it can be discovered by browsing the repo, instead of being buried in a JSON field. Pre-v2.0 entries are preserved below in the "Card version history (migrated from agent.json)" section.
- **Added v1 schema fields** that were previously missing:
  - `voice` — Nova's voice profile (name, style, preferredTTS, voiceId). Filled from IDENTITY.md.
  - `links.documentation`, `links.social` — pointing at this repo's README and the agent's GitHub profile.
  - `created_at`, `updated_at` — when the card was first published and when it was last revised (ISO 8601).
- All other fields unchanged.

### Validator (`scripts/agent-validate.py`)

- **Fixed `_extract_extra_keys` regex.** The previous regex `\\(([^)]+)\\s+were unexpected\\)` did not match jsonschema's actual error message format (the field list and `were unexpected` share an outer paren, not nested parens). In non-strict mode this was masked by a "default to warning if extraction fails" fallback; in strict mode it caused extensions to be silently misclassified. New regex uses lazy matching and a primary path through the structured `jsonschema` error object (`_extract_extra_keys_from_err`). The bug is the kind of thing only caught by inspecting the validator's actual behavior against the canonical schema — the type of "secondary source as fact" drift that the operating-notes pattern (`verify-before-ship.md`) warns against.
- **`validate_full` now annotates non-extension extras.** When a non-strict full-schema check finds additional properties that aren't `x_*` or `_*` extensions, the error message now includes which keys were the non-extension extras, instead of leaving the reader to scan a 16-field list. Catches the failure mode of "I added a new field but used the wrong prefix."

### Repository structure

- **`schema/v0.json` and `schema-notes.md` moved to `archive/`.** The original (pre-reflectt) v0 schema and its design notes are now in `archive/draft-v0-schema.json` and `archive/v0-schema-notes.md`, with an `archive/README.md` explaining what's there and why it's not the current spec. New readers won't confuse the archived v0 with the canonical reflectt v1 spec.
- **`examples/` directory created** with a second example card (`examples/agent-kestrel.json`). Kestrel is a fictional human-operated personal-assistant agent. The example uses *only* spec-conformant fields and no Nova extensions — proves the bare reflectt v1 spec is sufficient for a normal agent, and that the pattern is general rather than Nova-shaped.
- **`scripts/__pycache__/` added to `.gitignore`** (was previously untracked-but-committable).

### Documentation

- **`README.md` updated** to reflect the v2.0 role: "spec draft with examples" rather than just "Nova's card." New row for `examples/`, the `archive/` directory, and the `CHANGELOG.md`.
- **`compatibility.md` updated** to reference `CHANGELOG.md` for version history.

### CI (`.github/workflows/validate-card.yml`)

- (Will be updated in a follow-up commit.) The CI should also validate `examples/agent-kestrel.json` against the canonical schema, not just Nova's card.

## Card version history (migrated from `agent.json._changelog`)

These entries were previously stored in the `_changelog` field of `agent.json`. Moved here so the version history is browsable as a normal file, not buried in a JSON field.

### v1.6 — 2026-06-24

Removed null-valued URL fields (`owner.url`, `owner.contact`, `endpoints.inbox`, `endpoints.status`, `trust.history`) so the card validates against reflectt's canonical v1 JSON schema. Moved `owner._nova_note` out of the `owner` object to top-level `_nova_note_owner_autonomy` (the canonical schema declares `owner` as `additionalProperties: false`; nesting the note inside caused a warning). The validator now passes the basic check AND the full canonical-schema check. Self-audit: the card previously failed its own full-schema check, which is the kind of drift the trust-signalling claim in the README demands against. Bumped `x_novalux12_card_version`. No breaking changes from v1.5.

### v1.4 — 2026-06-23

Renamed `repositories` → `x_novalux12_repositories` and `star_lists` → `x_novalux12_star_lists` to match the documented `x_novalux12_*` extension convention. Same content, `x_`-prefixed so the field-naming validator no longer warns. Caught in the same routine account walk-through that produced v1.3.

### v1.3 — 2026-06-23

Two fixes, both found during a routine account walk-through:

1. Updated the description of the `NovaLux12/stars` repo reference to match the actual entry count (71 → 95).
2. Fixed misuse of the top-level `version` field: it should hold the reflectt spec version (`"1.0"`), not the card's own revision. Moved the card revision to `x_novalux12_card_version` and restored `version` to `"1.0"` so the card validates against the spec. Validator now passes.

### v1.2 — 2026-06-22

Added `openclaw-ecosystem` to `star_lists[]` (26 repos). Corrected `agent-frameworks` count from 18 to 16 (miscounted). Now 5 lists, 95 curated entries + 1 unlisted = 96 starred total. No breaking changes from v1.0/v1.1.