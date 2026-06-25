# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリの性質

これは**コードベースではなく、リサーチ成果物（Markdown + JSON のドキュメント集）** を保管するワークスペースです。`/Users/yousan/Desktop/game-analyze/` 配下で、国内（日本）と国際市場で著名なゲーム計 1025 本（うち 2020+ インディー 103 本、PC 拡張 500 本、2023+ インディー追補 114 本、国内モバイル拡張 108 本を含む）を以下3カテゴリに分類した分析カタログを管理します。

- **EXP（体験型）** — 遊ぶ過程の体験そのものが面白い。特に「他者との関わり方」を 6 サブタイプ（対戦／協力／非対称／非同期／観戦／ソロ）で分析
- **NAR（物語型）** — 物語を見ること／追体験することに特化
- **REW（報酬型）** — ガチャ・収集・成長など、ゲーム内報酬獲得が主動機

ビルド／テスト／lint はありません。編集ツールはエディタと（必要なら）`python3 -c '...'` で JSON を検証する程度です。

## ファイルの役割と編集時の責務

| ファイル / 場所 | 役割 | 編集時の注意 |
|---|---|---|
| **`data/games/{id:03d}-{slug}.json`** | **一次データソース（一ゲーム一ファイル）**。各ファイルは `id, title_jp, title_en, developer, publisher, year, platform[], genre, sales_jp, sales_world, primary, secondary[], social_axis, popularity, concept?, target?, tags[], slug, file` を持つ。`concept`（ゲームの positioning 1-2文）と `target`（想定プレイヤー層 1-2文）は任意フィールド、書かれていれば詳細ページに表示される。`tags[]` は現状 `"indie"` のみ（`scripts/tag_indie.py` で自動付与） | ここを編集／追加／削除したら **必ず** `python3 scripts/build_aggregate.py` を実行して `data/games.json` と `data/index.json` を再生成 |
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
| `scripts/tag_indie.py` | publisher/developer の denylist（メジャー大手 70+）と allowlist（インディー専門 publisher 60+）に基づいて `tags: ["indie"]` を全 JSON に書き込む。判定は **(a) developer == publisher の self-published か (b) indie 専門 publisher 配下** を indie とみなし、メジャー denylist にヒットしたら強制的に非 indie。alias 辞書で表記ゆれ（任天堂/Nintendo、スクエニ/Square Enix、Atlus/アトラス 等）を吸収する | `python3 scripts/tag_indie.py --dry-run` で件数確認 → 本実行後に `build_aggregate.py` |
| `site/facet.html`, `site/detail.html` | 公開サイトのUI実装（ファセット検索 + カード + 詳細）。`site/shared.css`, `site/shared.js` も共通アセット | `python3 -m http.server` でローカル配信、push で GitHub Pages 自動再デプロイ |
| `index.html` (root) | `site/facet.html` への meta-refresh リダイレクト。Pages トップの入口 | — |
| `.github/workflows/deploy-pages.yml` | GitHub Pages デプロイの Actions ワークフロー | push 時に自動実行、Actions タブから手動 Run も可 |

**ID #56 は 2026-06 に「桃太郎電鉄 〜昭和 平成 令和も定番！〜」で埋め、欠番を解消した**（当初プロセカ重複で欠番だった枠）。同時に **2020 年以降に日本国内で人気・話題になったゲーム 101 本を一括追加** し ID 1–200 を稼働化、続いて **2020 年以降に国内外で 20 万本超を売り上げたインディー作品 103 本（ID 201–303）を ultracode ワークフローで一括追加**、さらに **PC ゲーム 500 本（ID 304–803、Western CRPG / Grand Strategy / 4X / RTS / MMO / FPS / ARPG / Sim / Sandbox / VN・同人 / クラシック PC 等）を 22 並列 discover エージェントの ultracode + deep-research ワークフローで一括追加**、続いて **2023–2026 年の最新インディー 114 本（ID 804–917、都市伝説解体センター / SANABI / Magical Girl Witch Trials / Nine Sols / 8番のりば / ENDER MAGNOLIA / Refind Self / Manor Lords / Frostpunk 2 / Slay the Princess / In Stars and Time / Indika / 1000xRESIST / Lorelei and the Laser Eyes 等）を 12 並列 discover + 個別 enrich の ultracode ワークフローで一括追加**、さらに **2015 年以降に日本国内で一定規模に達したモバイルゲーム 108 本（ID 918–1025、ドッカンバトル / FEH / マリオカートツアー / 遊戯王マスターデュエル / ポケポケ / 遊戯王デュエルリンクス / Pokémon マスターズ EX / シャドウバース / ロマサガ RS / FFBE 幻影戦争 / ドラクエタクト / どうぶつの森ポケキャン / SINoALICE / アズールレーン / アイドリッシュセブン / ミリシタ / リネージュ2 レボリューション / リネージュM / 信長の野望 出陣 / 三國志覇道 / 戦国IXA モバイル / シャドウバース ワールズビヨンド / Brown Dust 2 / World Flipper / Alchemy Stars / Cookie Run Kingdom / エピックセブン / ラングリッサーモバイル / NieR Re[in]carnation / ドラガリアロスト / 千銃士 Rhodoknight / IDOLY PRIDE / Tokyo 7th シスターズ系 等）を 20 並列 discover + 個別 enrich の ultracode ワークフローで一括追加** した。現在 ID 1–1025 が全て稼働している。

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

