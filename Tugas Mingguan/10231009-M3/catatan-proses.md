# CATATAN PROSES — MINGGU 3

Nama / NIM / K : [Nama Mahasiswa] / [NIM Mahasiswa] / K = 3  
Tanggal        : 2026-10-12  
Waktu yang saya habiskan minggu ini : 8 jam  

---

## 1. Yang saya kerjakan minggu ini
Saya menyiapkan lingkungan kerja lokal (Python venv, package `requests`, `python-dotenv`), mengonfigurasi model gateway terpusat (OpenRouter) melalui file `.env`, membuat script pemanggilan mandiri `call_model.py`, menginisialisasi buku besar `catatan-pemakaian.md`, serta membandingkan performa 3 model berbeda pada tugas helpdesk IT yang sama.

## 2. Tahap READ
Yang saya amati :
Pada payload respon API model gateway, terdapat pemisahan tegas antara `role: system`, `role: user`, dan `role: assistant`. Di dalam objek metadata respon, terdapat rincian pasti `usage.prompt_tokens` dan `usage.completion_tokens` yang menjadi dasar faktual penagihan biaya, bukan perkiraan.

Yang mengejutkan saya :
Ketika `role: system` dihapus sama sekali, model kehilangan persona profesional helpdesk dan beralih ke gaya percakapan umum yang santai serta terlalu berbasa-basi ("Halo kawan! Tentu, aku bisa bantu masalah Wi-Fimu!").

## 3. Tahap BREAK
| # | Percobaan | Prediksi saya | Hasil sebenarnya | Prediksi tepat? |
|---|---|---|---|---|
| 1 | Hapus seluruh isi peran "system" | Model menolak menjawab | Model tetap menjawab dengan gaya santai dan tanpa batasan SOP | tidak |
| 2 | Turunkan batas max_tokens ke 20 | Model merangkum dalam 20 token | Respon terpotong persis di tengah kata `konfigura...` | tidak |
| 3 | Ganti nama model ke nama fiktif `openrouter/model-gaib-v1` | Error HTTP 404/400 Not Found | Menerima pesan error JSON `404: Model not found` | ya |
| 4 | Kirim konten masukan string kosong `""` | Error HTTP 400 Bad Request | Error 400 `Invalid request: messages cannot be empty` | ya |
| 5 | Prompt sama diuji pada model termurah vs model termahal | Model termahal 10x lebih bagus | Kualitas ekstraksi langkah SOP identik, namun model termahal 24x lebih mahal | tidak |

Prediksi saya yang paling MELESET : nomor 2 dan 5  
Apa yang salah dari cara saya berpikir sebelumnya :
Saya mengira pemotongan `max_tokens` membuat model pintar memadatkan kalimat; kenyataannya model dipotong paksa. Pada nomor 5, untuk tugas ekstraksi instruksi terarah sederhana, model hemat (*Gemini Flash*) memberikan kualitas yang tidak dapat dibedakan dari model termahal (*Claude Sonnet*).

## 4. Tahap FIX
Kesalahan yang saya temukan : (Tahap FIX modul belum dimulai pada Minggu 3).  
Bagaimana saya membuktikan diagnosis itu, bukan sekadar menduganya : N/A  
Kesalahan yang TIDAK saya temukan sendiri (bila ada) dan bagaimana akhirnya ketemu : N/A  

## 5. Tahap BUILD
Yang berhasil :
1. Script `call_model.py` berhasil dieksekusi dengan isolasi kredensial `.env` (aturan R2 & R11).
2. Buku besar `catatan-pemakaian.md` aktif mencatat token masuk/keluar secara kumulatif.
3. Tabel perbandingan 3 model (hemat, menengah, besar) selesai dengan data latensi dan biaya riil.

Yang tidak berhasil :
Sempat terjadi error koneksi `SSLError` saat pertama kali menjalankan script dari jaringan proxy kampus; berhasil diatasi dengan menambahkan konfigurasi penanganan timeout pada HTTP client.

