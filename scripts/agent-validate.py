#!/usr/bin/env python3
"""
agent-card-validate.py — validate an agent-card JSON document.

Implements the reflectt agent-identity-kit v1 schema:
    https://github.com/reflectt/agent-identity-kit/blob/main/SPEC.md

This is a basic, dependency-free validator. It checks:
- the document parses as JSON
- reflectt v1 required fields are present (top-level + nested)
- the Fediverse-style handle matches the spec pattern
- the trust.level value is one of the spec's enum
- capabilities, if present, are strings matching the spec pattern

If `jsonschema` is installed, a full schema check is performed too. With
`--schema` the canonical v1 JSON schema is loaded and used; the result
is reported as a list of issues. Fields prefixed `x_` (per HTTP header
naming convention) are treated as extension fields and do not trigger
"additional property" errors.

Usage:
    python3 agent-validate.py https://example.com/.well-known/agent.json
    python3 agent-validate.py path/to/agent.json
    python3 agent-validate.py --schema /path/to/v1.json URL
    python3 agent-validate.py --strict URL    # treat extensions as errors
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# reflectt agent-identity-kit v1 — kept in sync with the spec manually.
REQUIRED_TOP = ["version", "agent", "owner"]
REQUIRED_AGENT = ["name", "handle", "description"]
REQUIRED_OWNER = ["name"]
ALLOWED_VERSIONS = ["1.0"]
ALLOWED_TRUST_LEVELS = ["new", "active", "established", "verified"]
# Fediverse handle: @name@domain.tld (per spec)
HANDLE_PATTERN = re.compile(r"^@[a-zA-Z0-9_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
# Capability tags: lowercase, digits, hyphens only
CAPABILITY_PATTERN = re.compile(r"^[a-z0-9-]+$")
# Extension prefix: agents may add custom fields starting with `x_`
# (HTTP header convention) or `_` (GraphQL convention). Strict mode
# disables this.
EXTENSION_PREFIXES = ("x_", "_")


def fetch(url: str) -> dict:
    """Fetch JSON from a URL."""
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as r:  # noqa: S310 — URL is operator input
        return json.load(r)


def load(path: str) -> dict:
    """Load JSON from a local file."""
    return json.loads(Path(path).read_text())


def validate_basic(card: dict, *, strict: bool = False) -> list[str]:
    """
    Basic structural validation against the v1 schema (no jsonschema).

    Returns a list of human-readable issue strings. Empty list = pass.

    `strict=True` treats `x_*` extensions as errors. Default is permissive
    (extensions are warnings, not errors).
    """
    errs: list[str] = []

    # Top-level required
    for f in REQUIRED_TOP:
        if f not in card:
            errs.append(f"card.{f} is required")

    # version
    v = card.get("version")
    if v is not None and v not in ALLOWED_VERSIONS:
        errs.append(f"card.version must be one of {ALLOWED_VERSIONS}, got {v!r}")
    if v is not None and not isinstance(v, str):
        errs.append(f"card.version must be a string, got {type(v).__name__}")

    # agent
    agent = card.get("agent")
    if agent is not None and not isinstance(agent, dict):
        errs.append(f"card.agent must be an object, got {type(agent).__name__}")
    elif isinstance(agent, dict):
        for f in REQUIRED_AGENT:
            if f not in agent:
                errs.append(f"card.agent.{f} is required")
        handle = agent.get("handle")
        if handle is not None and not isinstance(handle, str):
            errs.append(f"card.agent.handle must be a string, got {type(handle).__name__}")
        elif isinstance(handle, str) and not HANDLE_PATTERN.match(handle):
            errs.append(
                f"card.agent.handle {handle!r} doesn't match Fediverse pattern "
                "'@name@domain.tld' (e.g. @kai@reflectt.ai)"
            )
        desc = agent.get("description")
        if isinstance(desc, str) and len(desc) > 500:
            errs.append(f"card.agent.description is {len(desc)} chars, max 500")

    # owner
    owner = card.get("owner")
    if owner is not None and not isinstance(owner, dict):
        errs.append(f"card.owner must be an object, got {type(owner).__name__}")
    elif isinstance(owner, dict):
        for f in REQUIRED_OWNER:
            if f not in owner:
                errs.append(f"card.owner.{f} is required")

    # trust.level (optional)
    trust = card.get("trust")
    if isinstance(trust, dict):
        level = trust.get("level")
        if level is not None and level not in ALLOWED_TRUST_LEVELS:
            errs.append(
                f"card.trust.level must be one of {ALLOWED_TRUST_LEVELS}, got {level!r}"
            )

    # capabilities (optional)
    caps = card.get("capabilities")
    if caps is not None:
        if not isinstance(caps, list):
            errs.append("card.capabilities must be an array if present")
        else:
            for i, c in enumerate(caps):
                if not isinstance(c, str) or not CAPABILITY_PATTERN.match(c):
                    errs.append(
                        f"card.capabilities[{i}] {c!r} should match {CAPABILITY_PATTERN.pattern!r}"
                    )

    # extension fields — check naming convention in non-strict mode
    for k in card:
        if not k.startswith(EXTENSION_PREFIXES) and not _is_known_top_level(k):
            msg = (
                f"card.{k} is not a known v1 field (extension fields should be "
                f"prefixed with one of {list(EXTENSION_PREFIXES)})"
            )
            if strict:
                errs.append(msg)
            else:
                # Warning only; surface as "warn:" prefix
                errs.append(f"warn: {msg}")

    return errs


_KNOWN_TOP_LEVEL = {
    "$schema", "version",
    "agent", "owner", "platform", "capabilities", "protocols",
    "endpoints", "trust", "links",  # v1 spec fields
    # Recognised extension names (informational only — strict mode still flags them)
    "_nova_compat", "_spec_ref", "_nova_note",
}
for f in REQUIRED_TOP:
    _KNOWN_TOP_LEVEL.add(f)


def _is_known_top_level(k: str) -> bool:
    return k in _KNOWN_TOP_LEVEL


def validate_full(card: dict, schema: dict, *, strict: bool = False) -> list[str]:
    """Full validation if jsonschema is available."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return ["jsonschema not installed — only basic validation performed"]
    v = jsonschema.Draft7Validator(schema)
    errs: list[str] = []
    for e in sorted(v.iter_errors(card), key=lambda e: list(e.absolute_path)):
        msg = e.message
        # In non-strict mode, demote "additional property" errors for x_*/_ extensions
        if not strict and "Additional properties are not allowed" in msg:
            # Try to extract which keys are extra
            extra = _extract_extra_keys(msg)
            non_ext = [k for k in extra if not k.startswith(EXTENSION_PREFIXES)]
            if not non_ext:
                # All extras are extensions — treat as warning
                errs.append(f"warn: {msg}")
                continue
        errs.append(msg)
    return errs


