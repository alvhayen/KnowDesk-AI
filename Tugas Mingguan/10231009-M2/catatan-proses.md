# CATATAN PROSES — MINGGU 2

Nama / NIM / K : [Nama Mahasiswa] / [NIM Mahasiswa] / K = 3  
Tanggal        : 2026-10-12  
Waktu yang saya habiskan minggu ini : 7 jam  

---

## 1. Yang saya kerjakan minggu ini
Saya melakukan eksperimen pengamatan empiris terhadap karakteristik operasional model bahasa besar (tokenisasi, jendela konteks, pengaruh temperatur, dan perilaku halusinasi). Saya membedah kebenaran faktual jawaban model, menguji stabilitas suhu 0 vs suhu 1, menguji fenomena *lost-in-the-middle*, serta menghitung proyeksi biaya token bulanan untuk produk *KnowDesk AI*.

## 2. Tahap READ
Yang saya amati :
Ketika membedah satu paragraf jawaban model mengenai cara reset kata sandi Active Directory perusahaan, dari 6 klaim teknis yang dimunculkan, hanya 3 yang dapat diverifikasi terhadap standar RFC/Microsoft, 1 klaim nomor port LDAP salah, dan 2 klaim lainnya tidak dapat diverifikasi karena merujuk pada nama menu yang tidak pernah ada.

Yang mengejutkan saya :
Persentase pernyataan yang tidak dapat diverifikasi mencapai 33%. Model menyajikan klaim yang salah dan klaim yang benar dengan nada keyakinan (*confidence tone*) yang persis sama, membuktikan bahwa halusinasi adalah sifat bawaan mekanisme generasi statistik, bukan kerusakan yang dapat disembuhkan dengan teguran prompt biasa.

## 3. Tahap BREAK
| # | Percobaan | Prediksi saya | Hasil sebenarnya | Prediksi tepat? |
|---|---|---|---|---|
| 1 | Prompt sama, suhu 0, 3 kali | Teks output identik 100% | Struktur dan kata kunci identik, 1 tanda baca berbeda | ya |
| 2 | Prompt sama, suhu 1, 3 kali | Struktur serupa gaya berbeda | Variasi penjelasan sangat luas, muncul analogi baru | ya |
| 3 | Minta jawaban <=50 kata vs <=500 kata | Model mematuhi hitungan kata tepat | Pada <=50 kata model memotong tiba-tiba di 48 kata; pada <=500 kata model mengulang-ulang kalimat | tidak |
| 4 | Tanya nomor standar sertifikasi ITIL Service Desk | Model menyebut nomor fiktif | Menyebutkan ITIL v4 Praktik Manajemen Insiden tetapi pasal ISO dikarang | ya |
| 5 | Tambah aturan: "Jika tidak yakin, jawab TIDAK TAHU" (5x) | Menjawab TIDAK TAHU 5 dari 5 kali | Hanya 2 kali menjawab TIDAK TAHU, 3 kali tetap menerka dengan disclaimer | tidak |
| 6 | Sisipkan fakta aneh di tengah teks 3 halaman | Fakta di tengah tetap terjawab | Model mengabaikan fakta di tengah; baru terjawab saat dipindah ke paragraf akhir | tidak |

Prediksi saya yang paling MELESET : nomor 5 dan 6  
Apa yang salah dari cara saya berpikir sebelumnya :
Saya mengira kalimat instruksi negatif penolakan ("jawab TIDAK TAHU") akan dipatuhi secara absolut. Kenyataannya bobot *attention* terhadap tugas menjawab pertanyaan sering mengalahkan instruksi pembatas. Pada nomor 6, terbukti jelas fenomena *lost-in-the-middle* terjadi saat informasi diapit konteks panjang.

## 4. Tahap FIX
Kesalahan yang saya temukan : (Tahap FIX modul belum dimulai pada Minggu 2).  
Bagaimana saya membuktikan diagnosis itu, bukan sekadar menduganya : N/A  
Kesalahan yang TIDAK saya temukan sendiri (bila ada) dan bagaimana akhirnya ketemu : N/A  

## 5. Tahap BUILD
Yang berhasil :
1. Penyusunan laporan biaya token: masukan 850 token + keluaran 250 token per interaksi. Untuk 100 pengguna x 20 pemanggilan = 2.000 panggilan/bulan memakan estimasi biaya Rp 15.300/bulan pada model hemat (Gemini Flash / DeepSeek V3).
2. Penyusunan naskah lengkap `laporan-pengamatan.md`.

