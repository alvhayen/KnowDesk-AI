"""Test paritas konfigurasi antara .env.example dan Settings (agents.md §8.1 Uji 8.1).

Memastikan setiap kunci di .env.example didefinisikan di Settings dan sebaliknya,
mencegah configuration drift dan kesalahan runtime.
"""

import sys
from pathlib import Path

# Memastikan backend directory berada pada sys.path untuk impor langsung
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import Settings


def get_env_example_path() -> Path:
    candidates = [
        Path(__file__).resolve().parents[2] / ".env.example",  # root workspace
        Path(__file__).resolve().parents[1] / ".env.example",  # backend directory
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError("Berkas .env.example tidak ditemukan di root maupun backend/")


def parse_env_keys(env_file_path: Path) -> set[str]:
    keys = set()
    with open(env_file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                if key:
                    keys.add(key)
    return keys


def parse_env_dict(env_file_path: Path) -> dict[str, str]:
    env_dict = {}
    with open(env_file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                key, val = stripped.split("=", 1)
                env_dict[key.strip()] = val.strip()
    return env_dict


def test_env_parity():
    """Setiap kunci di .env.example harus ada di Settings dan sebaliknya."""
    env_path = get_env_example_path()
    env_keys = parse_env_keys(env_path)
    settings_keys = set(Settings.model_fields.keys())

    missing_in_settings = env_keys - settings_keys
    missing_in_env_example = settings_keys - env_keys

    assert not missing_in_settings, f"Kunci ada di .env.example tetapi tidak di Settings: {missing_in_settings}"
    assert not missing_in_env_example, f"Kunci ada di Settings tetapi tidak di .env.example: {missing_in_env_example}"
    assert env_keys == settings_keys


def test_settings_can_load_from_env_example():
    """Settings harus dapat diinstansiasi menggunakan nilai contoh dari .env.example."""
    env_path = get_env_example_path()
    env_data = parse_env_dict(env_path)

    settings = Settings(**env_data)

    assert settings.CHAT_MODEL == "meta-llama/llama-3.1-8b-instruct"
    assert settings.EMBEDDING_MODEL == "openai/text-embedding-3-small"
    assert settings.RAG_MIN_COSINE == 0.35
    assert settings.RAG_HIGH_COSINE == 0.55
    assert settings.RAG_RRF_K == 60
    assert settings.AGENT_MAX_STEPS == 4
    assert settings.AGENT_MAX_CLARIFICATIONS == 2
    assert settings.AGENT_MAX_LLM_CALLS_PER_TURN == 3
    assert settings.INPUT_MAX_CHARS == 1000
    assert settings.LLM_MAX_TOKENS == 700
