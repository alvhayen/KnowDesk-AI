"""Definisi skema 3 tool kanonik KnowDesk AI untuk LLM Function Calling (agents.md §3 K6, §6.3, §7).

Tiga tool kanonik (K = 3):
1. search_kb: pencarian hybrid BM25 + cosine.
2. get_article: pembacaan artikel published (read-only).
3. draft_ticket: penyusunan draf tiket (tidak mengirim langsung).
"""

from typing import Literal

from pydantic import BaseModel, Field


class SearchKbArgs(BaseModel):
    """Argumen pemanggilan tool search_kb."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=300,
        description="Kueri pencarian kata kunci atau ringkasan gejala teknis (maksimal 300 karakter).",
    )


class GetArticleArgs(BaseModel):
    """Argumen pemanggilan tool get_article."""

    article_id: str = Field(
        ...,
        pattern=r"^KB-\d{3}$",
        description="ID kanonik artikel yang ditemukan pada hasil pencarian (misal: KB-001).",
    )


class DraftTicketArgs(BaseModel):
    """Argumen pemanggilan tool draft_ticket."""

    judul: str = Field(..., min_length=5, max_length=150, description="Judul ringkas kendala IT.")
    deskripsi: str = Field(..., min_length=10, max_length=1000, description="Rincian kendala.")
    langkah_dicoba: list[str] = Field(
        default_factory=list,
        description="Daftar langkah troubleshooting yang telah dijalankan di sesi ini.",
    )
    prioritas: Literal["rendah", "sedang", "tinggi"] = Field(
        default="sedang",
        description="Tingkat prioritas masalah.",
    )
    kategori: Literal["jaringan", "email", "aplikasi", "perangkat", "lainnya"] = Field(
        default="lainnya",
        description="Kategori kendala IT.",
    )


SEARCH_KB_TOOL = {
    "type": "function",
    "function": {
        "name": "search_kb",
        "description": (
            "Mencari artikel knowledge base IT internal berdasarkan gejala teknis pengguna. "
            "KAPAN DIPAKAI: Gunakan saat gejala masalah pengguna sudah spesifik dan perlu mencari panduan pemecahan masalah. "
            "KAPAN TIDAK DIPAKAI: JANGAN panggil jika gejala pengguna masih sangat ambigu/terlalu umum (lakukan klarifikasi teks), "
            "atau jika pencarian untuk masalah yang sama sudah dilakukan di sesi ini. "
            "BATASAN KEWENANGAN: Hanya membaca (read-only) maksimal 5 hasil dengan timeout 5 detik."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Kueri pencarian atau kata kunci gejala IT (maks 300 karakter).",
                }
            },
            "required": ["query"],
        },
    },
}

GET_ARTICLE_TOOL = {
    "type": "function",
    "function": {
        "name": "get_article",
        "description": (
            "Mengambil isi lengkap artikel knowledge base berdasarkan ID resmi artikel. "
            "KAPAN DIPAKAI: Gunakan setelah search_kb menemukan artikel relevan untuk membaca langkah-langkah solusi. "
            "KAPAN TIDAK DIPAKAI: JANGAN panggil sebelum pencarian dilakukan, dan JANGAN panggil article_id yang tidak ada pada hasil pencarian. "
            "BATASAN KEWENANGAN: Hanya membaca dokumen berstatus 'published'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "article_id": {
                    "type": "string",
                    "description": "ID kanonik artikel (contoh: 'KB-001').",
                }
            },
            "required": ["article_id"],
        },
    },
}

DRAFT_TICKET_TOOL = {
    "type": "function",
    "function": {
        "name": "draft_ticket",
        "description": (
            "Menyusun draf tiket eskalasi bantuan ke teknisi IT. "
            "KAPAN DIPAKAI: Gunakan jika batas 4 langkah solusi tercapai namun masalah belum teratasi, "
            "atau jika artikel solusi tidak ditemukan di knowledge base, atau pengguna meminta tiket. "
            "KAPAN TIDAK DIPAKAI: DILARANG dipanggil di awal percakapan sebelum mencoba pencarian panduan, "
            "dan DILARANG dipanggil jika langkah solusi masih tersedia dan belum dicoba pengguna. "
            "BATASAN KEWENANGAN: HANYA membuat draf; TIDAK mengirimkan tiket ke teknisi sebelum konfirmasi pengguna."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "judul": {
                    "type": "string",
                    "description": "Subjek singkat masalah IT.",
                },
                "deskripsi": {
                    "type": "string",
                    "description": "Deskripsi lengkap gejala kendala.",
                },
                "langkah_dicoba": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Langkah-langkah yang sudah dicoba di sesi ini.",
                },
                "prioritas": {
                    "type": "string",
                    "enum": ["rendah", "sedang", "tinggi"],
                    "description": "Prioritas kendala IT.",
                },
                "kategori": {
                    "type": "string",
                    "enum": ["jaringan", "email", "aplikasi", "perangkat", "lainnya"],
                    "description": "Kategori unit kerja IT.",
                },
            },
            "required": ["judul", "deskripsi", "langkah_dicoba", "prioritas", "kategori"],
        },
    },
}

CANONICAL_TOOLS = [SEARCH_KB_TOOL, GET_ARTICLE_TOOL, DRAFT_TICKET_TOOL]