期待値（2026-06-25 時点）: total=1025 / EXP 705, NAR 125, REW 195 / ids missing=[] / collisions=0
社会軸 (EXP のみ): ソロ 501 / 対戦 111 / 協力 70 / 非同期 6 / 非対称 5 / 観戦 3 / 未設定 9
タグ: indie 320 / non-indie 705（標準定義: 大手 publisher 配下を除外、self-published or indie 専門 publisher 配下を indie とする）

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
- 2023+ インディー追補（ID 804–917、計 114 本）は **12 並列 discover + 個別 enrich** の ultracode ワークフロー（181 エージェント、計 4.4M subagent トークン、2.2 時間）で生成。169 raw 候補 → 既存 803 とローカル dedup（タイトル正規化 + slug マッチ）で 114 採用。PC 拡張と異なり **各エントリを個別 enrich エージェントで構造化済み**なので `social_axis`、`popularity`、`concept`、`target` がいずれも日本語で記載され、`_source_urls`（最低 1 件）も裏取りされている。1 angle (experimental-art) が 6 連続 stall で脱落、`Liar's Bar` の enrich が接続エラーで脱落（計 2 件不取り）。一部 2019/2022 年作（Inorikaze、Voices of the Void、Front Mission 1st Remake）も注目度から拾った。具体的に補充された主要タイトル：都市伝説解体センター (Hakaba Bunko / 集英社ゲームズ 2025)、SANABI (Wonder Potion 2023)、Magical Girl Witch Trials (2025)、Nine Sols (RedCandle Games 2024)、8番のりば (KOTAKE CREATE 2024)、ENDER MAGNOLIA (Adglobe 2025)、Refind Self (Lizardry 2023)、Manor Lords (Slavic Magic 2024)、Frostpunk 2 (11 bit 2024)、Slay the Princess、In Stars and Time、Indika (Odd Meter 2024)、1000xRESIST (sunset visitor 2024)、Lorelei and the Laser Eyes (Simogo 2024)、Tokyo Necro (Nitroplus 2023)、CRYMACHINA (Aquria/FURYU 2023)、Eiyuden Chronicle (Rabbit & Bear 2024)、Wildfrost、Backpack Hero、Ratopia、Halls of Torment、Schedule I、Peak (Aggro Crab 2025)、Webfishing、Khazan: The First Berserker など。
- 2026-06-25 にバグハント ultracode（12 角度 discover + 個別 verify、計 62 エージェント / 2.2M subagent トークン）で 27 件のバグを確認・修正した。主な修正：(1) `scripts/normalize_platforms.py` を新規追加し platform 表記ゆれ 30+ 種類を統一（Steam/GOG/Epic 系→PC、macOS→Mac、Xbox Series/XSX/Xbox Series X|S→Xbox Series X/S、Vita→PS Vita、Switch (cloud)→Switch、PS3/4・PS4/PS5・Xbox 360/One・iOS/Android はスラッシュ分解、ブラウザ→Browser、AC→Arcade、PS VR/2→PSVR2）。`Multi` 40 件 / `consoles` 5 件 / 単独 `Xbox` 87 件は個別エンリッチ必須なので残置。(2) `site/facet.html` の検索バーを developer/publisher/popularity/concept/target/secondary まで対象拡張。`data/index.json` にも検索対象フィールドを追加（943KB に肥大化）。(3) ファセット axis フィルタが NAR/REW を巻き込んでいた問題を「EXP のときのみ axis を適用」に修正。(4) platform ファセットの 12 件カットを「件数 ≥5」閾値方式に変更（Linux/PS3 等が見える）。(5) `games-catalog.md` の ID 56 重複行削除（行数 1026→1025）。(6) `data/meta.json` の `total_titles: 200`（陳腐化していた）削除。(7) `data/games/{29,35,...,96}` 29 ファイルで欠落していた `secondary: []` を補填。(8) ID 77 エルデンリング SOTE の `platform: ["DLC"]` を base game の platform 配列で置換。テスト面では `tests/python/test_data_integrity.py` に platform 禁止語テスト・secondary 必須テスト・meta.json 派生量混入禁止テスト・catalog 重複行検知テストを追加、`tests/js/ui/facet.test.mjs` にパズドラ/モンスト×iOS/Xbox Series X/S 統合/Mac 統合/Steam チップ非表示/publisher 検索/developer 検索/axis EXP 専用の 7 件追加（最終: Python 87 / JS 132 すべて緑）。
- 国内モバイル拡張（ID 918–1025、計 108 本）は **20 並列 discover + 個別 enrich** の ultracode ワークフロー（途中 rate limit で 2 回 resume、最終的に 224 エージェント / 約 4.2M subagent トークン）で生成。最初の起動でセッション上限に当たり、resume を 2 回挟むことでようやく日本国内系の 5 angle（jp-major-mobile-2015-2020、jp-major-mobile-2021-2026、jp-idol-otome-bishojo、jp-strategy-sim-card、jp-puzzle-casual-arcade）が完走。114 candidate → 111 enrich → 2014 リリース 3 件除外で 108 採用。グローバル / 中華 / 韓国 / SEA / カジュアル系の 15 angle（global-moba-shooter-pvp、global-match3-casual-puzzle、cn-major-gacha-rpg、kr-mmo-gacha、sea-india-mena 等）は **rate limit で全 enrich が脱落したため未取得**で、Honor of Kings / Royal Match / Whiteout Survival / Last War: Survival Game / Lords Mobile / Brawl Stars / Mobile Legends / Subway Surfers / Candy Crush 系 / Among Us! mobile / Cookie Run: Kingdom 等は次回追補で扱う。enrich 済み 108 本は `concept`/`target`/`popularity` がいずれも日本語、`_source_urls` 1 件以上付き。`primary` は **REW 92 本 / EXP 16 本** に偏っており、モバイルガチャ＝REW、PvP/操作型＝EXP のルールで自然に分布した。`social_axis` は **非同期 90 / 対戦 14 / 協力 5 / ソロ 2**（NIKKE 型ガチャは「非同期＝ランキング/フレンド/同盟戦」、PUBG Mobile / 荒野行動 / ポケモンユナイト系は「対戦」、Lineage 2: Revolution は「協力」、シングル特化のスーパーマリオラン等は「ソロ」）。具体的に補充された主要タイトル：ドラゴンボールZ ドッカンバトル (2015、累計 3.5 億 DL / 37 億ドル収益)、Fire Emblem Heroes (2017、13 億ドル超)、遊戯王 デュエルリンクス (2017、10 億ドル超)、ポケモンTCGポケット (2024、配信初月 1.2 億ドル収益)、PUBG Mobile (2018、世界累計 12 億 DL)、Pokémon マスターズ EX (2019、累計 5,000 万 DL)、ロマサガ リ・ユニバース (2018、累計 3,000 万 DL)、シャドウバース (2016、累計 2,200 万 PL)、信長の野望 出陣 (2023、配信 3 日で 100 万 DL)、SINoALICE (2017、年間アプリヒットランキング 1 位)、リネージュ2 レボリューション / リネージュM (Netmarble / NCSOFT 国内最大級重課金 MMO)、どうぶつの森 ポケットキャンプ (2017、6 日で 1,500 万 DL)、マリオカート ツアー (2019、98 日で 1.42 億 DL)、シャドウバース ワールズビヨンド (2025)、ポケモン GO 派生 (Peridot 系は未取得) など。

## 作業時の心構え

- このリポジトリは「研究レポート」であり、コードリファクタの感覚ではなく **編集者・データジャーナリスト** の感覚で扱う
- 数字や分類を変える際は、必ず Markdown と JSON 両方を一貫させ、変更理由（出典の更新／分類判断の見直し）をコミットメッセージかセクション末尾に残す
- 「100本にこだわって水増しする」より、「掲載されている各 1 件が出典と分類根拠を持っている」状態を優先する
