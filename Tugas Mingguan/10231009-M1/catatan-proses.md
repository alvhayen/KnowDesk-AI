# CATATAN PROSES — MINGGU 1

Nama / NIM / K : [Nama Mahasiswa] / [NIM Mahasiswa] / K = 3  
Tanggal        : 2026-10-12  
Waktu yang saya habiskan minggu ini : 6 jam  

---

## 1. Yang saya kerjakan minggu ini
Saya menetapkan fondasi konseptual proyek AI Engineering, menghitung parameter lingkup wajib berdasarkan kode peserta $K = 3$, membedah batas antara AI Engineering vs Machine Learning vs Sistem Berbasis Aturan, dan merumuskan tiga calon persoalan nyata di bidang Sistem Informasi dan Dukungan IT. Saya memilih proyek *KnowDesk AI* (asisten bantuan mandiri helpdesk IT) sebagai tema yang akan dipertahankan hingga Minggu 16.

## 2. Tahap READ
Yang saya amati :
Banyak persoalan yang disangka membutuhkan AI generatif ternyata murni persoalan basis data relasional atau logika kondisional biasa (*rule-based*). Pada tabel perbandingan tiga persoalan, menghitung sisa SKS murni ranah RPL/basis data, memprediksi jumlah pengunjung pelabuhan adalah Machine Learning klasik (regresi deret waktu), dan meringkas laporan survei berformat tetap adalah AI Engineering.

Yang mengejutkan saya :
Ketika jumlah laporan disimulasikan melonjak dari 40 menjadi 40.000, metode AI Engineering satu panggilan prompt runtuh total akibat kendala jendela konteks dan biaya token. Persoalan tersebut bergeser menjadi persoalan rekayasa data dan pengindeksan terdistribusi.

## 3. Tahap BREAK
| # | Percobaan | Prediksi saya | Hasil sebenarnya | Prediksi tepat? |
|---|---|---|---|---|
| 1 | Tanya spesifikasi protokol WPA3 Enterprise 3x di chat baru | Jawaban identik 100% | Struktur poin sama, tetapi pilihan diksi pembuka berbeda | tidak |
| 2 | Tanya berita lokal kampus bulan lalu | Model menolak tahu batas cut-off | Model mengaku tahu namun mengarang nama wakil rektor | tidak |
| 3 | Tanya isi SOP pengajuan cuti server lab kampus internal | Model menjawab "tidak tahu" | Model mengarang prosedur umum yang tampak meyakinkan | tidak |
| 4 | Tanya biografi tokoh fiktif "Dr. Hendra Wijayakusuma, Pakar AI Maritim Unhas" | Model menolak karena tokoh fiktif | Model mengarang riwayat studi dan buku karyanya | tidak |

Prediksi saya yang paling MELESET : nomor 3 dan 4  
Apa yang salah dari cara saya berpikir sebelumnya :
Saya sebelumnya mengira model bahasa memiliki mekanisme "introspeksi basis data" untuk mendeteksi ketiadaan informasi. Kenyataannya, mekanisme generasi adalah pelengkapan token berikutnya yang paling masuk akal statistik, sehingga ketiadaan fakta justru memicu halusinasi yang terdengar sangat percaya diri. Pada nomor 4 model *tidak tahu bahwa ia tidak tahu*.

## 4. Tahap FIX
Kesalahan yang saya temukan : (Tahap FIX modul belum dimulai pada Minggu 1).  
Bagaimana saya membuktikan diagnosis itu, bukan sekadar menduganya : N/A  
Kesalahan yang TIDAK saya temukan sendiri (bila ada) dan bagaimana akhirnya ketemu : N/A  

## 5. Tahap BUILD
Yang berhasil :
1. Perhitungan parameter batas minimum lingkup $K = 3$ selesai: Dokumen KB $= 8$, Kasus Uji $= 15$, Tool $= 3$, Mode Keluaran $= 1$ standar.
2. Penyusunan 3 calon persoalan dengan analisis lengkap 6 unsur pada berkas `peta-minat.md`.

