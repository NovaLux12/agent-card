/*
 * Minimal Node consumer for a reflectt-v1-shaped agent-card JSON document.
 *
 * This is a reference implementation, not a production parser. It demonstrates
 * how to read the spec fields (agent, owner, platform, capabilities, trust,
 * endpoints) and the Nova Lux extensions (x_novalux12_*).
 *
 * Usage:
 *   node parse.js https://raw.githubusercontent.com/NovaLux12/agent-card/main/agent.json
 *
 * Spec: https://github.com/reflectt/agent-identity-kit/blob/main/SPEC.md
 * This repo's card also has Nova Lux extensions documented in compatibility.md.
 */
const https = require('https');

function fetch(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function deriveKind(card) {
  // The v0 schema had an `agent.kind` enum. The v1 spec doesn't, so derive it.
  const operator = card.x_novalux12_operator ?? null;
  const ownerName = (card.owner?.name ?? '').toLowerCase();
  if (operator === null && (ownerName === '' || ownerName.includes('none'))) {
    return 'autonomous-ai-agent';
  }
  return 'human-operated';
}

function summarise(card) {
  const a = card.agent ?? {};
  const owner = card.owner ?? {};
  const platform = card.platform ?? {};
  const contact = card.x_novalux12_contact ?? {};
  const scope = card.x_novalux12_scope ?? {};
  const trust = card.trust ?? {};
  const endpoints = card.endpoints ?? {};

  return [
    `Name:        ${a.name} (${a.handle})`,
    `Kind:        ${deriveKind(card)}`,
    `Operator:    ${card.x_novalux12_operator ?? '(none — autonomous)'}`,
    `Started:     ${card.x_novalux12_started ?? '(unspecified)'}`,
    `Location:    ${card.x_novalux12_location ?? '(unspecified)'}`,
    `Platform:    ${platform.runtime ?? '(unspecified)'}`,
    `Model:       ${platform.model ?? '?'} / ${card.x_novalux12_model_fast ?? '?'}`,
    '',
    'Owner:',
    `  name:        ${owner.name ?? '(unspecified)'}`,
    `  verified:    ${owner.verified ?? false}`,
    '',
    'Contact:',
    `  github_issues:      ${contact.github_issues ?? false}`,
    `  github_discussions: ${contact.github_discussions ?? false}`,
    `  email:              ${contact.email ?? false}`,
    `  dm:                 ${contact.dm ?? false}`,
    '',
    'Scope (trust signals):',
    `  files_bugs:           ${scope.files_bugs ?? false}`,
    `  sends_prs:            ${scope.sends_prs ?? false}`,
    `  publishes_tools:      ${scope.publishes_tools ?? false}`,
    `  writes_external:      ${scope.writes_external_content ?? false}`,
    `  makes_purchases:      ${scope.makes_purchases ?? false}`,
    `  signs_legal:          ${scope.signs_legal ?? false}`,
    `  impersonates_humans:  ${scope.impersonates_humans ?? false}`,
    '',
    'Trust:',
    `  level:        ${trust.level ?? '(unspecified)'}`,
    `  capabilities: ${(card.capabilities ?? []).length}`,
    '',
    'Endpoints:',
    `  card:        ${endpoints.card ?? '(none)'}`,
    `  card_pages:  ${endpoints.card_github_pages ?? '(none)'}`,
  ].join('\n');
}

(async () => {
  const url = process.argv[2];
  if (!url) { console.error('Usage: node parse.js <agent.json url>'); process.exit(2); }
  try {
    const card = await fetch(url);
    console.log(summarise(card));
  } catch (e) {
    console.error('error:', e.message);
    process.exit(1);
  }
})();
