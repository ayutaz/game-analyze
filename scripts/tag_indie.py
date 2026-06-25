#!/usr/bin/env python3
"""data/games/*.json の各ファイルに `tags` フィールドを書き込み、
インディーズ判定（"indie" タグ）を一括付与する。

定義（標準ルール）:
- 「非インディー」: developer / publisher が MAJOR_PUBLISHERS に含まれる
- 「インディー」: 以下のいずれか
    (a) developer == publisher（self-published）
    (b) publisher が INDIE_PUBLISHERS に含まれる
- それ以外（中堅 AA や不明 publisher）は非インディー（保守的）

実行:
    python3 scripts/tag_indie.py            # 書き込み + 集計
    python3 scripts/tag_indie.py --dry-run  # 集計のみ、ファイルは書き換えない

判定後に必ず `python3 scripts/build_aggregate.py` を流して
data/games.json / data/index.json を再生成すること。
"""
from __future__ import annotations

import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES_DIR = ROOT / "data" / "games"


def _norm(s: str | None) -> str:
    """publisher / developer 表記ゆれを吸収するための正規化キー。
    NFKC + 小文字 + 空白/句読点除去 + 表記ゆれ統一。"""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s).lower().strip()
    for ch in [" ", "・", ",", ".", "/", "&", "+", "(", ")", "[", "]", "the ", "-"]:
        s = s.replace(ch, "")
    # 略称統一
    aliases = {
        # スクエニ系
        "スクエニ": "squareenix",
        "スクウェアエニックス": "squareenix",
        "スクウェア・エニックス": "squareenix",
        "squareenixltd": "squareenix",
        # カプコン
        "カプコン": "capcom",
        # セガ系
        "セガ": "sega",
        "segacorporation": "sega",
        "segagames": "sega",
        "atlus": "atlus_sega",
        "アトラス": "atlus_sega",
        # バンナム
        "バンナム": "bandainamco",
        "バンダイナムコ": "bandainamco",
        "バンダイナムコエンターテインメント": "bandainamco",
        "bandainamcoentertainment": "bandainamco",
        "bandainamcogames": "bandainamco",
        # コナミ
        "コナミ": "konami",
        "konamidigitalentertainment": "konami",
        # 任天堂
        "任天堂": "nintendo",
        "thepokemoncompany": "pokemon",
        "ポケモン": "pokemon",
        "ポケモン株式会社": "pokemon",
        "thepokemoncompanynintendo": "pokemon",
        # SIE / PlayStation
        "sonyinteractiveentertainment": "sie",
        "sonycomputerentertainment": "sie",
        "ソニー": "sie",
        "playstationstudios": "sie",
        "sonyplaystationpc": "sie",
        # Xbox / Bethesda
        "electronicarts": "ea",
        "microsoftgamestudios": "xboxgamestudios",
        "microsoftstudios": "xboxgamestudios",
        "xboxgamestudiosglobalpublishing": "xboxgamestudios",
        "bethesdasoftworks": "bethesda",
        "zenimaxmediabethesda": "bethesda",
        # Activision/Blizzard, Take-Two
        "activisionblizzard": "activision",
        "blizzardentertainment": "blizzard",
        "rockstargames": "rockstar",
        "takentwointeractive": "taketwo",
        "taketwointeractive": "taketwo",
        # 中華大手
        "tencentgames": "tencent",
        "neteasegames": "netease",
        "mihoyo": "hoyoverse",
        "ホヨバース": "hoyoverse",
        "ミホヨ": "hoyoverse",
        "lilithgames": "lilith",
        "moonton": "moonton",
        "igg": "igg",
        "centurygames": "centurygames",
        "camelgames": "camelgames",
        "funplus": "funplus",
        "yostar": "yostar",
        "happyelements": "happyelements",
        "kurogames": "kurogames",
        "klei": "klei",  # 後で見る
        # 韓国大手
        "ncsoft": "ncsoft",
        "netmarble": "netmarble",
        "ネットマーブル": "netmarble",
        "pearlabyss": "pearlabyss",
        "com2us": "com2us",
        "devsisters": "devsisters",
        "neowiz": "neowiz",
        "kakaogames": "kakao",
        "nexon": "nexon",
        "ネクソン": "nexon",
        "smilegate": "smilegate",
        # サイバーエージェント系
        "cygames": "cygames",
        "サイゲームス": "cygames",
        # GungHo / Colopl / DeNA / GREE / Mixi
        "ガンホー": "gungho",
        "gunghoonlineentertainment": "gungho",
        "コロプラ": "colopl",
        "ディー・エヌ・エー": "dena",
        "ブシロード": "bushiroad",
        "アニプレックス": "aniplex",
        "aniplexinc": "aniplex",
        "klabgames": "klab",
        "ミクシィ": "mixi",
        # Ubisoft
        "ubisoftentertainment": "ubisoft",
        # 中堅・ドイツ
        "deepsilver": "deepsilver",
        "kochmediadeepsilver": "deepsilver",
        "embracergroup": "embracer",
        "thqnordic": "thqnordic",
        # Warner / WB
        "warnerbrosgames": "warnerbros",
        "wbgames": "warnerbros",
        "warnerbrosinteractiveentertainment": "warnerbros",
        "warnerbrosgames": "warnerbros",
        # Level-5 / Marvelous / Spike / Kadokawa / From
        "level5": "level5",
        "レベルファイブ": "level5",
        "marvelous": "marvelous",
        "マーベラス": "marvelous",
        "spikechunsoft": "spikechunsoft",
        "スパイク・チュンソフト": "spikechunsoft",
        "スパイクチュンソフト": "spikechunsoft",
        "チュンソフト": "spikechunsoft",
        "kadokawagames": "kadokawa",
        "kadokawa": "kadokawa",
        "カドカワ": "kadokawa",
        "fromsoftware": "fromsoftware",
        "フロム・ソフトウェア": "fromsoftware",
        "フロムソフトウェア": "fromsoftware",
        # 中堅 AA
        "505games": "505games",
        "focusentertainment": "focus",
        "focushomeinteractive": "focus",
        "techland": "techland",
        "nacon": "nacon",
        "gearboxpublishing": "gearbox",
        "frontierdevelopments": "frontier",
        "valve": "valve",
        "epicgames": "epic",
        "epicgamespublishing": "epic",
        "riotgames": "riot",
        "supercell": "supercell",
        "niantic": "niantic",
        "ナイアンティック": "niantic",
        "cdpr": "cdprojekt",
        "cdprojekt": "cdprojekt",
        "cdprojektred": "cdprojekt",
        "larianstudios": "larian",
        "disneylucasartsaspyr": "disney",
        "disneylucasarts": "disney",
        "lucasarts": "disney",
        "koeitecmo": "koeitecmo",
        "ｋｏｅｉｔｅｃｍｏ": "koeitecmo",
        "behaviourinteractive": "behaviour",
        # LINE / NHN / coly
        "linegames": "linegames",
        "linecorporation": "linegames",
        "nhnplayart": "nhn",
        "ｎｈｎｐｌａｙａｒｔ": "nhn",
        "coly": "coly",
    }
    return aliases.get(s, s)


