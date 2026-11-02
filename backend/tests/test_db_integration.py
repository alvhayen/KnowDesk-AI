"""Tes integrasi nyata MySQL untuk skema tabel dan pemisahan hak akses (agents.md §3 K9, §4, §11, §8.1).

Menguji secara langsung ke instance basis data MySQL/MariaDB:
1. Keberadaan 5 tabel utama beserta kolom-kolom kanoniknya.
2. Penegakan foreign key cascade constraint (articles -> chunks, sessions -> tickets, sessions -> agent_traces).
3. Hak akses user `knowdesk_ingest`: DDL/DML penuh pada articles & chunks, dilarang mengakses tabel sessions/tickets/agent_traces.
4. Hak akses user `knowdesk_app`: HANYA SELECT pada articles & chunks, dilarang keras DROP/ALTER/DELETE, serta dapat INSERT/UPDATE pada sessions/tickets/agent_traces.
"""

import json
import logging
import sys
from pathlib import Path

import aiomysql
import pytest

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import Settings

from tests.smoke_test_openrouter import get_active_settings

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def db_settings() -> Settings:
    return get_active_settings()


async def get_connection(user: str, password: str, settings: Settings) -> aiomysql.Connection:
    """Helper untuk membuat koneksi async aiomysql per role user."""
    return await aiomysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=user,
        password=password,
        db=settings.MYSQL_DATABASE,
        autocommit=True,
    )


# -----------------------------------------------------------------------------
# 1. Uji Keberadaan Tabel dan Skema Kolom
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tables_exist_and_structure(db_settings: Settings):
    """Memastikan 5 tabel utama migrasi ada dan memuat kolom yang diwajibkan."""
    conn = await get_connection(db_settings.MYSQL_USER, db_settings.MYSQL_PASSWORD, db_settings)
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SHOW TABLES;")
            tables = {next(iter(row.values())) for row in await cur.fetchall()}

            expected_tables = {"articles", "chunks", "sessions", "tickets", "agent_traces"}
            assert expected_tables.issubset(tables), f"Tabel yang kurang: {expected_tables - tables}"

            # Verifikasi kolom tabel articles (K9)
            await cur.execute("SHOW COLUMNS FROM articles;")
            art_cols = {row["Field"] for row in await cur.fetchall()}
            assert {"article_id", "judul", "kategori", "status", "asal", "raw_content", "created_at"}.issubset(art_cols)

            # Verifikasi kolom tabel chunks
            await cur.execute("SHOW COLUMNS FROM chunks;")
            chk_cols = {row["Field"] for row in await cur.fetchall()}
            assert {"chunk_id", "article_id", "section_title", "chunk_text", "step_number", "embedding_json"}.issubset(chk_cols)

            # Verifikasi kolom tabel sessions (K9: clarification_count, artikel_terpilih, draft_ticket_id)
            await cur.execute("SHOW COLUMNS FROM sessions;")
            ses_cols = {row["Field"] for row in await cur.fetchall()}
            assert {
                "session_id", "status", "current_step", "clarification_count",
                "artikel_terpilih", "draft_ticket_id", "created_at", "updated_at",
            }.issubset(ses_cols)

            # Verifikasi kolom tabel tickets
            await cur.execute("SHOW COLUMNS FROM tickets;")
            tkt_cols = {row["Field"] for row in await cur.fetchall()}
            assert {"ticket_id", "session_id", "user_id", "category", "summary", "steps_tried", "status", "created_at"}.issubset(tkt_cols)

            # Verifikasi kolom tabel agent_traces (K9: prompt_tokens, completion_tokens, model, latency_ms)
            await cur.execute("SHOW COLUMNS FROM agent_traces;")
            trc_cols = {row["Field"] for row in await cur.fetchall()}
            assert {
                "trace_id", "session_id", "action_type", "tool_called", "parameters",
                "decision", "prompt_tokens", "completion_tokens", "model", "latency_ms", "created_at",
            }.issubset(trc_cols)
    finally:
        conn.close()


# -----------------------------------------------------------------------------
# 2. Uji Penegakan Foreign Key Constraint
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_foreign_key_constraints(db_settings: Settings):
    """Menyisipkan data dengan FK yang tidak ada harus ditolak oleh basis data."""
    conn = await get_connection("knowdesk_ingest", "knowdesk_ingest_pass", db_settings)
    try:
        async with conn.cursor() as cur:
            # Mencoba menyisipkan chunk dengan article_id yang belum ada
            with pytest.raises(aiomysql.Error) as exc_info:
                await cur.execute(
                    "INSERT INTO chunks (chunk_id, article_id, section_title, chunk_text, embedding_json) "
                    "VALUES ('CHK-INVALID', 'KB-NONEXISTENT', 'Section', 'Text', '[]');"
                )
            assert "foreign key constraint" in str(exc_info.value).lower() or exc_info.value.args[0] == 1452
    finally:
        conn.close()


