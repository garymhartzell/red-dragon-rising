"""
SoundManager: thin wrapper around sound_lib (BASS bindings) for playing
speech, sound effects, and music.

Requires: pip install sound_lib
On Windows this bundles the BASS DLLs it needs. On Linux/macOS you may
need to install libbass yourself; see the sound_lib docs.

Design notes:
- `speech` channel is used for TTS output (menu reads, narration). New
  speech interrupts and replaces whatever is currently speaking, similar
  to how a screen reader behaves, since audiogame players expect to be
  able to move through menus quickly without waiting on old speech.
- `sfx` channels are fire-and-forget, short one-shots (hits, coins, UI
  blips) and don't interrupt speech.
- `music` is a single long-running background channel with its own
  volume control, independent from speech/sfx.
"""

from __future__ import annotations

from pathlib import Path

from sound_lib import output, stream


class SoundManager:
    def __init__(self) -> None:
        self._output = output.Output()
        self._speech_stream: stream.FileStream | None = None
        self._music_stream: stream.FileStream | None = None
        self.sfx_volume = 1.0
        self.speech_volume = 1.0
        self.music_volume = 0.5

    # -- Speech -----------------------------------------------------
    def speak_file(self, path: str | Path) -> None:
        """Play a rendered TTS wav/mp3, interrupting any current speech."""
        self.stop_speech()
        self._speech_stream = stream.FileStream(file=str(path))
        self._speech_stream.volume = self.speech_volume
        self._speech_stream.play()

    def stop_speech(self) -> None:
        if self._speech_stream is not None:
            try:
                self._speech_stream.stop()
            except Exception:
                pass
            self._speech_stream = None

    def is_speaking(self) -> bool:
        return self._speech_stream is not None and self._speech_stream.is_playing

    # -- Sound effects ------------------------------------------------
    def play_sfx(self, path: str | Path, volume: float | None = None) -> None:
        """Fire-and-forget one-shot sound effect. Does not block or interrupt speech."""
        sfx_stream = stream.FileStream(file=str(path))
        sfx_stream.volume = volume if volume is not None else self.sfx_volume
        sfx_stream.play()
        # Not tracked/stored: sound_lib streams free themselves once
        # playback finishes and the object is garbage collected. For a
        # busier game, keep a list of active sfx streams and prune
        # finished ones periodically instead of relying on GC timing.

    def play_blocking(self, path: str | Path, volume: float | None = None) -> None:
        """
        Play a one-shot sound (e.g. a welcome jingle, victory fanfare)
        and don't return until it finishes. Use this for moments where
        you want the sound to fully play out before anything else
        happens or speaks — sound_lib's play_blocking() handles the
        waiting for us.
        """
        one_shot = stream.FileStream(file=str(path))
        one_shot.volume = volume if volume is not None else self.sfx_volume
        one_shot.play_blocking()

    # -- Music ----------------------------------------------------------
    def play_music(self, path: str | Path, loop: bool = True) -> None:
        self.stop_music()
        self._music_stream = stream.FileStream(file=str(path))
        self._music_stream.volume = self.music_volume
        if loop:
            self._music_stream.looping = True
        self._music_stream.play()

    def stop_music(self) -> None:
        if self._music_stream is not None:
            try:
                self._music_stream.stop()
            except Exception:
                pass
            self._music_stream = None

    def set_music_volume(self, volume: float) -> None:
        self.music_volume = volume
        if self._music_stream is not None:
            self._music_stream.volume = volume
