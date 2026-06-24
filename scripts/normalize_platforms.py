"""One-shot platform normalization for data/games/*.json.

Resolves notational drift that breaks facet filtering:
  - Storefronts (Steam/GOG/Epic/...) collapse into 'PC'.
  - Xbox Series 系 (Xbox Series, Xbox Series X|S, XSX) collapse into 'Xbox Series X/S'.
  - Mac/macOS, Vita/PS Vita, Browser/ブラウザ get one canonical spelling.
  - Slash compounds (PS3/4, PS4/PS5, Xbox 360/One, iOS/Android) split into separate entries.
  - Switch cloud variants collapse into 'Switch'.
  - DLC marker on ID 77 (Elden Ring SOTE) gets replaced with base-game platforms.

Skips: 'Multi' (40 files), 'consoles' (5 files), 'Xbox' (87 files) — these are
ambiguous and need per-game enrichment; tracked separately.

Run: python3 scripts/normalize_platforms.py && python3 scripts/build_aggregate.py
"""
from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "games"

# 1:1 replacements (storefronts → PC, casing/locale unification).
REPLACE_ONE = {
    # Storefronts and PC variants → PC
    "Steam": "PC",
    "GOG": "PC",
    "Epic": "PC",
    "Epic Games Store": "PC",
    "itch.io": "PC",
    "Origin": "PC",
    "PC Game Pass": "PC",
    "Game Pass": "PC",
    "Battle.net (PC)": "PC",
    "Windows": "PC",
    "PC (itch.io)": "PC",
    "PC (DMM GAMES)": "PC",
    "PC (Windows)": "PC",
    # Mac
    "macOS": "Mac",
    # Vita
    "Vita": "PS Vita",
    # Xbox Series 系
    "Xbox Series": "Xbox Series X/S",
    "Xbox Series X|S": "Xbox Series X/S",
    "XSX": "Xbox Series X/S",
    # Switch cloud
    "Switch (cloud)": "Switch",
    "Switch Cloud": "Switch",
    "Switch (primary)": "Switch",
    "Cloud": "Switch",
    # Browser
    "ブラウザ": "Browser",
    # Arcade
    "AC": "Arcade",
    # VR variants
    "PS VR/2": "PSVR2",
}

# Slash compounds → multiple entries.
SPLIT_MANY = {
    "PS3/4": ["PS3", "PS4"],
    "PS4/PS5": ["PS4", "PS5"],
    "Xbox 360/One": ["Xbox 360", "Xbox One"],
    "Xbox 360/One origin": ["Xbox 360", "Xbox One"],
    "iOS/Android": ["iOS", "Android"],
}

# Per-game manual fixes.
PER_GAME = {
    77: ["PC", "PS4", "PS5", "Xbox One", "Xbox Series X/S"],  # Elden Ring SOTE: was ["DLC"]
}


def normalize(plat: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for p in plat:
        if p in SPLIT_MANY:
            for q in SPLIT_MANY[p]:
                if q not in seen:
                    seen.add(q)
                    out.append(q)
        else:
            q = REPLACE_ONE.get(p, p)
            if q not in seen:
                seen.add(q)
                out.append(q)
    return out


def main() -> None:
    changed = 0
    for path in sorted(DATA_DIR.glob("*.json")):
        g = json.loads(path.read_text(encoding="utf-8"))
        original = list(g.get("platform") or [])
        if g["id"] in PER_GAME:
            new = list(PER_GAME[g["id"]])
        else:
            new = normalize(original)
        if new != original:
            g["platform"] = new
            path.write_text(json.dumps(g, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changed += 1
    print(f"normalized {changed} files")


if __name__ == "__main__":
    main()
