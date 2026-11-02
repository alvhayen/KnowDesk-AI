# Catatan Pemakaian Token dan Biaya (Buku Besar)
## Proyek: KnowDesk AI (K = 3)
**Mata Kuliah:** Kapita Selekta: AI Engineering | Ganjil 2026/2027  
**Inisialisasi:** Minggu 3 (2026-10-12)

---

## 1. Buku Catatan Transaksi Pemanggilan Model

| Tanggal | Kegiatan / Skenario | Model Digunakan | Token Masukan | Token Keluaran | Total Token | Estimasi Biaya (IDR) | Akumulasi Biaya |
|---|---|---|---|---|---|---|---|
| 2026-10-12 | Smoke Test Pemanggilan Pertama | `google/gemini-flash` | 128 | 42 | 170 | Rp 0,42 | Rp 0,42 |
| 2026-10-12 | Eksperimen BREAK 1–4 (Modul M3) | `google/gemini-flash` | 512 | 168 | 680 | Rp 1,68 | Rp 2,10 |
| 2026-10-12 | Komparasi Model 1 (Model Ekonomis) | `google/gemini-flash` | 320 | 85 | 405 | Rp 0,81 | Rp 2,91 |
| 2026-10-12 | Komparasi Model 2 (Model Menengah) | `deepseek/deepseek-chat`| 320 | 82 | 402 | Rp 0,72 | Rp 3,63 |
| 2026-10-12 | Komparasi Model 3 (Model Penalaran) | `anthropic/claude-3.5-sonnet`| 320 | 88 | 408 | Rp 36,48 | Rp 40,11 |
| 2026-10-12 | Evaluasi Kasus Tantangan Wajib M3 | `google/gemini-flash` | 640 | 170 | 810 | Rp 1,62 | Rp 41,73 |

---

## 2. Ringkasan Mingguan

- **Total Token Minggu 3:** 2.875 token
- **Biaya Minggu 3:** **Rp 41,73**
- **Total Biaya Kumulatif:** **Rp 41,73**
- **Catatan Efisiensi:** Model Claude 3.5 Sonnet memakan 87% dari total biaya meskipun hanya dijalankan 1 kali untuk perbandingan. Oleh karena itu, operasional harian KnowDesk AI dikunci pada model kelas ekonomis (`gemini-flash` / `deepseek-chat`).
