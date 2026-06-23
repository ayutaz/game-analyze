# 日本市場の有名ゲーム303本 — 3カテゴリ分類カタログ

本リポジトリは、国内（日本）で発売・配信され、一定規模の販売・DL本数を記録した、または SNS でバズった有名ゲーム計 **303本** を、以下3つの分類軸で整理した分析カタログです。
1985–2026年を網羅し、2026年6月に **2020年以降の人気作 101本を一括追加** して 200本へ、さらに **2020年以降に国内外で 20万本超を売り上げたインディー作品 103本を一括追加** して 303本に拡張しました。

---

## 1. 3カテゴリの定義

| カテゴリ | 略号 | 定義 | 中核となる「面白さ」の源泉 |
|---|---|---|---|
| 体験型 | EXP | 遊ぶ過程の体験そのものが面白いゲーム。メカニクス・操作・対戦・協力に価値の重心がある。特に「他者（人間）」との相互作用が中核のものを重視 | プレイヤー自身の判断・反射・他者との駆け引き |
| 物語型 | NAR | 物語・ストーリーを「見る／追体験する」ことに特化したゲーム。読み物・映像演出的体験 | シナリオ・キャラクター・世界観の没入 |
| 報酬型 | REW | アイテム・ガチャ・ランキング・経験値・キャラ収集などゲーム内報酬を得ること自体が目的化しているゲーム | 収集・成長・運（ガチャ）・序列の達成感 |

複数該当はあり（例：ペルソナ5 = 物語型主／報酬型副）。各タイトルでは **主分類 (primary)** を1つ、**副分類 (secondary)** を必要に応じて1〜2つ設定。

### 体験型における「他者軸」サブタイプ

| サブタイプ | 内容 | 代表例 |
|---|---|---|
| 対戦 (PvP) | 同期型の対人対戦 | スマブラ、スプラトゥーン、ストリートファイター |
| 協力 (Co-op) | 同期型の協力プレイ | モンハン、Overcooked、It Takes Two |
| 非対称 (Asym) | 役割が非対称な対戦 | Dead by Daylight |
| 非同期 (Async) | 時間差での相互作用 | あつ森（島訪問）、ポケモンGO（レイド） |
| 観戦／実況 (Spectate) | 配信・大会観戦価値が高い | LoL、ストVI、APEX |
| ソロ中心 (Solo) | 他者相互作用が薄い体験型 | スーパーマリオオデッセイ |

---

## 2. 集計サマリ

- **総タイトル数**: **303本**（`data/games.json` 基準、ID 1–303 が連続稼働）
- **主分類の内訳**（`data/games.json` 集計）:
  - 体験型 (EXP): **183本**
  - 物語型 (NAR): **69本**
  - 報酬型 (REW): **51本**
- **体験型の「他者軸」内訳**: ソロ 88 / 対戦 41 / 協力 35 / 非同期 4 / 非対称 3 / 観戦 3 / 未設定 9（既存99本のうち未設定が残る）
- **プラットフォーム分布**: Switch / Switch 2 / PS4 / PS5 / Xbox / XSX / 3DS / Wii / PC (Steam) / iOS / Android / Arcade / Multi
- **時代分布**: 1985–2019 = 99本 / 2020–2026 = 204本（2020+ メジャー101本＋2020+ インディー103本、2026年6月時点のスナップショット）

### 売上・収益で見た日本市場 Top クラス（verified）

| 順位 | タイトル | プラットフォーム | 国内累計 | 主分類 |
|---|---|---|---|---|
| 1 | あつまれ どうぶつの森 | Switch | 約 11.91M (累計) / 約 8.44M (Switch内集計) | EXP (Async) |
| 2 | マリオカート8 デラックス | Switch | 約 9.03M | EXP (対戦) |
| 3 | ポケットモンスター スカーレット・バイオレット | Switch | 約 8.66M | REW |
| — | ポケットモンスター 赤・緑 | GB | 約 8.22M | REW |
| — | スマブラ SP | Switch | 約 5.74M | EXP (対戦) |
| — | スプラトゥーン3 | Switch | 約 7.09M | EXP (対戦) |
| — | モンスターハンター：ワールド | PS4 | 約 1.97M (PS4国内1位) | EXP (協力) |
| — | ポケモン X・Y | 3DS | 約 4.50M (3DS国内1位) | REW |

出典: achikochi-data.com / teitengame.com / frontlinejp.net（Famitsu 集計ベース）

### 2025年の日本国内モバイル収益 Top（verified）

