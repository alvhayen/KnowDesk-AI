"""Kontrak skema API (FastAPI Pydantic) untuk KnowDesk AI.

Mengikuti keputusan kanonik:
- K3: 'berhasil' = masalah teratasi, 'belum' = masih bermasalah, 'minta_tiket' = eskalasi manual.
- K4: Satu jalur konfirmasi tiket (/api/ticket/confirm), hapus konfirmasi_tiket/tolak_tiket dari ChatRequest.
- K17: Model hanya mengeluarkan pesan dan kutipan; kode mengisi judul, keyakinan, jumlah langkah, dan memerlukan_konfirmasi.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Permintaan pesan chat dari pengguna."""

    session_id: str | None = Field(
        default=None,
        description="ID sesi unik (UUID). Jika kosong, server membuat sesi baru.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Pesan teks pengguna (maksimal 1000 karakter, Lapis 1 Input Guard).",
    )
    confirmation: Literal["berhasil", "belum", "minta_tiket"] | None = Field(
        default=None,
        description="Status konfirmasi langkah solusi (K3 & K4).",
    )


class SumberKutipan(BaseModel):
    """Kutipan sumber dokumen knowledge base (Lapis 4 Output Guard)."""

    article_id: str = Field(..., description="ID kanonik artikel (misal: KB-001).")
    section: str = Field(..., description="Bagian dokumen rujukan (misal: Bagian 3).")
    judul: str = Field(..., description="Judul lengkap artikel dari database.")
    kutipan: str = Field(..., description="Cuplikan teks asli yang menjadi rujukan (K10).")


class DraftTicket(BaseModel):
    """Draf tiket eskalasi teknisi (Lapis 3 & 5)."""

    ticket_id: str = Field(..., description="ID draf tiket unik (misal: TK-0042).")
    judul: str = Field(..., description="Subjek singkat masalah IT.")
    deskripsi: str = Field(..., description="Deskripsi rinci gejala masalah.")
    langkah_dicoba: list[str] = Field(
        default_factory=list,
        description="Daftar langkah yang sudah dicoba di sesi ini.",
    )
    prioritas: Literal["rendah", "sedang", "tinggi"] = Field(
        default="sedang",
        description="Prioritas tiket IT.",
    )
    kategori: Literal["jaringan", "email", "aplikasi", "perangkat", "lainnya"] = Field(
        default="lainnya",
        description="Kategori unit kerja IT.",
    )


class ChatResponse(BaseModel):
    """Respons API sistem ke pengguna (sumber kebenaran kontrak frontend)."""

    session_id: str = Field(..., description="ID sesi aktif.")
    tipe_respons: Literal[
        "klarifikasi",
        "langkah_solusi",
        "tidak_ditemukan",
        "draf_tiket",
        "tiket_terkirim",
        "selesai",
    ] = Field(..., description="Jenis respons agen.")
    pesan: str = Field(
        ...,
        description="Teks polos pesan bantuan untuk pengguna tanpa markdown (K17 & §6.5).",
    )
    sumber: list[SumberKutipan] = Field(
        default_factory=list,
        description="Daftar kutipan sumber KB yang mendasari jawaban.",
    )
    langkah_saat_ini: int = Field(
        default=0,
        ge=0,
        le=4,
        description="Nomor urut langkah solusi yang sedang ditampilkan (1-4).",
    )
    langkah_total_tersedia: int = Field(
        default=0,
        ge=0,
        description="Total langkah solusi yang tersedia di artikel terkait.",
    )
    keyakinan: Literal["tinggi", "sedang", "rendah", "tidak_dapat_ditentukan"] = Field(
        default="sedang",
        description="Tingkat keyakinan retrieval yang dihitung oleh kode (K17 & §6.4).",
    )
    memerlukan_konfirmasi: bool = Field(
        default=True,
        description="Menentukan apakah antarmuka pengguna perlu menampilkan tombol aksi.",
    )
    draf_tiket: DraftTicket | None = Field(
        default=None,
        description="Objek draf tiket jika tipe_respons adalah draf_tiket.",
    )


class TicketConfirmRequest(BaseModel):
    """Permintaan konfirmasi pengiriman draf tiket (Lapis 5 HITL via POST /api/ticket/confirm)."""

    ticket_id: str | None = Field(
        default=None,
        description="ID tiket yang akan dikonfirmasi.",
    )
    action: Literal["confirm", "cancel"] = Field(
        ...,
        description="'confirm' untuk mengirim tiket ke teknisi, 'cancel' untuk membatalkan.",
    )
    catatan: str | None = Field(
        default=None,
        max_length=500,
        description="Catatan tambahan opsional dari pengguna saat konfirmasi.",
    )