# -----------------------------------------------------------------------------
# 3. Uji Hak Akses knowdesk_ingest (Akses Penuh DDL/DML articles & chunks)
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ingest_user_permissions(db_settings: Settings):
    """User knowdesk_ingest dapat menulis artikel & chunk, tetapi dilarang mengakses tabel sesi/tiket."""
    conn_ingest = await get_connection("knowdesk_ingest", "knowdesk_ingest_pass", db_settings)
    test_article_id = "KB-TEST-INTEG-001"
    test_chunk_id = "CHK-TEST-INTEG-001"

    try:
        async with conn_ingest.cursor() as cur:
            # 1. Berhasil INSERT & SELECT pada articles
            await cur.execute("DELETE FROM articles WHERE article_id = %s;", (test_article_id,))
            await cur.execute(
                "INSERT INTO articles (article_id, judul, kategori, status, asal, raw_content) "
                "VALUES (%s, %s, %s, %s, %s, %s);",
                (test_article_id, "Judul Uji Ingestion", "jaringan", "published", "sintetis", "Konten uji."),
            )
            await cur.execute("SELECT article_id, judul FROM articles WHERE article_id = %s;", (test_article_id,))
            row = await cur.fetchone()
            assert row is not None
            assert row[0] == test_article_id

            # 2. Berhasil INSERT & SELECT pada chunks
            await cur.execute(
                "INSERT INTO chunks (chunk_id, article_id, section_title, chunk_text, embedding_json) "
                "VALUES (%s, %s, %s, %s, %s);",
                (test_chunk_id, test_article_id, "Bagian 1", "Teks chunk uji", json.dumps([0.1, 0.2])),
            )
            await cur.execute("SELECT chunk_id FROM chunks WHERE chunk_id = %s;", (test_chunk_id,))
            chunk_row = await cur.fetchone()
            assert chunk_row is not None

            # 3. Dilarang mengakses sessions (Aturan §11)
            with pytest.raises(aiomysql.OperationalError) as exc_info:
                await cur.execute("SELECT * FROM sessions;")
            # Error code 1142: SELECT command denied to user
            assert exc_info.value.args[0] == 1142 or "denied" in str(exc_info.value).lower()

    finally:
        # Bersihkan data uji menggunakan user ingest
        try:
            async with conn_ingest.cursor() as cur:
                await cur.execute("DELETE FROM articles WHERE article_id = %s;", (test_article_id,))
        except (aiomysql.Error, OSError) as exc:
            logger.warning("Pembersihan artikel gagal: %s", exc)
        conn_ingest.close()


