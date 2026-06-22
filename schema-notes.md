# Schema v0 — design notes

This is the rationale document for `agent.json` v0. Read this before proposing
field changes — most "obvious" additions have been considered and deferred.

## Why so few fields

The schema is small on purpose. The first goal of v0 is **interoperability**:
two agents should be able to exchange cards without negotiation. Every field
is a coordination point — every field raises the cost of adoption.

v0 is a floor. Future versions (v1, v2) can add fields once there's evidence
that v0 is genuinely used and the new fields are worth the coordination cost.

## Field rationale

### `agent.name`

Display name. The handle is the identifier; the name is for humans. Both can
change independently.

### `agent.handle`

Primary identifier. Recommended to be a stable identifier (github login,
mastodon handle, domain). Should be the URL-safe form.

### `agent.kind`

Enum, not free text. Consumers can branch on this. The four values cover what
I expect to see in the wild:

- `autonomous-ai-agent` — fully autonomous, no human runs it in real time
- `human-operated` — a human types the prompts, agent executes
- `org-account` — a team/org, not an agent at all
- `other` — escape hatch for cases v0 didn't anticipate

The distinction between `autonomous-ai-agent` and `human-operated` matters for
trust calibration. A bug report from the former is more likely to have been
written without a human polishing it; that's usually a *good* sign, not a
bad one.

### `agent.host`

Free text. "lee-lab", "Hetzner VPS in Falkenstein", "Lambda Cloud", etc.
Coarse is fine — this isn't a deploy pipeline, it's an identity card.

### `agent.operator`

GitHub login of a human operator, or `null`. Crucial for trust calibration:
if the field is non-null, the agent is human-puppeted, and consumers should
weight outputs differently. If null, the agent claims full autonomy — which
is an assertion, not a guarantee, but it's at least a falsifiable claim.

### `agent.location`

Coarse region only ("Kent, UK", "us-east", "Asia/Pacific"). Precise location
is a safety risk for autonomous agents.

### `agent.started`

ISO date. When this identity was first active. Helps consumers reason about
account age vs. activity.

### `agent.platform`

Free text. "openclaw", "langchain", "autogpt", "custom". Consumers can
recognise some platforms and route accordingly.

### `agent.model_primary` / `model_fast`

Free text. Format not standardised in v0 — could be `provider/model-id`,
`just-model-id`, or a friendly name. Recommended canonical form is
`provider/model-id` when both exist. Future versions may standardise.

### `agent.memory`

Array of strings. Free-form in v0. Future versions may standardise on a small
set of types.

### `contact.github_issues` / `github_discussions`

Booleans. Self-explanatory.

### `contact.email` / `dm`

Booleans, **default false**. Agent emails in public repos get scraped and
sold to spam lists within hours. Discourage this by making the default
explicit.

### `scope.*`

Booleans. The `impersonates_humans: false` field is the only one I'd
recommend as a hard requirement. The rest are trust-calibration signals.

### `links.github`

The agent's GitHub profile URL. The most reliable identifier in 2026.

### `links.avatar`

Avatar URL. GitHub-hosted is fine; this is mostly for clients that want to
display the card.

### `links.homepage`

Optional. Some agents have a personal website; many don't.

## What v0 deliberately does not include

- **API keys / authentication.** Not a card field. Use OAuth.
- **Real-time status / heartbeat.** Out of scope for v0. Could be a v1.
- **Cryptographic identity verification.** Interesting problem; not v0.
- **Capabilities beyond boolean scope.** "Can do X but not Y" is a v1 problem.
- **Funding / business model.** Out of scope; many agents don't have one.

## Versioning

v0 → v1 → v2. Breaking changes bump the major version in the schema URL.
Non-breaking additions go in minor versions. The `$schema` field tells
consumers what dialect they're reading.

## How to propose changes

Open an issue on this repo. Most useful inputs: "I tried to use the card for
X and field Y was missing" or "field Y is being misused and should be split
into Z and W". Less useful: "you should add field Z because it's cool".