# メジャー大手 publisher（denylist）— 配下作品は indie ではない
MAJOR_PUBLISHERS_RAW = [
    # 日本 first-party / コンソール大手
    "任天堂", "Nintendo",
    "ポケモン", "The Pokemon Company",
    "SIE", "Sony Interactive Entertainment", "PlayStation Studios", "Sony Computer Entertainment",
    "Xbox Game Studios", "Microsoft Studios", "Microsoft Game Studios",
    "Bethesda", "Bethesda Softworks",
    # 大手 publisher（西洋 AAA）
    "EA", "Electronic Arts",
    "Ubisoft", "Ubisoft Entertainment",
    "Activision", "Activision Blizzard",
    "Blizzard", "Blizzard Entertainment",
    "Take-Two", "Take-Two Interactive", "Rockstar", "Rockstar Games", "2K", "2K Games",
    "Warner Bros", "Warner Bros Games", "WB Games",
    "Valve",
    "Epic Games",
    "Riot Games",
    "CD Projekt", "CD Projekt Red", "CDPR",
    "Disney", "LucasArts",
    "Larian Studios",
    # 日本 publisher 大手
    "Square Enix", "スクエニ", "スクウェア・エニックス", "Square Enix Ltd",
    "Capcom", "カプコン",
    "Sega", "SEGA", "セガ",
    "Atlus", "アトラス",
    "Bandai Namco", "Bandai Namco Entertainment", "バンダイナムコ", "バンダイナムコエンターテインメント", "バンナム",
    "Konami", "Konami Digital Entertainment", "コナミ", "KONAMI",
    "Koei Tecmo", "コーエーテクモ",
    "Level-5", "Level 5", "レベルファイブ",
    "Marvelous", "マーベラス",
    "Spike Chunsoft", "スパイク・チュンソフト", "スパイクチュンソフト", "チュンソフト",
    "Kadokawa", "Kadokawa Games", "カドカワ",
    "FromSoftware", "From Software", "フロム・ソフトウェア",
    # 中華大手
    "Tencent", "Tencent Games",
    "NetEase", "NetEase Games",
    "miHoYo", "HoYoverse", "ホヨバース", "ミホヨ",
    "Lilith Games",
    "Moonton",
    "IGG",
    "Century Games",
    "Camel Games",
    "FunPlus",
    "Yostar",
    "Happy Elements",
    "Kuro Games",
    # 韓国大手
    "NCSOFT", "NCsoft",
    "Netmarble", "ネットマーブル",
    "Krafton",
    "Nexon", "ネクソン",
    "Smilegate",
    "Pearl Abyss",
    "Com2uS",
    "Devsisters",
    "NEOWIZ",
    "Kakao Games",
    # 国内モバイル運営大手（ガチャゲー資本力 = AAA 相当）
    "Cygames", "サイゲームス",
    "GungHo", "ガンホー", "GungHo Online Entertainment",
    "Colopl", "コロプラ",
    "DeNA", "ディー・エヌ・エー",
    "GREE", "グリー",
    "Mixi", "ミクシィ",
    "Supercell",
    "Niantic", "ナイアンティック",
    "Bushiroad", "ブシロード",
    "Aniplex", "アニプレックス",
    "KLab", "KLabGames",
    "Line Games", "LINE",
    "NHN PlayArt",
    "coly",
    # 中堅大手（年商規模で AAA 周辺）
    "Embracer Group", "THQ Nordic", "Deep Silver", "Koch Media",
    "Paradox Interactive",  # 自社開発もあるが Stellaris / CK3 等は AAA 規模
    "505 Games",
    "Focus Entertainment", "Focus Home Interactive",
    "Techland",
    "Nacon",
    "Gearbox Publishing",
    "Frontier Developments",
    "Behaviour Interactive",
    # self-published だが規模・予算が AAA 相当で indie とは呼べない単発スタジオ
    "Game Science",          # 黒神話：悟空（予算 ~$70M、Tencent 出資）
    "Bluepoch",              # リバース：1999（中華中堅、$300M+）
    "Bank of Innovation",    # メメントモリ（東証上場、$180M+）
    "MINTROCKET", "Mintrocket",  # デイヴ・ザ・ダイバー（Nexon 内部レーベル）
    "Funcom",                # Conan Exiles / Dune Awakening（Tencent 子会社）
    "Crytek",                # Crysis / Hunt: Showdown（CryEngine 開発元、AAA）
    "Quantic Dream",         # Heavy Rain / Detroit（NetEase 子会社）
    "Cloud Imperium Games",  # Star Citizen（クラファン $1B+、AAA）
]

