"""Modul pembangkitan vektor embedding untuk KnowDesk AI (agents.md §3 K15, §4).

Mendukung panggilan embedding via OpenRouter API dan fallback deterministik lokal K15.
"""


import logging

import httpx
from scripts.ingest_kb import generate_local_embedding_k15

from app.config import Settings

logger = logging.getLogger(__name__)


async def get_text_embedding(
    text: str,
    settings: Settings | None = None,
    client: httpx.AsyncClient | None = None,
    dimension: int = 1536,
) -> tuple[list[float], str]:
    """Mengambil vektor embedding dari OpenRouter atau fallback lokal K15."""
    settings = settings or Settings()
    api_key = settings.OPENROUTER_API_KEY.strip()

    if api_key and api_key != "your_openrouter_api_key_here":
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/knowdesk-ai",
            "X-Title": "KnowDesk AI Embedder",
        }
        payload = {
            "model": settings.EMBEDDING_MODEL,
            "input": text[:8000],
        }

        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_S)
            should_close = True

        try:
            res = await client.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers=headers,
                json=payload,
            )
            if res.status_code == 200:
                data = res.json()
                embeddings = data.get("data", [])
                if embeddings and "embedding" in embeddings[0]:
                    return embeddings[0]["embedding"], "openrouter"
        except (httpx.HTTPError, OSError, KeyError) as err:
            logger.debug("Gagal mengambil embedding OpenRouter, menggunakan fallback K15: %s", err)
        finally:
            if should_close:
                await client.aclose()

    # K15: Fallback representasi lokal jika endpoint berbayar 403 atau offline
    return generate_local_embedding_k15(text, dim=dimension), "local_k15"
