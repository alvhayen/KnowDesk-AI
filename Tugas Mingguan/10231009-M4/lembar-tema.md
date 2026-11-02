# LEMBAR TEMA PROYEK
## Lampiran B — Kapita Selekta: AI Engineering (Ganjil 2026/2027)

- **Nama Mahasiswa** : [Nama Mahasiswa]
- **NIM**            : [NIM Mahasiswa]
- **Program Studi**  : Sistem Informasi / Teknik Informatika
- **Kode Peserta K** : **3**

---

## Angka Lingkup Saya ($K = 3$)
- **Dokumen Rujukan Minimum** : $5 + (K \pmod 4) = 5 + (3 \pmod 4) =$ **8 dokumen**
- **Kasus Uji Minimum**       : $12 + (K \pmod 6) = 12 + (3 \pmod 6) =$ **15 kasus**
- **Tool Minimum**            : $2 + (K \pmod 2) = 2 + (3 \pmod 2) =$ **3 tool**
- **Mode Keluaran Tambahan**  : **Tidak Wajib** ($K = 3$, ganjil)

---

## 1. Persoalan

### Judul Kerja Produk:
**KnowDesk AI — Asisten Bantuan Mandiri Service Desk IT Berbasis AI Agentik dan Grounded RAG**

### Siapa yang Mengalami Persoalan Ini:
1. **Karyawan dan staf kantor non-teknis** di lingkungan enterprise/institusi yang mengalami kendala operasional komputer harian (Wi-Fi putus, lupa kata sandi email/SSO, gagal terhubung ke VPN kantor, printer jaringan macet, aplikasi ERP crash).
2. **Teknisi helpdesk IT tier-1** yang waktu kerjanya habis terkuras untuk menjawab pertanyaan repetitif sepele yang sebenarnya sudah tertulis di dokumen SOP.

### Bagaimana Persoalan Ini Diselesaikan Sekarang:
Pengguna harus membuka dokumen portal wiki IT internal setebal puluhan halaman yang penuh istilah teknis rumit, atau langsung menelepon/membuat tiket ad-hoc ke teknisi IT sehingga antrean tiket eskalasi membengkak.

### Mengapa Cara Sekarang Tidak Memadai:
- Staf kantor non-teknis enggan membaca dokumen PDF/wiki yang panjang dan teknis (*cognitive overload*).
- Pengguna sering salah mendiagnosis kendala sehingga tiket yang dikirimkan minim informasi (contoh: hanya melapor *"komputer rusak"* tanpa konteks kode error).
- Waktu tunggu respon teknisi helpdesk rata-rata 1–4 jam hanya untuk masalah reset password atau restart adapter jaringan.

---

## 2. Mengapa AI Generatif

### Mengapa Persoalan Ini TIDAK Cukup Diselesaikan dengan Basis Data atau Aturan Biasa:
Keluhan pengguna disampaikan dalam bahasa alami yang sangat beragam, ambigu, dan sarat bahasa sehari-hari (*"laptop tidak bisa internetan"*, *"sinyal Wi-Fi silang merah"*, *"tidak bisa buka portal gaji"*). Sistem berbasis aturan kata kunci (*keyword search*) akan langsung gagal jika tidak menemukan padanan kata yang persis.

### Apa yang Membuat Persoalan Ini Menuntut Penafsiran Bahasa:
- Memerlukan kemampuan klarifikasi dialogis interaktif untuk mempersempit gejala yang kabur sebelum mencari solusi.
- Memerlukan kemampuan adaptasi sintaksis untuk menerjemahkan langkah teknis rumit dari dokumen SOP menjadi kalimat panduan langkah-demi-langkah yang ramah bagi pengguna awam.
- Memerlukan pemahaman konteks percakapan riwayat interaksi untuk merangkum seluruh langkah yang telah gagal dicoba menjadi draf tiket eskalasi formal.

---

## 3. Ukuran Keberhasilan

### Bukti Bahwa Produk Ini Berhasil:
1. Pengguna berhasil menyelesaikan kendala mandiri mengikuti instruksi langkah-demi-langkah (1 pesan 1 langkah) dengan tingkat penyelesaian mandiri $\ge 70\%$ pada kasus uji yang tercakup dalam dokumen KB.
2. Setiap instruksi solusi menyertakan kutipan persis (*exact substring quote*) dari SOP resmi tanpa halusinasi langkah fiktif.
3. Bila kendala tidak dapat diselesaikan atau dokumen tidak ditemukan, sistem berhasil menyusun draf tiket eskalasi terstruktur yang siap dikonfirmasi oleh pengguna.

