"""Smoke test mandiri untuk integrasi OpenRouter API (agents.md §2 R7, §3 K15, §12 M0).

Menguji:
1. Panggilan Chat Completion dengan Function Calling / Tool Call.
2. Panggilan Embedding (K15).
3. Pencatatan usage token riil dari respons API (R7).
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

# Pastikan backend berada di sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import Settings
from pydantic import ValidationError

from tests.test_env_parity import get_env_example_path, parse_env_dict


def get_active_settings() -> Settings:
    """Memuat Settings dari .env jika ada, atau menggunakan .env.example untuk pengujian."""
    try:
        return Settings()
    except (ValidationError, ValueError):
        env_data = parse_env_dict(get_env_example_path())
        return Settings(**env_data)


async def execute_openrouter_chat_smoke(settings: Settings) -> dict:
    """Menjalankan 1 panggilan chat completion nyata dengan tool calling ke OpenRouter."""
    api_key = settings.OPENROUTER_API_KEY.strip()
    if not api_key or api_key == "your_openrouter_api_key_here":
        return {
            "status": "skipped",
            "reason": "OPENROUTER_API_KEY belum dikonfigurasi di .env",
            "model": settings.CHAT_MODEL,
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/knowdesk-ai",
        "X-Title": "KnowDesk AI Smoke Test",
    }

    # Definisi tool uji: search_kb (salah satu dari 3 tool wajib K=3)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_kb",
                "description": "Mencari artikel bantuan IT berdasarkan kueri gejala masalah pengguna",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Kata kunci atau gejala masalah IT",
                        }
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    payload = {
        "model": settings.CHAT_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Wi-Fi di lantai 2 kantor mendadak putus-putus. Tolong cari artikel solusinya.",
            }
        ],
        "tools": tools,
        "tool_choice": "auto",
        "temperature": settings.LLM_TEMPERATURE,
        "max_tokens": settings.LLM_MAX_TOKENS,
    }

    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_S) as client:
        start_time = datetime.now(UTC)
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        latency_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        if response.status_code != 200:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "error": response.text,
                "latency_ms": latency_ms,
                "model": settings.CHAT_MODEL,
            }

        data = response.json()
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls", [])
        usage = data.get("usage", {})

        return {
            "status": "passed",
            "status_code": 200,
            "model": data.get("model", settings.CHAT_MODEL),
            "supports_tool_calls": len(tool_calls) > 0,
            "tool_calls": tool_calls,
            "message_content": message.get("content"),
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
            },
            "latency_ms": latency_ms,
        }


async def execute_openrouter_embedding_smoke(settings: Settings) -> dict:
    """Menjalankan 1 panggilan embedding nyata ke OpenRouter (K15)."""
    api_key = settings.OPENROUTER_API_KEY.strip()
    if not api_key or api_key == "your_openrouter_api_key_here":
        return {
            "status": "skipped",
            "reason": "OPENROUTER_API_KEY belum dikonfigurasi di .env",
            "model": settings.EMBEDDING_MODEL,
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/knowdesk-ai",
        "X-Title": "KnowDesk AI Smoke Test",
    }

    payload = {
        "model": settings.EMBEDDING_MODEL,
        "input": "Koneksi Wi-Fi kantor tidak stabil dan sering terputus.",
    }

    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_S) as client:
        start_time = datetime.now(UTC)
        response = await client.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers=headers,
            json=payload,
        )
        latency_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        if response.status_code != 200:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "error": response.text,
                "latency_ms": latency_ms,
                "model": settings.EMBEDDING_MODEL,
            }

        data = response.json()
        embeddings = data.get("data", [])
        dim = len(embeddings[0].get("embedding", [])) if embeddings else 0
        usage = data.get("usage", {})

        return {
            "status": "passed",
            "status_code": 200,
            "model": data.get("model", settings.EMBEDDING_MODEL),
            "embedding_dimension": dim,
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens"),
                "total_tokens": usage.get("total_tokens"),
            },
            "latency_ms": latency_ms,
        }


@pytest.mark.asyncio
async def test_smoke_openrouter_chat_and_tools():
    """Uji chat completion OpenRouter dengan function calling."""
    settings = get_active_settings()
    result = await execute_openrouter_chat_smoke(settings)
    if result["status"] == "skipped":
        pytest.skip(result["reason"])
    assert result["status"] == "passed"
    assert result["usage"]["prompt_tokens"] is not None
    assert result["usage"]["completion_tokens"] is not None


@pytest.mark.asyncio
async def test_smoke_openrouter_embedding():
    """Uji embedding OpenRouter (K15)."""
    settings = get_active_settings()
    result = await execute_openrouter_embedding_smoke(settings)
    if result["status"] == "skipped":
        pytest.skip(result["reason"])
    assert result["status"] == "passed"
    assert result["embedding_dimension"] > 0
    assert result["usage"]["prompt_tokens"] is not None


if __name__ == "__main__":
    import asyncio

    async def main():
        settings = get_active_settings()
        print(f"--- Smoke Test OpenRouter ({settings.CHAT_MODEL}) ---")
        chat_res = await execute_openrouter_chat_smoke(settings)
        print("Chat Result:", json.dumps(chat_res, indent=2))

        print(f"\n--- Smoke Test Embedding ({settings.EMBEDDING_MODEL}) ---")
        embed_res = await execute_openrouter_embedding_smoke(settings)
        print("Embedding Result:", json.dumps(embed_res, indent=2))

    asyncio.run(main())