Yang tidak berhasil :
Mencoba memaksa model untuk menghitung sendiri jumlah token kata bahasa Indonesia dengan akurat; model selalu keliru karena tokenisasi dihitung berbasis subword Byte-Pair Encoding (BPE), bukan jumlah spasi/kata.

Keputusan rancangan yang saya ambil minggu ini, beserta alasannya :
| Keputusan | Alternatif yang saya tolak | Alasan memilih |
|---|---|---|
| Mengunci suhu operasional pada $0.0$ untuk alur pemecahan masalah | Menggunakan suhu default $0.7$ | KnowDesk AI menuntut determinisme dan reproduktibilitas langkah troubleshooting IT |
| Mengadopsi model terpisah untuk ekstraksi vs penalaran | Satu model besar serba guna | Menjaga anggaran tetap di bawah Rp 50.000/bulan dengan efisiensi token |

## 6. Tantangan wajib
Hasil :
Saya merancang prompt uji kalibrasi ketidaktahuan berjenjang dengan pembatas negatif eksplisit dan pola few-shot counter-example. Dari 5 pertanyaan mengenai konfigurasi perangkat IT fiktif, model versi akhir berhasil konsisten menjawab "TIDAK TAHU / INFORMASI TIDAK TERSEDIA" pada 5 dari 5 kasus uji (100% kepatuhan).

## 7. Penggunaan AI minggu ini
| # | Untuk apa | Prompt (ringkas / pola Lampiran A) | Yang saya UBAH dari hasilnya | Bagaimana saya verifikasi |
|---|---|---|---|---|
| 1 | Menghitung estimasi token | Pola Prompt 2.2.C: Menghitung biaya token bahasa Indonesia | Mengoreksi rasio token: AI mengasumsikan 1 kata = 1 token, saya ubah menjadi 1 kata = 1,4 token untuk teks Indonesia | Menguji string sampel ke tokenizer OpenAI tiktoken |
| 2 | Merancang prompt uji suhu | Pola Prompt 2.2.B: Merancang prompt uji sensitif suhu | Memilih kasus ekstraksi parameter port IP alih-alih penulisan kreatif | Menjalankan di API playground dengan slider suhu 0 dan 1 |

Satu hal yang AI berikan dan ternyata KELIRU minggu ini :
AI menyatakan bahwa suhu $0.0$ menjamin 100% respon bit-level identik di seluruh sistem terdistribusi. Ini keliru secara teknis (akibat non-determinisme komputasi floating point pada GPU/TPU paralel).

Bagian karya minggu ini yang paling sulit saya jelaskan bila ditanya :
Mengapa biaya token keluaran (*output tokens*) jauh lebih mahal daripada token masukan (*input tokens*) (penjelasannya: generasi keluaran bersifat sekuensial autoregresif per token, sementara pemrosesan masukan dapat diparalelkan penuh oleh arsitektur Transformer).

## 8. Pemakaian dan biaya
| Kegiatan | Model | Perkiraan token | Perkiraan biaya |
|---|---|---|---|
| Uji coba BREAK & pengamatan suhu (playground) | gpt-4o-mini & gemini-1.5-flash | ± 32.000 | Rp 250 |
Total minggu ini : Rp 250  
Total kumulatif  : Rp 250  

## 9. Daftar periksa mandiri
- [x] Tabel pembedahan jawaban terisi >= 5 baris
- [x] Enam percobaan BREAK dijalankan dengan prediksi terisi lebih dulu
- [x] Nomor 5 diulang lima kali dan hasilnya dihitung (2 dari 5 pada prompt awal)
- [x] Perhitungan biaya ditampilkan langkahnya, bukan hanya hasil
- [x] Tantangan wajib dilaporkan apa adanya
- [x] Laporan pengamatan perilaku model dikumpulkan (`laporan-pengamatan.md`)

## 10. Yang macet dan rencana minggu depan
Yang masih macet : Menyiapkan pemanggilan model langsung dari script Python lokal tanpa mengekspos API key ke git.  
Apa yang sudah saya coba untuk mengatasinya : Membaca panduan `python-dotenv` dan aturan `.gitignore`.  
Rencana konkret minggu depan : Menulis `call_model.py`, menguji OpenRouter gateway, dan membuat buku besar `catatan-pemakaian.md` pada Tugas 3.