### Siapa yang Dapat Memeriksa Keluarannya Benar atau Salah:
Staf IT Support Senior dan Administrator Jaringan melalui perbandingan langsung antara jawaban agen dengan dokumen kanonik SOP IT internal.

### Apa yang Terjadi Bila Keluarannya Salah, dan Siapa yang Menanggungnya:
Jika sistem memberikan instruksi yang salah atau berhalusinasi, pengguna kantor dapat salah mengonfigurasi perangkat (misalnya salah menghapus profil sertifikat Wi-Fi). Risiko ini ditanggulangi dengan:
- Pembatasan model hanya pada mode *read-only* dari dokumen rujukan KB.
- Larangan eksekusi otomatis: agen tidak diizinkan mengubah sistem operasi pengguna secara langsung.
- Prinsip *Human-in-the-Loop*: tiket eskalasi hanya dikirim jika disetujui pengguna.

---

## 4. Dokumen Rujukan Kanonik ($K = 3 \rightarrow 8$ Dokumen)

| # | ID | Judul Dokumen | Penerbit / Asal | Tahun | Halaman Setara | Status Kelayakan |
|---|---|---|---|---|---|---|
| 1 | KB-001 | Panduan Troubleshooting Koneksi Wi-Fi Kantor | Sintetis Mandiri (IT SOP) | 2026 | 4 halaman | Sah, bebas data pribadi |
| 2 | KB-002 | Prosedur Reset dan Pemulihan Password Email | Sintetis Mandiri (IT SOP) | 2026 | 3 halaman | Sah, bebas data pribadi |
| 3 | KB-003 | Panduan Konfigurasi VPN untuk Akses Jarak Jauh | Sintetis Mandiri (IT SOP) | 2026 | 3 halaman | Sah, bebas data pribadi |
| 4 | KB-004 | Panduan Instalasi dan Troubleshooting Printer Jaringan | Sintetis Mandiri (IT SOP) | 2026 | 3 halaman | Sah, bebas data pribadi |
| 5 | KB-005 | Panduan Penggunaan Microsoft Teams dan Outlook | Sintetis Mandiri (IT SOP) | 2026 | 3 halaman | Sah, bebas data pribadi |
| 6 | KB-006 | Prosedur Permintaan Akses Folder Bersama | Sintetis Mandiri (IT SOP) | 2026 | 3 halaman | Sah, bebas data pribadi |
| 7 | KB-007 | Panduan Keamanan Akun dan Autentikasi Dua Faktor | Sintetis Mandiri (IT SOP) | 2026 | 3 halaman | Sah, bebas data pribadi |
| 8 | KB-008 | Panduan Troubleshooting Aplikasi ERP (Modul Dasar) | Sintetis Mandiri (IT SOP) | 2026 | 3 halaman | Sah, bebas data pribadi |

### Konfirmasi Kelayakan:
- [x] Seluruh dokumen sah saya pakai (100% data sintetis terkurasi mandiri, mematuhi Aturan R1 & K5).
- [x] Tidak ada data pribadi orang sungguhan di dalamnya (seluruh nama entitas dan URL fiktif: `example.com`).
- [x] Sedikitnya enam pertanyaan uji saya terjawab oleh kumpulan ini (15 kasus uji dirancang mencakup ke-8 dokumen).

---

## 5. Uji Lima Kriteria Penolakan

1. **AI Tidak Dipaksakan pada Persoalan Deterministik:**  
   *LOLOS:* Kalkulasi teknis, pencarian ranking dokumen (BM25 + Cosine similarity), dan status tiket ditangani oleh kode logika deterministik Python/MySQL; AI hanya dipakai untuk pemahaman bahasa keluhan, dialog klarifikasi, dan penyusunan kalimat panduan.
2. **Keluaran Dapat Dibuktikan Benar atau Salah:**  
   *LOLOS:* Kebenaran jawaban dapat diverifikasi secara biner dengan mencocokkan kutipan (*quote*) terhadap teks asli dokumen SOP di knowledge base.
3. **Memiliki Sumber Pengetahuan yang Sah dan Dapat Diakses:**  
   *LOLOS:* 8 dokumen Markdown sintetis kanonik telah tersedia penuh di repositori proyek.
4. **Bebas dari Ketergantungan Data Pribadi Nyata:**  
   *LOLOS:* Menggunakan entitas fiktif korporat "PT Contoh Sejahtera" dan tidak menggunakan data karyawan riil.
5. **Lingkup Persoalan Terfokus dan Realistis:**  
   *LOLOS:* Dibatasi tegas pada 8 kategori kendala helpdesk IT kantor level-1 umum yang dapat diselesaikan staf dalam $\le 4$ langkah mandiri.
