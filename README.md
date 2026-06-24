# 日本／世界市場の有名ゲーム — 3カテゴリ分類カタログ

本リポジトリは、国内（日本）および世界市場で発売・配信され、一定規模の販売・DL本数を記録した、または SNS でバズった有名ゲーム計 **1025本** を、以下3つの分類軸で整理した分析カタログです。
1985–2026年を網羅し、2026年6月に **2020年以降の人気作 101本を一括追加** して 200本へ、続いて **2020年以降に国内外で 20万本超を売り上げたインディー作品 103本を一括追加** して 303本へ、さらに **PC ゲーム 500本（西洋 CRPG、グランドストラテジー、RTS、MMO、FPS、ARPG、シム、サンドボックス、VN・同人、クラシック PC ほか）を一括追加** して 803本へ、続いて **2023–2026年の最新インディーゲーム 114本（『都市伝説解体センター』『SANABI』『Magical Girl Witch Trials』『Nine Sols』『Animal Well 派生』『Lethal Company 系』『Vampire Survivors 系』など）を ultracode + deep-research ワークフローで一括追加** して 917本へ、さらに **2015年以降に一定規模に達した国内モバイルゲーム 108本（『ドッカンバトル』『FEH』『マリオカートツアー』『遊戯王マスターデュエル』『ポケポケ』『ポケモンマスターズEX』『SINoALICE』『シャドウバース』『ロマサガ RS』『FFBE 幻影戦争』『ドラクエタクト』『どうぶつの森ポケキャン』『荒野行動』『PUBG Mobile』など）を ultracode ワークフローで一括追加** して 1025本に拡張しました。

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

- **総タイトル数**: **1025本**（`data/games.json` 基準、ID 1–1025 が連続稼働）
- **主分類の内訳**（`data/games.json` 集計）:
  - 体験型 (EXP): **705本**
  - 物語型 (NAR): **125本**
  - 報酬型 (REW): **195本**
