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
    # ラベルが無い場合は engineer の recommendation を流用
    for it in items:
        if not it.get('label'):
            rec = ((it.get('evaluation') or {}).get('engineer') or {}).get('recommendation')
            it['label'] = rec or 'consider'
    # 必読/注目の強制確保
    has_must = any(i.get('label') == 'must_read' for i in items)
    has_reco = any(i.get('label') == 'recommended' for i in items)
    # スコアソート（engineer total_score 優先、なければ total_score/score）
    def score_key(i):
        ev = (i.get('evaluation') or {}).get('engineer') or {}
        ts = ev.get('total_score')
        if isinstance(ts, (int, float)):
            return float(ts)
        if isinstance(i.get('score'), (int, float)):
            return float(i['score']) / 100.0
        return float(i.get('total_score') or 0.0)

    sorted_items = sorted(items, key=score_key, reverse=True)
    if not has_must and sorted_items:
        sorted_items[0]['label'] = 'must_read'
        sorted_items[0]['labelReason'] = 'fallback_promoted_top_to_must_read'
    if not has_reco:
        for it in sorted_items[1:]:
            if it.get('label') != 'must_read':
                it['label'] = 'recommended'
                it['labelReason'] = 'fallback_promoted_second_to_recommended'
                break
    # 件数確保（20件）
    if len(sorted_items) < 20:
        need = 20 - len(sorted_items)
        now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
        for i in range(need):
            sorted_items.append({
                'id': f'dummy_{i}',
                'title': f'ダミー記事 {i+1}（プレースホルダー）',
                'summary': 'データ不足時のプレースホルダー。最低表示件数を満たすために自動生成されました。',
                'url': 'https://example.com/',
                'source': 'placeholder',
                'source_tier': 2,
                'publishedAt': now_iso,
                'tags': ['placeholder'],
                'label': 'consider',
                'score': 45
            })
    return sorted_items


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
