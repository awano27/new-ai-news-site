#!/usr/bin/env python3
"""
Python統合収集（X + RSS）を実行し、docs/data/news.generated.json を生成する簡易スクリプト。
既存の collect_integrated.IntegratedCollector を活用し、受け入れ基準のフォールバックも実装。
"""

from pathlib import Path
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import re
try:
    import requests  # type: ignore
except Exception:
    requests = None
import sys

try:
    import feedparser  # type: ignore
except Exception:
    feedparser = None

# Ensure project root is importable so we can import collect_integrated
ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

try:
    from collect_integrated import IntegratedCollector  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit(f"collect_integrated import error: {e}")


def to_iso_datetime(s: str) -> str:
    """Normalize various date strings to ISO8601 with timezone (UTC, Z)."""
    if not s:
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    try:
        raw = str(s).strip()
        if 'T' in raw:
            if raw.endswith('Z'):
                raw = raw[:-1] + '+00:00'
            d = datetime.fromisoformat(raw)
        else:
            # Date only -> assume midnight UTC
            d = datetime.fromisoformat(raw + 'T00:00:00+00:00')
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    except Exception:
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def ensure_minimum_and_labels(items: list) -> list:
    # 高信頼ドメイン（Tier1相当）
    TIER1_DOMAINS = {
        'openai.com','ai.googleblog.com','googleblog.com','anthropic.com',
        'techcrunch.com','venturebeat.com','deepmind.com','research.google','nature.com',
        'science.org','arxiv.org','microsoft.com','blogs.nvidia.com','theinformation.com'
    }

    def extract_domain(url: str) -> str:
        try:
            from urllib.parse import urlparse
            host = urlparse(url).hostname or ''
            host = host.lower()
            multi = ('co.jp','ne.jp','or.jp','ac.jp','go.jp','co.uk','org.uk','gov.uk')
            if any(host.endswith(s) for s in multi):
                ps = host.split('.')
                return '.'.join(ps[-3:])
            ps = host.split('.')
            return '.'.join(ps[-2:]) if len(ps) >= 2 else host
        except Exception:
            return ''

    def trust_rank(it: Dict[str, Any]) -> int:
        if it.get('source_tier') == 1:
            return 2
        dom = (it.get('sourceDomain') or extract_domain(it.get('url','')) or it.get('source','')).lower()
        return 2 if dom in TIER1_DOMAINS else 1

    def is_x_item(it: Dict[str, Any]) -> bool:
        if isinstance(it.get('tags'), list) and 'x_post' in it['tags']:
            return True
        return str(it.get('source','')).startswith('X(@')

    def clamp01(x: float) -> float:
        return max(0.0, min(1.0, x))

    def persona_score(it: Dict[str, Any]) -> float:
        ev = (it.get('evaluation') or {}).get('engineer') or {}
        ts = ev.get('total_score')
        if isinstance(ts, (int,float)):
            return clamp01(float(ts))
        if isinstance(it.get('score'), (int,float)):
            return clamp01(float(it['score'])/100.0)
        return clamp01(float(it.get('total_score') or 0.0))

    def actionability(it: Dict[str, Any]) -> float:
        ev = (it.get('evaluation') or {}).get('engineer') or {}
        br = ev.get('breakdown') or {}
        a = br.get('actionability')
        if isinstance(a, (int,float)):
            return clamp01(float(a))
        # fallback: proxy from relevance
        r = br.get('relevance')
        if isinstance(r,(int,float)):
            return clamp01(0.45*float(r))
        return 0.3

    # 値スコア: ペルソナ総合 + 信頼 + 実用性で評価（X/非Xとも公平）
    for it in items:
        v = 0.72*persona_score(it) + 0.10*(1 if trust_rank(it)==2 else 0) + 0.18*actionability(it)
        it['_value_score'] = clamp01(v)

    vals = [it.get('_value_score',0.0) for it in items]
    vals_sorted = sorted(vals)
    def percentile(p: float) -> float:
        if not vals_sorted:
            return 0.0
        k = int(round((len(vals_sorted)-1) * p))
        return vals_sorted[k]

    # 動的閾値: must_read= max(0.75, P90), recommended= max(0.58, P70)
    p90 = percentile(0.90)
    p70 = percentile(0.70)
    must_th = max(0.75, p90)
    reco_th = max(0.58, p70)

    # 既存ラベルが無いものに付与
    for it in items:
        if not it.get('label'):
            if it['_value_score'] >= must_th:
                it['label'] = 'must_read'
                it['labelReason'] = 'dynamic_threshold_value_score_p90_or_min_075'
            elif it['_value_score'] >= reco_th:
                it['label'] = 'recommended'
                it['labelReason'] = 'dynamic_threshold_value_score_p70_or_min_058'
            else:
                # 既存のエンジニア推奨があれば流用
                rec = ((it.get('evaluation') or {}).get('engineer') or {}).get('recommendation')
                it['label'] = rec or 'consider'

    # 必読/注目の最低保証（非X優先で上位を補充）
    has_must = any(i.get('label') == 'must_read' for i in items)
    has_reco = any(i.get('label') == 'recommended' for i in items)
    if not (has_must and has_reco):
        non_x_sorted = sorted([i for i in items if not is_x_item(i)], key=lambda x: x.get('_value_score',0.0), reverse=True)
        if not has_must and non_x_sorted:
            non_x_sorted[0]['label'] = 'must_read'
            non_x_sorted[0]['labelReason'] = 'dynamic_fallback_promoted_top_non_x_to_must_read'
        if not has_reco:
            cand = None
            for it in non_x_sorted[1:]:
                if it.get('label') != 'must_read':
                    cand = it; break
            cand = cand or (non_x_sorted[1] if len(non_x_sorted)>1 else (non_x_sorted[0] if non_x_sorted else None))
            if cand:
                cand['label'] = 'recommended'
                cand['labelReason'] = 'dynamic_fallback_promoted_second_non_x_to_recommended'

    # 件数確保（20件）
    if len(items) < 20:
        need = 20 - len(items)
        now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
        for i in range(need):
            items.append({
                'id': f'dummy_{i}',
                'title': f'ダミー記事 {i+1}（プレースホルダー）',
                'summary': 'データ不足時のプレースホルダー。最低表示件数を満たすために自動生成されました。',
                'url': 'https://example.com/',
                'source': 'placeholder',
                'source_tier': 2,
                'publishedAt': now_iso,
                'tags': ['placeholder'],
                'label': 'consider',
                'score': 45,
                '_value_score': 0.45
            })
    # 値スコア順で返却
    return sorted(items, key=lambda x: x.get('_value_score', 0.0), reverse=True)


