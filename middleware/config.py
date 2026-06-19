"""
config.py — Environment-based configuration for AI WAF Middleware.
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # Groq API key (required)
    GROQ_API_KEY: str = ""

    # Groq model — llama-3.3-70b-versatile is fast + accurate for JSON tasks
    # Other options: llama3-8b-8192 (fastest), mixtral-8x7b-32768
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Operating mode:
    #   "block"  — return 403 immediately when score >= threshold
    #   "detect" — log & tag, but always forward to backend
    MODE: Literal["block", "detect"] = "block"

    # Score threshold at which action = "block"
    BLOCK_THRESHOLD: int = 70

    # URL of the upstream VulnApp (Docker internal hostname)
    BACKEND_URL: str = "http://vulnapp:80"

    # Max bytes of request body forwarded to Groq (keep cost low)
    MAX_BODY_BYTES: int = 2048

    # File extensions that skip AI classification entirely
    STATIC_EXTENSIONS: tuple = (
        ".css", ".js", ".map", ".ico", ".png", ".jpg",
        ".jpeg", ".gif", ".svg", ".woff", ".woff2", ".ttf",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