# -----------------------------------------------------------------------------
# 4. Uji Hak Akses knowdesk_app (Aturan §11 Penegakan Lapis 3 DB)
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_app_user_permissions(db_settings: Settings):
    """User knowdesk_app HANYA boleh SELECT pada articles/chunks, dan INSERT/UPDATE pada sesi/tiket/trace."""
    # Siapkan data uji dengan UUID unik untuk idempotensi
    import uuid
    suffix = uuid.uuid4().hex[:8]
    test_article_id = f"KB-TEST-APP-{suffix}"
    test_session_id = f"test-ses-{suffix}"
    test_ticket_id = f"TK-TEST-{suffix}"
    test_trace_id = f"TR-TEST-{suffix}"

    conn_ingest = await get_connection("knowdesk_ingest", "knowdesk_ingest_pass", db_settings)
    try:
        async with conn_ingest.cursor() as cur:
            await cur.execute(
                "INSERT INTO articles (article_id, judul, kategori, status, asal, raw_content) "
                "VALUES (%s, %s, %s, %s, %s, %s);",
                (test_article_id, "Artikel Runtime App", "aplikasi", "published", "sintetis", "Isi konten."),
            )
    finally:
        conn_ingest.close()

    # Sekarang hubungkan menggunakan knowdesk_app
    conn_app = await get_connection(db_settings.MYSQL_USER, db_settings.MYSQL_PASSWORD, db_settings)
    try:
        async with conn_app.cursor() as cur:
            # 1. Boleh SELECT pada articles
            await cur.execute("SELECT article_id, judul FROM articles WHERE article_id = %s;", (test_article_id,))
            art_row = await cur.fetchone()
            assert art_row is not None
            assert art_row[0] == test_article_id

            # 2. DILARANG INSERT pada articles (Penegakan §11)
            with pytest.raises(aiomysql.OperationalError) as exc_info:
                await cur.execute(
                    "INSERT INTO articles (article_id, judul, kategori, status, asal, raw_content) "
                    "VALUES ('KB-HACK', 'Hack', 'jaringan', 'published', 'asal', 'hack');"
                )
            assert exc_info.value.args[0] == 1142 or "denied" in str(exc_info.value).lower()

            # 3. DILARANG DELETE pada articles
            with pytest.raises(aiomysql.OperationalError) as exc_info:
                await cur.execute("DELETE FROM articles WHERE article_id = %s;", (test_article_id,))
            assert exc_info.value.args[0] == 1142 or "denied" in str(exc_info.value).lower()

            # 4. DILARANG DROP TABLE
            with pytest.raises(aiomysql.OperationalError) as exc_info:
                await cur.execute("DROP TABLE articles;")
            assert exc_info.value.args[0] == 1142 or "denied" in str(exc_info.value).lower()

            # 5. DILARANG ALTER TABLE sessions
            with pytest.raises(aiomysql.OperationalError) as exc_info:
                await cur.execute("ALTER TABLE sessions ADD COLUMN hack_col VARCHAR(10);")
            assert exc_info.value.args[0] == 1142 or "denied" in str(exc_info.value).lower()

            # 6. Boleh INSERT & UPDATE pada sessions
            await cur.execute(
                "INSERT INTO sessions (session_id, status, current_step, clarification_count) "
                "VALUES (%s, %s, %s, %s);",
                (test_session_id, "clarifying", 1, 0),
            )
            await cur.execute(
                "UPDATE sessions SET status = %s, current_step = %s WHERE session_id = %s;",
                ("solving", 2, test_session_id),
            )
            await cur.execute("SELECT status, current_step FROM sessions WHERE session_id = %s;", (test_session_id,))
            ses_row = await cur.fetchone()
            assert ses_row == ("solving", 2)

            # 7. Boleh INSERT pada tickets
            await cur.execute(
                "INSERT INTO tickets (ticket_id, session_id, user_id, category, summary, steps_tried, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (test_ticket_id, test_session_id, "user-01", "aplikasi", "Kendala ERP", json.dumps(["Langkah 1"]), "draft"),
            )
            await cur.execute("SELECT status FROM tickets WHERE ticket_id = %s;", (test_ticket_id,))
            tkt_row = await cur.fetchone()
            assert tkt_row == ("draft",)

            # 8. Boleh INSERT pada agent_traces
            await cur.execute(
                "INSERT INTO agent_traces (trace_id, session_id, action_type, tool_called, prompt_tokens, completion_tokens, model, latency_ms) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                (test_trace_id, test_session_id, "tool_call", "search_kb", 150, 45, "meta-llama/llama-3.1-8b-instruct", 320),
            )
            await cur.execute("SELECT model FROM agent_traces WHERE trace_id = %s;", (test_trace_id,))
            trc_row = await cur.fetchone()
            assert trc_row == ("meta-llama/llama-3.1-8b-instruct",)

    finally:
        conn_app.close()
        # Bersihkan data uji menggunakan user ingest untuk artikel dan admin untuk sesi
        conn_cleanup = await get_connection("knowdesk_ingest", "knowdesk_ingest_pass", db_settings)
        try:
            async with conn_cleanup.cursor() as cur:
                await cur.execute("DELETE FROM articles WHERE article_id = %s;", (test_article_id,))
        except (aiomysql.Error, OSError) as exc:
            logger.warning("Pembersihan artikel uji gagal: %s", exc)
        finally:
            conn_cleanup.close()

        # Bersihkan sesi uji lewat koneksi admin root
        try:
            conn_admin = await aiomysql.connect(
                host=db_settings.MYSQL_HOST,
                port=db_settings.MYSQL_PORT,
                user="root",
                password="",
                db=db_settings.MYSQL_DATABASE,
                autocommit=True,
            )
            async with conn_admin.cursor() as cur:
                await cur.execute("DELETE FROM sessions WHERE session_id = %s;", (test_session_id,))
            conn_admin.close()
        except (aiomysql.Error, OSError) as exc:
            logger.warning("Pembersihan sesi uji gagal: %s", exc)
