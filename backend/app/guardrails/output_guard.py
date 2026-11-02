"""Lapis 4: Output Guardrails untuk KnowDesk AI (agents.md §3 K10, §6.5, §8.1).

Memvalidasi bahwa kutipan sumber yang dihasilkan LLM benar-benar merupakan
substring dari teks langkah dokumen rujukan yang sah (anti-halusinasi kutipan).
"""

import re
from collections.abc import Sequence

from app.schemas.contracts import SumberKutipan


class OutputGuardError(ValueError):
    """Pengecualian saat keluaran model melanggar verifikasi kutipan atau skema."""



def normalize_for_substring_check(text: str) -> str:
    """Menormalisasi spasi ganda, jeda baris, dan huruf besar/kecil untuk pencocokan substring robust."""
    # Ubah newline dan whitespace berulang menjadi spasi tunggal, lowercase
    cleaned = re.sub(r"\s+", " ", text).strip().lower()
    return cleaned


def validate_source_quotes(
    sumber_list: Sequence[SumberKutipan],
    expected_article_id: str,
    step_content: str,
) -> bool:
    """Memverifikasi keabsahan kutipan sumber terhadap teks langkah dokumen (Keputusan K10).

    Aturan:
    1. article_id harus sama persis dengan artikel terpilih di sesi ini.
    2. kutipan harus merupakan substring dari teks langkah yang dikirim ke model.
    3. Jika kutipan kosong atau mengarang teks di luar dokumen, tolak keras.

    Args:
        sumber_list: Daftar objek SumberKutipan dari respon model.
        expected_article_id: ID artikel kanonik yang dipilih sesi (contoh: 'KB-001').
        step_content: Teks asli dokumen langkah yang dikirimkan ke model.

    Returns:
        True jika semua kutipan valid.

    Raises:
        OutputGuardError: Jika terdapat kutipan halusinasi atau ID artikel salah.
    """
    if not sumber_list:
        raise OutputGuardError("Sumber rujukan kosong. Respons langkah solusi wajib memuat kutipan.")

    normalized_step = normalize_for_substring_check(step_content)

    for idx, s in enumerate(sumber_list):
        # 1. Verifikasi kecocokan article_id
        if s.article_id != expected_article_id:
            raise OutputGuardError(
                f"Kutipan #{idx + 1} merujuk article_id '{s.article_id}', "
                f"tetapi artikel sesi yang sah adalah '{expected_article_id}'."
            )

        # 2. Verifikasi kutipan tidak kosong
        raw_kutipan = s.kutipan.strip()
        if not raw_kutipan:
            raise OutputGuardError(f"Kutipan #{idx + 1} tidak boleh kosong.")

        # 3. Verifikasi kutipan adalah substring dari teks langkah
        normalized_kutipan = normalize_for_substring_check(raw_kutipan)
        if normalized_kutipan not in normalized_step:
            raise OutputGuardError(
                f"Kutipan #{idx + 1} '{raw_kutipan}' bukan substring dari teks langkah dokumen rujukan (halusinasi terdeteksi)."
            )

    return True
