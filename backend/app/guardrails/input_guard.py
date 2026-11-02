"""Lapis 1: Input Guardrails untuk KnowDesk AI (agents.md §4, §7, §8.1).

Memvalidasi dan mensanitasi input pengguna sebelum diproses oleh orchestrator.
"""

import re


class InputGuardError(ValueError):
    """Pengecualian ketika masukan pengguna melanggar aturan pengamanan."""



def validate_and_sanitize_input(text: str, max_chars: int = 1000) -> str:
    """Memvalidasi dan mensanitasi teks input pengguna.

    Args:
        text: Masukan teks dari pengguna.
        max_chars: Batas maksimal karakter (default 1000).

    Returns:
        Teks yang sudah disanitasi.

    Raises:
        InputGuardError: Jika panjang melebihi batas atau teks kosong.
    """
    if not text or not text.strip():
        raise InputGuardError("Pesan pengguna tidak boleh kosong atau hanya berisi spasi.")

    if len(text) > max_chars:
        raise InputGuardError(
            f"Pesan pengguna melebihi batas maksimal {max_chars} karakter (panjang: {len(text)})."
        )

    # Sanitasi delimiter tag penutup untuk mencegah injection (agents.md §7)
    sanitized = text.replace("</pesan_pengguna>", "&lt;/pesan_pengguna&gt;")
    sanitized = sanitized.replace("</konteks_kb>", "&lt;/konteks_kb&gt;")

    # Hapus karakter kontrol biner yang tidak valid (selain whitespace standar)
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", sanitized)

    return sanitized
