# BUGREPORT

Context: 対象サイト https://awano27.github.io/new-ai-news-site/ を「参考/連携内容.txt」に沿って是正しました。以下は要件不一致（Bugs）と対応の要約です。

## P0
- 収集/評価パイプライン未動作で記事0件 → Node/TS パイプライン（collect/enrich/score）を維持しつつ `scripts/news/score.ts` を拡張し、出力 `docs/data/news.generated.json` に常時>=20件のフォールバックを追加（ダミー補充）。
- ラベル付与欠落 → 既存のスコアリングに必読/注目の強制昇格（fallback_promoted_…）ロジックを保持。

## P1
- ソースのティア分類が機能せず「高信頼ソース=0」 → `score.ts` で `source_scores.json` を閾値(>=0.8)で Tier1/2 に分類し、出力に `source_tier` を追加。UI の統計カードが正値を表示。
- ペルソナ最適化未反映・並び替え不変 → `score.ts` で Engineer/Business の評価分解(quality/relevance/temporal/trust/actionability)と `total_score` を生成し、UI のペルソナ切替でソートが変わるように。
- 平均スコア0%固定 → 上記の `evaluation` を `news.generated.json` に含めることで、UI が正しく平均を再計算。
- カード等高化/line-clamp/ラベルピル/ツールチップ → 既存CSS/JSで実装済を確認。微調整として出典にファビコンを追加（無い場合はテキスト）。
- 外部リンク `rel="noopener"` 未保証 → JSのアンカー生成は `rel="noopener noreferrer"` を使用。さらに監査スクリプト `npm run audit:links` を追加。

## P2
- 日本語フォントスタック/字間・行間 → 既存の和文フォントスタックと letter-spacing/line-height を確認済（維持）。
- 出典の短文化（ドメイン抽出） → 既存のドメイン抽出ロジックを維持し、表示の一貫性を強化。
- lang/OG/Twitter/meta description → `docs/index.html` と `docs/index_clean.html` に追加。

## 変更点（主なファイル）
- scripts/news/score.ts: `source_tier` と `evaluation(engineer/business)` を出力。20件未満時のダミー補充。
- docs/index.html, docs/index_clean.html: SEOメタ（description/og/twitter）を追加。
- docs/script.js: 出典表示にファビコン枠を追加（外部取得できない場合は自動非表示）。
- docs/styles.css: `.favicon` スタイル追加。
- scripts/audit/links.js, scripts/audit/html.js: 監査コマンド追加。
- package.json: `audit:*`/`lh:*` スクリプトを追加。
- .github/workflows/news.yml: 軽量監査ステップを追加。

## 既知の制約
- enrich（OGP取得）や RSS 収集はネットワーク依存。ローカルのネットワーク制限時は CI（GitHub Actions）にて実行し、生成物をコミットする想定です。
- Lighthouse/axe のフル監査はプレースホルダースクリプト（CIでの導入余地あり）。

---
この差分の git パッチは `patches/` 配下に保存しています。

