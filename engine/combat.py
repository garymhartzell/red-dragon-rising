"""
Turn-based combat: each round the player chooses Fight, Run, Item, or
Spell. Resolution is pure math (no AI) so it's fast, free, and works
fully offline. AI is reserved for NPC dialogue elsewhere in the game,
per project design.

This is a first pass meant to establish the loop and hook points:
- Skill/spell effects are stubbed (apply_skill) for specialties to fill
  in later (Cleave, Shadowstep, Backstab, etc. from the outline).
- Flavor lines are pulled from small local pools rather than generated,
  matching the "templated snark" approach discussed for combat.
- Enemy behavior is a simple always-attack for now; a later pass can
  add enemy items/abilities at higher tiers.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.menu import Menu
from engine.player import Player

if TYPE_CHECKING:
    # Import only for type hints; keeps engine logic importable/testable
    # without the audio stack (sound_lib, kokoro) installed.
    from audio.narrator import Narrator

STAMINA_COST_PER_FIGHT = 10

HIT_LINES = [
    "You land a solid hit.",
    "Your strike connects hard.",
    "That one's going to leave a mark.",
]
MISS_LINES = [
    "You swing and miss completely.",
    "Your attack goes wide.",
    "You stumble and miss your opening.",
]
ENEMY_HIT_LINES = [
    "{enemy} hits you hard.",
    "{enemy} lands a nasty blow.",
]
ENEMY_MISS_LINES = [
    "{enemy} swings and misses.",
    "{enemy} fumbles the attack.",
]


@dataclass
class Enemy:
    name: str
    hp: int
    max_hp: int
    offense: int
    defense: int
    gold: int
    xp: int


def roll_damage(attacker_offense: int, defender_defense: int) -> tuple[int, bool]:
    """
    Returns (damage, hit). A very simple model: chance to hit scales
    with offense vs defense, damage is offense minus a defense
    reduction, with some randomness. Tune freely once you're
    playtesting.
    """
    hit_chance = max(0.15, min(0.95, 0.5 + (attacker_offense - defender_defense) / 200))
    if random.random() > hit_chance:
        return 0, False
    base = max(1, attacker_offense - defender_defense // 2)
    damage = random.randint(int(base * 0.7), int(base * 1.3))
    return max(1, damage), True


class Combat:
    def __init__(self, narrator: "Narrator", player: Player, enemy: Enemy) -> None:
        self.narrator = narrator
        self.player = player
        self.enemy = enemy

    def run(self) -> str:
        """
        Runs the fight to completion. Returns one of:
        "victory", "fled", "defeat"
        """
        if not self.player.spend_stamina(STAMINA_COST_PER_FIGHT):
            self.narrator.say(
                "You're too exhausted to fight. Rest up first.", cache=True
            )
            return "too_tired"

        self.narrator.say(
            f"A {self.enemy.name} appears! It has {self.enemy.hp} health.",
            cache=False,
        )

        while True:
            choice = self._prompt_turn()

            if choice == "run":
                if self._attempt_flee():
                    self.narrator.say("You escape safely.", cache=False)
                    return "fled"
                else:
                    self.narrator.say(
                        "You fail to get away!", cache=False
                    )
                    # failed flee still costs the player the enemy's turn
                    if self._enemy_turn():
                        return "defeat"
                    continue

            if choice == "item":
                self._use_item()
                continue

            if choice == "spell":
                self._use_spell()
                if self.enemy.hp <= 0:
                    return self._victory()
                if self._enemy_turn():
                    return "defeat"
                continue

            # default: fight
            self._player_attack()
            if self.enemy.hp <= 0:
                return self._victory()
            if self._enemy_turn():
                return "defeat"

    def _prompt_turn(self) -> str:
        menu = Menu(
            self.narrator,
            f"Your turn. HP: {self.player.hp}/{self.player.max_hp}. "
            f"{self.enemy.name} HP: {self.enemy.hp}/{self.enemy.max_hp}.",
        )
        mapping = {"Fight": "fight", "Run": "run", "Use item": "item",
                   "Cast spell / use skill": "spell"}
        for label in mapping:
            menu.add(label, lambda: None)  # action unused; we read the label below
        chosen = menu.run_once()
        return mapping[chosen.label]

    def _player_attack(self) -> None:
        damage, hit = roll_damage(self.player.offense, self.enemy.defense)
        if hit:
            self.enemy.hp = max(0, self.enemy.hp - damage)
            line = random.choice(HIT_LINES)
            self.narrator.say(f"{line} {damage} damage.", cache=False)
        else:
            self.narrator.say(random.choice(MISS_LINES), cache=False)

    def _enemy_turn(self) -> bool:
        """Returns True if this attack killed the player."""
        damage, hit = roll_damage(self.enemy.offense, self.player.defense)
        if hit:
            line = random.choice(ENEMY_HIT_LINES).format(enemy=self.enemy.name)
            self.narrator.say(f"{line} {damage} damage.", cache=False)
            if self.player.take_damage(damage):
                self.narrator.say("You have been defeated!", cache=False)
                return True
        else:
            self.narrator.say(
                random.choice(ENEMY_MISS_LINES).format(enemy=self.enemy.name),
                cache=False,
            )
        return False

    def _attempt_flee(self) -> bool:
        # Simple flee chance; tune once playtesting.
        return random.random() < 0.7

    def _use_item(self) -> None:
        # Stub: hook up to player.inventory (healing potions, etc.)
        self.narrator.say("You rummage through your bag, but decide against it for now.", cache=False)

    def _use_spell(self) -> None:
        # Stub: hook up to specialty skill trees (Cleave, Shadowstep, Backstab, etc.)
        self.narrator.say("You attempt a special technique, but haven't learned one yet.", cache=False)

    def _victory(self) -> str:
        self.narrator.say(
            f"You defeat the {self.enemy.name}! You gain {self.enemy.gold} gold.",
            cache=False,
        )
        self.player.gold += self.enemy.gold
        for event in self.player.gain_xp(self.enemy.xp):
            self.narrator.say(event, cache=False)
        return "victory"
