"""
Keyboard input via a real window (using pygame), replacing raw console
input.

Why: a console window's text buffer gets narrated by screen readers as
you move around in it (NVDA's review cursor reads whatever character
is at the cursor's position, saying "blank" when there's nothing
there). A plain windowed app has no exposed text or controls for a
screen reader to read automatically, so this eliminates that noise
without asking the player to do anything. It's also just a normal,
native, double-clickable Windows app window rather than a terminal,
which is friendlier for non-technical players.

Public interface is unchanged from the old console version: Key.* and
read_key(), so engine/menu.py and engine/combat.py don't need to know
this changed underneath them.
"""

from __future__ import annotations

import sys

import pygame

WINDOW_TITLE = "Red Dragon Rising"
WINDOW_SIZE = (520, 220)
BACKGROUND_COLOR = (18, 18, 28)
TEXT_COLOR = (225, 225, 235)


class Key:
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    ENTER = "enter"
    ESCAPE = "escape"
    OTHER = "other"


_KEY_MAP = {
    pygame.K_UP: Key.UP,
    pygame.K_DOWN: Key.DOWN,
    pygame.K_LEFT: Key.LEFT,
    pygame.K_RIGHT: Key.RIGHT,
    pygame.K_RETURN: Key.ENTER,
    pygame.K_KP_ENTER: Key.ENTER,
    pygame.K_ESCAPE: Key.ESCAPE,
}

# Numpad digit keycodes are NOT sequential in pygame (K_KP0 is higher
# than K_KP1 through K_KP9), so this has to be an explicit mapping
# rather than a range check.
_NUMPAD_DIGIT_MAP = {
    pygame.K_KP0: "0",
    pygame.K_KP1: "1",
    pygame.K_KP2: "2",
    pygame.K_KP3: "3",
    pygame.K_KP4: "4",
    pygame.K_KP5: "5",
    pygame.K_KP6: "6",
    pygame.K_KP7: "7",
    pygame.K_KP8: "8",
    pygame.K_KP9: "9",
}

_initialized = False
_screen: "pygame.Surface | None" = None
_font: "pygame.font.Font | None" = None
_status_lines: list[str] = ["Red Dragon Rising", "Use arrow keys and Enter to play."]


def init_window() -> None:
    """
    Creates the game window. Safe to call more than once. This is
    called automatically the first time read_key() is used, but
    calling it explicitly earlier (e.g. at the top of main()) makes the
    window appear before anything speaks, which is a bit more natural.
    """
    global _initialized, _screen, _font
    if _initialized:
        return
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    _screen = pygame.display.set_mode(WINDOW_SIZE)
    _font = pygame.font.SysFont(None, 26)
    _redraw()
    _initialized = True


def set_status_text(text: str) -> None:
    """
    Updates the text shown in the window to match whatever was last
    spoken. Purely a visual convenience (for sighted playtesting,
    demoing, or a helper looking over someone's shoulder) — a screen
    reader has nothing here to read regardless, since this is just
    pixels drawn on a surface, not an accessible text control.
    """
    global _status_lines
    # Simple manual wrap so long lines don't run off the window.
    max_chars = 60
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > max_chars:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    _status_lines = lines[:6] if lines else [""]
    if _initialized:
        _redraw()


def _redraw() -> None:
    if _screen is None:
        return
    _screen.fill(BACKGROUND_COLOR)
    if _font is not None:
        y = 30
        for line in _status_lines:
            surf = _font.render(line, True, TEXT_COLOR)
            _screen.blit(surf, (20, y))
            y += 30
    pygame.display.flip()


def read_key() -> str:
    """
    Blocks until a relevant key is pressed in the game window. Returns
    a Key.* value, or a single digit character (e.g. "3") for number
    keys, matching the old console version's interface.
    """
    init_window()
    while True:
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

        if event.type == pygame.KEYDOWN:
            if event.key in _KEY_MAP:
                return _KEY_MAP[event.key]
            if pygame.K_0 <= event.key <= pygame.K_9:
                return chr(event.key - pygame.K_0 + ord("0"))
            if event.key in _NUMPAD_DIGIT_MAP:
                return _NUMPAD_DIGIT_MAP[event.key]
            return Key.OTHER
