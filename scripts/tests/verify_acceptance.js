const fs = require('fs');
const path = require('path');

function readJSONCandidate() {
  const p1 = path.join('docs','data','news.generated.json');
  const p2 = path.join('docs','data','news.json');
  const p = fs.existsSync(p1) ? p1 : p2;
  if (!fs.existsSync(p)) throw new Error('No docs/data JSON found');
  const arr = JSON.parse(fs.readFileSync(p, 'utf8'));
  if (!Array.isArray(arr)) throw new Error('JSON is not array');
  return arr;
}

const TIER1_DOMAINS = new Set(['openai.com','ai.googleblog.com','googleblog.com','anthropic.com','techcrunch.com','venturebeat.com']);
function extractDomain(u) {
  try {
    const host = new URL(u).hostname.toLowerCase();
    const multi = ['co.jp','ne.jp','or.jp','ac.jp','go.jp','co.uk','org.uk','gov.uk'];
    if (multi.some(s => host.endsWith(s))) {
      const ps = host.split('.');
      return ps.slice(-3).join('.');
    }
    const ps = host.split('.');
    return ps.slice(-2).join('.');
  } catch { return ''; }
}
function clamp01(n){ return Math.max(0, Math.min(1, n)); }
function daysFromNow(dateStr){
  if (!dateStr) return 999;
  const raw = String(dateStr).trim();
  let d = new Date(raw);
  if (isNaN(d.getTime())) d = /\d{4}-\d{2}-\d{2}$/.test(raw) ? new Date(`${raw}T00:00:00Z`) : new Date();
  const now = new Date();
  const diff = Math.floor((now - d) / (1000*60*60*24));
  return diff < 0 ? 0 : diff;
}
function engineerTotal(a){
  const domain = (a.sourceDomain || extractDomain(a.url || '') || a.source || '').toLowerCase();
  const trust = TIER1_DOMAINS.has(domain) ? 0.9 : 0.5;
  const temporal = clamp01((30 - Math.min(30, daysFromNow(a.publishedAt || a.published_date))) / 30);
  const text = (`${a.title} ${a.summary||a.content||''}`).toLowerCase();
  let rel = 0; ['agent','agents','rag','latency','benchmark','release','model','inference','github','code','sample','tutorial','手順','導入','実装','開発'].forEach(k=>{ if(text.includes(k)) rel+=0.08; });
  rel = Math.min(1, rel);
  const quality = clamp01(0.6*trust + 0.4*rel);
  const actionability = /(github|コード|サンプル|手順|チュートリアル|how to|guide|実装|導入)/i.test(text) ? 0.9 : 0.45*rel;
  return (quality + rel + temporal + trust + actionability) / 5;
}
function businessTotal(a){
  const domain = (a.sourceDomain || extractDomain(a.url || '') || a.source || '').toLowerCase();
  const trust = TIER1_DOMAINS.has(domain) ? 0.9 : 0.5;
  const temporal = clamp01((30 - Math.min(30, daysFromNow(a.publishedAt || a.published_date))) / 30);
  const text = (`${a.title} ${a.summary||a.content||''}`).toLowerCase();
  const relevance = /(roi|cost|コスト|売上|収益|採用|事業|市場|投資|影響|効率|生産性|導入|成功|ケーススタディ)/i.test(text) ? 0.9 : 0.4;
  const quality = clamp01(0.5*trust + 0.5*relevance);
  const actionability = /(導入|ロードマップ|戦略|ケーススタディ|事例|フレームワーク|テンプレート)/.test(text) ? 0.85 : 0.4;
  return (quality + relevance + temporal + trust + actionability) / 5;
}

function testAcceptance() {
  const a = readJSONCandidate();
  const results = [];

  // 1) 件数
  results.push({ name:'count>=20', pass: a.length >= 20, detail: `count=${a.length}` });
  // 2) ラベル存在
  const hasMust = a.some(x => x.label === 'must_read');
  const hasRec = a.some(x => x.label === 'recommended');
  results.push({ name:'has must_read', pass: hasMust });
  results.push({ name:'has recommended', pass: hasRec });
  // 3) 統計（平均スコア>0）
  const avgEng = a.reduce((s,x)=>s+engineerTotal(x),0)/(a.length||1);
  const avgBiz = a.reduce((s,x)=>s+businessTotal(x),0)/(a.length||1);
  results.push({ name:'avg engineer > 0', pass: avgEng > 0, detail: avgEng.toFixed(3) });
  results.push({ name:'avg business > 0', pass: avgBiz > 0, detail: avgBiz.toFixed(3) });
  // 4) 高信頼ソース>0
  const tier1 = a.filter(x => x.source_tier === 1 || TIER1_DOMAINS.has((x.source||'').toLowerCase()) || TIER1_DOMAINS.has((x.sourceDomain||'').toLowerCase())).length;
  results.push({ name:'tier1>0', pass: tier1 > 0, detail: `tier1=${tier1}` });
  // 5) ペルソナ切替で順位が変化
  const topEng = [...a].sort((x,y)=>businessTotal(y) - businessTotal(x)); // business
  const topBiz = [...a].sort((x,y)=>engineerTotal(y) - engineerTotal(x)); // engineer
  const idsA = topEng.slice(0,10).map(x=>x.id||x.url||x.title);
  const idsB = topBiz.slice(0,10).map(x=>x.id||x.url||x.title);
  const differ = idsA.some((id,idx)=>id !== idsB[idx]);
  results.push({ name:'persona order differs', pass: differ });
  // 6) CSS クランプ
  const css = fs.readFileSync(path.join('docs','styles.css'),'utf8');
  const hasTitleClamp = /\.article-title a[^}]*-webkit-line-clamp:\s*2/i.test(css);
  const hasSummaryClamp = /\.article-content[^}]*-webkit-line-clamp:\s*3/i.test(css);
  results.push({ name:'title 2-line clamp', pass: hasTitleClamp });
  results.push({ name:'summary 3-line clamp', pass: hasSummaryClamp });
  // 7) Meta/OG/Twitter
  const html = fs.readFileSync(path.join('docs','index.html'),'utf8');
  const metaOk = /<meta[^>]*name=["']description["'][^>]*>/i.test(html) && /<meta[^>]*property=["']og:title["'][^>]*>/i.test(html) && /<meta[^>]*name=["']twitter:card["'][^>]*>/i.test(html);
  results.push({ name:'meta/og/twitter', pass: metaOk });

  const failed = results.filter(r=>!r.pass);
  results.forEach(r => console.log(`${r.pass?'✅':'❌'} ${r.name}${r.detail?` => ${r.detail}`:''}`));
  if (failed.length) {
    process.exitCode = 1;
  } else {
    console.log('All acceptance checks passed (static verification).');
  }
}

// 48時間以内制約の追加検査
function checkFreshness() {
  const a = readJSONCandidate();
  const now = new Date();
  const tooOld = a.filter(x => {
    const raw = x.publishedAt || x.published_date;
    if (!raw) return true;
    let d = new Date(raw);
    if (isNaN(d)) d = /\d{4}-\d{2}-\d{2}$/.test(String(raw)) ? new Date(String(raw)+'T00:00:00Z') : new Date(0);
    const ageH = (now - d) / 36e5;
    return ageH >= 48; // 48時間以上はNG
  });
  if (tooOld.length) {
    console.error(`❌ freshness: ${tooOld.length} item(s) are older than 48h`);
    process.exit(1);
  } else {
    console.log('✅ freshness: all items are within 48h');
  }
}

try {
  testAcceptance();
  checkFreshness();
} catch (e) { console.error('Test error:', e.message); process.exit(1); }
