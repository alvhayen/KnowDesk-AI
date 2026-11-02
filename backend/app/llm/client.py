"""Klien komunikasi OpenRouter API asinkron (agents.md §2 R7, §4, §6.7).

Mencatat penggunaan token aktual (prompt_tokens & completion_tokens) langsung dari
respons API tanpa konstanta estimasi (Aturan R7). Mendukung function calling.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import Settings


@dataclass
class LLMResponse:
    """Hasil panggilan chat completion OpenRouter."""

    content: str
    tool_calls: list[dict[str, Any]]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    latency_ms: int
    raw_response: dict[str, Any]


class LLMClient:
    """Klien OpenRouter API untuk inferensi agen KnowDesk AI."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        """Memanggil endpoint chat completions OpenRouter dengan pelacakan token riil.

        Args:
            messages: Daftar riwayat pesan percakapan.
            tools: Skema tools yang diizinkan untuk giliran ini.
            tool_choice: Opsi pemilihan tool ('auto', 'required', atau tool tertentu).
            max_tokens: Batas token keluaran (default dari konfigurasi).
            temperature: Derajat kreativitas model.

        Returns:
            LLMResponse memuat konten, pemanggilan tool, dan token aktual.
        """
        api_key = self.settings.OPENROUTER_API_KEY.strip()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/knowdesk-ai",
            "X-Title": "KnowDesk AI Orchestrator",
        }

        payload: dict[str, Any] = {
            "model": self.settings.CHAT_MODEL,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.settings.LLM_TEMPERATURE,
            "max_tokens": max_tokens or self.settings.LLM_MAX_TOKENS,
        }

        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice

        # Cegah pemborosan token pada reasoning model di OpenRouter (R7, R17)
        if "nemotron" in self.settings.CHAT_MODEL.lower():
            payload["reasoning"] = {"effort": "none"}

        start_time = datetime.now(UTC)
        async with httpx.AsyncClient(timeout=self.settings.LLM_TIMEOUT_S) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            latency_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            if resp.status_code != 200:
                # Upayakan retry 1x untuk transient error (agents.md §6.7)
                if resp.status_code in (429, 500, 502, 503, 504):
                    retry_start = datetime.now(UTC)
                    resp = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    latency_ms += int((datetime.now(UTC) - retry_start).total_seconds() * 1000)

                if resp.status_code != 200:
                    raise RuntimeError(
                        f"OpenRouter API error (status {resp.status_code}): {resp.text}"
                    )

            data = resp.json()
            choice = data.get("choices", [{}])[0]
            message_obj = choice.get("message", {})
            content = message_obj.get("content") or ""
            tool_calls = message_obj.get("tool_calls") or []

            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens") or 0
            completion_tokens = usage.get("completion_tokens") or 0
            total_tokens = usage.get("total_tokens") or (prompt_tokens + completion_tokens)

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                model=data.get("model", self.settings.CHAT_MODEL),
                latency_ms=latency_ms,
                raw_response=data,
            )
