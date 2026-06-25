#!/usr/bin/env python3
"""
data/games/*.json を一次データとし、data/games.json (集約形式) と
data/index.json を再生成する。

実行: python3 scripts/build_aggregate.py
"""
import json
from collections import Counter
from pathlib import Path
from typing import Optional, Union

ROOT = Path(__file__).resolve().parent.parent
GAMES_DIR = ROOT / "data" / "games"
META_PATH = ROOT / "data" / "meta.json"
AGG_PATH = ROOT / "data" / "games.json"
INDEX_PATH = ROOT / "data" / "index.json"


def main(repo_root: Optional[Union[str, Path]] = None) -> None:
    """Regenerate data/games.json and data/index.json.

    Parameters
    ----------
    repo_root:
        Optional repository root. When provided, all paths are computed
        relative to it. Defaults to the module-level ``ROOT`` (the actual
        repo root). This makes the function testable against a temporary
        copy of the data tree without relying on the current working
        directory or mutating the real ``data/`` files.
    """
    root = Path(repo_root).resolve() if repo_root is not None else ROOT
    games_dir = root / "data" / "games"
    meta_path = root / "data" / "meta.json"
    agg_path = root / "data" / "games.json"
    index_path = root / "data" / "index.json"

    with meta_path.open(encoding="utf-8") as f:
        meta = json.load(f)

    games = []
    game_paths = sorted(games_dir.glob("*.json"))
    for path in game_paths:
        with path.open(encoding="utf-8") as f:
            games.append((path, json.load(f)))
    games.sort(key=lambda item: item[1]["id"])

    game_dicts = [g for _, g in games]
    primary_count = Counter(g["primary"] for g in game_dicts)
    meta["total_titles"] = len(game_dicts)
    meta["primary_breakdown"] = dict(primary_count)

    agg = {
        "meta": meta,
        "games": [
            {k: v for k, v in g.items() if k not in ("file",)}
            for g in game_dicts
        ],
    }
    with agg_path.open("w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=2)
        f.write("\n")

    index_rows = [
        {
            "id": g["id"],
            "title_jp": g["title_jp"],
            "title_en": g.get("title_en"),
            "developer": g.get("developer"),
            "publisher": g.get("publisher"),
            "year": g.get("year"),
            "genre": g.get("genre"),
            "primary": g["primary"],
            "secondary": g.get("secondary", []),
            "social_axis": g.get("social_axis"),
            "platform": g.get("platform", []),
            "popularity": g.get("popularity"),
            "concept": g.get("concept"),
            "target": g.get("target"),
            "tags": g.get("tags", []),
            "file": g.get("file") or f"data/games/{path.name}",
        }
        for path, g in games
    ]
    index_doc = {
        "generated_from": "data/games/*.json",
        "total": len(index_rows),
        "primary_breakdown": dict(primary_count),
        "games": index_rows,
    }
    with index_path.open("w", encoding="utf-8") as f:
        json.dump(index_doc, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"aggregated {len(game_dicts)} games")
    print(f"  primary: {dict(primary_count)}")
    print(f"  wrote {agg_path.relative_to(root)}")
    print(f"  wrote {index_path.relative_to(root)}")


if __name__ == "__main__":
    main()
