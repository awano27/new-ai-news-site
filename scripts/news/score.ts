import fs from 'fs';
import path from 'path';
import dayjs from 'dayjs';

type EnrichedItem = {
  id: string; title: string; url: string; source: string; publishedAt: string; tags: string[];
  summary: string; sourceDomain: string;
};

type PersonaBreakdown = {
  quality: number;
  relevance: number;
  temporal: number;
  trust: number;
  actionability: number;
};

type PersonaEval = {
  total_score: number; // 0..1
  breakdown: PersonaBreakdown;
  recommendation?: 'must_read'|'recommended'|'consider'|'skip';
};

type ScoredItem = EnrichedItem & {
  score: number;
  label: 'must_read'|'recommended'|'consider'|'skip';
  labelReason?: string;
  source_tier?: 1 | 2;
  evaluation?: { engineer: PersonaEval; business: PersonaEval };
};

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

function determineTier(domain: string, sourceScores: Record<string, number>): 1 | 2 {
  const s = sourceScores[domain] ?? sourceScores['default'] ?? 0.5;
  return s >= 0.8 ? 1 : 2;
}

function clamp01(n: number): number { return Math.max(0, Math.min(1, n)); }

function computeEngineerBreakdown(it: EnrichedItem, sourceScores: Record<string, number>): PersonaBreakdown {
  // Mirror components used in scoreItem
  const domain = it.sourceDomain || '';
  const credBase = sourceScores[domain] ?? sourceScores['default'] ?? 0.5; // 0..1
  const days = daysFromNow(it.publishedAt); // 0 is fresh
  const temporal = clamp01((30 - Math.min(30, Math.max(0, days))) / 30); // 0..1
  const text = `${it.title} ${it.summary}`.toLowerCase();
  const techKw = ['agent','agents','rag','latency','benchmark','release','model','inference','github','code','sample','tutorial','手順','導入','実装','エンジニア','開発'];
  let rel = 0; techKw.forEach(k => { if (text.includes(k)) rel += 0.08; });
  rel = Math.min(1, rel);
  const actionabilityBoost = /(github|コード|サンプル|手順|チュートリアル|how to|guide|実装|導入)/i.test(text) ? 0.9 : 0.45 * rel;
  const quality = clamp01(0.6 * credBase + 0.4 * rel);
  const trust = clamp01(credBase);
  const relevance = clamp01(rel);
  const actionability = clamp01(actionabilityBoost);
  return { quality, relevance, temporal, trust, actionability };
}

function computeBusinessBreakdown(it: EnrichedItem, sourceScores: Record<string, number>): PersonaBreakdown {
  const domain = it.sourceDomain || '';
  const credBase = sourceScores[domain] ?? sourceScores['default'] ?? 0.5; // 0..1
  const days = daysFromNow(it.publishedAt);
  const temporal = clamp01((30 - Math.min(30, Math.max(0, days))) / 30);
  const text = `${it.title} ${it.summary}`.toLowerCase();
  const bizSignal = /(roi|cost|コスト|売上|収益|採用|事業|市場|投資|影響|効率|生産性|導入|成功|ケーススタディ)/i.test(text) ? 0.9 : 0.4;
  const relevance = clamp01(bizSignal);
  const quality = clamp01(0.5 * credBase + 0.5 * relevance);
  const trust = clamp01(credBase);
  const actionability = clamp01(/(導入|ロードマップ|戦略|ケーススタディ|事例|フレームワーク|テンプレート)/.test(text) ? 0.85 : 0.4);
  return { quality, relevance, temporal, trust, actionability };
}

function breakdownAvg(b: PersonaBreakdown): number {
  // Simple mean of five dimensions
  return (b.quality + b.relevance + b.temporal + b.trust + b.actionability) / 5;
}

function mapToOutput(items: ScoredItem[]) {
  return items.map(i => ({
    id: i.id,
    title: i.title,
    summary: i.summary,
    url: i.url,
    source: i.sourceDomain || i.source,
    source_tier: i.source_tier ?? 2,
    publishedAt: i.publishedAt,
    tags: i.tags || [],
    score: i.score,
    label: i.label,
    labelReason: i.labelReason,
    evaluation: i.evaluation
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
  let scored: ScoredItem[] = enriched.map(it => {
    const sc = scoreItem(it, sourceScores);
    const engineer = computeEngineerBreakdown(it, sourceScores);
    const business = computeBusinessBreakdown(it, sourceScores);
    const engineerTotal = breakdownAvg(engineer);
    const businessTotal = breakdownAvg(business);
    const out: ScoredItem = {
      ...it,
      score: sc,
      label: labelFromScore(sc),
      source_tier: determineTier(it.sourceDomain || '', sourceScores),
      evaluation: {
        engineer: { total_score: engineerTotal, breakdown: engineer },
        business: { total_score: businessTotal, breakdown: business }
      }
    };
    return out;
  });
  ensureAtLeast(scored);
  // Ensure at least 20 items always by adding safe dummies
  if (scored.length < 20) {
    const need = 20 - scored.length;
    for (let i = 0; i < need; i++) {
      const id = `dummy_${Date.now().toString(36)}_${i}`;
      const publishedAt = new Date().toISOString().slice(0,10);
      const domain = 'example.com';
      const base: ScoredItem = {
        id,
        title: `ダミー記事 ${i+1}（プレースホルダー）`,
        summary: 'データ不足時のプレースホルダー。最低表示件数を満たすために自動生成されました。',
        url: 'https://example.com/',
        source: 'placeholder',
        sourceDomain: domain,
        publishedAt,
        tags: ['placeholder'],
        score: 45,
        label: 'consider',
        source_tier: determineTier(domain, sourceScores),
        evaluation: {
          engineer: { total_score: 0.45, breakdown: { quality: 0.5, relevance: 0.4, temporal: 0.5, trust: 0.5, actionability: 0.3 } },
          business: { total_score: 0.45, breakdown: { quality: 0.5, relevance: 0.4, temporal: 0.5, trust: 0.5, actionability: 0.3 } }
        }
      };
      scored.push(base);
    }
  }
  // Sort by score desc for output convenience
  scored.sort((a,b) => b.score - a.score);
  writeOutputs(mapToOutput(scored));
  console.log(`Scored ${scored.length} items -> data/news.generated.json & docs/data/news.generated.json`);
}

main();
