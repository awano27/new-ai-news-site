# VERIFY

目的: `参考/連携内容.txt` の受け入れ基準に対して、データとUIが一致することを検証します。

## 1) データ生成（CI/ローカル）
- 推奨: GitHub Actions で実行（`.github/workflows/news.yml` あり）。
  - Node 20 / `npm i` → `npm run news`（collect→enrich→score）
  - 成果物: `data/news.generated.json` と `docs/data/news.generated.json`
- ローカルでも実行可（ネットワークが必要）
  - `npm run news`

期待値:
- `docs/data/news.generated.json` に最低20件の項目が存在。
- 各項目に `source`, `source_tier`, `publishedAt`, `label`, `score`, `evaluation.engineer/business.total_score` が含まれる。
- `labelReason` が必要に応じて付与（必読/注目の強制昇格）。

## 2) UI 確認
1. `docs/index.html` をブラウザで開く（Pagesでも可）。
2. 画面上部の統計カードを確認:
   - 記事数 >= 20
   - 平均スコアが 0% ではない（データに連動）
   - 高信頼ソース数（Tier1）が 0 ではない（OpenAI等をTier1に分類）
3. ペルソナ切替:
   - 「技術者向け」「ビジネス向け」を切り替えると、カードの並び（スコア順）が変化
4. 推奨度グループ:
   - 「必読」「注目」が最低1件ずつ存在
5. カード表示:
   - タイトル2行 / 要約3行のクランプ
   - ラベルピルにツールチップ（title/aria-label）
   - 出典にドメイン短文化 + ファビコン（取得不可時は非表示）
6. a11y/SEO:
   - `<html lang="ja">` が設定済
   - `<meta name="description">` / `og:*` / `twitter:*` が head に存在
   - 記事リンクは `target="_blank" rel="noopener noreferrer"`

## 3) 監査コマンド
- 外部リンク/relチェック: `npm run audit:links`
- HTMLメタ/Langチェック: `npm run audit:html`
- axe（プレースホルダー）: `npm run audit:axe`
- Lighthouse（プレースホルダー）: `npm run lh:mobile` / `npm run lh:desktop`

## 4) 期待する受け入れ基準まとめ
- 画面に >=20件表示。必読>=1、注目>=1 が常に存在。
- 統計カード（記事数/平均スコア/高信頼ソース）が `news.generated.json` と一致。
- カード崩れ無し。タイトル2行・要約3行のクランプ。ラベルピル＆ツールチップ動作。
- ペルソナ切替で順位が変化。
- すべての外部リンクに `rel="noopener"`。lang/OG/metaが反映。

