# Red Dragon Rising

A fully-voiced, audio-first solo remake of Legend of the Red Dragon.

## Setup

Requires Python 3.10–3.12 (Kokoro's dependencies don't yet support 3.13+).

1. System dependency for Kokoro's phonemizer:
   - Linux: `apt-get install espeak-ng`
   - macOS: `brew install espeak`
   - Windows: see Kokoro's docs for the espeak-ng installer

2. Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. First run will download the Kokoro model weights (~350MB) from
   Hugging Face and cache them under `~/.cache/huggingface/hub/`. After
   that, everything runs fully offline.

4. Run the game:
   ```
   python main.py
   ```

## Project layout

```
rdr/
├── main.py                  # entry point / vertical-slice demo loop
├── audio/
│   ├── tts.py                # Kokoro wrapper: cached + on-the-fly rendering
│   ├── sound.py               # sound_lib wrapper: speech/sfx/music playback
│   └── narrator.py            # glues tts.py + sound.py -> narrator.say(text)
├── engine/
│   ├── data.py                 # loads data/*.json into GameData
│   ├── player.py                # Player stats, stamina, XP, death penalty
│   ├── combat.py                 # turn-based Fight/Run/Item/Spell loop
│   ├── enemy_factory.py           # generates enemies from tier tables
│   ├── menu.py                     # arrow-key-navigable spoken menu
│   └── keyboard_input.py            # windowed (pygame) key capture
├── data/
│   ├── leveling.json                # XP curve + rank thresholds
│   ├── base_stats.json                # HP/offense/defense per level
│   ├── enemies.json                    # enemy tier ranges per level
│   ├── weapons.json                     # weapon shop data
│   └── armor.json                        # armor shop data
├── content/
│   ├── audio_cache/    # auto-populated: cached TTS renders of static lines
│   ├── music/          # background music files (not yet wired up)
│   └── sfx/            # sound effect files (not yet wired up)
└── saves/              # player save files (not yet implemented)
```

## Design notes baked into this skeleton

- **Windowed, not console.** Input is captured through a real pygame
  window (`engine/keyboard_input.py`) rather than a terminal. This is
  what stops screen readers from narrating console text-grid movement
  (the "Blank" noise you get from a console app) — a plain window has
  no exposed text or controls for a screen reader to auto-read. It's
  also just a normal, native, double-clickable app window. The window
  shows a text readout of whatever was last spoken, purely for sighted
  playtesting/debugging — a screen reader can't read it either way,
  since it's pixels on a surface, not an accessible control.
- **Stamina, not daily turns.** Player spends stamina per action (10 per
  forest fight currently) and can keep playing until it hits 0 or they
  die. 0 stamina ≠ game over — it just means "go rest." See
  `engine/player.py`.
- **No AI in combat.** Combat is deterministic turn-based math with a
  small pool of templated flavor lines (`engine/combat.py`), so it's
  instant and free to run. AI is reserved for NPC dialogue, which isn't
  built yet — that's the natural next system to add, likely as an
  `online`/`offline` toggle in a settings module.
- **Voice caching split.** `TTSManager.get_or_render()` caches by a hash
  of (voice, speed, text) — use this for anything that repeats (menu
  labels, item names, shop text). `TTSManager.render_transient()` skips
  the cache — use this for combat rolls and other one-off lines so the
  cache directory doesn't fill up with lines that will basically never
  repeat.
- **Data-driven content.** All the tables from the design outline
  (leveling, base stats, enemy tiers, weapons, armor) live in `data/*.json`
  rather than in code. This is the pattern the future add-ons system
  should follow: an add-on supplies its own JSON (new enemies, forest
  events, NPCs) that gets merged in by the loader, without touching
  engine code.

## Known placeholders / next steps

- `Thunder Hammer`'s `level_unlocked` was blank in the original outline;
  filled in as 16 based on table position — confirm this is correct.
- The startup tip about NVDA's `NVDA+Shift+S`/`NVDA+Shift+Z` sleep-mode
  toggle in `main.py` was written for the old console version. It's
  harmless to leave in (still valid advice for any screen reader user),
  but since the windowed app shouldn't trigger unwanted narration in
  the first place, it could be trimmed down or dropped once you've
  confirmed things are quiet in practice.
- Input is currently `input()` in the console. This should be replaced
  with real keyboard-event capture (no Enter key needed) once you're
  ready — `accessible_output2` pairs well with a screen-reader-style
  input loop, or a library like `pyglet` for lower-level key events.
- Item/spell/skill use in combat (`_use_item`, `_use_spell` in
  `combat.py`) are stubs — wire these up to `Player.inventory` and the
  specialty skill trees (Cleave, Shadowstep, Backstab, etc.) from the
  outline.
- Resurrection currently auto-revives the player at full HP after
  applying the gold/XP penalty. The "pay for immediate resurrection vs.
  otherwise recover" choice from the design discussion isn't built yet.
- Town Square only has Rest and Status so far — the other shops
  (Garrison's Warrior Training, Bard's Song Tavern, Healer's Hut,
  Mid-World Weaponry, Able's Armor, Ye Old Bank) aren't built yet.
- No save/load system yet.
- Adult mode toggle isn't stubbed in yet — recommend adding it as an
  explicit off-by-default settings flag with its own separate content
  pack, as discussed.
