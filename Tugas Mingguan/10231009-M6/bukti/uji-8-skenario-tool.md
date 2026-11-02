# Hasil Pengujian 8 Skenario Pemilihan Tool — Tugas 6

Komposisi pengujian mengacu pada panduan Prompt Pack 6.2.B:

| # | Komposisi Skenario | Pertanyaan Pengguna | Tool yang Seharusnya Dipilih | Tool yang Sebenarnya Dipilih Model | Status Evaluasi |
|:--:|---|---|---|---|:--:|
| 1 | Jelas 1 Tool | "Cari artikel SOP tentang cara koneksi VPN kantor." | `search_kb` | `search_kb("koneksi VPN kantor")` | **TEPAT** |
| 2 | Jelas 1 Tool | "Tampilkan isi panduan dengan kode KB-002." | `get_article` | `get_article("KB-002")` | **TEPAT** |
| 3 | Jelas 1 Tool | "Saya sudah coba semua 4 langkah di panduan Wi-Fi tapi tetap gagal, tolong buatkan tiket ke teknisi." | `draft_ticket` | `draft_ticket(...)` | **TEPAT** |
| 4 | 2 Tool Berurutan | "Bagaimana langkah pertama mengatasi printer yang tidak merespons?" | `search_kb` $\rightarrow$ `get_article` | `search_kb` lalu `get_article` | **TEPAT** |
| 5 | 2 Tool Berurutan | "Akun email saya terkunci, apa yang harus saya lakukan?" | `search_kb` $\rightarrow$ `get_article` | `search_kb` lalu `get_article` | **TEPAT** |
| 6 | Tanpa Tool | "Selamat pagi, siapa namamu dan apa tugasmu?" | *Tanpa Tool* | *Tidak memanggil tool* (menjawab langsung ramah) | **TEPAT** |
| 7 | Tanpa Tool | "Terima kasih banyak, masalah Wi-Fi saya sudah selesai!" | *Tanpa Tool* | *Tidak memanggil tool* (menjawab penutup sopan) | **TEPAT** |
| 8 | Tampak Butuh Tool Padahal Tidak | "Komputer saya rusak." (Gejala terlalu umum / ambigu) | *Tanpa Tool (Klarifikasi Dulu)* | *Tidak memanggil tool* (mengajukan pertanyaan klarifikasi gejala) | **TEPAT** |

### Analisis Skor Pemilihan:
- **Tingkat Ketepatan:** **8 dari 8 pertanyaan (100%)**.
- Pada kasus nomor 8, model berhasil menahan diri untuk tidak memanggil `search_kb` secara serampangan, melainkan mematuhi aturan untuk meminta klarifikasi detail kerusakan terlebih dahulu.
