"""Script Python pembuat dan konfigurasi hak akses pengguna basis data (agents.md §11).

Menegakkan pemisahan wewenang Lapis 3 di tingkat basis data:
1. knowdesk_ingest : Akses penuh DDL & DML pada tabel articles dan chunks.
2. knowdesk_app    : HANYA hak SELECT pada articles & chunks, serta SELECT, INSERT, UPDATE
                     pada sessions, tickets, dan agent_traces. Dilarang keras hak DROP atau ALTER.
"""

import argparse
import asyncio
import os
import sys

import aiomysql


async def setup_database_users(
    host: str = "localhost",
    port: int = 3306,
    admin_user: str = "root",
    admin_password: str = "",
    database: str = "knowdesk_ai",
    app_password: str = "knowdesk_app_pass",
    ingest_password: str = "knowdesk_ingest_pass",
) -> bool:
    """Mengonfigurasi akun database terpisah untuk runtime aplikasi dan proses ingestion."""
    print("==================================================")
    print("KnowDesk AI — Database Users Setup (Aturan §11)")
    print(f"Server Target : {host}:{port}")
    print(f"Database      : {database}")
    print("==================================================")

    try:
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=admin_user,
            password=admin_password,
            autocommit=True,
        )
    except (aiomysql.Error, OSError) as exc:
        print(f"[FATAL] Gagal menyambung sebagai admin ({admin_user}): {exc}")
        print("Risiko: Konfigurasi keamanan user database tidak dapat diterapkan.")
        return False

    try:
        async with conn.cursor() as cur:
            # 1. Buat user jika belum ada
            sql_create_users = [
                f"CREATE USER IF NOT EXISTS 'knowdesk_ingest'@'localhost' IDENTIFIED BY '{ingest_password}';",
                f"CREATE USER IF NOT EXISTS 'knowdesk_ingest'@'%' IDENTIFIED BY '{ingest_password}';",
                f"CREATE USER IF NOT EXISTS 'knowdesk_app'@'localhost' IDENTIFIED BY '{app_password}';",
                f"CREATE USER IF NOT EXISTS 'knowdesk_app'@'%' IDENTIFIED BY '{app_password}';",
            ]
            for stmt in sql_create_users:
                await cur.execute(stmt)

            # 2. Hak knowdesk_ingest: DDL dan DML penuh pada articles dan chunks
            sql_grant_ingest = [
                f"GRANT ALL PRIVILEGES ON `{database}`.articles TO 'knowdesk_ingest'@'localhost';",
                f"GRANT ALL PRIVILEGES ON `{database}`.articles TO 'knowdesk_ingest'@'%';",
                f"GRANT ALL PRIVILEGES ON `{database}`.chunks TO 'knowdesk_ingest'@'localhost';",
                f"GRANT ALL PRIVILEGES ON `{database}`.chunks TO 'knowdesk_ingest'@'%';",
            ]
            for stmt in sql_grant_ingest:
                await cur.execute(stmt)
            print("[OK] User `knowdesk_ingest` dikonfigurasi (Hak DDL/DML articles & chunks).")

            # 3. Hak knowdesk_app: HANYA SELECT pada articles & chunks
            sql_grant_app_read = [
                f"GRANT SELECT ON `{database}`.articles TO 'knowdesk_app'@'localhost';",
                f"GRANT SELECT ON `{database}`.articles TO 'knowdesk_app'@'%';",
                f"GRANT SELECT ON `{database}`.chunks TO 'knowdesk_app'@'localhost';",
                f"GRANT SELECT ON `{database}`.chunks TO 'knowdesk_app'@'%';",
            ]
            for stmt in sql_grant_app_read:
                await cur.execute(stmt)

            # Hak SELECT, INSERT, UPDATE pada sessions, tickets, agent_traces
            sql_grant_app_write = [
                f"GRANT SELECT, INSERT, UPDATE ON `{database}`.sessions TO 'knowdesk_app'@'localhost';",
                f"GRANT SELECT, INSERT, UPDATE ON `{database}`.sessions TO 'knowdesk_app'@'%';",
                f"GRANT SELECT, INSERT, UPDATE ON `{database}`.tickets TO 'knowdesk_app'@'localhost';",
                f"GRANT SELECT, INSERT, UPDATE ON `{database}`.tickets TO 'knowdesk_app'@'%';",
                f"GRANT SELECT, INSERT, UPDATE ON `{database}`.agent_traces TO 'knowdesk_app'@'localhost';",
                f"GRANT SELECT, INSERT, UPDATE ON `{database}`.agent_traces TO 'knowdesk_app'@'%';",
            ]
            for stmt in sql_grant_app_write:
                await cur.execute(stmt)
            print("[OK] User `knowdesk_app` dikonfigurasi (Hanya SELECT articles/chunks & INSERT/UPDATE state).")

            await cur.execute("FLUSH PRIVILEGES;")
            print("[BERHASIL] Seluruh hak akses berhasil diperbarui dan disinkronkan.")
            return True

    except (aiomysql.Error, OSError) as exc:
        print(f"[ERROR] Gagal mengonfigurasi user database: {exc}")
        print("Risiko: Hak akses pengguna mungkin belum terisolasi sesuai aturan keamanan §11.")
        return False
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="KnowDesk AI Database Users Setup")
    parser.add_argument("--host", default=os.getenv("MYSQL_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MYSQL_PORT", "3306")))
    parser.add_argument("--admin-user", default=os.getenv("MYSQL_ROOT_USER", "root"))
    parser.add_argument("--admin-password", default=os.getenv("MYSQL_ROOT_PASSWORD", ""))
    parser.add_argument("--db", default=os.getenv("MYSQL_DATABASE", "knowdesk_ai"))
    parser.add_argument("--app-pass", default="knowdesk_app_pass")
    parser.add_argument("--ingest-pass", default="knowdesk_ingest_pass")

    args = parser.parse_args()

    success = asyncio.run(
        setup_database_users(
            host=args.host,
            port=args.port,
            admin_user=args.admin_user,
            admin_password=args.admin_password,
            database=args.db,
            app_password=args.app_pass,
            ingest_password=args.ingest_pass,
        )
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
