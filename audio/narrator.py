"""
Narrator ties TTSManager (render) and SoundManager (playback) together
so the rest of the game just calls `narrator.say("some text")` without
worrying about caching or playback details.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable

from audio.sound import SoundManager
from audio.tts import TTSManager


class Narrator:
    def __init__(
        self,
        tts: TTSManager,
        sound: SoundManager,
        on_speak: Callable[[str], None] | None = None,
    ) -> None:
        self.tts = tts
        self.sound = sound
        self.on_speak = on_speak
        self._tmp_dir = Path(tempfile.mkdtemp(prefix="rdr_tts_"))
        self._tmp_counter = 0

    def say(self, text: str, cache: bool = True, interrupt: bool = True) -> None:
        """
        Speak `text` aloud. Static/repeated lines should use cache=True
        (menu options, item names, location text) so they're only
        rendered once ever. Dynamic one-off lines (combat rolls, unique
        NPC dialogue) should use cache=False to avoid filling the cache
        directory with lines that will basically never repeat.
        """
        if self.on_speak is not None:
            self.on_speak(text)

        if interrupt:
            self.sound.stop_speech()

        if cache:
            path = self.tts.get_or_render(text)
        else:
            self._tmp_counter += 1
            path = self._tmp_dir / f"line_{self._tmp_counter}.wav"
            self.tts.render_transient(text, path)

        self.sound.speak_file(path)

    def say_menu(self, title: str, options: list[str]) -> None:
        """
        Convenience for a numbered menu: speaks the title, then each
        option prefixed with its number, as one combined utterance so
        the whole menu is read in one go without gaps between options.
        """
        lines = [title]
        for i, option in enumerate(options, start=1):
            lines.append(f"{i}. {option}")
        self.say(" ".join(lines), cache=True)
