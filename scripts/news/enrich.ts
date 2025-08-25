import fs from 'fs';
import path from 'path';
import cheerio from 'cheerio';

type RawItem = {
  id: string; title: string; url: string; source: string; publishedAt: string; tags: string[];
};
type EnrichedItem = RawItem & { summary: string; sourceDomain: string };

const ROOT = process.cwd();
const DATA_DIR = path.join(ROOT, 'data');
const DOCS_DATA_DIR = path.join(ROOT, 'docs', 'data');

function ensureDirs() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(DOCS_DATA_DIR, { recursive: true });
}

function readRaw(): RawItem[] {
  const p = path.join(DATA_DIR, 'news.raw.json');
  if (!fs.existsSync(p)) return [];
  return JSON.parse(fs.readFileSync(p, 'utf-8')) as RawItem[];
}

function extractDomain(u: string): string {
  try {
    const host = new URL(u).hostname.toLowerCase();
    const multi = ['co.jp','ne.jp','or.jp','ac.jp','go.jp','co.uk','org.uk','gov.uk'];
    if (multi.some(s => host.endsWith(s))) {
      const parts = host.split('.');
      return parts.slice(-3).join('.');
    }
    const parts = host.split('.');
    return parts.slice(-2).join('.');
  } catch { return ''; }
}

function isJapanese(text: string): boolean {
  return /[\u3040-\u30FF\u4E00-\u9FAF]/.test(text);
}

async function tryFetchOG(url: string): Promise<{title?: string, description?: string}> {
  try {
    const res = await fetch(url, { headers: { 'user-agent': 'Mozilla/5.0 (+AI News Bot)' } as any });
    if (!('ok' in res) || !(res as any).ok) return {} as any;
    const html = await (res as any).text();
    const $ = cheerio.load(html);
    const ogt = $('meta[property="og:title"]').attr('content') || $('title').text();
    const ogd = $('meta[property="og:description"]').attr('content') || $('meta[name="description"]').attr('content') || '';
    return { title: ogt?.trim(), description: ogd?.trim() };
  } catch { return {}; }
}

function makeJapaneseSummary(title: string, desc: string, url: string): string {
  const baseTitle = title || '';
  const baseDesc = desc || '';
  const domain = extractDomain(url);
  let s = '';
  if (isJapanese(baseTitle) || isJapanese(baseDesc)) {
    s = `${baseDesc || baseTitle}`;
  } else {
    // 簡易和文サマリ（ヒューリスティック）
    s = `${baseTitle || baseDesc} に関する記事。${domain ? `（出典: ${domain}）` : ''}`;
  }
  s = s.replace(/\s+/g, ' ').trim();
  if (s.length < 220) s = s.padEnd(220, '。');
  if (s.length > 450) s = s.slice(0, 450) + '…';
  return s;
}

async function enrichAll(raw: RawItem[]): Promise<EnrichedItem[]> {
  const out: EnrichedItem[] = [];
  for (const item of raw) {
    let og: any = {};
    try {
      og = await tryFetchOG(item.url);
    } catch {}
    const title = og.title || item.title;
    const desc = og.description || '';
    const summary = makeJapaneseSummary(title, desc, item.url);
    const sourceDomain = extractDomain(item.url) || extractDomain('https://' + (item.source || ''));
    out.push({ ...item, title, summary, sourceDomain });
  }
  return out;
}

async function main() {
  ensureDirs();
  const raw = readRaw();
  const enriched = await enrichAll(raw);
  const p = path.join(DATA_DIR, 'news.enriched.json');
  fs.writeFileSync(p, JSON.stringify(enriched, null, 2));
  const docsOut = path.join(DOCS_DATA_DIR, 'news.enriched.json');
  fs.writeFileSync(docsOut, JSON.stringify(enriched, null, 2));
  console.log(`Enriched ${enriched.length} items -> ${p}`);
}

main().catch(err => { console.error(err); process.exit(1); });