# インディー専門 publisher（allowlist）— 配下作品は indie とみなす
INDIE_PUBLISHERS_RAW = [
    "Devolver Digital",
    "Annapurna Interactive",
    "Raw Fury",
    "Team17",
    "Hooded Horse",
    "Curve Digital", "Curve Games",
    "11 bit studios",
    "Playism",
    "Yacht Club Games",
    "Klei Entertainment",
    "Supergiant Games",
    "ConcernedApe",
    "Tinybuild", "tinyBuild",
    "Chucklefish",
    "Daedalic Entertainment",
    "Akupara Games",
    "Iceberg Interactive",
    "No More Robots",
    "Versus Evil",
    "Kepler Interactive",
    "Skybound Games",
    "Future Friends Games",
    "Forever Entertainment",
    "Pikii", "ピキイ",
    "集英社ゲームズ", "Shueisha Games",
    "KOTAKE CREATE",
    "Toge Productions",
    "Hakaba Bunko",
    "Aggro Crab",
    "Coffee Stain Publishing", "Coffee Stain Studios",
    "Dotemu",
    "Modus Games",
    "Humble Games", "Humble Bundle",
    "Whitethorn Games",
    "Application Systems Heidelberg",
    "Freedom Games",
    "Sekai Project",
    "Top Hat Studios",
    "Forever Entertainment",
    "Wonder Potion",
    "Lizardry",
    "Slavic Magic",
    "Odd Meter",
    "sunset visitor",
    "Simogo",
    "Nitroplus",
    "Rabbit & Bear Studios",
    "Adglobe",
    "RedCandle Games", "Red Candle Games",
    "Mooneye Studios",
    "Studio MDHR",
    "Maddy Makes Games",
    "Inti Creates",
    "Vanillaware",
    "Mountains",
    "Mossmouth",
    "Subset Games",
    "Re-Logic",
    "Galactic Cafe",
    "Crows Crows Crows",
    "Mega Crit Games", "Mega Crit",
    "Number None",
    "Frictional Games",
    "Heart Machine",
    "Beethoven & Dinosaur",
    "Acid Wizard Studio",
    "Megagon Industries",
    "Ghost Town Games",
    "Hempuli",
    "House House",
    "Bombservice",
    "Mobius Digital",
    "Local Thunk",
    "Innersloth",
    "Toby Fox", "tobyfox",
    "Eric Barone",
]

