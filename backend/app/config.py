"""Konfigurasi terpusat aplikasi KnowDesk AI berbasis pydantic-settings.

Membaca variabel lingkungan (.env) sesuai batasan agents.md §2 R6, §4, §10.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenRouter API & Model (dipilih pengguna, tanpa default di kode per §4 & §13)
    OPENROUTER_API_KEY: str = ""
    CHAT_MODEL: str
    EMBEDDING_MODEL: str

    # Parameter LLM & Eksekusi Tool
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 700
    LLM_TIMEOUT_S: float = 30.0
    TOOL_TIMEOUT_S: float = 5.0

    # Batasan State Machine & Eksekusi Agent
    AGENT_MAX_STEPS: int = 4
    AGENT_MAX_CLARIFICATIONS: int = 2
    AGENT_MAX_LLM_CALLS_PER_TURN: int = 3

    # Konfigurasi RAG & Retrieval
    RAG_MIN_COSINE: float = 0.35
    RAG_HIGH_COSINE: float = 0.55
    RAG_RRF_K: int = 60
    RAG_MAX_RESULTS: int = 5
    RAG_CHUNK_OVERLAP: int = 50

    # Input Guardrails (Lapis 1)
    INPUT_MAX_CHARS: int = 1000

    # Basis Data MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "knowdesk_app"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "knowdesk_ai"

    # Server Aplikasi & CORS
    APP_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173"
    LOG_LEVEL: str = "INFO"
