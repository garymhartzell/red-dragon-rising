"""
Menu: an arrow-key-navigable, spoken menu.

Behavior, matching how screen readers / self-voicing apps normally work:
- On first entering the menu, the title and full option list are read
  once.
- Up/Down moves the selection and speaks ONLY the newly-selected
  option (not the whole list again), so navigation feels instant.
- Enter activates the currently-selected option.
- Number keys still jump straight to and activate that option, for
  players who already know the menu and want to skip navigating.
- Escape is reserved for a future "back/cancel" behavior; currently
  ignored unless a menu opts in via `escape_action`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from engine.keyboard_input import Key, read_key

if TYPE_CHECKING:
    from audio.narrator import Narrator


@dataclass
class MenuOption:
    label: str
    action: Callable[[], None]


class Menu:
    def __init__(
        self,
        narrator: "Narrator",
        title: str,
        escape_action: Callable[[], None] | None = None,
    ) -> None:
        self.narrator = narrator
        self.title = title
        self.options: list[MenuOption] = []
        self.escape_action = escape_action

    def add(self, label: str, action: Callable[[], None]) -> None:
        self.options.append(MenuOption(label=label, action=action))

    def _speak_full_menu(self) -> None:
        self.narrator.say_menu(self.title, [o.label for o in self.options])

    def _speak_option(self, index: int) -> None:
        # Not cached: index-in-menu isn't stable content on its own, and
        # the option label alone is short/cheap enough to render fresh.
        # If this becomes a hot path, cache by option label instead.
        self.narrator.say(self.options[index].label, cache=True)

    def run_once(self) -> MenuOption | None:
        """
        Speaks the menu, lets the player navigate with arrow keys and
        confirm with Enter (or jump straight there with a number key),
        runs the chosen option's action, and returns the MenuOption that
        was chosen. Returns None only if escape_action fires.
        """
        if not self.options:
            return None

        index = 0
        self._speak_full_menu()

        while True:
            key = read_key()

            if key == Key.UP:
                index = (index - 1) % len(self.options)
                self._speak_option(index)

            elif key == Key.DOWN:
                index = (index + 1) % len(self.options)
                self._speak_option(index)

            elif key == Key.ENTER:
                chosen = self.options[index]
                chosen.action()
                return chosen

            elif key == Key.ESCAPE and self.escape_action is not None:
                self.escape_action()
                return None

            elif isinstance(key, str) and key.isdigit():
                num = int(key)
                if 1 <= num <= len(self.options):
                    index = num - 1
                    chosen = self.options[index]
                    self._speak_option(index)
                    chosen.action()
                    return chosen

    def run_loop(self, exit_label: str = "Leave") -> None:
        """
        Repeats the menu until the option matching exit_label is chosen.
        Useful for hub locations (Town Square, shops) where the player
        picks options repeatedly until they choose to leave.
        """
        while True:
            chosen = self.run_once()
            if chosen is None or chosen.label == exit_label:
                return
