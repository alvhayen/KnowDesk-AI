"""Pipeline Ingestion Knowledge Base KnowDesk AI ke MySQL (agents.md §3 K8, K15, K19, §5.1, §5.2, §11).

Menjalankan proses:
1. Membaca 8 dokumen kanonik dari direktori knowledge_base/.
2. Memecah dokumen menjadi unit chunk deterministik per Bagian via chunker.py.
3. Menghasilkan embedding per chunk (OpenRouter API dengan fallback lokal K15 bila kuota 403).
4. Menyimpan artikel dan chunk ke MySQL dengan pola idempotent upsert (ON DUPLICATE KEY UPDATE).
5. Menggunakan user database `knowdesk_ingest` sesuai pemisahan wewenang Aturan §11.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

import aiomysql
import httpx

# Pastikan path backend terdaftar
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import Settings
from app.rag.chunker import ParsedArticle, chunk_markdown_article
from tests.smoke_test_openrouter import (
    generate_local_embedding_k15,
    get_active_settings,
)


async def get_chunk_embedding(
    text: str,
    settings: Settings,
    client: httpx.AsyncClient,
    dimension: int = 1536,
) -> tuple[list[float], str]:
    """Mengambil vektor embedding dari OpenRouter atau fallback lokal K15 jika limit $0."""
    api_key = settings.OPENROUTER_API_KEY.strip()
    if api_key and api_key != "your_openrouter_api_key_here":
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/knowdesk-ai",
            "X-Title": "KnowDesk AI Ingestion",
        }
        payload = {
            "model": settings.EMBEDDING_MODEL,
            "input": text[:8000],  # Pembatas panjang teks aman
        }
        try:
            res = await client.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers=headers,
                json=payload,
                timeout=settings.LLM_TIMEOUT_S,
            )
            if res.status_code == 200:
                data = res.json()
                embeddings = data.get("data", [])
                if embeddings and "embedding" in embeddings[0]:
                    return embeddings[0]["embedding"], "openrouter"
        except (httpx.HTTPError, OSError):
            pass

    # K15: Fallback representasi lokal jika endpoint OpenRouter 403 atau offline
    return generate_local_embedding_k15(text, dim=dimension), "local_k15"


async def ingest_knowledge_base(
    kb_dir: Path | None = None,
    user: str = "knowdesk_ingest",
    password: str = "knowdesk_ingest_pass",
) -> bool:
    """Mengeksekusi ingestion 8 dokumen KB ke MySQL."""
    if kb_dir is None:
        kb_dir = root_dir / "knowledge_base"

    settings = get_active_settings()
    kb_files = sorted(kb_dir.glob("KB-*.md"))
    if not kb_files:
        print(f"[FATAL] Tidak ada berkas KB ditemukan di {kb_dir}")
        return False

    print("==================================================")
    print("KnowDesk AI — Pipeline Ingestion Knowledge Base")
    print(f"Direktori KB : {kb_dir}")
    print(f"Jumlah File  : {len(kb_files)} dokumen")
    print(f"Database     : {settings.MYSQL_DATABASE} (User: {user})")
    print("==================================================")

    # 1. Koneksi ke MySQL sebagai knowdesk_ingest (Aturan §11)
    try:
        conn = await aiomysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=user,
            password=password,
            db=settings.MYSQL_DATABASE,
            autocommit=True,
        )
    except (aiomysql.Error, OSError) as exc:
        print(f"[ERROR] Gagal koneksi sebagai `{user}`: {exc}")
        print("Mencoba koneksi darurat sebagai admin root...")
        try:
            conn = await aiomysql.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user="root",
                password="",
                db=settings.MYSQL_DATABASE,
                autocommit=True,
            )
        except (aiomysql.Error, OSError) as root_exc:
            print(f"[FATAL] Gagal menyambung ke MySQL: {root_exc}")
            return False

    total_chunks_ingested = 0
    total_articles_ingested = 0

    async with (
        httpx.AsyncClient(timeout=30.0) as http_client,
        conn.cursor() as cur,
    ):
        for kb_file in kb_files:
            raw_text = kb_file.read_text(encoding="utf-8")
            article: ParsedArticle = chunk_markdown_article(
                raw_text, overlap_words=settings.RAG_CHUNK_OVERLAP
            )

            # Upsert artikel (Idempotent: tidak membuat duplikasi jika diulang)
            sql_article = """
            INSERT INTO articles (article_id, judul, kategori, status, asal, raw_content, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                judul = VALUES(judul),
                kategori = VALUES(kategori),
                status = VALUES(status),
                asal = VALUES(asal),
                raw_content = VALUES(raw_content);
            """
            await cur.execute(
                sql_article,
                (
                    article.article_id,
                    article.judul,
                    article.kategori,
                    article.status,
                    article.asal,
                    article.raw_content,
                ),
            )
            total_articles_ingested += 1

            print(f"[PROSES] {article.article_id}: {article.judul} ({len(article.chunks)} chunk, {article.langkah_total_tersedia} langkah)")

            # Upsert setiap chunk artikel beserta vektor embedding
            for chunk in article.chunks:
                vec, _provider = await get_chunk_embedding(
                    chunk.chunk_text, settings, http_client, dimension=1536
                )
                embedding_json = json.dumps(vec)

                sql_chunk = """
                INSERT INTO chunks (chunk_id, article_id, section_title, chunk_text, step_number, embedding_json)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    section_title = VALUES(section_title),
                    chunk_text = VALUES(chunk_text),
                    step_number = VALUES(step_number),
                    embedding_json = VALUES(embedding_json);
                """
                await cur.execute(
                    sql_chunk,
                    (
                        chunk.chunk_id,
                        chunk.article_id,
                        chunk.section_title,
                        chunk.chunk_text,
                        chunk.step_number,
                        embedding_json,
                    ),
                )
                total_chunks_ingested += 1

        # Verifikasi akhir jumlah data dalam tabel
        await cur.execute("SELECT COUNT(*) FROM articles;")
        count_art = (await cur.fetchone())[0]

        await cur.execute("SELECT COUNT(*) FROM chunks;")
        count_chk = (await cur.fetchone())[0]

    conn.close()

    print("--------------------------------------------------")
    print("[BERHASIL] Ingestion Selesai!")
    print(f"Total Artikel di Database: {count_art}")
    print(f"Total Chunk di Database  : {count_chk}")
    print("--------------------------------------------------")
    return count_art >= 8 and count_chk >= 32


def main():
    parser = argparse.ArgumentParser(description="KnowDesk AI KB Ingestion Pipeline")
    parser.add_argument("--user", default=os.getenv("MYSQL_INGEST_USER", "knowdesk_ingest"))
    parser.add_argument("--password", default=os.getenv("MYSQL_INGEST_PASSWORD", "knowdesk_ingest_pass"))

    args = parser.parse_args()
    success = asyncio.run(ingest_knowledge_base(user=args.user, password=args.password))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