Keputusan rancangan yang saya ambil minggu ini, beserta alasannya :
| Keputusan | Alternatif yang saya tolak | Alasan memilih |
|---|---|---|
| Menggunakan Model Gateway (OpenRouter) | Berlangganan API langsung ke masing-masing vendor | Satu API key seragam, dapat berganti model instan tanpa mengubah kode, dan ada batas saldo terpusat |
| Memilih arsitektur model bertingkat (*tiered*) | Selalu memanggil model terbesar | Menghemat lebih dari 85% anggaran operasional bulanan tanpa menurunkan akurasi grounding |

## 6. Tantangan wajib
Hasil :
Saya menemukan bahwa untuk tugas ekstraksi ringkasan gejala (misal: membedakan apakah keluhan termasuk kategori "Wi-Fi", "Email", atau "VPN"), model termurah (`google/gemini-flash-1.5`) menghasilkan klasifikasi yang 100% identik dengan model termahal (`anthropic/claude-3.5-sonnet`).
- Hasil Berdampingan: Keduanya menghasilkan `kategori: jaringan`.
- Penghematan Biaya per 1.000 panggilan: Gemini Flash menghabiskan Rp 4.200, sedangkan Claude Sonnet menghabiskan Rp 102.000 (Penghematan: **Rp 97.800 atau 95.8%**).

## 7. Penggunaan AI minggu ini
| # | Untuk apa | Prompt (ringkas / pola Lampiran A) | Yang saya UBAH dari hasilnya | Bagaimana saya verifikasi |
|---|---|---|---|---|
| 1 | Boilerplate script HTTP API | Pola Prompt 3.2.A: Panduan penyiapan script API requests | Menambahkan masking sensor API key pada log output dan blok exception handling | Menguji print variabel environment di terminal |
| 2 | Desain protokol benchmarking | Pola Prompt 3.2.C: Penyusunan parameter uji komparasi model | Menghapus penilaian subjektif "kecerdasan", menggantinya dengan metrik latensi ms dan rupiah | Memeriksa response time menggunakan `time.perf_counter()` |

Satu hal yang AI berikan dan ternyata KELIRU minggu ini :
AI menyarankan menaruh fallback string `OPENROUTER_API_KEY="sk-or-v1-dummy..."` langsung di kode. Ini berbahaya karena mudah terunggah; saya hapus dan ganti dengan pengecekan `if not key: raise ValueError`.

Bagian karya minggu ini yang paling sulit saya jelaskan bila ditanya :
Mengapa penggunaan model gateway lebih aman daripada menyimpan kredensial lokal ke banyak provider (penjelasannya: satu titik rotasi kunci dan satu batas kuota terpusat).

## 8. Pemakaian dan biaya
| Kegiatan | Model | Perkiraan token | Perkiraan biaya |
|---|---|---|---|
| Uji pemanggilan pertama & perbandingan 3 model | gemini-flash, deepseek-v3, claude-sonnet | 8.240 token | Rp 380 |
Total minggu ini : Rp 380  
Total kumulatif  : Rp 630  

## 9. Daftar periksa mandiri
- [x] Pemanggilan model pertama berhasil dan buktinya tersimpan
- [x] API key berada di luar file kode dan di luar repositori (.gitignore)
- [x] Tabel pembedahan pemanggilan terisi lengkap
- [x] Lima percobaan BREAK dijalankan dengan prediksi lebih dulu
- [x] Perbandingan tiga model terisi biaya, latensi, dan kualitas
- [x] catatan-pemakaian.md dibuat dan sudah berisi baris pertama
- [x] Tantangan wajib disertai bukti berdampingan dan hitungan penghematan

## 10. Yang macet dan rencana minggu depan
Yang masih macet : Menjaga agar format output model tidak menyisipkan salam pembuka/penutup.  
Apa yang sudah saya coba untuk mengatasinya : Memberi instruksi "jawab langsung tanpa basa-basi".  
Rencana konkret minggu depan : Mengunci lembar tema resmi pada Lampiran B dan merancang instruksi sistem v1 pada Tugas 4.
