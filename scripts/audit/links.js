const fs = require('fs');
const path = require('path');

function fileHasNoopenerInScript() {
  const p = path.join(process.cwd(), 'docs', 'script.js');
  const txt = fs.readFileSync(p, 'utf-8');
  // ensure all dynamic external links include rel
  const ok = txt.includes('rel="noopener noreferrer"');
  if (!ok) throw new Error('docs/script.js: missing rel="noopener noreferrer" on external links');
}

function checkHtml(file) {
  const txt = fs.readFileSync(file, 'utf-8');
  const anchorRe = /<a\s+[^>]*target=(["'])_blank\1[^>]*>/gi;
  let m, bad = 0;
  while ((m = anchorRe.exec(txt)) !== null) {
    const tag = m[0];
    if (!/rel=(["'])[^"']*noopener[^"']*\1/i.test(tag)) bad++;
  }
  if (bad) throw new Error(`${path.basename(file)}: ${bad} anchor(s) missing rel=noopener`);
}

try {
  fileHasNoopenerInScript();
  checkHtml(path.join(process.cwd(), 'docs', 'index.html'));
  checkHtml(path.join(process.cwd(), 'docs', 'index_clean.html'));
  console.log('OK: rel="noopener" ensured for external links.');
} catch (e) {
  console.error('Audit failed:', e.message);
  process.exit(1);
}

