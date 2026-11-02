"""Modul akses basis data MySQL asinkron berbasis aiomysql (agents.md §3 K9, K16, §4).

Menggunakan query SQL berparameter murni tanpa ORM berat, sesuai prinsip kanonik.
"""

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import aiomysql

from app.config import Settings


class Database:
    """Pengelola koneksi dan query basis data KnowDesk AI."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._pool: aiomysql.Pool | None = None

    async def get_pool(self) -> aiomysql.Pool:
        """Mengambil atau menginisialisasi connection pool aiomysql."""
        if self._pool is None or self._pool.closed:
            self._pool = await aiomysql.create_pool(
                host=self.settings.MYSQL_HOST,
                port=self.settings.MYSQL_PORT,
                user=self.settings.MYSQL_USER,
                password=self.settings.MYSQL_PASSWORD,
                db=self.settings.MYSQL_DATABASE,
                autocommit=True,
                minsize=1,
                maxsize=10,
                charset="utf8mb4",
            )
        return self._pool

    async def close(self) -> None:
        """Menutup connection pool saat shutdown aplikasi."""
        if self._pool and not self._pool.closed:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None

    @asynccontextmanager
    async def cursor(self) -> AsyncGenerator[aiomysql.DictCursor, None]:
        """Context manager untuk mendapatkan cursor DictCursor dari connection pool."""
        pool = await self.get_pool()
        async with pool.acquire() as conn, conn.cursor(aiomysql.DictCursor) as cur:
            yield cur

    # --- Sesi Queries ---

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Mengambil data sesi berdasarkan session_id."""
        async with self.cursor() as cur:
            await cur.execute(
                """
                SELECT session_id, status, current_step, clarification_count,
                       artikel_terpilih, draft_ticket_id, created_at, updated_at
                FROM sessions
                WHERE session_id = %s
                """,
                (session_id,),
            )
            return await cur.fetchone()

    async def create_session(
        self,
        session_id: str,
        status: str = "clarifying",
        current_step: int = 0,
        clarification_count: int = 0,
        artikel_terpilih: str | None = None,
        draft_ticket_id: str | None = None,
    ) -> None:
        """Membuat rekaman sesi baru di basis data."""
        async with self.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO sessions (
                    session_id, status, current_step, clarification_count,
                    artikel_terpilih, draft_ticket_id
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    session_id,
                    status,
                    current_step,
                    clarification_count,
                    artikel_terpilih,
                    draft_ticket_id,
                ),
            )

    async def update_session(
        self,
        session_id: str,
        status: str,
        current_step: int,
        clarification_count: int,
        artikel_terpilih: str | None = None,
        draft_ticket_id: str | None = None,
    ) -> None:
        """Memperbarui state sesi di basis data."""
        async with self.cursor() as cur:
            await cur.execute(
                """
                UPDATE sessions
                SET status = %s,
                    current_step = %s,
                    clarification_count = %s,
                    artikel_terpilih = %s,
                    draft_ticket_id = %s
                WHERE session_id = %s
                """,
                (
                    status,
                    current_step,
                    clarification_count,
                    artikel_terpilih,
                    draft_ticket_id,
                    session_id,
                ),
            )

    # --- Artikel & Chunk Queries ---

    async def get_published_article(self, article_id: str) -> dict[str, Any] | None:
        """Mengambil artikel bertatus published."""
        async with self.cursor() as cur:
            await cur.execute(
                """
                SELECT article_id, judul, kategori, status, asal, raw_content
                FROM articles
                WHERE article_id = %s AND status = 'published'
                """,
                (article_id,),
            )
            return await cur.fetchone()

    async def get_all_chunks(self) -> list[dict[str, Any]]:
        """Mengambil seluruh data chunk untuk pencarian similarity."""
        async with self.cursor() as cur:
            await cur.execute(
                """
                SELECT chunk_id, article_id, section_title, chunk_text,
                       step_number, embedding_json
                FROM chunks
                """
            )
            return await cur.fetchall()

    # --- Tiket Queries ---

    async def create_ticket(
        self,
        ticket_id: str,
        session_id: str,
        summary: str,
        steps_tried: list[str],
        category: str = "lainnya",
        user_id: str | None = None,
        status: str = "draft",
    ) -> None:
        """Menyimpan tiket baru (status awal 'draft')."""
        async with self.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO tickets (
                    ticket_id, session_id, user_id, category, summary,
                    steps_tried, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    ticket_id,
                    session_id,
                    user_id,
                    category,
                    summary,
                    json.dumps(steps_tried, ensure_ascii=False),
                    status,
                ),
            )

    async def get_ticket(self, ticket_id: str) -> dict[str, Any] | None:
        """Mengambil data tiket berdasarkan ticket_id."""
        async with self.cursor() as cur:
            await cur.execute(
                """
                SELECT ticket_id, session_id, user_id, category, summary,
                       steps_tried, status, created_at
                FROM tickets
                WHERE ticket_id = %s
                """,
                (ticket_id,),
            )
            return await cur.fetchone()

    async def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """Mengubah status tiket (misal: 'confirmed' atau 'cancelled')."""
        async with self.cursor() as cur:
            await cur.execute(
                "UPDATE tickets SET status = %s WHERE ticket_id = %s",
                (status, ticket_id),
            )
            return cur.rowcount > 0

    # --- Trace Queries ---

    async def record_trace(
        self,
        trace_id: str,
        session_id: str,
        action_type: str,
        tool_called: str | None = None,
        parameters: dict[str, Any] | None = None,
        decision: str | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        model: str = "",
        latency_ms: int = 0,
    ) -> None:
        """Mencatat jejak eksekusi agen dan token aktual ke tabel agent_traces (Aturan R7)."""
        async with self.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO agent_traces (
                    trace_id, session_id, action_type, tool_called, parameters,
                    decision, prompt_tokens, completion_tokens, model, latency_ms
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    trace_id,
                    session_id,
                    action_type,
                    tool_called,
                    json.dumps(parameters, ensure_ascii=False) if parameters else None,
                    decision,
                    prompt_tokens,
                    completion_tokens,
                    model,
                    latency_ms,
                ),
            )

    async def get_session_traces(self, session_id: str) -> list[dict[str, Any]]:
        """Mengambil seluruh jejak audit dalam satu sesi."""
        async with self.cursor() as cur:
            await cur.execute(
                """
                SELECT trace_id, session_id, action_type, tool_called, parameters,
                       decision, prompt_tokens, completion_tokens, model,
                       latency_ms, created_at
                FROM agent_traces
                WHERE session_id = %s
                ORDER BY created_at ASC
                """,
                (session_id,),
            )
            return await cur.fetchall()


# Singleton instance default
db = Database()
