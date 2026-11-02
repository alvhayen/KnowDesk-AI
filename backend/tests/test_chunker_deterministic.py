"""Unit test untuk parsing deterministik heading markdown KB (agents.md §3 K8, K19, §5.1, §5.2).

Memastikan:
1. Jumlah langkah pada KB-001 (Wi-Fi), KB-002 (Reset Password), dan KB-003 (VPN) terhitung tepat 4 langkah (K8).
2. Teks per langkah dapat diekstrak secara terpisah untuk LLM (K8).
3. Integritas data kotor KB-005 dan KB-008 tetap terjaga tanpa modifikasi (§5.2).
4. Seluruh 8 dokumen KB memiliki metadata front matter yang valid.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.rag.chunker import parse_article_file

KB_DIR = root_dir / "knowledge_base"


def test_kb_001_wifi_deterministic_steps():
    """Memverifikasi KB-001 (Wi-Fi) memiliki tepat 4 langkah solusi deterministik."""
    kb_path = KB_DIR / "KB-001-troubleshoot-wifi.md"
    article = parse_article_file(kb_path)

    assert article.article_id == "KB-001"
    assert article.kategori == "jaringan"
    assert article.langkah_total_tersedia == 4
    assert len(article.steps) == 4

    # Verifikasi urutan dan judul langkah
    expected_step_titles = [
        "Lupakan Jaringan Wi-Fi Kantor (Forget Network)",
        "Hubungkan Ulang dengan Kredensial Domain",
        "Perbarui Alamat IP dan Bersihkan Cache DNS (Flush DNS)",
        "Reset Network Adapter Windows",
    ]
    for idx, expected_title in enumerate(expected_step_titles, start=1):
        step = article.get_step(idx)
        assert step is not None, f"Langkah {idx} tidak ditemukan"
        assert step.step_number == idx
        assert expected_title in step.title
        assert len(step.content) > 20

    # Verifikasi pengambilan teks langkah spesifik (K8)
    step1_text = article.get_step_text(1)
    assert step1_text is not None
    assert "Forget" in step1_text


def test_kb_002_reset_password_deterministic_steps():
    """Memverifikasi KB-002 (Reset Password) memiliki tepat 4 langkah solusi deterministik."""
    kb_path = KB_DIR / "KB-002-reset-password-email.md"
    article = parse_article_file(kb_path)

    assert article.article_id == "KB-002"
    assert article.kategori == "email"
    assert article.langkah_total_tersedia == 4
    assert len(article.steps) == 4

    expected_step_titles = [
        "Buka Portal Pemulihan Akun Mandiri (SSPR)",
        "Verifikasi Identitas Melalui Kode OTP atau Authenticator",
        "Buat Kata Sandi Baru Sesuai Standar Keamanan",
        "Perbarui Kata Sandi di Aplikasi Email dan Browser",
    ]
    for idx, expected_title in enumerate(expected_step_titles, start=1):
        step = article.get_step(idx)
        assert step is not None
        assert step.step_number == idx
        assert expected_title in step.title
        assert len(step.content) > 20


def test_kb_003_vpn_deterministic_steps():
    """Memverifikasi KB-003 (VPN) memiliki tepat 4 langkah solusi deterministik."""
    kb_path = KB_DIR / "KB-003-konfigurasi-vpn.md"
    article = parse_article_file(kb_path)

    assert article.article_id == "KB-003"
    assert article.kategori == "jaringan"
    assert article.langkah_total_tersedia == 4
    assert len(article.steps) == 4

    expected_step_titles = [
        "Periksa Sambungan Internet Publik dan DNS",
        "Verifikasi Alamat Server Gateway dan Protokol",
        "Masukkan Kredensial dan Selesaikan Prompt 2FA",
        "Restart VPN Virtual Adapter dan Layanan Client",
    ]
    for idx, expected_title in enumerate(expected_step_titles, start=1):
        step = article.get_step(idx)
        assert step is not None
        assert step.step_number == idx
        assert expected_title in step.title
        assert len(step.content) > 20


def test_all_8_kb_articles_chunking_integrity():
    """Seluruh 8 dokumen KB kanonik harus memiliki 4 bagian chunk dan 4 langkah solusi."""
    expected_articles = [
        ("KB-001", "jaringan"),
        ("KB-002", "email"),
        ("KB-003", "jaringan"),
        ("KB-004", "perangkat"),
        ("KB-005", "aplikasi"),
        ("KB-006", "lainnya"),
        ("KB-007", "lainnya"),
        ("KB-008", "aplikasi"),
    ]

    for expected_id, expected_kat in expected_articles:
        matching_files = list(KB_DIR.glob(f"{expected_id}*.md"))
        assert len(matching_files) == 1, f"Berkas {expected_id} tidak ditemukan"

        article = parse_article_file(matching_files[0])
        assert article.article_id == expected_id
        assert article.kategori == expected_kat
        assert article.status == "published"
        assert len(article.chunks) == 4, f"{expected_id} harus memiliki tepat 4 unit chunk bagian"
        assert article.langkah_total_tersedia == 4, f"{expected_id} harus memiliki tepat 4 langkah solusi"


def test_kb_005_and_008_unmodified_raw_integrity():
    """Menegakkan aturan §5.2: KB-005 dan KB-008 tidak boleh dimodifikasi atau dirapikan teks aslinya."""
    kb005 = parse_article_file(KB_DIR / "KB-005-teams-outlook.md")
    kb008 = parse_article_file(KB_DIR / "KB-008-troubleshoot-erp.md")

    # Pastikan catatan sengaja tidak rapi tetap ada pada pola front matter
    assert "sengaja tidak rapi" in (kb005.pola or "")
    assert "sengaja tidak rapi" in (kb008.pola or "")

    # Pastikan raw content persis sama dengan isi file di disk
    assert kb005.raw_content == (KB_DIR / "KB-005-teams-outlook.md").read_text(encoding="utf-8")
    assert kb008.raw_content == (KB_DIR / "KB-008-troubleshoot-erp.md").read_text(encoding="utf-8")
