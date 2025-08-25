import fs from 'fs';
import path from 'path';
import dayjs from 'dayjs';

type EnrichedItem = {
  id: string; title: string; url: string; source: string; publishedAt: string; tags: string[];
  summary: string; sourceDomain: string;
};

type ScoredItem = EnrichedItem & { score: number; label: 'must_read'|'recommended'|'consider'|'skip'; labelReason?: string };

const ROOT = process.cwd();
const DATA_DIR = path.join(ROOT, 'data');
const DOCS_DATA_DIR = path.join(ROOT, 'docs', 'data');
const CONFIG_DIR = path.join(ROOT, 'config');

function ensureDirs() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(DOCS_DATA_DIR, { recursive: true });
}

function readEnriched(): EnrichedItem[] {
  const p = path.join(DATA_DIR, 'news.enriched.json');
  if (!fs.existsSync(p)) return [];
  return JSON.parse(fs.readFileSync(p, 'utf-8')) as EnrichedItem[];
}

function readSourceScores(): Record<string, number> {
  try {
    const p = path.join(CONFIG_DIR, 'source_scores.json');
    return JSON.parse(fs.readFileSync(p, 'utf-8')) as Record<string, number>;
  } catch { return { default: 0.5 }; }
}

function daysFromNow(dateStr: string): number {
  const d = dayjs(dateStr);
  if (!d.isValid()) return 999;
  const diff = dayjs().diff(d, 'day');
  return diff < 0 ? 0 : diff;
}

function scoreItem(it: EnrichedItem, sourceScores: Record<string, number>): number {
  // Recency 0-40 (0 days -> 40, 30+ -> 0)
  const days = daysFromNow(it.publishedAt);
  const recency = Math.max(0, Math.min(40, Math.round((30 - Math.min(30, days)) * (40 / 30))));

  // Source credibility 0-25
  const domain = it.sourceDomain || '';
  const credBase = sourceScores[domain] ?? sourceScores['default'] ?? 0.5;
  const credibility = Math.round(credBase * 25);

  // Relevance 0-20 by keywords in title/summary
  const text = `${it.title} ${it.summary}`.toLowerCase();
  const kw = ['agent','agents','tooling','rag','evaluation','latency','cost','security','benchmark','release','model','inference'];
  let rel = 0;
  kw.forEach(k => { if (text.includes(k)) rel += 3; });
  if (/\b(agents?|rag|latency|cost|security)\b/.test(text)) rel += 5;
  const relevance = Math.min(20, rel);

  // Impact 0-15 (rule-based)
  let impact = 0;
  if (/release|laun(ch|ced)|announce|発表|リリース/i.test(text)) impact += 8;
  if (/benchmark|SOTA|性能|大規模|大幅|大規模モデル/i.test(text)) impact += 7;
  impact = Math.min(15, impact);

  return recency + credibility + relevance + impact;
}

function labelFromScore(score: number): 'must_read'|'recommended'|'consider'|'skip' {
  if (score >= 80) return 'must_read';
  if (score >= 60) return 'recommended';
  if (score >= 40) return 'consider';
  return 'skip';
}

function ensureAtLeast(items: ScoredItem[]) {
  const hasMust = items.some(i => i.label === 'must_read');
  const hasRec = items.some(i => i.label === 'recommended');
  const sorted = [...items].sort((a,b) => b.score - a.score);
  if (!hasMust && sorted[0]) {
    sorted[0].label = 'must_read';
    sorted[0].labelReason = 'fallback_promoted_top_to_must_read';
  }
  if (!hasRec) {
    const next = sorted.find(i => i.label !== 'must_read');
    if (next) {
      next.label = 'recommended';
      next.labelReason = 'fallback_promoted_second_to_recommended';
    }
  }
}

function mapToOutput(items: ScoredItem[]) {
  return items.map(i => ({
    id: i.id,
    title: i.title,
    summary: i.summary,
    url: i.url,
    source: i.sourceDomain || i.source,
    publishedAt: i.publishedAt,
    tags: i.tags || [],
    score: i.score,
    label: i.label,
    labelReason: i.labelReason
  }));
}

function writeOutputs(items: any[]) {
  const out = JSON.stringify(items, null, 2);
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(DOCS_DATA_DIR, { recursive: true });
  fs.writeFileSync(path.join(DATA_DIR, 'news.generated.json'), out);
  fs.writeFileSync(path.join(DOCS_DATA_DIR, 'news.generated.json'), out);
}

function main() {
  ensureDirs();
  const enriched = readEnriched();
  const sourceScores = readSourceScores();
  const scored: ScoredItem[] = enriched.map(it => {
    const sc = scoreItem(it, sourceScores);
    return { ...it, score: sc, label: labelFromScore(sc) };
  });
  ensureAtLeast(scored);
  // Sort by score desc for output convenience
  scored.sort((a,b) => b.score - a.score);
  writeOutputs(mapToOutput(scored));
  console.log(`Scored ${scored.length} items -> data/news.generated.json & docs/data/news.generated.json`);
}

main();

