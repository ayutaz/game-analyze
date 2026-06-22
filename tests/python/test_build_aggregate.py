"""Unit tests for scripts/build_aggregate.py.

Every test operates against a tempfile.TemporaryDirectory copy of the real
data tree (or a small fixture tree) so the real ``data/games.json`` and
``data/index.json`` are never written by the test suite.
"""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

# Ensure repo root + scripts dir are on sys.path (mirrors conftest.py logic so
# the module is importable when unittest discovers this file directly).
_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_REPO_ROOT), str(_SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import build_aggregate  # noqa: E402  (sys.path hacked above)

REAL_GAMES_DIR = _REPO_ROOT / "data" / "games"
REAL_META_PATH = _REPO_ROOT / "data" / "meta.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_repo_copy(tmpdir: Path) -> Path:
    """Copy the real data tree into ``tmpdir/data`` and return tmpdir."""
    dst_data = tmpdir / "data"
    (dst_data / "games").mkdir(parents=True, exist_ok=True)
    shutil.copy2(REAL_META_PATH, dst_data / "meta.json")
    for p in REAL_GAMES_DIR.glob("*.json"):
        shutil.copy2(p, dst_data / "games" / p.name)
    return tmpdir


def _make_minimal_fixture(tmpdir: Path, games: list[dict], meta: dict | None = None) -> Path:
    """Build a fixture repo tree with only the supplied games + meta."""
    data = tmpdir / "data"
    (data / "games").mkdir(parents=True, exist_ok=True)
    if meta is None:
        meta = {
            "generated": "2026-06-22",
            "categories": {"EXP": "体験型", "NAR": "物語型", "REW": "報酬型"},
            "social_axis_for_EXP": {},
            "sources": [],
        }
    (data / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for g in games:
        slug = g.get("slug", "test")
        fname = f"{g['id']:03d}-{slug}.json"
        (data / "games" / fname).write_text(
            json.dumps(g, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return tmpdir


def _silent_main(repo_root: Path) -> str:
    """Run build_aggregate.main(repo_root) capturing stdout."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        build_aggregate.main(repo_root)
    return buf.getvalue()


class BuildAggregateRealDataTests(unittest.TestCase):
    """Tests that exercise build_aggregate against a copy of the real tree."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp_holder = tempfile.TemporaryDirectory()
        cls.tmpdir = Path(cls._tmp_holder.name)
        _make_repo_copy(cls.tmpdir)
        _silent_main(cls.tmpdir)
        cls.agg_path = cls.tmpdir / "data" / "games.json"
        cls.index_path = cls.tmpdir / "data" / "index.json"
        with cls.agg_path.open(encoding="utf-8") as f:
            cls.agg = json.load(f)
        with cls.index_path.open(encoding="utf-8") as f:
            cls.index = json.load(f)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp_holder.cleanup()

    def test_runs_without_error_on_real_data(self) -> None:
        # Re-run inside a separate temp tree so we exercise the main()
        # entry point and confirm it does not raise.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            _silent_main(tmp)  # would raise on failure

    def test_writes_both_outputs(self) -> None:
        self.assertTrue(self.agg_path.exists(), "data/games.json not written")
        self.assertTrue(self.index_path.exists(), "data/index.json not written")

    def test_aggregate_top_level_shape(self) -> None:
        self.assertEqual(set(self.agg.keys()), {"meta", "games"})

    def test_aggregate_meta_has_total_titles(self) -> None:
        self.assertEqual(self.agg["meta"]["total_titles"], 200)
        self.assertEqual(self.agg["meta"]["total_titles"], len(self.agg["games"]))

    def test_aggregate_meta_has_primary_breakdown(self) -> None:
        self.assertEqual(
            self.agg["meta"]["primary_breakdown"],
            {"EXP": 105, "NAR": 48, "REW": 47},
        )

    def test_aggregate_meta_preserves_original_keys(self) -> None:
        with REAL_META_PATH.open(encoding="utf-8") as f:
            original_meta = json.load(f)
        # All original keys must survive into the aggregate's meta.
        for key in ("generated", "categories", "social_axis_for_EXP", "sources"):
            self.assertIn(key, original_meta, f"sanity: meta.json missing {key}")
            self.assertIn(key, self.agg["meta"], f"aggregate dropped {key}")

    def test_aggregate_games_sorted_by_id(self) -> None:
        ids = [g["id"] for g in self.agg["games"]]
        self.assertEqual(ids, sorted(ids), "games not sorted by id")
        self.assertEqual(len(ids), len(set(ids)), "duplicate ids in aggregate")

    def test_aggregate_games_strip_file_field(self) -> None:
        for g in self.agg["games"]:
            self.assertNotIn("file", g, f"game id={g.get('id')} still has 'file' key")

    def test_aggregate_games_equals_sum_of_individual_files(self) -> None:
        agg_by_id = {g["id"]: g for g in self.agg["games"]}
        for src in sorted(REAL_GAMES_DIR.glob("*.json")):
            with src.open(encoding="utf-8") as f:
                src_game = json.load(f)
            expected = {k: v for k, v in src_game.items() if k != "file"}
            self.assertIn(src_game["id"], agg_by_id)
            self.assertEqual(agg_by_id[src_game["id"]], expected)

    def test_index_top_level_shape(self) -> None:
        self.assertEqual(
            set(self.index.keys()),
            {"generated_from", "total", "primary_breakdown", "games"},
        )

    def test_index_total_matches_games_length(self) -> None:
        self.assertEqual(self.index["total"], len(self.index["games"]))
        self.assertEqual(self.index["total"], 200)

    def test_index_primary_breakdown_matches_aggregate(self) -> None:
        self.assertEqual(
            self.index["primary_breakdown"],
            self.agg["meta"]["primary_breakdown"],
        )

    def test_index_row_keys_minimum(self) -> None:
        expected_keys = {
            "id",
            "title_jp",
            "title_en",
            "year",
            "primary",
            "secondary",
            "social_axis",
            "platform",
            "file",
        }
        for row in self.index["games"]:
            self.assertEqual(set(row.keys()), expected_keys)

    def test_index_row_file_path_present(self) -> None:
        for row in self.index["games"]:
            f = row["file"]
            self.assertIsInstance(f, str)
            self.assertTrue(f.endswith(".json"), f"file does not end with .json: {f}")
            self.assertTrue(
                f.startswith("data/games/"),
                f"file does not start with data/games/: {f}",
            )

    def test_index_row_secondary_is_list(self) -> None:
        for row in self.index["games"]:
            self.assertIsInstance(row["secondary"], list, f"id={row['id']}")

    def test_index_row_platform_is_list(self) -> None:
        for row in self.index["games"]:
            self.assertIsInstance(row["platform"], list, f"id={row['id']}")

    def test_idempotency_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            _silent_main(tmp)
            agg1 = (tmp / "data" / "games.json").read_bytes()
            index1 = (tmp / "data" / "index.json").read_bytes()
            _silent_main(tmp)
            agg2 = (tmp / "data" / "games.json").read_bytes()
            index2 = (tmp / "data" / "index.json").read_bytes()
            self.assertEqual(agg1, agg2, "games.json bytes changed on second run")
            self.assertEqual(index1, index2, "index.json bytes changed on second run")

    def test_idempotency_no_source_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            games_dir = tmp / "data" / "games"
            before = {p.name: _sha256(p) for p in games_dir.glob("*.json")}
            _silent_main(tmp)
            after = {p.name: _sha256(p) for p in games_dir.glob("*.json")}
            self.assertEqual(before, after, "source game files were mutated")

    def test_output_files_end_with_newline(self) -> None:
        self.assertTrue(self.agg_path.read_bytes().endswith(b"\n"))
        self.assertTrue(self.index_path.read_bytes().endswith(b"\n"))

    def test_output_files_utf8_japanese_preserved(self) -> None:
        agg_text = self.agg_path.read_text(encoding="utf-8")
        index_text = self.index_path.read_text(encoding="utf-8")
        # 「あつまれ どうぶつの森」 is id=1 — its Japanese characters must survive.
        self.assertIn("あつまれ", agg_text)
        self.assertIn("あつまれ", index_text)
        # The unicode escape would be あ... — ensure we did NOT escape.
        self.assertNotIn("\\u3042", agg_text)

    def test_output_files_indent_two_spaces(self) -> None:
        # First line is "{", second line should be 2-space indented "meta".
        for p in (self.agg_path, self.index_path):
            lines = p.read_text(encoding="utf-8").splitlines()
            # Find first indented line.
            indented = [ln for ln in lines if ln.startswith(" ")]
            self.assertTrue(indented, f"{p.name} has no indented lines")
            self.assertTrue(
                indented[0].startswith("  ") and not indented[0].startswith("   "),
                f"{p.name} indent is not 2-space: {indented[0]!r}",
            )

    def test_paths_are_relative_to_script_location(self) -> None:
        # Constants must be absolute Paths anchored under the real repo.
        self.assertTrue(build_aggregate.ROOT.is_absolute())
        self.assertEqual(
            build_aggregate.GAMES_DIR,
            build_aggregate.ROOT / "data" / "games",
        )
        self.assertEqual(
            build_aggregate.META_PATH,
            build_aggregate.ROOT / "data" / "meta.json",
        )
        self.assertEqual(
            build_aggregate.AGG_PATH,
            build_aggregate.ROOT / "data" / "games.json",
        )
        self.assertEqual(
            build_aggregate.INDEX_PATH,
            build_aggregate.ROOT / "data" / "index.json",
        )


class BuildAggregateFixtureTests(unittest.TestCase):
    """Tests using small synthetic fixtures."""

    def test_handles_minimal_two_file_fixture(self) -> None:
        games = [
            {
                "id": 1,
                "title_jp": "テスト1",
                "title_en": "Test 1",
                "primary": "EXP",
                "secondary": [],
                "platform": ["PC"],
                "slug": "test-1",
                "file": "data/games/001-test-1.json",
            },
            {
                "id": 2,
                "title_jp": "テスト2",
                "title_en": "Test 2",
                "primary": "NAR",
                "secondary": ["REW"],
                "platform": ["PS5"],
                "slug": "test-2",
                "file": "data/games/002-test-2.json",
            },
        ]
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_minimal_fixture(tmp, games)
            _silent_main(tmp)
            with (tmp / "data" / "games.json").open(encoding="utf-8") as f:
                agg = json.load(f)
            self.assertEqual(len(agg["games"]), 2)
            self.assertEqual(
                agg["meta"]["primary_breakdown"],
                {"EXP": 1, "NAR": 1},
            )
            self.assertEqual(agg["meta"]["total_titles"], 2)

    def test_empty_games_dir_produces_zero_total(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_minimal_fixture(tmp, [])
            _silent_main(tmp)
            with (tmp / "data" / "games.json").open(encoding="utf-8") as f:
                agg = json.load(f)
            with (tmp / "data" / "index.json").open(encoding="utf-8") as f:
                idx = json.load(f)
            self.assertEqual(agg["meta"]["total_titles"], 0)
            self.assertEqual(agg["games"], [])
            self.assertEqual(agg["meta"]["primary_breakdown"], {})
            self.assertEqual(idx["total"], 0)
            self.assertEqual(idx["games"], [])

    def test_missing_meta_json_raises(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            (tmp / "data" / "games").mkdir(parents=True)
            # No meta.json created.
            with self.assertRaises(FileNotFoundError):
                _silent_main(tmp)

    def test_malformed_game_json_raises(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_minimal_fixture(tmp, [])
            bad = tmp / "data" / "games" / "001-bad.json"
            bad.write_text("{ this is not valid json", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                _silent_main(tmp)

    def test_game_missing_required_id_raises(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_minimal_fixture(tmp, [])
            # A game JSON with no 'id' must cause KeyError when sorting.
            bad = tmp / "data" / "games" / "001-no-id.json"
            bad.write_text(
                json.dumps(
                    {"title_jp": "noid", "primary": "EXP", "slug": "noid"},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with self.assertRaises(KeyError):
                _silent_main(tmp)

    def test_game_missing_primary_raises(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_minimal_fixture(tmp, [])
            bad = tmp / "data" / "games" / "001-no-primary.json"
            bad.write_text(
                json.dumps(
                    {"id": 1, "title_jp": "noprim", "slug": "noprim"},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with self.assertRaises(KeyError):
                _silent_main(tmp)

    def test_game_with_optional_fields_omitted_passes(self) -> None:
        # Required only: id, title_jp, primary. Everything else omitted.
        minimal_game = {
            "id": 42,
            "title_jp": "最小ゲーム",
            "primary": "EXP",
            "slug": "minimal",
        }
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_minimal_fixture(tmp, [minimal_game])
            _silent_main(tmp)
            with (tmp / "data" / "index.json").open(encoding="utf-8") as f:
                idx = json.load(f)
            self.assertEqual(len(idx["games"]), 1)
            row = idx["games"][0]
            self.assertEqual(row["id"], 42)
            self.assertEqual(row["title_jp"], "最小ゲーム")
            self.assertIsNone(row["title_en"])
            self.assertIsNone(row["year"])
            self.assertEqual(row["primary"], "EXP")
            self.assertEqual(row["secondary"], [])
            self.assertIsNone(row["social_axis"])
            self.assertEqual(row["platform"], [])
            self.assertTrue(row["file"].startswith("data/games/"))

    def test_index_file_field_falls_back_when_missing(self) -> None:
        # Two games: first omits 'file' (must fall back), second supplies its own.
        games = [
            {
                "id": 1,
                "title_jp": "noFile",
                "primary": "EXP",
                "slug": "no-file",
                # Intentionally no 'file' key.
            },
            {
                "id": 2,
                "title_jp": "withFile",
                "primary": "NAR",
                "slug": "with-file",
                "file": "data/games/002-with-file.json",
            },
        ]
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_minimal_fixture(tmp, games)
            _silent_main(tmp)
            with (tmp / "data" / "index.json").open(encoding="utf-8") as f:
                idx = json.load(f)
            by_id = {row["id"]: row for row in idx["games"]}
            # Row 1 must derive its 'file' from the basename.
            self.assertEqual(by_id[1]["file"], "data/games/001-no-file.json")
            # Row 2 keeps the explicit value.
            self.assertEqual(by_id[2]["file"], "data/games/002-with-file.json")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