- **体験型の「他者軸」内訳**: ソロ 501 / 対戦 111 / 協力 70 / 非同期 6 / 非対称 5 / 観戦 3 / 未設定 9（既存99本のうち未設定が残る）
- **プラットフォーム分布**: PC (Steam/GOG/Epic) を主軸に、Switch / Switch 2 / PS4 / PS5 / Xbox One / Xbox Series / 3DS / Wii / iOS / Android / Arcade / Multi
- **時代分布**: 1985–2019 = 高比率（PC 古典含む） / 2020–2026 = 多数（2020+ メジャー101本＋2020+ インディー103本、2026年6月時点のスナップショット）

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
6. **PC ゲーム大規模拡張（ID 304–803、計 500 本）**：本カタログは長らく Switch／モバイル中心だったが、**ultracode + deep-research ワークフロー**（22 並列 discover エージェント、1271 raw 候補 → 1140 dedup → 500 採用）で PC エコシステムを補強。**Western CRPG** (Mass Effect 2/3、Pillars of Eternity 1/2、Wasteland 3、Pathfinder Kingmaker/Wrath、Tyranny、KOTOR 1/2、Skyrim、Fallout 3/NV/4)、**Grand Strategy / 4X** (Civilization VI/V、Crusader Kings 3、Europa Universalis IV、Stellaris、Total War Warhammer 1/2/3、Three Kingdoms)、**RTS / MOBA** (StarCraft 2、Age of Empires II/IV、Company of Heroes 3、DOTA 2)、**MMO** (World of Warcraft Classic Era/Retail、Lost Ark、ESO、Black Desert、Tower of Fantasy)、**FPS** (Counter-Strike 2、Modern Warfare、Hunt: Showdown、Hell Let Loose、Squad、Insurgency Sandstorm、Tarkov)、**ARPG** (Path of Exile 1/2、Last Epoch、Grim Dawn、Torchlight 1/2)、**シム** (Cities: Skylines 1/2、Factorio、Microsoft Flight Simulator、ETS 2、Football Manager 各年版)、**サンドボックス・サバイバル** (RimWorld、Kenshi、Rust、ARK、Conan Exiles、Project Zomboid)、**クラシック・没入型** (Half-Life 1/2、Portal 1/2、Bioshock 1/2/Infinite、Dishonored 1/2、Deus Ex 各作、Hitman WOA、Outer Worlds)、**ナラティブ／走るシム** (Firewatch、Edith Finch、Stanley Parable Ultra Deluxe、Disco Elysium 派生)、**メトロイドヴァニア** (Ori 1/2、Bloodstained、Axiom Verge 1/2、Blasphemous 1/2)、**ローグライク** (FTL、Into the Breach、Slay the Spire 1、Dead Cells、Enter the Gungeon、Rogue Legacy 1/2、Caves of Qud)、**VN・同人** (Tsukihime Remake、Fate/stay night Réalta Nua、Umineko、ATRI、Doki Doki Literature Club、Higurashi Hou)、**レース／スポーツ** (Forza Horizon 4/5、Assetto Corsa Competizione、iRacing、F1 25、NBA 2K25)、**タワーディフェンス／パズル** (Tetris Effect、Baba Is You、Talos Principle 1/2、Antichamber、SpaceChem、Opus Magnum)、**アジア発 PC** (Naraka: Bladepoint、Once Human、Snowbreak、Punishing Gray Raven、Yakuza 0/Like a Dragon)。これにより EXP 603 / NAR 100 / REW 100 と PC 主軸ジャンル網羅性が大幅に向上した。
7. **最新インディー追補（ID 804–917、計 114 本）**：『都市伝説解体センター』『SANABI』『Magical Girl Witch Trials』が未収録だった反省から、**12 並列 discover + 個別 enrich の ultracode ワークフロー**で 2023–2026 年のインディーシーンを補強（169 raw → 既存 803 とローカル dedup → 114 採用）。**日本同人/インディー** (都市伝説解体センター、和階堂真の事件簿 TRILOGY DELUXE、魔法少女ノ魔女裁判、Tokyo Necro、CRYMACHINA、ENDER MAGNOLIA、Shadow Corridor 2、Sea Fantasy、Inorikaze、百英雄伝)、**韓国・東アジア** (SANABI、Limbus Company、Detective Dotson、Once Human、Sangokushi 系)、**ホラー** (FAITH: The Unholy Trinity Chapter III、World of Horror、Voices of the Void、Buckshot Roulette 派生)、**ローグライト** (Backpack Hero、Wildfrost、Ratopia、Tiny Rogues、Halls of Torment、20 Minutes Till Dawn、Megabonk、Slice & Dice、Boneraiser Minions)、**メトロイドヴァニア** (Nine Sols、Prince of Persia: The Lost Crown、Ultros、Bo: Path of the Teal Lotus、Crypt Custodian、Voidwrought)、**ナラティブ／VN** (Slay the Princess、Roadwarden、In Stars and Time、Tactical Breach Wizards、Indika、1000xRESIST、Lorelei and the Laser Eyes、Thank Goodness You're Here!、Botany Manor、Tales of Kenzera: ZAU、Venba)、**シム／経営** (Manor Lords、Frostpunk 2、Farthest Frontier、Outpath、Songs of Conquest、Tiny Bookshop)、**マルチプレイヤー協力** (Schedule I、Peak、Webfishing、Mor Phaaning Door)、**アクション／ソウルライク** (Khazan: The First Berserker、Enotria: The Last Song)、**コージー** (Coral Island、Fields of Mistria、Sun Haven 派生、Bear and Breakfast 続編)。EXP 689 / NAR 125 / REW 103 となり、2023–2026 の現行インディーシーンの網羅性が大幅に向上した。
8. **国内モバイル拡張（ID 918–1025、計 108 本、2015 年以降）**：「モバイルデータが少ない」という指摘を受け、**20 並列 discover + 個別 enrich の ultracode ワークフロー**で 2015 年以降に日本国内で一定規模に到達したモバイルゲームを補強した（rate limit 切れによる resume を 2 回挟み、最終的に jp-major-2015-2020、jp-major-2021-2026、jp-idol-otome-bishojo、jp-strategy-sim-card、jp-puzzle-casual-arcade の 5 angle で 114 candidate → 111 enrich → 2014 リリース除外で 108 採用）。**ガチャ系大型 IP** (ドラゴンボールZ ドッカンバトル、Fire Emblem Heroes、ロマサガ RS、Pokémon マスターズ EX、FFBE 幻影戦争、ドラクエタクト、シャドウバース、シャドウバース ワールズビヨンド、遊戯王マスターデュエル、遊戯王 デュエルリンクス、ポケモンTCGポケット、デュエル・マスターズ プレイス、信長の野望 出陣、三國志覇道、PUBG Mobile、荒野行動 別カバー)、**長期運営アイドル/乙女系** (アイドリッシュセブン、ミリシタ、SINoALICE、A3!、IDOLY PRIDE、千銃士 Rhodoknight、ヴァンガード ZERO、ピオフィオーレの晩鐘、文豪とアルケミスト、夢色キャスト、八月のシンデレラナイン、夢100、戦刻ナイトブラッド)、**カジュアル/パズル/位置情報** (どうぶつの森 ポケットキャンプ、スーパーマリオラン、マリオカート ツアー、ねこあつめ、LINE バブル2、LINE レンジャー、LINE ポコポコ、ぷよぷよ!!クエスト、太鼓の達人 ポップタップビート)、**MMO/SLG** (リネージュ2 レボリューション、リネージュM、信長の野望オンライン スマホ、戦国IXA モバイル)、**韓国ガチャ** (エピックセブン、ラングリッサーモバイル、サマナーズウォー Chronicles、Cookie Run Kingdom)、**派生・継続運営系** (アズールレーン、アナザーエデン、World Flipper、Alchemy Stars、Brown Dust 2、Merc Storia、Phantom of the Kill、ロックマンX DiVE、星のドラゴンクエスト、NieR Re[in]carnation、ドラガリアロスト)を網羅。EXP 705 / NAR 125 / REW 195 となり、モバイル収益型カタログの主要 IP がほぼカバーされた。なおグローバル/中華/欧米モバイル系の 15 angle（Honor of Kings、Royal Match、Whiteout Survival、Last War 系など）はワークフローが rate limit に当たり未完了で、次回追補の対象となる。

---

## 4. ファイル構成

- `README.md` — 本書（全体サマリ・カテゴリ定義・集計）
- `games-catalog.md` — 全1025本のマスターテーブル（既存99本＋2020年以降追加101本＋2020年以降インディー103本＋PC 拡張500本＋最新インディー追補114本＋国内モバイル拡張108本の6部構成）
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
