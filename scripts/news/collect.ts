import fs from 'fs';
import path from 'path';
import Parser from 'rss-parser';

type Source = { type: 'rss' | 'json'; name: string; url: string };
type RawItem = {
  id: string;
  title: string;
  url: string;
  source: string; // name or domain
  publishedAt: string; // ISO or YYYY-MM-DD
  tags: string[];
};

const ROOT = process.cwd();
const DATA_DIR = path.join(ROOT, 'data');
const DOCS_DATA_DIR = path.join(ROOT, 'docs', 'data');
const CONFIG_DIR = path.join(ROOT, 'config');

function ensureDirs() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(DOCS_DATA_DIR, { recursive: true });
}

function readSources(): Source[] {
  const p = path.join(CONFIG_DIR, 'sources.json');
  const buf = fs.readFileSync(p, 'utf-8');
  return JSON.parse(buf) as Source[];
}

function shortId(text: string) {
  let h = 0;
  for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) >>> 0;
  return h.toString(16).slice(0, 8);
}

function toISODate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

async function collect(): Promise<RawItem[]> {
  const sources = readSources();
  const parser = new Parser({ timeout: 10000 });
  const items: RawItem[] = [];
  const MAX_PER_SOURCE = 20;

  for (const s of sources) {
    try {
      if (s.type === 'rss') {
        const feed = await parser.parseURL(s.url);
        for (const e of feed.items.slice(0, MAX_PER_SOURCE)) {
          const url = (e.link || '').trim();
          const title = (e.title || '').trim();
          if (!url || !title) continue;
          const pub = e.isoDate || e.pubDate || '';
          const pubDate = pub ? new Date(pub) : new Date();
          const publishedAt = toISODate(pubDate);
          items.push({
            id: `rss_${shortId(s.name + '_' + url)}`,
            title,
            url,
            source: s.name,
            publishedAt,
            tags: ['rss_feed']
          });
        }
      } else if (s.type === 'json') {
        // Optional: JSON endpoints (not used by default)
        // const res = await fetch(s.url);
        // const json = await res.json();
      }
    } catch (e) {
      console.error(`collect error for ${s.name}:`, (e as Error).message);
    }
  }
  // Sort by publishedAt desc
  items.sort((a, b) => (a.publishedAt < b.publishedAt ? 1 : -1));
  // Limit overall
  return items.slice(0, 50);
}

async function main() {
  ensureDirs();
  const items = await collect();
  const outPath = path.join(DATA_DIR, 'news.raw.json');
  fs.writeFileSync(outPath, JSON.stringify(items, null, 2), 'utf-8');
  // Also copy to docs for debugging if needed
  const docsOut = path.join(DOCS_DATA_DIR, 'news.raw.json');
  fs.writeFileSync(docsOut, JSON.stringify(items, null, 2), 'utf-8');
  console.log(`Collected ${items.length} items -> ${outPath}`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});

