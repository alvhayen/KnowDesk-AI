"""Smoke test mandiri untuk konektivitas basis data MySQL via aiomysql (agents.md §4, §12 M0).

Menguji:
1. Koneksi async ke host & port MySQL lokal.
2. Query sederhana `SELECT 1, VERSION()` untuk verifikasi kesiapan database.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import aiomysql
import pytest

# Pastikan backend berada di sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import Settings

from tests.smoke_test_openrouter import get_active_settings


async def execute_mysql_smoke(settings: Settings) -> dict:
    """Menjalankan pengujian konektivitas async ke database MySQL."""
    start_time = datetime.now(UTC)
    try:
        conn = await aiomysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DATABASE,
            connect_timeout=5,
            autocommit=True,
        )
        latency_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT 1 AS ok, VERSION() AS db_version;")
            row = await cur.fetchone()

        conn.close()

        return {
            "status": "passed",
            "host": settings.MYSQL_HOST,
            "port": settings.MYSQL_PORT,
            "database": settings.MYSQL_DATABASE,
            "db_version": row.get("db_version") if row else None,
            "latency_ms": latency_ms,
        }

    except (aiomysql.Error, OSError, ConnectionError, TimeoutError) as e:
        latency_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
        return {
            "status": "failed",
            "host": settings.MYSQL_HOST,
            "port": settings.MYSQL_PORT,
            "database": settings.MYSQL_DATABASE,
            "error": str(e),
            "error_type": type(e).__name__,
            "latency_ms": latency_ms,
        }


@pytest.mark.asyncio
async def test_smoke_mysql_connectivity():
    """Uji konektivitas basis data MySQL."""
    settings = get_active_settings()
    result = await execute_mysql_smoke(settings)
    if result["status"] == "failed":
        pytest.fail(f"Gagal koneksi ke MySQL ({settings.MYSQL_HOST}:{settings.MYSQL_PORT}): {result.get('error')}")
    assert result["status"] == "passed"
    assert result["db_version"] is not None


if __name__ == "__main__":
    import asyncio

    async def main():
        settings = get_active_settings()
        print(f"--- Smoke Test MySQL ({settings.MYSQL_HOST}:{settings.MYSQL_PORT}) ---")
        res = await execute_mysql_smoke(settings)
        print("MySQL Result:", json.dumps(res, indent=2))

    asyncio.run(main())
