# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリの性質

これは**コードベースではなく、リサーチ成果物（Markdown + JSON のドキュメント集）** を保管するワークスペースです。`/Users/yousan/Desktop/game-analyze/` 配下で、国内（日本）と国際市場で著名なゲーム計 803 本（うち 2020+ インディー 103 本、PC 拡張 500 本を含む）を以下3カテゴリに分類した分析カタログを管理します。

- **EXP（体験型）** — 遊ぶ過程の体験そのものが面白い。特に「他者との関わり方」を 6 サブタイプ（対戦／協力／非対称／非同期／観戦／ソロ）で分析
- **NAR（物語型）** — 物語を見ること／追体験することに特化
- **REW（報酬型）** — ガチャ・収集・成長など、ゲーム内報酬獲得が主動機

ビルド／テスト／lint はありません。編集ツールはエディタと（必要なら）`python3 -c '...'` で JSON を検証する程度です。

## ファイルの役割と編集時の責務

| ファイル / 場所 | 役割 | 編集時の注意 |
|---|---|---|
| **`data/games/{id:03d}-{slug}.json`** | **一次データソース（一ゲーム一ファイル）**。各ファイルは `id, title_jp, title_en, developer, publisher, year, platform[], genre, sales_jp, sales_world, primary, secondary[], social_axis, popularity, concept?, target?, slug, file` を持つ。`concept`（ゲームの positioning 1-2文）と `target`（想定プレイヤー層 1-2文）は任意フィールド、書かれていれば詳細ページに表示される | ここを編集／追加／削除したら **必ず** `python3 scripts/build_aggregate.py` を実行して `data/games.json` と `data/index.json` を再生成 |
| `data/analyses/{id:03d}-{slug}.md` | 深い分析（マークダウン）。詳細ページの本文として表示される。任意（未作成なら「未分析」表示） | 自由に書ける。サンプル: 001/006/020/066/076 |
| `data/meta.json` | カテゴリ定義・出典 URL・社会軸の定義（不変メタ） | カテゴリ定義や出典を増やしたときだけ編集 |
| `data/index.json` | **派生物**: 軽量インデックス（id/タイトル/年/分類/ファイルパス） | 手で編集しない。`build_aggregate.py` が生成 |
| `data/games.json` | **派生物**: 集約形式（`{meta, games[]}`）。後方互換と Markdown 編集の参照用 | 手で編集しない。`build_aggregate.py` が生成 |
| `README.md` | 全体サマリ・カテゴリ定義・売上Top・出典注記 | §2「集計サマリ」の本数は JSON 集計と一致させる |
| `games-catalog.md` | 全タイトルのマスターテーブル（マークダウン表） | 列順は JSON のキー順に揃える。ID は JSON と一致 |
| `category-experience.md` | EXP の一覧 + 「他者軸」6 サブタイプ別解説 | EXP の追加・分類変更時に他者軸サブタイプの集計も更新 |
| `category-narrative.md` | NAR 一覧 + 解説 | — |
| `category-reward.md` | REW 一覧 + 解説（モバイル収益、ガチャ系、IP×軽量ループ等） | — |
| `scripts/split_games.py` | 一度きり用: 集約 `games.json` を `data/games/` に分解 | 通常は使わない（履歴的に保持） |
| `scripts/build_aggregate.py` | `data/games/*.json` から `games.json` と `index.json` を再生成 | データ変更後に必ず実行 |
| `scripts/patch_games.py` | 複数ゲームに同じフィールド（concept/target等）を一括で書き込むユーティリティ。中の `PATCHES` 辞書を編集して実行 | 一括追記後は `build_aggregate.py` を必ず実行 |
| `site/facet.html`, `site/detail.html` | 公開サイトのUI実装（ファセット検索 + カード + 詳細）。`site/shared.css`, `site/shared.js` も共通アセット | `python3 -m http.server` でローカル配信、push で GitHub Pages 自動再デプロイ |
| `index.html` (root) | `site/facet.html` への meta-refresh リダイレクト。Pages トップの入口 | — |
| `.github/workflows/deploy-pages.yml` | GitHub Pages デプロイの Actions ワークフロー | push 時に自動実行、Actions タブから手動 Run も可 |

**ID #56 は 2026-06 に「桃太郎電鉄 〜昭和 平成 令和も定番！〜」で埋め、欠番を解消した**（当初プロセカ重複で欠番だった枠）。同時に **2020 年以降に日本国内で人気・話題になったゲーム 101 本を一括追加** し ID 1–200 を稼働化、続いて **2020 年以降に国内外で 20 万本超を売り上げたインディー作品 103 本（ID 201–303）を ultracode ワークフローで一括追加**、さらに **PC ゲーム 500 本（ID 304–803、Western CRPG / Grand Strategy / 4X / RTS / MMO / FPS / ARPG / Sim / Sandbox / VN・同人 / クラシック PC 等）を 22 並列 discover エージェントの ultracode + deep-research ワークフローで一括追加** した。現在 ID 1–803 が全て稼働している。

## データ編集ワークフロー

1. **追加**: `data/games/{id:03d}-{slug}.json` を新規作成（id は既存と被らないように、slug は英語タイトルから kebab-case）
2. **修正**: 該当する `data/games/{id:03d}-*.json` を直接編集
3. **削除**: 該当ファイルを削除
4. **必ず最後に再生成**: `python3 scripts/build_aggregate.py`
5. **整合性チェック**:

