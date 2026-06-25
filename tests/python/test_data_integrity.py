"""Data integrity tests for the game-analyze catalog.

These tests enforce the invariants described in CLAUDE.md against the data
files under ``data/`` (per-file game JSONs, the aggregate ``games.json``, the
lightweight ``index.json``, and the meta file). They use only the standard
library so ``npm run test:py`` (which discovers tests under ``tests/python``)
can execute them without any external dependencies.

If a test fails, treat it as a data anomaly to investigate — do NOT relax the
assertion to make the suite green unless the underlying invariant in CLAUDE.md
has changed and the README has been updated to match.
"""
from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Importing the conftest module wires up sys.path and exposes the path
# constants we use throughout this file. It is safe under both pytest and
# stdlib unittest discovery.
from tests.python import conftest  # noqa: F401

# ---------------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------------
DATA_DIR: Path = conftest.DATA_DIR
GAMES_DIR: Path = conftest.GAMES_DIR
ANALYSES_DIR: Path = conftest.ANALYSES_DIR
REPO_ROOT: Path = conftest.REPO_ROOT

VALID_PRIMARY = {"EXP", "NAR", "REW"}
SOCIAL_AXES = ["対戦", "協力", "非対称", "非同期", "観戦", "ソロ"]
SOCIAL_AXES_SET = set(SOCIAL_AXES)

