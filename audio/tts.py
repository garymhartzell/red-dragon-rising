"""
TTSManager: wraps Kokoro TTS for both cached (static) and on-the-fly
(dynamic) speech generation, so menu labels and dynamic combat/NPC lines
can share a single voice.

Requires: pip install kokoro soundfile
Also requires the espeak-ng system package (apt-get install espeak-ng on
Linux, brew install espeak on macOS).

First run will download the Kokoro model weights (~350MB) from Hugging
Face and cache them under ~/.cache/huggingface/hub/. After that it runs
fully offline.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import soundfile as sf

try:
    from kokoro import KPipeline
except ImportError as exc:  # pragma: no cover - helpful message at import time
    raise ImportError(
        "Kokoro is not installed. Run: pip install kokoro soundfile "
        "and make sure espeak-ng is installed on your system."
    ) from exc


class TTSManager:
    """
    Generates and caches speech audio using Kokoro.

    Static content (menu options, shop labels, item names, etc.) is
    rendered once and cached to disk by a hash of (voice, speed, text).
    Dynamic content (combat results, NPC dialogue) can either be cached
    the same way (if it repeats often) or rendered straight to a temp
    file for immediate one-off playback.
    """

    def __init__(
        self,
        cache_dir: str | Path = "content/audio_cache",
        voice: str = "af_heart",
        lang_code: str = "a",  # 'a' = American English
        speed: float = 1.0,
        sample_rate: int = 24000,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.voice = voice
        self.speed = speed
        self.sample_rate = sample_rate
        self._pipeline = KPipeline(lang_code=lang_code)

    def _cache_path(self, text: str, voice: str | None, speed: float | None) -> Path:
        voice = voice or self.voice
        speed = speed if speed is not None else self.speed
        key = f"{voice}|{speed}|{text}".encode("utf-8")
        digest = hashlib.sha256(key).hexdigest()[:24]
        return self.cache_dir / f"{digest}.wav"

    def get_or_render(
        self,
        text: str,
        voice: str | None = None,
        speed: float | None = None,
    ) -> Path:
        """
        Return a path to a WAV file for `text`, generating and caching it
        if it doesn't already exist. Use this for static/repeated lines
        (menu options, item names, location descriptions).
        """
        path = self._cache_path(text, voice, speed)
        if path.exists():
            return path
        self._render_to_file(text, path, voice, speed)
        return path

    def render_transient(
        self,
        text: str,
        out_path: str | Path,
        voice: str | None = None,
        speed: float | None = None,
    ) -> Path:
        """
        Render `text` straight to `out_path` without caching. Use this
        for dynamic, rarely-repeated content (combat narration, unique
        NPC lines) where caching would just fill disk with one-off files.
        """
        out_path = Path(out_path)
        self._render_to_file(text, out_path, voice, speed)
        return out_path

    def _render_to_file(
        self,
        text: str,
        path: Path,
        voice: str | None,
        speed: float | None,
    ) -> None:
        voice = voice or self.voice
        speed = speed if speed is not None else self.speed
        chunks = []
        for _graphemes, _phonemes, audio in self._pipeline(
            text, voice=voice, speed=speed
        ):
            chunks.append(audio)
        full_audio = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
        sf.write(str(path), full_audio, self.sample_rate)

    def prewarm(self, phrases: list[str]) -> None:
        """
        Render a batch of static phrases into the cache ahead of time,
        e.g. at build time or on first launch, so nothing has to render
        mid-menu during play. Skips anything already cached.
        """
        for phrase in phrases:
            self.get_or_render(phrase)
