"""Aplikasi utama FastAPI untuk KnowDesk AI (agents.md §4, §6.1, §6.3).

Menyediakan REST API asinkron untuk:
- POST /api/chat (alur percakapan agentik)
- POST /api/ticket/confirm (konfirmasi satu jalur tiket IT)
- GET /api/session/{id} (audit dan pemulihan sesi)
- GET /api/health (pemeriksaan kesehatan layanan)
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.db import db
from app.routes.chat import router as chat_router

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Pengelola siklus hidup startup dan shutdown koneksi basis data."""
    # Inisialisasi pool koneksi database
    await db.get_pool()
    yield
    # Tutup pool koneksi database saat shutdown
    await db.close()


app = FastAPI(
    title="KnowDesk AI API",
    version="1.0.0",
    description="Sistem Bantuan Mandiri IT Agentik untuk Staf Perusahaan",
    lifespan=lifespan,
)

# Konfigurasi CORS
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Daftarkan router
app.include_router(chat_router)


@app.get("/api/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Pemeriksaan status kesehatan server dan backend API."""
    return {"status": "ok", "service": "KnowDesk AI"}