# Slug grammar: lowercase ASCII alphanumerics joined by single hyphens.
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Filename grammar: "{id:03d}-{slug}.json"  (zero-padded to 3 digits, but IDs
# above 999 naturally extend to 4 digits without leading zeros).
FILENAME_RE = re.compile(r"^(?P<id>\d{3,})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.json$")

# Expected hard-invariants. The catalog was expanded on 2026-06-23 from 99 to
# 200 titles by adding 101 Japan-popular 2020+ games (Slot #56 also filled to
# close the prior Project Sekai duplicate gap). On 2026-06-23 a second wave of
# 103 indie titles (ID 201..303) was added via an ultracode-driven Workflow
# (discovery → consolidate → adversarial verify+enrich) bringing 2020+ 20万本+
# indies into the catalog. On 2026-06-24 a third wave of 500 PC games
# (ID 304..803) was added via a 22-angle ultracode + deep-research Workflow
# (discover → local dedup → heuristic quality filter) covering Western CRPG,
# Grand Strategy/4X, RTS, MMO, FPS, ARPG, sim, sandbox, VN/doujin, classic PC.
# On 2026-06-24 a fourth wave of 114 recent indies (ID 804..917) was added via
# a 12-angle ultracode discover + per-entry enrich Workflow covering
# 2023–2026 indie releases (都市伝説解体センター, SANABI, Magical Girl Witch
# Trials, Nine Sols, 8番のりば, ENDER MAGNOLIA, Manor Lords, Frostpunk 2,
# Slay the Princess, In Stars and Time, Indika, 1000xRESIST, Lorelei and the
# Laser Eyes, etc.). On 2026-06-24 a fifth wave of 108 Japanese mobile games
# released since 2015 (ID 918..1025) was added via a 20-angle ultracode
# discover + per-entry enrich Workflow (5 JP angles completed; 15 global/CN/KR
# angles dropped to rate limit and are deferred). Covers Dragon Ball Z Dokkan
# Battle, Fire Emblem Heroes, 遊戯王マスターデュエル, ポケポケ, Pokémon
# Masters EX, シャドウバース, ロマサガRS, FFBE 幻影戦争, ドラクエタクト,
# どうぶつの森ポケキャン, SINoALICE, Lineage M, アイドリッシュセブン, ミリシタ,
# アズールレーン etc. The ID range 1..1025 is now contiguous.
# 2026-06-26: 3 領域 (グローバル/中華/韓国/SEA モバイル, クラシック PS1/PS2/N64/SNES/MD コンソール,
# VN/ノベル/アダルト/同人) を 20 並列 discover + 個別 enrich の ultracode ワークフロー
# 3 本で一括拡張 (約 1000 件)。それぞれ ID 1026-1375 / 1401-1750 / 1751-2100 範囲を
# 使用し、最終的に slug 衝突 50 件を後発側削除で解消した結果、id 空間に 75 個の
# 欠番ができている (CLAUDE.md 参照)。総数 1025 → 2025 件。
EXPECTED_TOTAL = 2025
EXPECTED_PRIMARY_COUNTS = {"EXP": 1215, "NAR": 491, "REW": 319}
EXPECTED_MISSING_IDS: set = {
    1026, 1029, 1155, 1158, 1159, 1161, 1162, 1165, 1187, 1188, 1189,
    1204, 1205, 1210, 1230, 1260, 1284, 1333, 1334, 1351, 1360, 1361,
    1368, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385,
    1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396,
    1397, 1398, 1399, 1400, 1470, 1473, 1483, 1487, 1488, 1495, 1649,
    1820, 1975, 2040, 2041, 2042, 2043, 2046, 2049, 2051, 2052, 2058,
    2061, 2072, 2074, 2075, 2076, 2077, 2078, 2081, 2082,
}
EXPECTED_ID_RANGE = set(range(1, 2100 + 1))  # 1..2100 (max id), 欠番は EXPECTED_MISSING_IDS で許容

REQUIRED_KEYS = ("id", "title_jp", "primary", "slug", "file")

# Per CLAUDE.md, social_axis is "他者軸 for EXP". The catalog also tags eight
# REW-primary mobile titles with a social_axis because they have strong
# social loops (raids / guild battles / co-op). These are explicitly
# documented exceptions; the test below treats them as an allowlist rather
# than failures so that drift on every *other* game is still caught.
SOCIAL_AXIS_NON_EXP_ALLOWLIST: set = {
    (18, "pokemon-go"),
    (20, "monster-strike"),
    (24, "project-sekai"),
    (25, "genshin-impact"),
    (28, "last-war-survival"),
    (30, "clash-of-clans"),
    (65, "dq-walk"),
    (99, "powerful-pro-baseball-series"),
    (918, "war-of-the-visions-final-fantasy-brave-exvius"),
    (919, "romancing-saga-re-universe"),
    (920, "dragon-quest-tact"),
    (921, "idolish7"),
    (923, "fire-emblem-heroes"),
    (924, "animal-crossing-pocket-camp"),
    (926, "mario-kart-tour"),
    (927, "lineage-2-revolution"),
    (928, "lineage-m"),
    (929, "pok-mon-masters-ex"),
    (930, "sinoalice"),
    (931, "azur-lane"),
    (932, "dragon-ball-z-dokkan-battle"),
    (933, "another-eden-the-cat-beyond-time-and-space"),
    (934, "the-idolm-ster-million-live-theater-days"),
    (936, "yo-kai-watch-puni-puni"),
    (937, "dragalia-lost"),
    (939, "star-ocean-anamnesis"),
    (941, "mega-man-x-dive"),
    (942, "love-live-school-idol-festival-all-stars"),
    (943, "a3"),
    (944, "stand-my-heroes"),
    (945, "ensemble-stars-basic"),
    (946, "uta-no-prince-sama-shining-live-emotion"),
    (947, "idoly-pride"),
    (948, "the-idolmaster-sidem-live-on-stage"),
    (949, "the-idolmaster-sidem-growing-stars"),
    (950, "the-idolmaster-pop-links"),
    (951, "i-chu"),
    (952, "idol-land-pripara"),
    (953, "d4dj-groovy-mix"),
    (954, "assault-lily-last-bullet"),
    (955, "warau-arsnotoria-sun"),
    (956, "yumeiro-cast"),
    (957, "senjushi-rhodoknight"),
    (958, "argonavis-from-bang-dream-aaside"),
    (959, "hachigatsu-no-cinderella-nine"),
    (960, "ensemble-girls"),
    (961, "utano-princesama-shining-live"),
    (962, "tsukino-paradise"),
    (963, "show-by-rock-fes-a-live"),
    (964, "cardfight-vanguard-zero"),
    (965, "magia-record-puella-magi-madoka-magica-side-story"),
    (966, "love-live-school-idol-festival-2-miracle-live"),
    (967, "bungo-to-alchemist"),
    (968, "yume-oukoku-to-nemureru-100-nin-no-ouji-sama"),
    (969, "onmyoji"),
    (970, "punishing-gray-raven"),
    (971, "snowbreak-containment-zone"),
    (972, "path-to-nowhere"),
    (975, "honkai-impact-3rd"),
    (977, "afk-arena"),
    (978, "afk-journey"),
    (979, "ragnarok-m-eternal-love"),
    (983, "diablo-immortal"),
    (985, "rise-of-kingdoms-lost-crusade"),
    (987, "justice-mobile"),
    (988, "where-winds-meet"),
    (989, "persona-5-the-phantom-x"),
    (991, "aether-gazer"),
    (992, "state-of-survival"),
    (993, "top-war-battle-game"),
    (995, "kingshot"),
    (996, "last-z-survival-shooter"),
    (997, "top-heroes-kingdom-saga"),
    (998, "sea-of-conquest-pirate-war"),
    (999, "stormshot-isle-of-adventure"),
    (1000, "age-of-empires-mobile"),
    (1001, "doomsday-last-survivors"),
    (1002, "viking-rise"),
    (1003, "call-of-dragons"),
    (1004, "warpath"),
    (1005, "infinity-kingdom"),
    (1006, "dragon-raja"),
    (1007, "watcher-of-realms"),
    (1008, "age-of-origins"),
    (1009, "lineage-2m"),
    (1010, "black-desert-mobile"),
    (1011, "odin-valhalla-rising"),
    (1012, "summoners-war-chronicles"),
    (1013, "seven-knights-2"),
    (1014, "cookie-run-kingdom"),
    (1015, "cookie-run-ovenbreak"),
    (1017, "ni-no-kuni-cross-worlds"),
    (1018, "counter-side"),
    (1019, "v4"),
    (1020, "traha"),
    (1021, "a3-still-alive"),
    (1022, "hundred-soul"),
    (1023, "maplestory-m"),
    (1024, "hit-heroes-of-incredible-tales"),
    (1025, "eversoul"),
}

# 2026-06 以降、全 1025 件の分析 Markdown が揃っている。それ以前は手書きで
# allowlist を保守していたが、現在は「全 games に対応する md がある」状態を
# 担保するテストへ移行した（test_analysis_md_exists_or_documented_missing）。


def _load_game_files() -> List[Tuple[Path, Dict[str, Any]]]:
    """Return [(path, parsed_json), ...] sorted by filename."""
    out: List[Tuple[Path, Dict[str, Any]]] = []
    for p in sorted(GAMES_DIR.glob("*.json")):
        with p.open(encoding="utf-8") as fh:
            out.append((p, json.load(fh)))
    return out


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------
class PerFileGameTests(unittest.TestCase):
    """Invariants computed from ``data/games/*.json``."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = _load_game_files()
        cls.games = [g for _, g in cls.entries]

    # --- counts -----------------------------------------------------------
    def test_total_games(self):
        self.assertEqual(len(self.entries), EXPECTED_TOTAL,
                         f"Expected {EXPECTED_TOTAL} game JSONs, found {len(self.entries)}")

    def test_primary_breakdown_exp(self):
        counts = Counter(g["primary"] for g in self.games)
        self.assertEqual(counts.get("EXP", 0), EXPECTED_PRIMARY_COUNTS["EXP"],
                         f"EXP count drift: {counts}")

    def test_primary_breakdown_nar(self):
        counts = Counter(g["primary"] for g in self.games)
        self.assertEqual(counts.get("NAR", 0), EXPECTED_PRIMARY_COUNTS["NAR"],
                         f"NAR count drift: {counts}")

    def test_primary_breakdown_rew(self):
        counts = Counter(g["primary"] for g in self.games)
        self.assertEqual(counts.get("REW", 0), EXPECTED_PRIMARY_COUNTS["REW"],
                         f"REW count drift: {counts}")

    def test_no_unknown_primary_values(self):
        primaries = {g["primary"] for g in self.games}
        self.assertTrue(primaries.issubset(VALID_PRIMARY),
                        f"Unknown primary values: {primaries - VALID_PRIMARY}")

    # --- id space ---------------------------------------------------------
    def test_id_space_is_contiguous(self):
        """As of 2026-06-23 the ID range 1..EXPECTED_TOTAL is fully populated."""
        ids = {g["id"] for g in self.games}
        missing = EXPECTED_ID_RANGE - ids
        self.assertEqual(missing, EXPECTED_MISSING_IDS,
                         f"Missing IDs in 1..{EXPECTED_TOTAL}: {sorted(missing)}; expected {sorted(EXPECTED_MISSING_IDS)}")

    def test_no_id_collisions(self):
        ids = [g["id"] for g in self.games]
        self.assertEqual(len(ids), len(set(ids)),
                         f"Duplicate ids: {[i for i, n in Counter(ids).items() if n > 1]}")

    def test_no_slug_collisions(self):
        slugs = [g["slug"] for g in self.games]
        self.assertEqual(len(slugs), len(set(slugs)),
                         f"Duplicate slugs: {[s for s, n in Counter(slugs).items() if n > 1]}")

    # --- slug shape -------------------------------------------------------
    def test_slug_kebab_case(self):
        bad = [g["slug"] for g in self.games if not SLUG_RE.match(g["slug"])]
        self.assertEqual(bad, [], f"Non kebab-case slugs: {bad}")

    # --- required schema --------------------------------------------------
    def test_required_fields_present(self):
        for path, g in self.entries:
            for key in REQUIRED_KEYS:
                self.assertIn(key, g, f"{path.name} missing required key '{key}'")

    def test_id_is_int(self):
        for path, g in self.entries:
            self.assertIsInstance(g["id"], int, f"{path.name}: id is not int")
            self.assertGreater(g["id"], 0, f"{path.name}: id must be positive")

    def test_title_jp_non_empty(self):
        for path, g in self.entries:
            self.assertIsInstance(g["title_jp"], str, f"{path.name}: title_jp not str")
            self.assertNotEqual(g["title_jp"].strip(), "",
                                f"{path.name}: title_jp is empty")

    # --- filename / file-field consistency -------------------------------
    def test_file_field_matches_filename(self):
        for path, g in self.entries:
            expected = f"data/games/{path.name}"
            self.assertEqual(g.get("file"), expected,
                             f"{path.name}: file field {g.get('file')!r} != {expected!r}")

    def test_file_field_id_padding(self):
        for path, g in self.entries:
            match = FILENAME_RE.match(path.name)
            self.assertIsNotNone(match, f"Filename does not match grammar: {path.name}")
            self.assertEqual(match.group("id"), f"{g['id']:03d}",
                             f"{path.name}: padded id prefix mismatch (id={g['id']})")

    def test_file_field_slug_matches_slug(self):
        for path, g in self.entries:
            match = FILENAME_RE.match(path.name)
            self.assertIsNotNone(match, f"Filename does not match grammar: {path.name}")
            self.assertEqual(match.group("slug"), g["slug"],
                             f"{path.name}: filename slug != game.slug ({g['slug']!r})")

    # --- optional field shape --------------------------------------------
    def test_year_is_int_or_missing(self):
        for path, g in self.entries:
            if "year" in g:
                y = g["year"]
                self.assertIsInstance(y, int, f"{path.name}: year not int: {y!r}")
                self.assertTrue(1970 <= y <= 2030,
                                f"{path.name}: year out of range: {y}")

    def test_platform_is_list_when_present(self):
        for path, g in self.entries:
            if "platform" in g:
                self.assertIsInstance(g["platform"], list,
                                     f"{path.name}: platform not list")
                for item in g["platform"]:
                    self.assertIsInstance(item, str,
                                         f"{path.name}: platform entry not str: {item!r}")
                    self.assertNotEqual(item.strip(), "",
                                        f"{path.name}: empty platform string")

    def test_platform_has_no_storefront_or_slashed_values(self):
        """Facet UI does strict-string matching, so a storefront tag like
        ``Steam`` or a compound like ``PS3/4`` becomes its own checkbox and
        leaks tagged games out of the corresponding canonical platform
        filter. ``scripts/normalize_platforms.py`` collapses these into the
        canonical set; this test guards against regression.

        The forbidden set is intentionally narrow: only tokens we already
        normalize. Ambiguous legacy values like ``Multi`` / ``consoles`` /
        bare ``Xbox`` need per-game enrichment and remain allowed for now.
        """
        FORBIDDEN_PLATFORM_VALUES = {
            "Steam", "GOG", "Epic", "Epic Games Store", "itch.io", "Origin",
            "PC Game Pass", "Game Pass", "Battle.net (PC)", "Windows",
            "PC (itch.io)", "PC (DMM GAMES)", "PC (Windows)",
            "macOS", "Vita",
            "Xbox Series", "Xbox Series X|S", "XSX",
            "Switch (cloud)", "Switch Cloud", "Switch (primary)", "Cloud",
            "ブラウザ", "AC",
            "PS3/4", "PS4/PS5", "Xbox 360/One", "Xbox 360/One origin",
            "iOS/Android", "PS VR/2",
            "Mobile",  # superseded by iOS+Android
            "DLC",     # not a platform; was a stray on ID 77
        }
        offenders = []
        for path, g in self.entries:
            for item in g.get("platform") or []:
                if item in FORBIDDEN_PLATFORM_VALUES:
                    offenders.append((path.name, item))
        self.assertEqual(
            offenders, [],
            "Forbidden platform tokens still present (run "
            "scripts/normalize_platforms.py): " + repr(offenders[:10]),
        )

    def test_secondary_is_present_and_list(self):
        """``secondary`` is part of the canonical schema in CLAUDE.md and is
        expected on every per-game file (use ``[]`` when there is no
        secondary motive). Missing keys cause downstream drift between the
        per-file JSON and the index.json/games.json (which backfill ``[]``).
        """
        for path, g in self.entries:
            self.assertIn("secondary", g,
                          f"{path.name}: secondary key missing")
            sec = g["secondary"]
            self.assertIsInstance(sec, list, f"{path.name}: secondary not list")
            for item in sec:
                self.assertIn(item, VALID_PRIMARY,
                              f"{path.name}: invalid secondary value {item!r}")

    def test_secondary_excludes_primary(self):
        for path, g in self.entries:
            sec = g.get("secondary", []) or []
            self.assertNotIn(g["primary"], sec,
                             f"{path.name}: primary {g['primary']!r} listed in secondary")

    # --- social_axis ------------------------------------------------------
    def test_social_axis_values_valid(self):
        for path, g in self.entries:
            axis = g.get("social_axis")
            if axis is None or axis == "":
                continue
            self.assertIn(axis, SOCIAL_AXES_SET,
                          f"{path.name}: unknown social_axis {axis!r}")

    def test_social_axis_only_for_EXP(self):
        """social_axis should only appear on EXP primaries, except for a
        documented allowlist of REW mobile titles with strong social loops.
        Updating the data (adding/removing social_axis on a non-EXP game)
        requires updating ``SOCIAL_AXIS_NON_EXP_ALLOWLIST`` above.
        """
        offenders = []
        for path, g in self.entries:
            if not g.get("social_axis"):
                continue
            if g["primary"] == "EXP":
                continue
            key = (g["id"], g["slug"])
            if key not in SOCIAL_AXIS_NON_EXP_ALLOWLIST:
                offenders.append((path.name, g["primary"], g["social_axis"]))
        self.assertEqual(offenders, [],
                         "Non-EXP games with social_axis outside allowlist: "
                         f"{offenders}")

    # --- concept / target -------------------------------------------------
    def test_concept_when_present_non_empty(self):
        for path, g in self.entries:
            if "concept" in g:
                self.assertIsInstance(g["concept"], str,
                                     f"{path.name}: concept not str")
                self.assertNotEqual(g["concept"].strip(), "",
                                    f"{path.name}: concept is empty")

    def test_target_when_present_non_empty(self):
        for path, g in self.entries:
            if "target" in g:
                self.assertIsInstance(g["target"], str,
                                     f"{path.name}: target not str")
                self.assertNotEqual(g["target"].strip(), "",
                                    f"{path.name}: target is empty")

    # --- tags / indie -----------------------------------------------------
    ALLOWED_TAGS = {"indie"}

    def test_tags_is_list_when_present(self):
        for path, g in self.entries:
            if "tags" in g:
                self.assertIsInstance(g["tags"], list,
                                      f"{path.name}: tags not list")
                for t in g["tags"]:
                    self.assertIsInstance(t, str,
                                          f"{path.name}: tag not str ({t!r})")

    def test_tags_only_known_values(self):
        for path, g in self.entries:
            for t in g.get("tags", []):
                self.assertIn(t, self.ALLOWED_TAGS,
                              f"{path.name}: unknown tag {t!r} "
                              f"(allowed: {sorted(self.ALLOWED_TAGS)})")

    def test_indie_count_within_expected_range(self):
        """インディーズ判定件数が想定レンジ内であることを担保。
        scripts/tag_indie.py の denylist/allowlist が壊れたとき検知する。
        2026-06-26 の 1000 件拡張で indie 580 / non-indie 1445 (総数 2025) になった
        ので、想定レンジを 500-700 に広げる。
        """
        indie_n = sum(1 for _, g in self.entries
                      if "indie" in (g.get("tags") or []))
        self.assertGreaterEqual(indie_n, 500,
                                f"indie 認定が少なすぎる: {indie_n}本（想定 500-700）")
        self.assertLessEqual(indie_n, 700,
                             f"indie 認定が多すぎる: {indie_n}本（想定 500-700）")

    def test_indie_excludes_known_majors(self):
        """大手 publisher 配下のタイトルが誤って indie タグ付けされていないか。"""
        forbidden_publishers = {
            "任天堂", "Nintendo",
            "Square Enix", "スクエニ", "スクウェア・エニックス",
            "Capcom", "カプコン",
            "Sega", "SEGA",
            "Atlus", "アトラス",
            "Bandai Namco", "バンダイナムコエンターテインメント", "バンナム",
            "Konami", "KONAMI",
            "Ubisoft", "EA", "Electronic Arts",
            "Activision", "Blizzard Entertainment", "Rockstar Games", "2K Games",
            "Bethesda Softworks", "Xbox Game Studios", "SIE",
            "Cygames", "Supercell", "Riot Games", "Epic Games",
            "Pearl Abyss", "Devsisters", "Lilith Games", "Moonton",
            "NetEase Games", "HoYoverse",
        }
        violations = []
        for path, g in self.entries:
            if "indie" in (g.get("tags") or []):
                if g.get("publisher") in forbidden_publishers:
                    violations.append(f"{path.name} (pub={g['publisher']})")
        self.assertEqual(violations, [],
                         f"大手 publisher なのに indie タグ付き: {violations}")


class AnalysesTests(unittest.TestCase):
    """Cross-checks between data/games/ and data/analyses/."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = _load_game_files()

    def test_analysis_md_exists_for_id_le_1025(self):
        """ID <= 1025 の games に対応する分析 Markdown が存在することを担保。
        2026-06-25 の一括生成で 1025/1025 揃ったので欠落 = 退行とみなす。
        2026-06-26 以降に追加した 1026..2100 範囲はまだ分析 md 未生成のため
        ここでは対象外（別フェーズで一括生成予定）。
        """
        missing = []
        for path, g in self.entries:
            if g['id'] > 1025:
                continue
            stem = f"{g['id']:03d}-{g['slug']}"
            md_path = ANALYSES_DIR / f"{stem}.md"
            if not md_path.exists():
                missing.append(stem)
        self.assertEqual(missing, [],
                         f"分析 Markdown が欠けている (ID<=1025): {missing}")

    def test_analyses_filename_matches_a_game(self):
        valid_stems = {f"{g['id']:03d}-{g['slug']}" for _, g in self.entries}
        orphans = []
        for md in sorted(ANALYSES_DIR.glob("*.md")):
            if md.stem not in valid_stems:
                orphans.append(md.name)
        self.assertEqual(orphans, [],
                         f"Orphan analyses with no matching game JSON: {orphans}")


class AggregateTests(unittest.TestCase):
    """Cross-checks against data/games.json (the aggregate)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = _load_game_files()
        cls.aggregate = _load_json(DATA_DIR / "games.json")

    def test_aggregate_matches_per_file(self):
        per_file_by_id = {g["id"]: g for _, g in self.entries}
        for agg_game in self.aggregate["games"]:
            gid = agg_game["id"]
            self.assertIn(gid, per_file_by_id,
                          f"games.json has id {gid} with no per-file source")
            pf = dict(per_file_by_id[gid])
            agg_copy = dict(agg_game)
            # The 'file' key is a derived path; comparing strict equality
            # other than that gives a strong cross-check.
            pf.pop("file", None)
            agg_copy.pop("file", None)
            self.assertEqual(pf, agg_copy,
                             f"games.json id={gid} drift vs per-file JSON")

        # And no extra ids on either side.
        agg_ids = {g["id"] for g in self.aggregate["games"]}
        pf_ids = set(per_file_by_id)
        self.assertEqual(agg_ids, pf_ids,
                         f"id-set mismatch agg vs per-file: "
                         f"only-in-agg={agg_ids - pf_ids}, "
                         f"only-in-files={pf_ids - agg_ids}")

    def test_aggregate_total_matches_meta(self):
        self.assertEqual(self.aggregate["meta"]["total_titles"],
                         len(self.aggregate["games"]),
                         "games.json meta.total_titles != len(games)")

    def test_aggregate_primary_breakdown_matches_real_counts(self):
        counts = Counter(g["primary"] for g in self.aggregate["games"])
        meta_counts = Counter(self.aggregate["meta"]["primary_breakdown"])
        self.assertEqual(meta_counts, counts,
                         f"games.json meta.primary_breakdown {dict(meta_counts)} "
                         f"!= real {dict(counts)}")


class IndexTests(unittest.TestCase):
    """Cross-checks against data/index.json."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = _load_game_files()
        cls.index = _load_json(DATA_DIR / "index.json")
        cls.aggregate = _load_json(DATA_DIR / "games.json")

    def test_index_matches_per_file(self):
        pf_by_id = {g["id"]: g for _, g in self.entries}
        for row in self.index["games"]:
            gid = row["id"]
            self.assertIn(gid, pf_by_id,
                          f"index.json has id {gid} with no per-file source")
            src = pf_by_id[gid]
            for key in ("id", "title_jp", "primary"):
                self.assertEqual(row.get(key), src.get(key),
                                 f"index.json id={gid}: {key} drift "
                                 f"({row.get(key)!r} vs {src.get(key)!r})")

        idx_ids = {r["id"] for r in self.index["games"]}
        pf_ids = set(pf_by_id)
        self.assertEqual(idx_ids, pf_ids,
                         f"id-set mismatch index vs per-file: "
                         f"only-in-index={idx_ids - pf_ids}, "
                         f"only-in-files={pf_ids - idx_ids}")

    def test_index_file_paths_resolve(self):
        for row in self.index["games"]:
            self.assertIn("file", row, f"index.json row missing 'file': {row}")
            abs_path = REPO_ROOT / row["file"]
            self.assertTrue(abs_path.exists(),
                            f"index.json file path does not exist: {row['file']}")

    def test_index_total_equals_aggregate_total(self):
        self.assertEqual(self.index["total"],
                         self.aggregate["meta"]["total_titles"],
                         "index.json.total != games.json.meta.total_titles")

    def test_index_rows_carry_tags(self):
        """site/facet.html のタグ絞り込みが動くよう、各行に tags が出ていること。"""
        pf_by_id = {g["id"]: g for _, g in self.entries}
        for row in self.index["games"]:
            self.assertIn("tags", row,
                          f"index.json row id={row['id']} missing 'tags' field")
            self.assertIsInstance(row["tags"], list,
                                  f"index.json id={row['id']} tags is not list")
            self.assertEqual(row["tags"], pf_by_id[row["id"]].get("tags", []),
                             f"index.json id={row['id']} tags drift vs per-file")


class MetaTests(unittest.TestCase):
    """Sanity checks on data/meta.json."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.meta = _load_json(DATA_DIR / "meta.json")

    def test_meta_json_categories_keys(self):
        self.assertEqual(set(self.meta["categories"].keys()), VALID_PRIMARY,
                         f"meta.categories keys: {set(self.meta['categories'].keys())}")

    def test_meta_json_social_axes_match_constant(self):
        self.assertEqual(self.meta["social_axis_for_EXP"], SOCIAL_AXES,
                         "meta.social_axis_for_EXP drifted from SOCIAL_AXES constant")

    def test_meta_sources_list_nonempty(self):
        sources = self.meta.get("sources")
        self.assertIsInstance(sources, list, "meta.sources is not a list")
        self.assertGreater(len(sources), 0, "meta.sources is empty")
        for url in sources:
            self.assertIsInstance(url, str, f"meta.sources entry not str: {url!r}")
            self.assertTrue(url.startswith("http"),
                            f"meta.sources entry not URL-like: {url!r}")

    def test_meta_json_has_no_derived_counts(self):
        """``total_titles`` and ``primary_breakdown`` are derived quantities
        owned by ``data/games.json`` (regenerated by build_aggregate.py).
        Keeping them in ``data/meta.json`` lets them go stale — they sat at
        200 for months while the catalog grew to 1025. The on-disk meta.json
        should be the immutable category/source definitions only.
        """
        self.assertNotIn("total_titles", self.meta,
                         "data/meta.json must not carry derived total_titles")
        self.assertNotIn("primary_breakdown", self.meta,
                         "data/meta.json must not carry derived primary_breakdown")


class MarkdownConsistencyTests(unittest.TestCase):
    """Best-effort Markdown drift checks.

    These are intentionally loose because Markdown formatting can vary; they
    only assert globally observable invariants (row counts, presence of a
    99-mention) rather than parsing the documents.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog_md = (REPO_ROOT / "games-catalog.md").read_text(encoding="utf-8")
        cls.readme_md = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        cls.entries = _load_game_files()

    def test_games_catalog_md_count_consistent(self):
        """Catalog は ID <= 1025 範囲を全て持ち、orphan / 重複が無いこと。
        2026-06-26 以降に追加した 1026..2100 は別フェーズで catalog 行を追記する
        予定のため、ここでは「ID<=1025 範囲はカバーされている」と「catalog 上の
        ID は全て data に存在する」の 2 点だけを担保する。
        """
        ids: list[int] = []
        for line in self.catalog_md.splitlines():
            m = re.match(r"^\|\s*(\d+)\s*\|", line)
            if m:
                ids.append(int(m.group(1)))
        distinct_ids = set(ids)
        # ID <= 1025 のレガシー範囲は完全カバー
        legacy_range = set(range(1, 1026))
        missing_legacy = legacy_range - distinct_ids
        self.assertEqual(missing_legacy, set(),
                         f"games-catalog.md に ID<=1025 で欠落: {sorted(missing_legacy)}")
        # catalog 上の ID は全て data/games/ に存在する
        valid_ids = {g['id'] for _, g in self.entries}
        orphan = distinct_ids - valid_ids
        self.assertEqual(orphan, set(),
                         f"games-catalog.md に orphan ID: {sorted(orphan)}")
        # 重複行なし
        dups = [i for i, n in Counter(ids).items() if n > 1]
        self.assertEqual(dups, [],
                         f"games-catalog.md has duplicate rows for IDs: {dups}")

    def test_readme_count_consistent(self):
        # Expect README §2 to mention the canonical 1025-title figure.
        self.assertRegex(self.readme_md, r"1025\s*本",
                         "README.md should reference '1025本' somewhere (集計サマリ)")


if __name__ == "__main__":  # pragma: no cover - manual runner
    unittest.main()