def _extract_extra_keys(msg: str) -> list[str]:
    """Pull the field-name list out of a jsonschema 'Additional properties' message."""
    m = re.search(r"\(([^)]+)\s+were unexpected\)", msg)
    if not m:
        return []
    return [s.strip().strip("'\"") for s in m.group(1).split(",")]


def main(argv: list[str]) -> int:
    args = list(argv)
    if not args:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    strict = False
    schema_path: str | None = None
    while True:
        if args and args[0] == "--strict":
            strict = True
            args = args[1:]
            continue
        if args and args[0] == "--schema":
            if len(args) < 2:
                print("error: --schema requires a path argument", file=sys.stderr)
                return 2
            schema_path = args[1]
            args = args[2:]
            continue
        break
    if not args:
        print("error: no target URL or file", file=sys.stderr)
        return 2
    target = args[-1]

    # Load the card
    if target.startswith(("http://", "https://")):
        try:
            card = fetch(target)
        except urllib.error.URLError as e:
            print(f"fetch error: {e}", file=sys.stderr)
            return 1
    else:
        try:
            card = load(target)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"load error: {e}", file=sys.stderr)
            return 1

    errs = validate_basic(card, strict=strict)
    if schema_path:
        try:
            schema = load(schema_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"schema load error: {e}", file=sys.stderr)
            return 1
        errs.extend(validate_full(card, schema, strict=strict))

    # Sort errors (warn: first, then errors)
    warnings = [e for e in errs if e.startswith("warn:")]
    real_errs = [e for e in errs if not e.startswith("warn:")]
    real_errs.sort()
    warnings.sort()

    if real_errs:
        print(f"FAIL — {len(real_errs)} error(s):", file=sys.stderr)
        for e in real_errs:
            print(f"  - {e}", file=sys.stderr)
        for w in warnings:
            print(f"  {w}", file=sys.stderr)
        return 1
    summary = {
        "name": card.get("agent", {}).get("name"),
        "handle": card.get("agent", {}).get("handle"),
        "version": card.get("version"),
        "trust_level": card.get("trust", {}).get("level"),
        "capabilities": len(card.get("capabilities") or []),
    }
    if warnings:
        print(f"OK — {json.dumps(summary)}  ({len(warnings)} non-blocking warning(s))")
    else:
        print(f"OK — {json.dumps(summary)}")

    # If the basic-only check passed, nudge users toward the canonical-schema
    # check for cards that look like trust-signalling artifacts. Catches the
    # "basic-permissive pass != canonical pass" gap that bit me on my own card.
    if not schema_path and _looks_like_trust_card(card):
        print(
            "\nhint: this card looks like a reflectt v1 trust-signalling card. "
            "The basic check above only enforces required-field presence -- "
            "type strictness (e.g. null-vs-string, additionalProperties) is "
            "only caught with --schema. To run the full check:\n"
            "  python3 agent-validate.py --schema "
            "https://raw.githubusercontent.com/reflectt/agent-identity-kit/main/schema/agent.schema.json "
            f"{target}",
            file=sys.stderr,
        )

    return 0


def _looks_like_trust_card(card: dict) -> bool:
    """Heuristic: card signals it is meant for trust calibration, not just discovery."""
    if not isinstance(card, dict):
        return False
    if card.get("x_novalux12_scope") or card.get("x_novalux12_operator") is not None:
        return True
    if card.get("scope") or card.get("operator") is not None:
        return True
    if isinstance(card.get("trust"), dict) and card["trust"].get("level"):
        return True
    return False


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