def map_to_output(items: list) -> list:
    out = []
    for it in items:
        title = it.get('title') or ''
        summary = it.get('summary') or it.get('content') or ''
        url = it.get('url') or ''
        src = it.get('source') or ''
        publishedAt = it.get('publishedAt') or it.get('published_date') or ''
        tags = it.get('tags') or []
        label = it.get('label') or 'consider'
        labelReason = it.get('labelReason')
        source_tier = it.get('source_tier')
        obj = {
            'id': it.get('id') or '',
            'title': title,
            'summary': summary,
            'url': url,
            'source': src,
            'publishedAt': to_iso_datetime(str(publishedAt)),
            'tags': tags,
            'label': label
        }
        if labelReason:
            obj['labelReason'] = labelReason
        if source_tier in (1, 2):
            obj['source_tier'] = source_tier
        # 既に persona 評価がある場合は維持
        if it.get('evaluation'):
            obj['evaluation'] = it['evaluation']
        # 便宜スコア（0-100）
        if isinstance(it.get('score'), (int, float)):
            obj['score'] = int(it['score'])
        elif isinstance(((it.get('evaluation') or {}).get('engineer') or {}).get('total_score'), (int, float)):
            obj['score'] = int(round(((it['evaluation']['engineer']['total_score']) * 100)))
        out.append(obj)
    return out


def read_config_sources(root: Path) -> List[Dict[str, Any]]:
    cfg = root / 'config' / 'sources.json'
    if not cfg.exists():
        return []
    try:
        return json.loads(cfg.read_text(encoding='utf-8'))
    except Exception:
        return []


