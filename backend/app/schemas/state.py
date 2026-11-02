"""Definisi status sesi dan tabel penegakan allowlist tool (agents.md §6.1, §6.2, §6.3).

Penegakan Lapis 3 (Kewenangan di kode):
- LLM hanya dapat memanggil tool yang diizinkan untuk status sesi saat ini.
- Tool `draft_ticket` ditolak keras jika belum melewati pencarian/tahap solusi.
"""

from enum import Enum


class SessionStatus(str, Enum):
    """Status alur sesi bantuan KnowDesk AI."""

    IDLE = "idle"                        # Sesi baru, menunggu masukan awal pengguna
    CLARIFYING = "clarifying"            # Sedang mengklarifikasi gejala yang terlalu umum/ambigu
    RETRIEVING = "retrieving"            # Sedang melakukan retrieval artikel knowledge base
    GUIDING = "guiding"                  # Sedang menyajikan langkah pemecahan masalah ke pengguna
    AWAITING_CONFIRM = "awaiting_confirm"# Menunggu tanggapan pengguna terhadap langkah solusi
    ESCALATING = "escalating"            # Menyiapkan eskalasi draf tiket (batas langkah / permintaan pengguna)
    RESOLVED = "resolved"                # Masalah berhasil diselesaikan mandiri oleh pengguna
    CLOSED = "closed"                    # Sesi ditutup (tiket dikonfirmasi atau dibatalkan)


# Tabel izin pemanggilan tool berdasarkan status sesi aktif (Aturan §6.3)
STATE_TOOL_ALLOWLIST: dict[SessionStatus, set[str]] = {
    SessionStatus.IDLE: {"search_kb"},
    SessionStatus.CLARIFYING: {"search_kb"},
    SessionStatus.RETRIEVING: {"get_article"},
    SessionStatus.GUIDING: set(),            # Hanya komunikasi teks langkah, tidak ada eksekusi tool
    SessionStatus.AWAITING_CONFIRM: set(),   # Menunggu tombol konfirmasi pengguna
    SessionStatus.ESCALATING: {"draft_ticket"}, # Hanya diizinkan saat eskalasi
    SessionStatus.RESOLVED: set(),           # Sesi selesai, menolak semua pemanggilan tool
    SessionStatus.CLOSED: set(),             # Sesi ditutup, menolak semua pemanggilan tool
}


def is_tool_allowed(status: SessionStatus, tool_name: str) -> bool:
    """Memvalidasi apakah pemanggilan tool diizinkan pada status sesi saat ini (Lapis 3).

    Args:
        status: Status sesi aktif.
        tool_name: Nama fungsi tool yang dipanggil LLM (search_kb, get_article, draft_ticket).

    Returns:
        True jika diizinkan dalam allowlist kode, False jika melanggar kewenangan.
    """
    allowed_tools = STATE_TOOL_ALLOWLIST.get(status, set())
    return tool_name in allowed_tools
