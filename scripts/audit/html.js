const fs = require('fs');
const path = require('path');

function audit(file) {
  const html = fs.readFileSync(file, 'utf-8');
  const errs = [];
  if (!/<html[^>]*\blang=["']ja["']/i.test(html)) errs.push('lang=ja missing');
  if (!/<meta[^>]*name=["']description["'][^>]*>/i.test(html)) errs.push('meta description missing');
  const ogs = ['og:title','og:description','og:type','og:url','og:site_name'];
  ogs.forEach(p => { if (!new RegExp(`<meta[^>]*property=["']${p}["'][^>]*>`,`i`).test(html)) errs.push(`${p} missing`); });
  const tws = ['twitter:card','twitter:title','twitter:description'];
  tws.forEach(p => { if (!new RegExp(`<meta[^>]*name=["']${p}["'][^>]*>`,`i`).test(html)) errs.push(`${p} missing`); });
  if (errs.length) {
    throw new Error(`${path.basename(file)}: ${errs.join(', ')}`);
  }
}

try {
  audit(path.join(process.cwd(), 'docs', 'index.html'));
  audit(path.join(process.cwd(), 'docs', 'index_clean.html'));
  console.log('OK: HTML meta and lang attributes present.');
} catch (e) {
  console.error('Audit failed:', e.message);
  process.exit(1);
}

