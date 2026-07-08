"""Text-to-speech with pluggable backends and graceful fallback.

Backends, in order of quality:
  chatterbox -> local Chatterbox-TTS-Server (custom cloned voice, needs GPU)
  piper      -> local Piper binary (CPU-only, solid, no cloning)
  say        -> macOS built-in `say` (zero setup, works on the Mac today)

Every path degrades: if the chosen backend fails, we fall back to `say`, so
Jarvis is never fully mute.
"""
from __future__ import annotations

import os
import subprocess
import time

import httpx

from .config import settings


def _out_path(ext: str) -> str:
    os.makedirs(settings.audio_dir, exist_ok=True)
    # No Date.now equivalent needed for correctness; monotonic keeps names unique.
    return os.path.join(settings.audio_dir, f"jarvis_{int(time.monotonic() * 1000)}.{ext}")


def _say(text: str) -> str:
    """macOS `say` -> aiff. The dependable last resort."""
    path = _out_path("aiff")
    subprocess.run(["say", "-v", settings.say_voice, "-o", path, text], check=True)
    return path


def _piper(text: str) -> str:
    """Local Piper -> wav. CPU-friendly."""
    if not settings.piper_model:
        raise RuntimeError("JARVIS_PIPER_MODEL not set")
    path = _out_path("wav")
    proc = subprocess.run(
        [settings.piper_bin, "--model", settings.piper_model, "--output_file", path],
        input=text.encode(),
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"piper failed: {proc.stderr.decode()[:200]}")
    return path


def _chatterbox(text: str) -> str:
    """Local Chatterbox-TTS-Server (OpenAI-compatible /v1/audio/speech) -> wav."""
    path = _out_path("wav")
    with httpx.Client(timeout=60) as c:
        r = c.post(
            settings.chatterbox_url,
            json={"input": text, "voice": settings.chatterbox_voice, "response_format": "wav"},
        )
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    return path


_BACKENDS = {"say": _say, "piper": _piper, "chatterbox": _chatterbox}


def synthesize(text: str) -> str:
    """Render `text` to an audio file, returning its path. Falls back to `say`."""
    backend = _BACKENDS.get(settings.tts_backend, _say)
    try:
        return backend(text)
    except Exception as exc:  # noqa: BLE001 — fallback is the whole point
        if backend is not _say:
            print(f"[tts] {settings.tts_backend} failed ({exc}); falling back to `say`")
            try:
                return _say(text)
            except Exception as exc2:  # noqa: BLE001
                raise RuntimeError(f"all TTS backends failed: {exc2}") from exc2
        raise