```bash
python3 -c "
import json
from collections import Counter
from pathlib import Path
games = [json.loads(p.read_text()) for p in sorted(Path('data/games').glob('*.json'))]
print('total:', len(games))
print('primary:', Counter(g['primary'] for g in games))
print('social_axis(EXP):', Counter(g.get('social_axis') for g in games if g['primary']=='EXP'))
ids = {g['id'] for g in games}
print('ids missing:', sorted(set(range(1, max(ids)+1)) - ids))
print('id collisions:', len(games) - len(ids))
print('slug collisions:', len(games) - len({g['slug'] for g in games}))
"
```

期待値（2026-06-24 時点）: total=803 / EXP 603, NAR 100, REW 100 / ids missing=[] / collisions=0
社会軸 (EXP のみ): ソロ 426 / 対戦 95 / 協力 62 / 非同期 4 / 非対称 4 / 観戦 3 / 未設定 9

## 分類ルール（複数該当タイトルの主分類判定）

ハイブリッド作品（ポケモン本編、FGO、エルデンリング、ペルソナ5 等）は **プレイヤーの主動機** で主分類を決める。ガイドライン：

- ポケモン本編 → **REW**（収集が主動機、物語は副）
- ペルソナ5 / FF / Detroit / 十三機兵 → **NAR**（物語消費が主動機）
- エルデンリング / モンハン / ゼルダ BotW → **EXP**（戦闘・探索の体験が主動機）
- あつ森 → **EXP（非同期）**（他者との交流体験が主動機、収集は副）

迷ったら「これを面白いと言うプレイヤーは何を楽しんでいるか」を1文で書き、その動詞（戦う／読む／集める）でカテゴリを選ぶ。`secondary[]` には副次的な動機を入れる。

## 出典・数値の扱い

- 売上・収益データは **2025年末〜2026年6月時点のスナップショット**。同一タイトルでも出典により ±20% 程度ぶれる（例：あつ森 11.91M = achikochi 累計 vs 8.44M = teitengame Switch 内集計、両方正しい）
- 数値を更新する際は **出典 URL を README §5 の出典リストに追記**。新規データの根拠を辿れる状態を保つ
- 一次出典: Famitsu / Sensor Tower / achikochi-data.com / teitengame.com / frontlinejp.net / mediag.bunka.go.jp / note.com/game_i / 4Gamer
- アダルトゲーム／インディーは数値非公開が多く、Kanon / AIR / 弟切草 等は「市場転換効果」を質的に記述する方針

## 既知のデータ品質メモ

- 体験型の `social_axis` は本来 1 タイトルが複数軸を持つ（例：スプラ3 = 対戦+収集+観戦）が、主動軸 1 つだけ記載している
- 既存99本側の EXP 9 タイトル（#073/#077/#079-#081/#083/#085-#087）で `social_axis` が未設定。2020+ で追加した EXP 50 件と、2020+ インディー拡張で追加した EXP 78 件はすべて埋めてある
- 2020+ 拡張で **デレステ・シャニマス・グラブル・グラブル Relink・あんスタ・ヒプマイ・刀剣乱舞・まほやく・アナデン・プリコネ・BLEACH Brave Souls・ブルアカ・ヘブバン・NIKKE** などアイドル／長期運営モバイル系は概ね追加済み。`ガールフレンド(仮)`・`ラブライブ SIF2`・`Sky 星を紡ぐ子どもたち` 等は未掲載のまま（小規模 IP・サ終済みなど）
- 2020+ インディー拡張（ID 201–303）は Workflow ベースで 363 raw → 115 consolidated → 103 kept で生成。Slay the Spire 2 (2026) など発売直後の作品も含む。Touhou Luna Nights / Satisfactory / Project Zomboid / Gnosia は 2019 以前リリースで除外、Ori 2 / Pentiment / Disney Dreamlight Valley は AAA（Microsoft/Gameloft）配給で除外。Hi-Fi Rush・Helldivers 2 は当初検討も AA / Sony first-party で workflow が消費前に除外済み。
- PC 拡張（ID 304–803、計 500 本）は ultracode + deep-research ワークフロー（22 並列 discover エージェント、計 1791K subagent トークン）で生成。1271 raw 候補 → ローカル dedup で 1140 ユニーク → ヒューリスティック品質スコアで上位 500 を採択。Consolidate フェーズに到達する前に western-crpg エージェントが 6 連続 stall でワークフロー全体が落ちたため、verify+enrich は走らず **discover の raw 出力を直接構造化** している。そのため `sales_world` の値はソースエージェントの推定がそのまま入っており、`Steam owners 1-2M` / `~5M concurrent` 等の表現ゆれが残る。重要な前提：(a) `social_axis` はジャンル＋angle ベースのルールで決定（CRPG=ソロ、MOBA=対戦、MMO=協力 等）、手書きの精査は未実施。(b) `popularity` 文は英文のまま保存されているケースがある。(c) Half-Life 1/2、Portal 1/2、Bioshock 1/2/Infinite、Skyrim、Civilization VI、Crusader Kings 3、StarCraft 2、World of Warcraft、Counter-Strike 2 等の PC 主力タイトルが未収録だった欠落を一気に埋めた。

## 作業時の心構え

- このリポジトリは「研究レポート」であり、コードリファクタの感覚ではなく **編集者・データジャーナリスト** の感覚で扱う
- 数字や分類を変える際は、必ず Markdown と JSON 両方を一貫させ、変更理由（出典の更新／分類判断の見直し）をコミットメッセージかセクション末尾に残す
- 「100本にこだわって水増しする」より、「掲載されている各 1 件が出典と分類根拠を持っている」状態を優先する
