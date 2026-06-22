#!/usr/bin/env python3
"""
data/games.json (集約形式) を data/games/{id:03d}-{slug}.json に分解し、
data/meta.json (カテゴリ定義・出典) と data/index.json (軽量インデックス) を生成する。

冪等: 何度実行しても同じ出力になる。
ソース・オブ・トゥルース: 分解後は data/games/*.json が一次データ。
data/games.json は build_aggregate.py で再生成される派生物。
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "games.json"
OUT_DIR = ROOT / "data" / "games"
META_PATH = ROOT / "data" / "meta.json"
INDEX_PATH = ROOT / "data" / "index.json"


def slugify(text: str) -> str:
    """英数字とハイフンのみの slug を生成。日本語は除去されるので title_en を入れること。"""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "game"


def main() -> None:
    with SRC.open(encoding="utf-8") as f:
        data = json.load(f)

    meta = data["meta"]
    games = data["games"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 既存ファイルを掃除（id が変わると孤児ファイルが残るため）
    for old in OUT_DIR.glob("*.json"):
        old.unlink()

    index_rows = []
    for game in sorted(games, key=lambda g: g["id"]):
        base = game.get("title_en") or game.get("title_jp") or f"game-{game['id']}"
        slug = slugify(base)
        filename = f"{game['id']:03d}-{slug}.json"
        path = OUT_DIR / filename

        record = dict(game)
        record["slug"] = slug
        record["file"] = f"data/games/{filename}"

        with path.open("w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
            f.write("\n")

        index_rows.append({
            "id": game["id"],
            "title_jp": game["title_jp"],
            "title_en": game.get("title_en"),
            "year": game.get("year"),
            "primary": game["primary"],
            "secondary": game.get("secondary", []),
            "social_axis": game.get("social_axis"),
            "platform": game.get("platform", []),
            "file": f"data/games/{filename}",
        })

    with META_PATH.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")

    index_doc = {
        "generated_from": "data/games/*.json",
        "total": len(index_rows),
        "games": index_rows,
    }
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(index_doc, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"wrote {len(index_rows)} game files to {OUT_DIR.relative_to(ROOT)}/")
    print(f"wrote {META_PATH.relative_to(ROOT)}")
    print(f"wrote {INDEX_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
