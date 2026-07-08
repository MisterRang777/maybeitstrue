"""The Claude brain: composes briefings and answers, in the JARVIS voice."""
from anthropic import Anthropic

from .config import settings
from .persona import system_prompt

_client: Anthropic | None = None


def client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def _text(resp) -> str:
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def compose_briefing(context: dict) -> str:
    """Turn structured data (calendar, weather, reminders, ...) into a spoken briefing."""
    resp = client().messages.create(
        model=settings.brain_model,
        max_tokens=800,
        system=system_prompt(settings.owner_name),
        messages=[{
            "role": "user",
            "content": (
                "Deliver this morning's briefing, spoken aloud. Greet the owner, give the "
                "day and time, then walk through what matters. Keep it under 120 words and "
                "end cleanly. Here is the data:\n\n"
                f"{context}"
            ),
        }],
    )
    return _text(resp)


def answer(user_text: str, history: list[dict] | None = None) -> str:
    """Reactive conversation turn."""
    messages = (history or []) + [{"role": "user", "content": user_text}]
    resp = client().messages.create(
        model=settings.brain_model,
        max_tokens=1000,
        system=system_prompt(settings.owner_name),
        messages=messages,
    )
    return _text(resp)