Yang tidak berhasil :
Mencoba membatasi halusinasi model pada tahap eksplorasi web UI hanya dengan kalimat sopan "tolong jawab jujur", yang terbukti gagal total.

Keputusan rancangan yang saya ambil minggu ini, beserta alasannya :
| Keputusan | Alternatif yang saya tolak | Alasan memilih |
|---|---|---|
| Memilih kasus IT Service Desk (*KnowDesk AI*) | Memilih sistem audit log keamanan otomatis | IT Service Desk memiliki basis SOP tekstual yang jelas dan batasan benar/salah dapat diverifikasi staf |
| Menolak pendekatan fine-tuning | Melatih model kecil khusus IT | Tugas helpdesk menuntut keterlacakan kutipan persis dari dokumen SOP; fine-tuning membekukan data dan mahal |

## 6. Tantangan wajib
Hasil :
Contoh nyata AI keliru diterapkan di lingkungan kampus: Penggunaan chatbot LLM publik untuk menghitung sisa jatah cuti tahunan dan absensi staf. Pendekatan ini salah karena jatah cuti adalah data deterministik relasional dengan toleransi kesalahan 0%. Menggunakan LLM rentan halusinasi angka dan boros biaya token; solusi yang benar adalah query SQL langsung ke tabel HRIS.

## 7. Penggunaan AI minggu ini
| # | Untuk apa | Prompt (ringkas / pola Lampiran A) | Yang saya UBAH dari hasilnya | Bagaimana saya verifikasi |
|---|---|---|---|---|
| 1 | Brainstorming calon persoalan | Pola Prompt 1.2.A: 8 pertanyaan bertahap untuk menggali kendala helpdesk | Menolak usulan chatbot serbaguna, mempersempit ke panduan mandiri per langkah | Mengecek kelayakan dokumen SOP yang dapat dibuat secara sintetis |
| 2 | Menguji klaim kemampuan LLM | Pola Prompt 1.2.B: Uji klaim "LLM dapat menggantikan teknisi IT sepenuhnya" | Mengoreksi klaim AI; mempertegas batas bahwa AI hanya memandu langkah minor | Mengamati breakdown keterbatasan akses fisik dan privasi akun |

Satu hal yang AI berikan dan ternyata KELIRU minggu ini :
AI sempat menyarankan agar sistem langsung terhubung dan mengubah password Active Directory secara otomatis. Ini berbahaya dan melanggar prinsip *Human-in-the-Loop*; saya ubah menjadi sekadar panduan mandiri dan penyusunan draf tiket eskalasi.

Bagian karya minggu ini yang paling sulit saya jelaskan bila ditanya :
Mengapa persoalan IT Service Desk menuntut AI Generatif jika sudah ada dokumen SOP (penjelasannya: pengguna awam tidak memahami istilah teknis dalam dokumen tebal dan memerlukan dialog pemahaman gejala bertahap).

## 8. Pemakaian dan biaya
| Kegiatan | Model | Perkiraan token | Perkiraan biaya |
|---|---|---|---|
| Eksplorasi pemetaan persoalan & uji BREAK | Web Chat Interface (Free Tier) | ± 14.500 | Rp 0 |
Total minggu ini : Rp 0  
Total kumulatif  : Rp 0  

## 9. Daftar periksa mandiri
- [x] Kode peserta K dicatat dan seluruh angka lingkup dihitung
- [x] Tabel READ terisi lengkap dengan alasan
- [x] Empat baris BREAK punya kolom prediksi terisi sebelum percobaan
- [x] Tiga calon persoalan terisi lengkap enam unsur
- [x] Tantangan wajib terjawab
- [x] Catatan proses ditulis memakai template Lampiran C

## 10. Yang macet dan rencana minggu depan
Yang masih macet : Memahami bagaimana mengatur suhu (*temperature*) dan penalti token agar model dapat membedakan kapan harus menjawab dan kapan harus menolak.  
Apa yang sudah saya coba untuk mengatasinya : Mencoba beberapa variasi prompt instruksi di playground web.  
Rencana konkret minggu depan : Menjalankan eksperimen terukur terhadap pengaruh suhu dan mengukur biaya token per interaksi pada Tugas 2.
