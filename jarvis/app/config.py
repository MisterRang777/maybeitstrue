"""Central config, loaded from environment / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JARVIS_", env_file=".env", extra="ignore")

    # Anthropic key uses its own conventional name, not the JARVIS_ prefix.
    anthropic_api_key: str = ""

    brain_model: str = "claude-opus-4-8"
    triage_model: str = "claude-haiku-4-5"

    owner_name: str = "sir"
    language: str = "en"

    tts_backend: str = "say"          # say | piper | chatterbox
    say_voice: str = "Daniel"
    piper_bin: str = "piper"
    piper_model: str = ""
    chatterbox_url: str = "http://127.0.0.1:8004/v1/audio/speech"
    chatterbox_voice: str = "jarvis"

    audio_dir: str = "./audio_out"


# Read ANTHROPIC_API_KEY from the environment explicitly (no JARVIS_ prefix).
import os  # noqa: E402

settings = Settings()
settings.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", settings.anthropic_api_key)
