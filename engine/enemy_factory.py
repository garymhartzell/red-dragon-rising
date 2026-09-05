"""
Generates enemies from GameData's tier tables. XP is derived from
leveling.json's avg_xp_per_enemy with some variance, since the outline
doesn't give a fixed XP number per enemy (only gold ranges).
"""

from __future__ import annotations

import random

from engine.combat import Enemy
from engine.data import GameData

TIER_NAMES = ["below_average", "average", "above_average"]
TIER_LABELS = {
    "below_average": "weak",
    "average": "average",
    "above_average": "fearsome",
}

GENERIC_NAMES = [
    "bandit", "wolf", "goblin", "cutthroat", "rogue knight",
    "swamp lurker", "highway thug", "feral hound",
]


def generate_enemy(data: GameData, player_level: int) -> Enemy:
    tier_key = random.choice(TIER_NAMES)
    tier = data.enemy_tiers[str(player_level)][tier_key]

    hp = random.randint(*tier["hp"])
    offense = random.randint(*tier["offense"])
    defense = random.randint(*tier["defense"])
    gold = random.randint(*tier["gold"])

    level_info = next(
        (l for l in data.leveling["levels"] if l["level"] == player_level), None
    )
    avg_xp = level_info["avg_xp_per_enemy"] if level_info else 10
    xp = max(1, int(avg_xp * random.uniform(0.8, 1.2)))

    name = f"{TIER_LABELS[tier_key]} {random.choice(GENERIC_NAMES)}"

    return Enemy(name=name, hp=hp, max_hp=hp, offense=offense, defense=defense, gold=gold, xp=xp)
