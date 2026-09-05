"""
Player: core stat block, stamina economy, inventory, and leveling logic.

Stamina design (per project notes):
- Stamina is spent on actions (forest fights, training, etc.), not a
  daily allowance. Player can keep playing until stamina hits 0 or they
  die.
- Hitting 0 stamina is NOT game over: the player is just gassed and
  needs to rest (Inn), eat (food items), or use a spell/potion to keep
  going now.
- Death is separate from 0 stamina: losing a fight costs gold + a
  rank-based percentage of XP (see GameData.death_loss_pct). Player can
  pay for immediate resurrection or otherwise recover through normal
  means (implementation of "otherwise" TBD by design).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from engine.data import GameData


@dataclass
class InventoryItem:
    name: str
    quantity: int = 1


@dataclass
class Player:
    name: str
    data: GameData
    level: int = 1
    xp: int = 0
    gold: int = 0
    specialty: str | None = None

    max_stamina: int = 100
    stamina: int = 100

    weapon: str = "Fists"
    armor: str = "T-shirt"
    charm: int = 10
    skill_points: int = 0

    inventory: list[InventoryItem] = field(default_factory=list)

    hp: int = field(init=False)
    max_hp: int = field(init=False)
    offense: int = field(init=False)
    defense: int = field(init=False)

    def __post_init__(self) -> None:
        self._recalculate_base_stats()
        self.hp = self.max_hp

    # -- Stats -------------------------------------------------------
    def _recalculate_base_stats(self) -> None:
        base = self.data.base_stats_for_level(self.level)
        self.max_hp = base["max_hp"]
        self.offense = base["offense"] + self._weapon_offense_boost()
        self.defense = base["defense"] + self._armor_defense_boost()

    def _weapon_offense_boost(self) -> int:
        for w in self.data.weapons:
            if w["name"] == self.weapon:
                return w["offense_boost"]
        return 0

    def _armor_defense_boost(self) -> int:
        for a in self.data.armor:
            if a["name"] == self.armor:
                return a["defense_boost"]
        return 0

    @property
    def rank(self) -> str:
        return self.data.rank_for_level(self.level)

    # -- XP / Leveling -------------------------------------------------
    def gain_xp(self, amount: int) -> list[str]:
        """
        Adds XP and applies any level-ups. Returns a list of narration
        events (e.g. ["You gained 45 XP.", "You reached level 3!"]) for
        the caller to hand to the narrator.
        """
        events = [f"You gained {amount} experience."]
        self.xp += amount
        while True:
            needed = self.data.xp_to_next(self.level)
            if needed is None or self.xp < needed:
                break
            self.xp -= needed
            self.level += 1
            old_max_hp = self.max_hp
            self._recalculate_base_stats()
            self.hp += self.max_hp - old_max_hp  # heal by the HP gained
            events.append(f"You reached level {self.level}!")
        return events

    # -- Stamina -------------------------------------------------------
    def spend_stamina(self, amount: int) -> bool:
        """Returns False if there isn't enough stamina to spend."""
        if self.stamina < amount:
            return False
        self.stamina -= amount
        return True

    def restore_stamina(self, amount: int) -> None:
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def is_exhausted(self) -> bool:
        return self.stamina <= 0

    # -- HP / Death ------------------------------------------------------
    def take_damage(self, amount: int) -> bool:
        """Returns True if this damage killed the player."""
        self.hp = max(0, self.hp - amount)
        return self.hp <= 0

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def apply_death_penalty(self) -> tuple[int, int]:
        """
        Applies the LORD-style death penalty: lose all gold and a
        rank-based percentage of current level XP. Returns
        (gold_lost, xp_lost) for narration.
        """
        gold_lost = self.gold
        self.gold = 0
        pct = self.data.death_loss_pct(self.level)
        xp_lost = int(self.xp * pct)
        self.xp -= xp_lost
        return gold_lost, xp_lost

    # -- Inventory -------------------------------------------------------
    def add_item(self, name: str, quantity: int = 1) -> None:
        for item in self.inventory:
            if item.name == name:
                item.quantity += quantity
                return
        self.inventory.append(InventoryItem(name=name, quantity=quantity))

    def remove_item(self, name: str, quantity: int = 1) -> bool:
        for item in self.inventory:
            if item.name == name:
                if item.quantity < quantity:
                    return False
                item.quantity -= quantity
                if item.quantity <= 0:
                    self.inventory.remove(item)
                return True
        return False

    def has_item(self, name: str) -> bool:
        return any(item.name == name for item in self.inventory)
