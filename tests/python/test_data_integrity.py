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

# Filename grammar: "{id:03d}-{slug}.json"
FILENAME_RE = re.compile(r"^(?P<id>\d{3})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.json$")

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
# Laser Eyes, etc.). The ID range 1..917 is now contiguous.
EXPECTED_TOTAL = 917
EXPECTED_PRIMARY_COUNTS = {"EXP": 689, "NAR": 125, "REW": 103}
EXPECTED_MISSING_IDS: set = set()
EXPECTED_ID_RANGE = set(range(1, EXPECTED_TOTAL + 1))  # 1..917 inclusive

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
}

# Current set of authored deep-analysis Markdown files. Most games do not
# have one yet; CLAUDE.md notes "未作成なら『未分析』表示". This allowlist
# documents the current state so the test still catches the *inverse* drift
# (an analyses/*.md whose (id, slug) does not correspond to a real game).
EXPECTED_ANALYSIS_STEMS: set = {
    "001-animal-crossing-new-horizons",
    "006-splatoon-3",
    "020-monster-strike",
    "066-persona-5-royal",
    "076-elden-ring",
}


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

    def test_secondary_is_list_when_present(self):
        for path, g in self.entries:
            if "secondary" in g:
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


class AnalysesTests(unittest.TestCase):
    """Cross-checks between data/games/ and data/analyses/."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = _load_game_files()

    def test_analysis_md_exists_or_documented_missing(self):
        """For each game, either the analysis MD exists OR its absence is
        explicitly allowed (CLAUDE.md notes most games are intentionally
        unanalysed). The allowlist is the *inverse*: every game whose
        analysis exists must be in EXPECTED_ANALYSIS_STEMS.
        """
        present_actual = set()
        for path, g in self.entries:
            stem = f"{g['id']:03d}-{g['slug']}"
            md_path = ANALYSES_DIR / f"{stem}.md"
            if md_path.exists():
                present_actual.add(stem)
        self.assertEqual(present_actual, EXPECTED_ANALYSIS_STEMS,
                         "Authored analyses set drifted. "
                         f"Found: {sorted(present_actual)}; "
                         f"expected: {sorted(EXPECTED_ANALYSIS_STEMS)}")

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

    def test_games_catalog_md_count_consistent(self):
        """The catalog has two sections: the basic 100-row table and the
        2020+ extension table. ID #56 appears in both because the 2020+
        extension explicitly lists every new entry (including the one that
        filled #56). Test by distinct ID count instead of by row count.
        """
        ids: list[int] = []
        for line in self.catalog_md.splitlines():
            m = re.match(r"^\|\s*(\d+)\s*\|", line)
            if m:
                ids.append(int(m.group(1)))
        distinct_ids = set(ids)
        self.assertEqual(len(distinct_ids), EXPECTED_TOTAL,
                         f"games-catalog.md mentions {len(distinct_ids)} distinct IDs; "
                         f"expected {EXPECTED_TOTAL}")
        # IDs should cover the contiguous 1..EXPECTED_TOTAL range.
        self.assertEqual(distinct_ids, EXPECTED_ID_RANGE,
                         f"games-catalog.md ID range drift: missing "
                         f"{sorted(EXPECTED_ID_RANGE - distinct_ids)}, "
                         f"extra {sorted(distinct_ids - EXPECTED_ID_RANGE)}")

    def test_readme_count_consistent(self):
        # Expect README §2 to mention the canonical 917-title figure.
        self.assertRegex(self.readme_md, r"917\s*本",
                         "README.md should reference '917本' somewhere (集計サマリ)")


if __name__ == "__main__":  # pragma: no cover - manual runner
    unittest.main()
