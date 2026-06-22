"""Unit tests for scripts/patch_games.py.

All tests operate against a tempfile.TemporaryDirectory copy of the real
data tree so the real ``data/games/*.json`` files are never modified.
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

# Ensure repo root + scripts dir are importable.
_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_REPO_ROOT), str(_SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import patch_games  # noqa: E402

REAL_GAMES_DIR = _REPO_ROOT / "data" / "games"
REAL_META_PATH = _REPO_ROOT / "data" / "meta.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_repo_copy(tmpdir: Path) -> Path:
    """Copy the real data tree into ``tmpdir/data``."""
    dst = tmpdir / "data" / "games"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REAL_META_PATH, tmpdir / "data" / "meta.json")
    for p in REAL_GAMES_DIR.glob("*.json"):
        shutil.copy2(p, dst / p.name)
    return tmpdir


def _silent_main(repo_root: Path) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        patch_games.main(repo_root)
    return buf.getvalue()


class PatchesDictShapeTests(unittest.TestCase):
    """Static checks on the PATCHES literal — no file I/O."""

    def test_patches_dict_keys_are_ints(self) -> None:
        for k in patch_games.PATCHES:
            self.assertIsInstance(k, int, f"non-int key in PATCHES: {k!r}")
            self.assertGreater(k, 0, f"non-positive id in PATCHES: {k}")

    def test_patches_dict_keys_unique(self) -> None:
        keys = list(patch_games.PATCHES.keys())
        self.assertEqual(len(keys), len(set(keys)), "duplicate ids in PATCHES")

    def test_patches_dict_covers_ids_1_to_100_except_56(self) -> None:
        # ID 56 is the documented gap (Project Sekai dedup).
        expected = set(range(1, 101)) - {56}
        self.assertEqual(
            set(patch_games.PATCHES),
            expected,
            "PATCHES key set drifted from documented 1..100 minus {56}",
        )

    def test_patches_values_have_concept_and_target(self) -> None:
        for k, v in patch_games.PATCHES.items():
            self.assertIn("concept", v, f"PATCHES[{k}] missing 'concept'")
            self.assertIn("target", v, f"PATCHES[{k}] missing 'target'")
            self.assertIsInstance(v["concept"], str)
            self.assertIsInstance(v["target"], str)
            self.assertGreater(len(v["concept"].strip()), 0, f"PATCHES[{k}] concept empty")
            self.assertGreater(len(v["target"].strip()), 0, f"PATCHES[{k}] target empty")

    def test_patches_concept_under_reasonable_length(self) -> None:
        for k, v in patch_games.PATCHES.items():
            self.assertLess(
                len(v["concept"]), 400, f"PATCHES[{k}] concept >= 400 chars"
            )

    def test_patches_target_under_reasonable_length(self) -> None:
        for k, v in patch_games.PATCHES.items():
            self.assertLess(
                len(v["target"]), 400, f"PATCHES[{k}] target >= 400 chars"
            )


class PatchesAgainstRealTreeTests(unittest.TestCase):
    """Cross-checks between PATCHES and the real data/games/*.json tree.

    These tests read but never write the real tree.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.real_ids: set[int] = set()
        for p in REAL_GAMES_DIR.glob("*.json"):
            with p.open(encoding="utf-8") as f:
                cls.real_ids.add(json.load(f)["id"])

    def test_patches_referenced_ids_exist_in_data(self) -> None:
        # Every PATCHES id should correspond to an existing game file,
        # except for ID 56 which is the documented gap. PATCHES intentionally
        # includes 56 to be future-proof, but it should not error.
        documented_gaps = {56}
        for pid in patch_games.PATCHES:
            if pid in documented_gaps:
                continue
            self.assertIn(
                pid,
                self.real_ids,
                f"PATCHES references id={pid} but no data/games/*.json file has that id",
            )

    def test_data_ids_have_patches_or_documented_missing(self) -> None:
        # Allowlist of ids that are intentionally NOT in PATCHES.
        allowlist: set[int] = set()
        for rid in self.real_ids:
            if rid in allowlist:
                continue
            self.assertIn(
                rid,
                patch_games.PATCHES,
                f"data has id={rid} but PATCHES has no entry (add to allowlist if intentional)",
            )

    def test_dry_run_safety_on_real_tree(self) -> None:
        """Snapshot real-tree hashes, run main() against a tempdir copy,
        confirm real-tree hashes are unchanged."""
        before = {p.name: _sha256(p) for p in REAL_GAMES_DIR.glob("*.json")}
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            _silent_main(tmp)
        after = {p.name: _sha256(p) for p in REAL_GAMES_DIR.glob("*.json")}
        self.assertEqual(before, after, "real data/games/*.json hashes changed!")


class PatchMainBehaviorTests(unittest.TestCase):
    """Tests of patch_games.main() against a tempdir copy of the real tree."""

    def test_main_writes_concept_and_target_to_each_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            # Wipe concept/target from a couple of files so we have something to write.
            games_dir = tmp / "data" / "games"
            sample = sorted(games_dir.glob("*.json"))[:5]
            for p in sample:
                with p.open(encoding="utf-8") as f:
                    g = json.load(f)
                g.pop("concept", None)
                g.pop("target", None)
                with p.open("w", encoding="utf-8") as f:
                    json.dump(g, f, ensure_ascii=False, indent=2)
                    f.write("\n")

            _silent_main(tmp)

            # Now every file whose id is in PATCHES must match the PATCHES values.
            for p in sorted(games_dir.glob("*.json")):
                with p.open(encoding="utf-8") as f:
                    g = json.load(f)
                gid = g["id"]
                if gid not in patch_games.PATCHES:
                    continue
                expected = patch_games.PATCHES[gid]
                self.assertEqual(g["concept"], expected["concept"], f"id={gid}")
                self.assertEqual(g["target"], expected["target"], f"id={gid}")

    def test_main_does_not_touch_other_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            games_dir = tmp / "data" / "games"

            # Snapshot every file's non-concept/non-target fields before main().
            before: dict[str, dict] = {}
            for p in sorted(games_dir.glob("*.json")):
                with p.open(encoding="utf-8") as f:
                    g = json.load(f)
                before[p.name] = {k: v for k, v in g.items() if k not in ("concept", "target")}

            _silent_main(tmp)

            for p in sorted(games_dir.glob("*.json")):
                with p.open(encoding="utf-8") as f:
                    g = json.load(f)
                after_others = {k: v for k, v in g.items() if k not in ("concept", "target")}
                self.assertEqual(
                    before[p.name],
                    after_others,
                    f"non concept/target fields changed in {p.name}",
                )

    def test_main_skips_id_56_gracefully(self) -> None:
        # ID 56 has no file in the real tree; main() must not raise.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            out = _silent_main(tmp)
            self.assertIn("patched", out)
            # No file in the tree should have id 56 (sanity check).
            games_dir = tmp / "data" / "games"
            ids = []
            for p in games_dir.glob("*.json"):
                with p.open(encoding="utf-8") as f:
                    ids.append(json.load(f)["id"])
            self.assertNotIn(56, ids)

    def test_main_reports_missing_ids(self) -> None:
        # Build a fixture that has TWO games: one with an id that exists in
        # PATCHES and one with an id 9999 that does NOT.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            (tmp / "data" / "games").mkdir(parents=True)
            (tmp / "data" / "meta.json").write_text("{}\n", encoding="utf-8")
            # Patched game (id=1 is in PATCHES).
            (tmp / "data" / "games" / "001-known.json").write_text(
                json.dumps(
                    {
                        "id": 1,
                        "title_jp": "あつまれ どうぶつの森",
                        "primary": "EXP",
                        "slug": "known",
                    },
                    ensure_ascii=False,
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )
            # Unknown game (id=9999 NOT in PATCHES).
            (tmp / "data" / "games" / "999-unknown.json").write_text(
                json.dumps(
                    {
                        "id": 9999,
                        "title_jp": "未知",
                        "primary": "NAR",
                        "slug": "unknown",
                    },
                    ensure_ascii=False,
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )
            out = _silent_main(tmp)
            # Expect "patched 1 game files" since only id=1 was new.
            self.assertIn("patched 1 game files", out)
            self.assertIn("9999", out, "missing id should be reported in stdout")

    def test_idempotency_second_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            _silent_main(tmp)  # first run brings everything in sync
            out2 = _silent_main(tmp)  # second run is a no-op
            self.assertIn("patched 0 game files", out2)

    def test_idempotency_file_mtime_unchanged_on_second_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            games_dir = tmp / "data" / "games"
            _silent_main(tmp)  # first run brings things in sync
            mtimes_before = {p.name: p.stat().st_mtime_ns for p in games_dir.glob("*.json")}
            _silent_main(tmp)  # second run should be a no-op
            mtimes_after = {p.name: p.stat().st_mtime_ns for p in games_dir.glob("*.json")}
            for name, before_ns in mtimes_before.items():
                self.assertEqual(
                    before_ns,
                    mtimes_after[name],
                    f"{name} was rewritten on second run despite no diff",
                )

    def test_partial_patch_only_updates_diff(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            games_dir = tmp / "data" / "games"
            _silent_main(tmp)  # sync everything first

            # Pre-mutate ONE file's concept to a stale value.
            target_file = games_dir / "001-animal-crossing-new-horizons.json"
            with target_file.open(encoding="utf-8") as f:
                g = json.load(f)
            original_target_value = g["target"]
            g["concept"] = "STALE VALUE"
            with target_file.open("w", encoding="utf-8") as f:
                json.dump(g, f, ensure_ascii=False, indent=2)
                f.write("\n")

            # Snapshot mtimes after the manual edit.
            mtimes_before = {p.name: p.stat().st_mtime_ns for p in games_dir.glob("*.json")}

            out = _silent_main(tmp)
            self.assertIn("patched 1 game files", out)

            # Verify target file was updated.
            with target_file.open(encoding="utf-8") as f:
                g = json.load(f)
            self.assertEqual(g["concept"], patch_games.PATCHES[1]["concept"])
            # Other field on the same file should be untouched (we didn't change it).
            self.assertEqual(g["target"], original_target_value)

            # Verify other files were NOT rewritten.
            for p in games_dir.glob("*.json"):
                if p.name == target_file.name:
                    continue
                self.assertEqual(
                    p.stat().st_mtime_ns,
                    mtimes_before[p.name],
                    f"{p.name} was rewritten despite no diff",
                )

    def test_main_preserves_utf8_japanese(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            target_file = tmp / "data" / "games" / "001-animal-crossing-new-horizons.json"
            # Wipe concept/target so main() rewrites.
            with target_file.open(encoding="utf-8") as f:
                g = json.load(f)
            g.pop("concept", None)
            g.pop("target", None)
            with target_file.open("w", encoding="utf-8") as f:
                json.dump(g, f, ensure_ascii=False, indent=2)
                f.write("\n")

            _silent_main(tmp)

            text = target_file.read_text(encoding="utf-8")
            self.assertIn("あつまれ", text)
            self.assertIn(patch_games.PATCHES[1]["concept"], text)
            # ensure_ascii=False means raw unicode, not \u escapes.
            self.assertNotIn("\\u3042", text)

    def test_main_preserves_two_space_indent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            target_file = tmp / "data" / "games" / "001-animal-crossing-new-horizons.json"
            with target_file.open(encoding="utf-8") as f:
                g = json.load(f)
            g.pop("concept", None)
            g.pop("target", None)
            with target_file.open("w", encoding="utf-8") as f:
                json.dump(g, f, ensure_ascii=False, indent=2)
                f.write("\n")

            _silent_main(tmp)

            content = target_file.read_text(encoding="utf-8")
            self.assertTrue(content.endswith("\n"), "file does not end with newline")
            lines = content.splitlines()
            # 2nd line should be 2-space indented (e.g., '  "id": 1,').
            indented = [ln for ln in lines if ln.startswith(" ")]
            self.assertTrue(indented, "no indented lines after patch")
            self.assertTrue(
                indented[0].startswith("  ") and not indented[0].startswith("   "),
                f"indentation is not 2-space: {indented[0]!r}",
            )

    def test_no_extra_fields_introduced(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            _make_repo_copy(tmp)
            games_dir = tmp / "data" / "games"

            # Snapshot key sets BEFORE main().
            before_keys: dict[str, set[str]] = {}
            for p in games_dir.glob("*.json"):
                with p.open(encoding="utf-8") as f:
                    g = json.load(f)
                before_keys[p.name] = set(g.keys())

            _silent_main(tmp)

            for p in games_dir.glob("*.json"):
                with p.open(encoding="utf-8") as f:
                    g = json.load(f)
                after = set(g.keys())
                gid = g["id"]
                # Allowed delta: only concept/target may have been added.
                expected = before_keys[p.name] | {"concept", "target"} if gid in patch_games.PATCHES else before_keys[p.name]
                self.assertTrue(
                    after.issubset(expected),
                    f"{p.name} introduced unexpected keys: {after - expected}",
                )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
