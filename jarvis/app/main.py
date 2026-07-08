"""Jarvis Phase 1 server — brain + briefing + TTS, over a tiny HTTP API.

Endpoints:
  GET  /health                 -> liveness
  POST /briefing               -> compose the morning briefing (JSON: {text})
  POST /briefing/audio         -> compose + synthesize, returns the audio file
  POST /say      {text}        -> synthesize arbitrary text, returns audio
  POST /ask      {text}        -> reactive conversation turn (JSON: {reply})
  POST /ask/audio{text}        -> ask + synthesize the reply, returns audio

The iOS Shortcut hits /briefing/audio in the morning and plays the result.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import brain, sources, tts
from .config import settings

app = FastAPI(title="Jarvis", version="0.1.0")


class TextIn(BaseModel):
    text: str


class AskIn(BaseModel):
    text: str
    history: list[dict] | None = None


@app.get("/health")
def health() -> dict:
    return {"ok": True, "backend": settings.tts_backend, "model": settings.brain_model}


@app.post("/briefing")
def briefing() -> dict:
    return {"text": brain.compose_briefing(sources.gather())}


@app.post("/briefing/audio")
def briefing_audio() -> FileResponse:
    text = brain.compose_briefing(sources.gather())
    return FileResponse(tts.synthesize(text), media_type="audio/mpeg")


@app.post("/say")
def say(body: TextIn) -> FileResponse:
    return FileResponse(tts.synthesize(body.text), media_type="audio/mpeg")


@app.post("/ask")
def ask(body: AskIn) -> dict:
    return {"reply": brain.answer(body.text, body.history)}


@app.post("/ask/audio")
def ask_audio(body: AskIn) -> FileResponse:
    reply = brain.answer(body.text, body.history)
    return FileResponse(tts.synthesize(reply), media_type="audio/mpeg")
