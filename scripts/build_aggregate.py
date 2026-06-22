#!/usr/bin/env python3
"""
data/games/*.json を一次データとし、data/games.json (集約形式) と
data/index.json を再生成する。

実行: python3 scripts/build_aggregate.py
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES_DIR = ROOT / "data" / "games"
META_PATH = ROOT / "data" / "meta.json"
AGG_PATH = ROOT / "data" / "games.json"
INDEX_PATH = ROOT / "data" / "index.json"


def main() -> None:
    with META_PATH.open(encoding="utf-8") as f:
        meta = json.load(f)

    games = []
    for path in sorted(GAMES_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            games.append(json.load(f))
    games.sort(key=lambda g: g["id"])

    primary_count = Counter(g["primary"] for g in games)
    meta["total_titles"] = len(games)
    meta["primary_breakdown"] = dict(primary_count)

    agg = {
        "meta": meta,
        "games": [
            {k: v for k, v in g.items() if k not in ("file",)}
            for g in games
        ],
    }
    with AGG_PATH.open("w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=2)
        f.write("\n")

    index_rows = [
        {
            "id": g["id"],
            "title_jp": g["title_jp"],
            "title_en": g.get("title_en"),
            "year": g.get("year"),
            "primary": g["primary"],
            "secondary": g.get("secondary", []),
            "social_axis": g.get("social_axis"),
            "platform": g.get("platform", []),
            "file": g.get("file") or f"data/games/{path.name}",
        }
        for g in games
    ]
    index_doc = {
        "generated_from": "data/games/*.json",
        "total": len(index_rows),
        "primary_breakdown": dict(primary_count),
        "games": index_rows,
    }
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(index_doc, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"aggregated {len(games)} games")
    print(f"  primary: {dict(primary_count)}")
    print(f"  wrote {AGG_PATH.relative_to(ROOT)}")
    print(f"  wrote {INDEX_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