MAJOR_KEYS = {_norm(p) for p in MAJOR_PUBLISHERS_RAW}
INDIE_KEYS = {_norm(p) for p in INDIE_PUBLISHERS_RAW}


def classify(developer: str | None, publisher: str | None) -> tuple[bool, str]:
    """インディー判定。
    戻り値: (is_indie, 判定理由のラベル)
    """
    dev_n = _norm(developer)
    pub_n = _norm(publisher)

    if pub_n in MAJOR_KEYS or dev_n in MAJOR_KEYS:
        return False, "major"

    if pub_n in INDIE_KEYS:
        return True, "indie-publisher"

    if developer and publisher and dev_n == pub_n:
        return True, "self-published"

    return False, "unknown-mid"


def main(write: bool = True) -> None:
    paths = sorted(GAMES_DIR.glob("*.json"))
    reasons: Counter[str] = Counter()
    indie_titles: list[tuple[int, str, str, str]] = []
    non_indie_self_pub: list[tuple[int, str, str]] = []

    for p in paths:
        data = json.loads(p.read_text(encoding="utf-8"))
        is_indie, reason = classify(data.get("developer"), data.get("publisher"))
        reasons[reason] += 1

        existing = data.get("tags") or []
        if not isinstance(existing, list):
            existing = []
        tag_set = {t for t in existing if isinstance(t, str)}
        if is_indie:
            tag_set.add("indie")
        else:
            tag_set.discard("indie")
        new_tags = sorted(tag_set)

        if is_indie:
            indie_titles.append((data["id"], data["title_jp"], data.get("publisher") or "", reason))

        if (data.get("tags") or []) == new_tags:
            continue
        if not write:
            continue
        data["tags"] = new_tags
        # tags フィールドが末尾になる位置を維持。dict は順序保持なので
        # 既存に tags があれば置換、なければ末尾に追加で OK。
        p.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    total = sum(reasons.values())
    print(f"total games: {total}")
    print("  classification breakdown:")
    for k, v in reasons.most_common():
        print(f"    {k:20s} {v:4d}")
    indie_n = reasons["indie-publisher"] + reasons["self-published"]
    print(f"  => indie total: {indie_n}")
    print(f"  => non-indie : {total - indie_n}")
    if not write:
        print("(dry-run: ファイルは書き換えていません)")
    print("\nsample indie titles (first 30):")
    for tup in indie_titles[:30]:
        print(f"  #{tup[0]:4d}  {tup[1][:30]:30s} | pub={tup[2][:25]:25s} | {tup[3]}")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    main(write=not dry)
