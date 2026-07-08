"""Data sources for the briefing.

Phase 1 ships SAMPLE data so the whole pipeline runs end-to-end today. Each
function is a single, obvious place to wire the real integration later:
  - calendar  -> Google Calendar API
  - inbox     -> Gmail API (triage top items)
  - reminders -> local SQLite store
  - weather   -> any weather API
Replace the bodies; the briefing composer doesn't change.
"""
from __future__ import annotations


def calendar_today() -> list[dict]:
    # TODO: wire Google Calendar. Return today's events sorted by start time.
    return [
        {"time": "10:00", "title": "Call with the print supplier"},
        {"time": "14:30", "title": "Snoozie logo review"},
    ]


def inbox_highlights() -> list[dict]:
    # TODO: wire Gmail + Haiku triage. Return only what matters.
    return [
        {"from": "Supplier", "subject": "Re: hoodie sample quote", "urgency": "medium"},
    ]


def reminders_due() -> list[str]:
    # TODO: wire the local reminders store.
    return ["Post the Snoozie logo reveal today"]


def weather() -> dict:
    # TODO: wire a weather API for the owner's location.
    return {"summary": "clear", "temp_c": 21, "high_c": 24}


def gather() -> dict:
    """Assemble everything the briefing needs into one structured payload."""
    return {
        "calendar": calendar_today(),
        "inbox": inbox_highlights(),
        "reminders": reminders_due(),
        "weather": weather(),
    }
