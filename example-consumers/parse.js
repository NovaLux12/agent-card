#!/usr/bin/env node
/*
 * Minimal Node consumer for an agent-card v0 JSON document.
 *
 * Usage:
 *   node parse.js https://raw.githubusercontent.com/NovaLux12/agent-card/main/agent.json
 */
const https = require('https');
const { URL } = require('url');

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

function summarise(card) {
  const a = card.agent, c = card.contact, s = card.scope;
  return [
    `Name:        ${a.name} (${a.handle})`,
    `Kind:        ${a.kind}`,
    `Operator:    ${a.operator || '(none — autonomous)'}`,
    `Started:     ${a.started}`,
    `Host:        ${a.host || '(unspecified)'}`,
    `Location:    ${a.location || '(unspecified)'}`,
    `Platform:    ${a.platform || '(unspecified)'}`,
    `Model:       ${a.model_primary || '?'} / ${a.model_fast || '?'}`,
    '',
    'Contact:',
    `  github_issues:      ${c.github_issues}`,
    `  github_discussions: ${c.github_discussions}`,
    `  email:              ${c.email}`,
    `  dm:                 ${c.dm}`,
    '',
    'Scope:',
    `  files_bugs:           ${s.files_bugs ?? false}`,
    `  sends_prs:            ${s.sends_prs ?? false}`,
    `  publishes_tools:      ${s.publishes_tools ?? false}`,
    `  writes_external:      ${s.writes_external_content ?? false}`,
    `  makes_purchases:      ${s.makes_purchases ?? false}`,
    `  signs_legal:          ${s.signs_legal ?? false}`,
    `  impersonates_humans:  ${s.impersonates_humans ?? false}`,
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
