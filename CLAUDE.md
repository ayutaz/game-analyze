# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリの性質

これは**コードベースではなく、リサーチ成果物（Markdown + JSON のドキュメント集）** を保管するワークスペースです。`/Users/yousan/Desktop/game-analyze/` 配下で、国内（日本）の有名ゲーム約100本を以下3カテゴリに分類した分析カタログを管理します。

- **EXP（体験型）** — 遊ぶ過程の体験そのものが面白い。特に「他者との関わり方」を 6 サブタイプ（対戦／協力／非対称／非同期／観戦／ソロ）で分析
- **NAR（物語型）** — 物語を見ること／追体験することに特化
- **REW（報酬型）** — ガチャ・収集・成長など、ゲーム内報酬獲得が主動機

ビルド／テスト／lint はありません。編集ツールはエディタと（必要なら）`python3 -c '...'` で JSON を検証する程度です。

## ファイルの役割と編集時の責務

| ファイル | 役割 | 編集時の注意 |
|---|---|---|
| `data/games.json` | **唯一の構造化された一次データソース**（`{meta, games[]}` の形）。各 game は `id, title_jp, title_en, developer, publisher, year, platform[], genre, sales_jp, sales_world, primary, secondary[], social_axis, popularity` | ここを更新したら **必ず** Markdown 系（README/games-catalog/category-*）にも反映する。Markdown だけ更新して JSON とずれるのは典型的なバグ |
| `README.md` | 全体サマリ・カテゴリ定義・売上Top・出典注記 | §2「集計サマリ」の本数（現状 EXP 55 / NAR 23 / REW 21、計99本）は JSON 集計と一致させる |
| `games-catalog.md` | 全タイトルのマスターテーブル（マークダウン表） | 列順は JSON のキー順に揃える。ID は JSON と一致 |
| `category-experience.md` | EXP の一覧 + 「他者軸」6 サブタイプ別解説 | EXP の追加・分類変更時に他者軸サブタイプの集計も更新 |
| `category-narrative.md` | NAR 一覧 + 解説 | — |
| `category-reward.md` | REW 一覧 + 解説（モバイル収益、ガチャ系、IP×軽量ループ等） | — |

**ID #56 は欠番（プロセカ重複を排除した結果）**。本数を 100 に揃えたい場合は、未掲載のタイトル（例：ウマ娘、デレステ、シャニマス、グラブル等 — 出典の openQuestions 参照）を追加して #56 を埋めるのが自然です。

## データの整合性チェック（編集後に毎回走らせる）

```bash
python3 -c "
import json
from collections import Counter
with open('data/games.json') as f:
    d = json.load(f)
games = d['games']
print('total:', len(games))
print('primary:', Counter(g['primary'] for g in games))
print('social_axis(EXP):', Counter(g.get('social_axis') for g in games if g['primary']=='EXP'))
print('ids missing:', sorted(set(range(1, max(g['id'] for g in games)+1)) - {g['id'] for g in games}))
"
```

期待値（2026-06 時点）: total=99 / EXP 55, NAR 23, REW 21 / ids missing=[56]

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
- EXP の 9 タイトルで `social_axis` が未設定。EXP に追加・移動するタイトルがあれば必ず埋める
- ガールフレンド(仮)、デレステ、シャニマス、グラブル、ラブライブ SIF2 等アイドル／Cygames 系の旧モバイル群は未掲載（追加余地あり）

## 作業時の心構え

- このリポジトリは「研究レポート」であり、コードリファクタの感覚ではなく **編集者・データジャーナリスト** の感覚で扱う
- 数字や分類を変える際は、必ず Markdown と JSON 両方を一貫させ、変更理由（出典の更新／分類判断の見直し）をコミットメッセージかセクション末尾に残す
- 「100本にこだわって水増しする」より、「掲載されている各 1 件が出典と分類根拠を持っている」状態を優先する