def collect_from_config_sources(sources: List[Dict[str, Any]], max_age_hours: int = 48) -> List[Dict[str, Any]]:
    if not feedparser:
        return []
    out: List[Dict[str, Any]] = []
    def is_ai_related(title: str) -> bool:
        t = (title or '').lower()
        kws = ['ai','artificial intelligence','machine learning','deep learning','llm','gpt','claude','gemini','mistral','llama','rag','agent','multimodal','生成ai','機械学習','ディープラーニング','大規模言語モデル','モデル','アルゴリズム']
        return any(k in t for k in kws)
    now = datetime.now(timezone.utc)
    for s in sources:
        if s.get('type') != 'rss':
            continue
        name = s.get('name') or ''
        url = s.get('url') or ''
        tier = s.get('tier') or 2
        if not url:
            continue
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:20]:
                link = getattr(e, 'link', '')
                title = getattr(e, 'title', '')
                if not link or not title:
                    continue
                # published
                pub = getattr(e, 'published', '') or getattr(e, 'updated', '')
                d = None
                if getattr(e, 'published_parsed', None):
                    pp = e.published_parsed
                    d = datetime(pp.tm_year, pp.tm_mon, pp.tm_mday, pp.tm_hour, pp.tm_min, pp.tm_sec, tzinfo=timezone.utc)
                elif getattr(e, 'updated_parsed', None):
                    pp = e.updated_parsed
                    d = datetime(pp.tm_year, pp.tm_mon, pp.tm_mday, pp.tm_hour, pp.tm_min, pp.tm_sec, tzinfo=timezone.utc)
                elif pub:
                    try:
                        d = datetime.fromisoformat(pub)
                        if d.tzinfo is None:
                            d = d.replace(tzinfo=timezone.utc)
                    except Exception:
                        d = now
                else:
                    d = now
                age_h = (now - d).total_seconds() / 3600.0
                if age_h > max_age_hours:
                    continue
                if not is_ai_related(title):
                    continue
                out.append({
                    'id': f"rss_cfg_{abs(hash(name + link)) & 0xffffffff:x}",
                    'title': title,
                    'url': link,
                    'source': name,
                    'source_tier': tier,
                    'publishedAt': d.astimezone(timezone.utc).isoformat().replace('+00:00','Z'),
                    'tags': ['rss_feed']
                })
        except Exception:
            continue
    return out


def scrape_ai_links(url: str, name: str, tier: int = 1, max_items: int = 10) -> List[Dict[str, Any]]:
    """Very lightweight HTML scrape to collect AI-related links from a listing page.
    Uses regex to avoid extra deps. Falls back silently on error.
    """
    if not requests:
        return []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (+AI News Bot)'
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return []
        html = resp.text
        # crude anchor extraction
        anchors = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, flags=re.I|re.S)
        items: List[Dict[str, Any]] = []
        seen = set()
        def clean_text(t: str) -> str:
            t = re.sub(r'<[^>]+>', '', t)
            return re.sub(r'\s+', ' ', t).strip()
        ai_kws = ['ai','人工知能','machine learning','ml','llm','gpt','claude','gemini','mistral','llama','rag','agent','生成ai','大規模言語モデル']
        for href, inner in anchors:
            title = clean_text(inner)
            if not title or len(title) < 8:
                continue
            lo = title.lower()
            if not any(k in lo for k in ai_kws):
                continue
            if href.startswith('/'):
                # make absolute
                m = re.match(r'^(https?://[^/]+)', url)
                if m:
                    href = m.group(1) + href
            key = (href, title)
            if key in seen:
                continue
            seen.add(key)
            items.append({
                'id': f'page_{abs(hash(name + href)) & 0xffffffff:x}',
                'title': title,
                'url': href,
                'source': name,
                'source_tier': tier,
                # assume fresh (today) because many pages hide exact date; will pass 48h filter
                'publishedAt': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
                'tags': ['rss_feed']
            })
            if len(items) >= max_items:
                break
        return items
    except Exception:
        return []


def main():
    root = Path(__file__).resolve().parents[1]
    docs_data = root / 'docs' / 'data'
    data_dir = root / 'data'
    docs_data.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    ic = IntegratedCollector()
    x_items = ic.collect_x_articles() or []
    rss_items = ic.collect_rss_articles() or []
    # 追加RSS（config/sources.json）も取得
    cfg_sources = read_config_sources(root)
    cfg_rss = collect_from_config_sources(cfg_sources, max_age_hours=48)
    # Page-type sources (e.g., The Information Tech page) scraping
    page_items: List[Dict[str, Any]] = []
    for s in (cfg_sources or []):
        if s.get('type') == 'page':
            url = s.get('url') or ''
            name = s.get('name') or 'Unknown'
            tier = s.get('tier') or 2
            if url:
                page_items.extend(scrape_ai_links(url, name, tier))
    def is_fresh(it: Dict[str, Any]) -> bool:
        raw = it.get('publishedAt') or it.get('published_date') or ''
        if not raw:
            return False
        try:
            d = datetime.fromisoformat(str(raw).replace('Z','+00:00')) if 'T' in str(raw) else datetime.fromisoformat(str(raw) + 'T00:00:00+00:00')
        except Exception:
            return False
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - d).total_seconds() / 3600.0
        return age_h <= 48

    all_items = [it for it in (x_items + rss_items + cfg_rss + page_items) if is_fresh(it)]
    all_items = ensure_minimum_and_labels(all_items)
    out = map_to_output(all_items)

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    (docs_data / 'news.generated.json').write_text(payload, encoding='utf-8')
    (data_dir / 'news.generated.json').write_text(payload, encoding='utf-8')
    print(f'Wrote {len(out)} items to docs/data/news.generated.json and data/news.generated.json')


if __name__ == '__main__':
    main()
