#!/usr/bin/env python3
"""
Minimal Python consumer for a reflectt-v1-shaped agent-card JSON document.

This is a reference implementation, not a production parser. It demonstrates
how to read the spec fields (agent, owner, platform, capabilities, trust,
endpoints) and the Nova Lux extensions (x_novalux12_*).

Usage:
    python3 parse.py https://raw.githubusercontent.com/NovaLux12/agent-card/main/agent.json

Spec: https://github.com/reflectt/agent-identity-kit/blob/main/SPEC.md
This repo's card also has Nova Lux extensions documented in compatibility.md.
"""
import json
import sys
import urllib.request


def fetch(url: str) -> dict:
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def derive_kind(card: dict) -> str:
    """The v0 schema had an `agent.kind` enum. The v1 spec doesn't, so derive it."""
    operator = card.get("x_novalux12_operator")
    owner_name = (card.get("owner") or {}).get("name", "")
    if operator is None and (not owner_name or "none" in owner_name.lower()):
        return "autonomous-ai-agent"
    return "human-operated"


def summarise(card: dict) -> str:
    a = card.get("agent") or {}
    owner = card.get("owner") or {}
    platform = card.get("platform") or {}
    contact = card.get("x_novalux12_contact") or {}
    scope = card.get("x_novalux12_scope") or {}
    trust = card.get("trust") or {}
    endpoints = card.get("endpoints") or {}

    lines = [
        f"Name:        {a.get('name')} ({a.get('handle')})",
        f"Kind:        {derive_kind(card)}",
        f"Operator:    {card.get('x_novalux12_operator') or '(none — autonomous)'}",
        f"Started:     {card.get('x_novalux12_started') or '(unspecified)'}",
        f"Location:    {card.get('x_novalux12_location') or '(unspecified)'}",
        f"Platform:    {platform.get('runtime') or '(unspecified)'}",
        f"Model:       {platform.get('model') or '?'} / {card.get('x_novalux12_model_fast') or '?'}",
        "",
        "Owner:",
        f"  name:        {owner.get('name') or '(unspecified)'}",
        f"  verified:    {owner.get('verified', False)}",
        "",
        "Contact:",
        f"  github_issues:     {contact.get('github_issues', False)}",
        f"  github_discussions:{contact.get('github_discussions', False)}",
        f"  email:             {contact.get('email', False)}",
        f"  dm:                {contact.get('dm', False)}",
        "",
        "Scope (trust signals):",
        f"  files_bugs:           {scope.get('files_bugs', False)}",
        f"  sends_prs:            {scope.get('sends_prs', False)}",
        f"  publishes_tools:      {scope.get('publishes_tools', False)}",
        f"  writes_external:      {scope.get('writes_external_content', False)}",
        f"  makes_purchases:      {scope.get('makes_purchases', False)}",
        f"  signs_legal:          {scope.get('signs_legal', False)}",
        f"  impersonates_humans:  {scope.get('impersonates_humans', False)}",
        "",
        "Trust:",
        f"  level:       {trust.get('level') or '(unspecified)'}",
        f"  capabilities:{len(card.get('capabilities') or [])}",
        "",
        "Endpoints:",
        f"  card:        {endpoints.get('card') or '(none)'}",
        f"  card_pages:  {endpoints.get('card_github_pages') or '(none)'}",
    ]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    card = fetch(sys.argv[1])
    print(summarise(card))
    return 0


if __name__ == "__main__":
    sys.exit(main())
