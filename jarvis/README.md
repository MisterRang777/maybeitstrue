# Jarvis — Phase 1: the server brain

The first working slice of Jarvis (see [`../JARVIS.md`](../JARVIS.md) for the full plan).
It composes a spoken morning briefing in the JARVIS voice using Claude, renders it with a
self-hosted open-source TTS engine, and serves it over a tiny HTTP API the iOS Shortcut can call.

**Runs on your Mac today** with zero voice setup — it uses the built-in macOS `say` voice as a
fallback so you can hear Jarvis in about two minutes, then upgrade the voice when ready.

## What's here

```
jarvis/
├── app/
│   ├── config.py     # settings from .env
│   ├── persona.py    # the JARVIS voice contract (from the film analysis)
│   ├── brain.py      # Claude: composes briefings + answers
│   ├── tts.py        # say / piper / chatterbox backends + fallback
│   ├── sources.py    # calendar / inbox / reminders / weather (sample data → wire real APIs)
│   └── main.py       # FastAPI endpoints
└── speak_briefing.py # hear Jarvis instantly, no server needed
```

## Quick start (Mac, ~2 minutes)

```bash
cd jarvis
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your ANTHROPIC_API_KEY into .env

python speak_briefing.py      # composes today's briefing and speaks it aloud
python speak_briefing.py "how much time until my next meeting?"
```

That's Jarvis talking, on sample calendar/weather data, in his own voice.

## Run as a server (for the iOS Shortcut later)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
# then:
curl -X POST localhost:8080/briefing            # -> {"text": "..."}
curl -X POST localhost:8080/briefing/audio -o brief.mp3 && afplay brief.mp3
```

The morning Shortcut will call `POST /briefing/audio` and play the returned audio.

## Upgrading the voice

Edit `.env` → `JARVIS_TTS_BACKEND`:

- **`say`** (default) — macOS built-in. Zero setup. Good enough to start.
- **`piper`** — CPU-only, runs anywhere. Set `JARVIS_PIPER_MODEL` to a downloaded
  [Piper voice](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md).
- **`chatterbox`** — the target: a **custom cloned Jarvis voice**, MIT-licensed, beats
  ElevenLabs. Run [Chatterbox-TTS-Server](https://github.com/devnen/Chatterbox-TTS-Server)
  (needs a small GPU), point `JARVIS_CHATTERBOX_URL` at it. Any backend that fails falls
  back to `say`, so Jarvis is never mute.

## Next (Phase 2+)

Wire the real data sources in `app/sources.py` (Google Calendar, Gmail + Haiku triage,
reminders store), then the iOS Shortcut, then the watcher. Roadmap in [`../JARVIS.md`](../JARVIS.md).
