"""Script eksekusi migrasi DDL otomatis berbasis aiomysql (agents.md §3 K9, K16, §4, §11).

Menjalankan migrasi SQL murni tanpa ORM / Alembic (Batasan K16 & Ponytail Full).
Mendukung pembuatan database, inisialisasi tabel, dan konfigurasi hak akses user.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

import aiomysql

# Pastikan path backend terdaftar
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def read_sql_statements(file_path: Path) -> list[str]:
    """Membaca berkas SQL dan memecahnya menjadi daftar statement yang valid."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    statements = []
    # Bersihkan baris komentar penuh dan kumpulkan statement berdasarkan pemisah titik-koma
    raw_statements = content.split(";")
    for raw in raw_statements:
        lines = []
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.startswith(("--", "/*")):
                continue
            lines.append(line)
        stmt = "\n".join(lines).strip()
        if stmt:
            statements.append(stmt)
    return statements


async def run_migrations(
    host: str = "localhost",
    port: int = 3306,
    user: str = "root",
    password: str = "",
    database: str = "knowdesk_ai",
    migrations_dir: Path | None = None,
    with_users: bool = True,
) -> bool:
    """Mengeksekusi migrasi DDL ke server MySQL lokal via aiomysql."""
    if migrations_dir is None:
        migrations_dir = backend_dir / "migrations"

    print("==================================================")
    print("KnowDesk AI — Database Migration Runner")
    print(f"Target Server: {host}:{port}")
    print(f"Database     : {database}")
    print(f"Admin User   : {user}")
    print("==================================================")

    # 1. Hubungkan ke server MySQL tanpa memilih database dahulu untuk inisialisasi awal
    try:
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connect_timeout=10,
            autocommit=True,
        )
    except (aiomysql.Error, OSError) as exc:
        print(f"[FATAL] Gagal menyambung ke server MySQL ({host}:{port}): {exc}")
        print("Risiko: Sistem database mati atau kredensial salah. Ingestion dan runtime FastAPI tidak akan dapat berfungsi.")
        return False

    try:
        async with conn.cursor() as cur:
            # Pastikan database ada
            await cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
            print(f"[OK] Database `{database}` dipastikan tersedia.")

            # Pindah konteks ke database target
            await cur.execute(f"USE `{database}`;")

            # Urutkan file migrasi berdasarkan nama
            migration_files = sorted(migrations_dir.glob("*.sql"))
            if not with_users:
                migration_files = [f for f in migration_files if not f.name.endswith("_users.sql")]

            for sql_file in migration_files:
                print(f"\n[INFO] Menjalankan migrasi: {sql_file.name}")
                stmts = read_sql_statements(sql_file)
                for idx, stmt in enumerate(stmts, start=1):
                    try:
                        await cur.execute(stmt)
                    except (aiomysql.Error, OSError) as stmt_err:
                        # Abaikan jika user sudah ada atau revoke warning, tetapi laporkan galat lainnya
                        first_line = stmt.strip().splitlines()[0][:60]
                        print(f"  [WARN] Statement #{idx} ({first_line}...): {stmt_err}")

            # 2. Verifikasi status tabel yang berhasil dibuat
            print("\n--------------------------------------------------")
            print("Status Verifikasi Tabel:")
            print("--------------------------------------------------")
            expected_tables = ["articles", "chunks", "sessions", "tickets", "agent_traces"]
            await cur.execute("SHOW TABLES;")
            rows = await cur.fetchall()
            existing_tables = {row[0] for row in rows}

            all_passed = True
            for tbl in expected_tables:
                if tbl in existing_tables:
                    # Ambil jumlah kolom
                    await cur.execute(f"SHOW COLUMNS FROM `{tbl}`;")
                    cols = await cur.fetchall()
                    print(f"  [OK] Tabel `{tbl}`: TERSEDIA ({len(cols)} kolom)")
                else:
                    print(f"  [FAIL] Tabel `{tbl}`: TIDAK DITEMUKAN")
                    all_passed = False

            print("--------------------------------------------------")
            if all_passed:
                print("[BERHASIL] Seluruh tabel skema migrasi berhasil dibuat.")
            else:
                print("[PERINGATAN] Sebagian tabel gagal dibuat. Periksa log eksekusi.")
            return all_passed

    except (aiomysql.Error, OSError) as exc:
        print(f"[ERROR] Terjadi kesalahan selama proses migrasi: {exc}")
        print("Risiko: State skema database berada dalam kondisi tidak konsisten.")
        return False
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="KnowDesk AI Migration Runner")
    parser.add_argument("--host", default=os.getenv("MYSQL_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MYSQL_PORT", "3306")))
    parser.add_argument("--user", default=os.getenv("MYSQL_ROOT_USER", "root"))
    parser.add_argument("--password", default=os.getenv("MYSQL_ROOT_PASSWORD", ""))
    parser.add_argument("--db", default=os.getenv("MYSQL_DATABASE", "knowdesk_ai"))
    parser.add_argument("--skip-users", action="store_true", help="Lewati pembuatan user knowdesk_app & knowdesk_ingest")

    args = parser.parse_args()

    success = asyncio.run(
        run_migrations(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.db,
            with_users=not args.skip_users,
        )
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
