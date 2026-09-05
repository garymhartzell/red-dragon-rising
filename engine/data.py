"""
Loads the static game-design data (leveling curve, base stats, enemy
tiers, weapons, armor) from the JSON files in data/. This is the
"content" layer — designed so an add-on could later supply its own
weapons.json/armor.json/enemies.json and have them merged in, without
touching engine code.
"""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def _load(filename: str) -> dict:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


class GameData:
    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.leveling = _load("leveling.json")
        self.base_stats = _load("base_stats.json")["by_level"]
        self.enemy_tiers = _load("enemies.json")["tiers"]
        self.weapons = _load("weapons.json")["weapons"]
        self.armor = _load("armor.json")["armor"]

    def xp_to_next(self, level: int) -> int | None:
        for entry in self.leveling["levels"]:
            if entry["level"] == level:
                return entry["xp_to_next"]
        return None  # max level

    def rank_for_level(self, level: int) -> str:
        for rank in self.leveling["ranks"]:
            lo, hi = rank["levels"]
            if lo <= level <= hi:
                return rank["name"]
        return "Hero"

    def death_loss_pct(self, level: int) -> float:
        for rank in self.leveling["ranks"]:
            lo, hi = rank["levels"]
            if lo <= level <= hi:
                return rank["loss_pct_on_death"]
        return 0.0

    def base_stats_for_level(self, level: int) -> dict:
        return self.base_stats[str(level)]

    def weapons_available_at(self, level: int) -> list[dict]:
        return [w for w in self.weapons if w["level_unlocked"] <= level]

    def armor_available_at(self, level: int) -> list[dict]:
        return [a for a in self.armor if a["level_unlocked"] <= level]
