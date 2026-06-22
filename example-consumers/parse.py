#!/usr/bin/env python3
"""
Minimal Python consumer for an agent-card v0 JSON document.

Usage:
    python3 parse.py https://raw.githubusercontent.com/NovaLux12/agent-card/main/agent.json
"""
import json
import sys
import urllib.request


def fetch(url: str) -> dict:
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def summarise(card: dict) -> str:
    a = card["agent"]
    c = card["contact"]
    s = card["scope"]
    lines = [
        f"Name:        {a['name']} ({a['handle']})",
        f"Kind:        {a['kind']}",
        f"Operator:    {a.get('operator') or '(none — autonomous)'}",
        f"Started:     {a['started']}",
        f"Host:        {a.get('host') or '(unspecified)'}",
        f"Location:    {a.get('location') or '(unspecified)'}",
        f"Platform:    {a.get('platform') or '(unspecified)'}",
        f"Model:       {a.get('model_primary') or '?'} / {a.get('model_fast') or '?'}",
        "",
        "Contact:",
        f"  github_issues:     {c['github_issues']}",
        f"  github_discussions:{c['github_discussions']}",
        f"  email:             {c['email']}",
        f"  dm:                {c['dm']}",
        "",
        "Scope:",
        f"  files_bugs:           {s.get('files_bugs', False)}",
        f"  sends_prs:            {s.get('sends_prs', False)}",
        f"  publishes_tools:      {s.get('publishes_tools', False)}",
        f"  writes_external:      {s.get('writes_external_content', False)}",
        f"  makes_purchases:      {s.get('makes_purchases', False)}",
        f"  signs_legal:          {s.get('signs_legal', False)}",
        f"  impersonates_humans:  {s.get('impersonates_humans', False)}",
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
