"""
Red Dragon Rising - entry point.

This is a minimal but functional vertical slice: Town Square (rest to
restore stamina, check status) and The Endless Forest (fight a
generated enemy). It's meant as a skeleton to extend with the real
shops, NPCs, and events from the design outline.

Run with: python main.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Force Kokoro/huggingface_hub to use the local model cache only, skipping
# the network check it otherwise makes on every launch. Must be set before
# TTSManager (which imports kokoro) is imported.
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from audio.narrator import Narrator
from audio.sound import SoundManager
from audio.tts import TTSManager
from engine.combat import Combat
from engine.data import GameData
from engine.enemy_factory import generate_enemy
from engine.menu import Menu
from engine.player import Player

REST_STAMINA_RESTORED = 40

# Looked up in order; first one found is played. Drop your file in
# content/sfx/ under either name — mp3 keeps the repo smaller, wav
# works identically, sound_lib/BASS plays both natively.
WELCOME_SOUND_CANDIDATES = [
    Path("content/sfx/welcome.mp3"),
    Path("content/sfx/welcome.wav"),
]


def build_narrator() -> Narrator:
    tts = TTSManager(voice="af_heart")
    sound = SoundManager()
    return Narrator(tts, sound)


def town_square(narrator: Narrator, player: Player, data: GameData) -> None:
    def status() -> None:
        narrator.say(
            f"Level {player.level} {player.rank}. "
            f"HP {player.hp} of {player.max_hp}. "
            f"Stamina {player.stamina} of {player.max_stamina}. "
            f"Gold {player.gold}. "
            f"Weapon: {player.weapon}. Armor: {player.armor}.",
            cache=False,
        )

    def rest() -> None:
        player.restore_stamina(REST_STAMINA_RESTORED)
        player.heal(player.max_hp)
        narrator.say(
            "You rest at the Knight Fall Inn and wake up refreshed.",
            cache=False,
        )

    menu = Menu(narrator, "You are in the Town Square.")
    menu.add("Check your status", status)
    menu.add("Rest at the Knight Fall Inn", rest)
    menu.add("Go to the Endless Forest", lambda: forest(narrator, player, data))
    menu.add("Leave the game", lambda: sys.exit(0))
    menu.run_loop(exit_label="Leave the game")


def forest(narrator: Narrator, player: Player, data: GameData) -> None:
    if player.is_exhausted():
        narrator.say(
            "You're too exhausted to venture into the forest. Head back to town to rest.",
            cache=False,
        )
        return

    enemy = generate_enemy(data, player.level)
    result = Combat(narrator, player, enemy).run()

    if result == "defeat":
        gold_lost, xp_lost = player.apply_death_penalty()
        player.hp = player.max_hp  # revived for now; hook up resurrection cost later
        narrator.say(
            f"You lose {gold_lost} gold and {xp_lost} experience. "
            "You wake up back in town.",
            cache=False,
        )


def play_welcome_sound(narrator: Narrator) -> None:
    """
    Plays a one-time welcome jingle before the spoken intro line, if a
    file is present. Silently does nothing if you haven't added one yet
    — this is meant to be optional, not required for the game to run.
    """
    for candidate in WELCOME_SOUND_CANDIDATES:
        if candidate.exists():
            narrator.sound.play_blocking(candidate)
            return


def main() -> None:
    data = GameData()
    narrator = build_narrator()
    player = Player(name="Adventurer", data=data)

    play_welcome_sound(narrator)
    narrator.say(
        "Welcome to Red Dragon Rising. Your journey begins in the Town Square.",
        cache=True,
    )
    town_square(narrator, player, data)


if __name__ == "__main__":
    main()