| 順位 | タイトル | 2025年収益（App Store ベース） |
|---|---|---|
| 1 (Q4・年間) | ラストウォー：サバイバル | モンスト比 約1.3倍 |
| 2 | モンスターストライク | 2026年1月第1週、超・獣神祭で前週比 +282% |
| 3 | ポケモンTCGポケット | 約 ¥65.0B |
| 9 | Fate/Grand Order | 約 ¥29.3B |

### 2025年 国内パッケージ年間 Top（verified, Famitsu）

| 順位 | タイトル | プラットフォーム | 本数 |
|---|---|---|---|
| 1 | マリオカートワールド | Switch 2 | 2,268,381 |
| 2 | ポケモン LEGENDS Z-A | Switch | 1,529,893 |
| 3 | ポケモン LEGENDS Z-A Switch 2 Edition | Switch 2 | 1,004,154 |
| 4 | モンスターハンターワイルズ | PS5 | 838,319 |

---

## 3. 主要観察

1. **国内コンソールの売上 Top は「体験型（対戦・協力・非同期マルチ）」に強く偏る。** あつ森・マリカ8DX・スプラ3・スマブラSP の4タイトルで Switch 国内 Top の半数以上を占める。日本市場は「ローカル＋友人/家族とのプレイ」を含めた体験型が依然支配的。
2. **モバイル収益 Top は「報酬型」がほぼ独占。** モンスト、FGO、ポケポケはガチャ／カード収集型。ラストウォー：サバイバルは「報酬型 + 競争メタ（同盟戦）」。
3. **物語型はパッケージ売上では中位、しかし話題性・SNSバズで強い**。Ghost of Tsushima、ペルソナ5、FF7 リバース、Detroit、十三機兵などが代表。アダルトゲーム発の Key 系『Kanon』『AIR』はノベル型を主流化させた。
4. **インディーズ／配信文化との結びつき**：Overcooked、Among Us、Vampire Survivors、Phasmophobia、Buckshot Roulette、8番出口、Splatoon 3、ポケポケなどが配信／SNSバズ駆動でユーザーを獲得。
5. **2020年以降のインディー躍進（ID 201–303）**：本カタログでは Valheim (1200万本+)、Inscryption、Loop Hero、Tunic、Pizza Tower、Pacific Drive、PEAK、Sons of the Forest (1390万本+ Steam)、Disco Elysium: The Final Cut、Citizen Sleeper、Slay the Princess、Mouthwashing など 103本 のインディーを追加収録。ローグライト・デッキ構築 (Inscryption, Loop Hero, Cobalt Core, Wildfrost, Monster Train 2)、協力ホラー (Phasmophobia, Lethal Company, R.E.P.O., Demonologist, DEVOUR)、サバイバル・クラフト (Valheim, Sons of the Forest, Enshrouded, V Rising, Core Keeper)、コージーシム (Dredge, Spiritfarer, Strange Horticulture, Coral Island, Sun Haven)、ナラティブ／VN (Disco Elysium, Citizen Sleeper, NORCO, In Stars and Time, Slay the Princess, Chained Echoes)、日本産インディー (ENDER LILIES, ASTLIBRA Revision, PARANORMASIGHT, Refind Self, BOKURA, HoloCure) などジャンルを網羅。

---

## 4. ファイル構成

- `README.md` — 本書（全体サマリ・カテゴリ定義・集計）
- `games-catalog.md` — 全303本のマスターテーブル（既存99本＋2020年以降追加101本＋2020年以降インディー103本の3部構成）
- `category-experience.md` — 体験型ゲーム一覧と「他者軸」分析
- `category-narrative.md` — 物語型ゲーム一覧
- `category-reward.md` — 報酬型ゲーム一覧
- `data/games.json` — 機械可読な構造化データ（集約形式）
- `data/games/{id:03d}-{slug}.json` — 一次データソース（一ゲーム一ファイル）
- `data/index.json` — 軽量インデックス（派生物）

---

## 5. 出典 / 注記

- 売上・収益データは **2025年末〜2026年6月時点** のスナップショット。Famitsu・Sensor Tower・achikochi-data.com・teitengame.com・frontlinejp.net・mediag.bunka.go.jp・note.com/game_i・4Gamer等を参照。
- 数値は「パッケージのみ」「DL含む累計」「App Store内のみ」など計測スコープが異なる場合があるため、各セルの注記を参照。
- 分類は主観的判断を含む。複数該当タイトルは設計意図・プレイヤーの主動機を勘案して主分類を決定した。

---

## テスト

Python と JS の両テストスイートを揃えて実行できます。初回のみ依存をインストールしてください。

```bash
npm install   # 初回のみ（jsdom などをインストール）
npm test      # Python + JS のテストを全部実行
```

push と main への PR では GitHub Actions (`.github/workflows/tests.yml`) が `npm test` を自動実行します。
