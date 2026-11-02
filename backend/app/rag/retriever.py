"""Engine retrieval hybrid / similarity untuk RAG KnowDesk AI (agents.md §3 K1, §6.4).

Menggunakan cosine similarity (numpy) terhadap embedding chunk yang tersimpan di MySQL.
Menerapkan gerbang ambang batas empiris RAG_MIN_COSINE dan perhitungan keyakinan.
"""

import json
from dataclasses import dataclass
from typing import Any

import numpy as np

from app.config import Settings
from app.db import Database, db
from app.rag.embedder import get_text_embedding


@dataclass
class SearchResult:
    """Hasil pencarian artikel dan chunk."""

    top_article_id: str | None
    top_score: float
    passed_gate: bool
    keyakinan: str
    chunks: list[dict[str, Any]]


def calculate_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Menghitung cosine similarity antara dua vektor embedding."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


async def search_knowledge_base(
    query: str,
    database: Database | None = None,
    settings: Settings | None = None,
) -> SearchResult:
    """Mencari chunk relevan di knowledge base berdasarkan kueri pengguna (agents.md §6.4).

    Args:
        query: Kueri pencarian gejala IT.
        database: Objek akses basis data MySQL.
        settings: Pengaturan konfigurasi aplikasi.

    Returns:
        SearchResult berisi artikel teratas, skor top-1, status gerbang, dan keyakinan.
    """
    database = database or db
    settings = settings or Settings()

    # 1. Ambil embedding kueri
    raw_vec, _ = await get_text_embedding(query, settings)
    query_vec = np.array(raw_vec, dtype=np.float32)

    # 2. Ambil seluruh chunk dari database
    chunks_data = await database.get_all_chunks()
    if not chunks_data:
        return SearchResult(
            top_article_id=None,
            top_score=0.0,
            passed_gate=False,
            keyakinan="tidak_dapat_ditentukan",
            chunks=[],
        )

    # 3. Hitung cosine similarity terhadap seluruh chunk
    scored_chunks = []
    for c in chunks_data:
        raw_emb = c.get("embedding_json")
        if isinstance(raw_emb, str):
            emb = json.loads(raw_emb)
        else:
            emb = raw_emb
        chunk_vec = np.array(emb, dtype=np.float32)
        score = calculate_cosine_similarity(query_vec, chunk_vec)
        scored_chunks.append({**c, "score": score})

    # 4. Urutkan berdasarkan skor tertinggi
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    top_chunk = scored_chunks[0]
    top_score = top_chunk["score"]
    top_article_id = top_chunk["article_id"]

    # 5. Evaluasi gerbang ambang batas (K1: cosine top-1 >= RAG_MIN_COSINE)
    passed_gate = top_score >= settings.RAG_MIN_COSINE

    # 6. Tentukan keyakinan (§6.4)
    if not passed_gate:
        keyakinan = "tidak_dapat_ditentukan"
    elif top_score >= settings.RAG_HIGH_COSINE:
        keyakinan = "tinggi"
    else:
        keyakinan = "sedang"

    # Filter chunk yang lolos ambang batas (maksimal RAG_MAX_RESULTS)
    filtered_chunks = [c for c in scored_chunks if c["score"] >= settings.RAG_MIN_COSINE][
        : settings.RAG_MAX_RESULTS
    ]

    return SearchResult(
        top_article_id=top_article_id if passed_gate else None,
        top_score=round(top_score, 4),
        passed_gate=passed_gate,
        keyakinan=keyakinan,
        chunks=filtered_chunks,
    )
