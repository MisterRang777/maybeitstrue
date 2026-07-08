#!/usr/bin/env python3
"""Fastest way to hear Jarvis on your Mac — no server required.

    python speak_briefing.py            # compose today's briefing and speak it
    python speak_briefing.py "hello"    # speak an arbitrary line in his voice

With JARVIS_TTS_BACKEND=say (the default) this needs only your ANTHROPIC_API_KEY
and a Mac. It composes the briefing with Claude, renders it, and plays it aloud.
"""
import subprocess
import sys

from app import brain, sources, tts


def main() -> None:
    if len(sys.argv) > 1:
        text = brain.answer(" ".join(sys.argv[1:]))
    else:
        text = brain.compose_briefing(sources.gather())

    print(f"\nJARVIS: {text}\n")
    path = tts.synthesize(text)
    # Play it (macOS `afplay`; harmless no-op message elsewhere).
    try:
        subprocess.run(["afplay", path], check=True)
    except FileNotFoundError:
        print(f"(audio written to {path} — play it with any audio player)")


if __name__ == "__main__":
    main()
