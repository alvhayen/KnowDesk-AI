# Catatan Proses 00: Inisialisasi Workspace dan Keputusan Struktur Folder

- **Tanggal:** 2026-10-11
- **Fase:** Fase 0 (M0 Fondasi)
- **Status:** Selesai

---

## 1. Konteks dan Tujuan

Inisialisasi awal workspace proyek KnowDesk AI (K = 3) mengacu pada panduan `agents.md` (§2, §5, §10, §12) serta prinsip implementasi minimalis (Ponytail Full: YAGNI, tanpa boilerplate dummy).

---

## 2. Keputusan Struktur Direktori

Struktur folder dibuat secara esensial tanpa membuat file placeholder kosong (`.gitkeep` dsb.) yang tidak langsung digunakan:

1. **`backend/`**:
   - `backend/app/`: Kode aplikasi utama FastAPI (orchestrator agent manual tanpa framework berat, modul RAG BM25 + cosine + RRF, endpoint API, Pydantic schemas, guardrails).
   - `backend/config/`: Konfigurasi terpusat berbasis `pydantic-settings` (`config.py` yang memuat `.env`) dan tabel tarif token (`pricing.json`).
   - `backend/instruksi/`: Penyimpanan prompt sistem terversi (`v1.md`, `v2.md`) dan `CATATAN.md` sesuai Aturan R8 (larangan prompt panjang inline di Python).
   - `backend/tests/`: Rangkaian pengujian otomatis (`test_env_parity`, `test_gate_uses_cosine_not_rrf`, dsb. sesuai §8.1).

2. **`knowledge_base/`**:
   - Lokasi 8 dokumen sintetis kanonik berformat Markdown dengan YAML front matter (`KB-001` s.d. `KB-008`).

3. **`set-uji/`**:
   - Lokasi dataset evaluasi 15 kasus uji (K = 3: 6 khas, 4 klarifikasi, 3 tak berjawab, 2 injeksi) yang akan dibekukan dengan tag git `testset-v1`.

4. **`bukti/`**:
   - Tempat penyimpanan artefak pembuktian evaluasi, log verifikasi, hasil runner benchmark, dan rekaman pengujian sistem untuk penilaian.

5. **`catatan-proses/`**:
   - Dokumentasi keputusan teknis, arsitektural, dan catatan perubahan bertahap agar keputusan dapat dipertanggungjawabkan di depan penguji.

---

## 3. Kebijakan Git dan Keamanan (Aturan R2)

- Repositori git diinisialisasi pada root workspace sejak hari pertama (`git init`).
- File `.gitignore` dikonfigurasi ketat untuk mencegah kebocoran:
  - File rahasia/lingkungan: `.env`, `.env.*` (kecuali `.env.example`).
  - Cache dan virtual environment Python: `__pycache__/`, `venv/`, `.pytest_cache/`, `.ruff_cache/`.
  - Frontend artifacts dan dependensi: `node_modules/`, `dist/`, `.svelte-kit/`.
  - File log dan temporary run: `logs/`, `*.log`.
