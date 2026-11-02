# TUGAS 1 — PETA MINAT DAN CALON PERSOALAN
## Mata Kuliah: Kapita Selekta: AI Engineering (Ganjil 2026/2027)

- **Nama Mahasiswa** : [Nama Mahasiswa]
- **NIM**            : [NIM Mahasiswa]
- **Program Studi**  : Sistem Informasi / Teknik Informatika
- **Kode Peserta K** : **3**

---

## 1. Perhitungan Angka Lingkup Wajib ($K = 3$)

Mengacu pada rumus resmi **Lampiran B (Lembar Tema Proyek dan Penurunan Lingkup)**:

| Parameter Lingkup | Rumus Acuan | Perhitungan ($K = 3$) | Nilai Wajib Minimum |
|---|---|---|---|
| **Jumlah Dokumen Rujukan KB** | $5 + (K \pmod 4)$ | $5 + (3 \pmod 4) = 5 + 3$ | **8 Dokumen** |
| **Jumlah Kasus Uji Evaluasi** | $12 + (K \pmod 6)$ | $12 + (3 \pmod 6) = 12 + 3$ | **15 Kasus** |
| **Jumlah Tool Minimum** | $2 + (K \pmod 2)$ | $2 + (3 \pmod 2) = 2 + 1$ | **3 Tool** |
| **Mode Keluaran Tambahan** | Genap = Wajib, Ganjil = Tidak | $K = 3$ (Ganjil) | **1 Mode Standar** (Teks Terstruktur) |
| **Jumlah Rekan Peer-Review** | Ketentuan Modul | UTS: 2 rekan, M12: 2 rekan | **4 Review** |

---

## 2. Pemetaan Disiplin: Kapan AI Engineering Dibutuhkan

Berdasarkan telaah Tahap READ modul:

| No | Persoalan | Disiplin yang Tepat | Alasan Teknis |
|:--:|---|---|---|
| 1 | Menghitung sisa kuota SKS mahasiswa dari riwayat transkrip | **Rekayasa Perangkat Lunak / Basis Data** | Persoalan deterministik murni dengan aturan aritmatika baku (SKS lulus - batas minimum). Toleransi kesalahan 0% dan tidak memerlukan interpretasi semantik bahasa. |
| 2 | Memperkirakan volume kontainer dan kunjungan kapal bulan depan dari data 5 tahun | **Machine Learning (Time-Series Regression)** | Persoalan ekstraksi pola statistik dari data numerik tabular historis untuk regresi/prediksi kuantitatif berbobot. |
| 3 | Meringkas 40 laporan survei lapangan menjadi tabel temuan berformat tetap | **AI Engineering** | Memerlukan pemahaman teks bahasa alami tidak terstruktur, ekstraksi entitas ke skema baku, dan perakitan alur kendali keluaran di atas model bahasa besar. |

> **Analisis Skala Data:**  
> Jika jumlah data laporan survei pada nomor 3 melonjak dari 40 menjadi 40.000 dokumen, persoalan tersebut berubah menjadi persoalan **Data Engineering & Retrieval Pipeline**. Satu panggilan prompt tidak lagi mampu menampung seluruh teks, sehingga sistem menuntut pemenggalan dokumen (*chunking*), indexing vektor terdistribusi, serta penyaringan metadata hierarkis sebelum model bahasa dipanggil.

---

## 3. Telaah Tiga Calon Persoalan Nyata

### Calon Persoalan 1: Asisten Bantuan Mandiri Service Desk IT (*KnowDesk AI*) — [PILIHAN UTAMA]
| Unsur Analisis | Uraian |
|---|---|
| **Siapa yang mengalaminya** | Karyawan dan staf kantor non-teknis yang mengalami kendala teknis harian (Wi-Fi putus, lupa kata sandi email, VPN macet, printer jaringan error), serta staf IT Support yang kewalahan melayani tiket berulang. |
| **Bagaimana diselesaikan sekarang** | Pengguna menghubungi meja helpdesk lewat pesan chat/telepon, atau mencari manual di portal wiki/PDF SOP IT internal yang tebal dan berisi jargon teknis rumit. |
| **Mengapa cara sekarang tidak memadai** | Dokumen SOP statis jarang dibaca karena terlalu panjang; antrean teknisi IT menumpuk hanya untuk menyelesaikan masalah sepele seperti salah memasukkan gateway atau proxy. |
| **Bukti keberhasilan sistem** | Pengguna berhasil menyelesaikan kendala mandiri mengikuti instruksi bertahap (1 pesan 1 langkah) dengan rujukan kutipan persis dari SOP, atau sistem menghasilkan draf tiket eskalasi yang terstruktur rapi. |
| **Sumber dokumen sah yang dimiliki** | 8 dokumen SOP helpdesk sintetis kanonik yang disusun mandiri berformat Markdown (`KB-001` s/d `KB-008`), bebas data pribadi, dan berbasis skenario enterprise umum. |
| **Satu alasan mengapa AI mungkin BUKAN jawabannya** | Jika kendala menyangkut kegagalan perangkat keras fisik (kabel LAN putus, monitor pecah), model AI tidak memiliki kemampuan intervensi fisik. |

---

### Calon Persoalan 2: Analisis Otomatis Audit Log Akses Server IT
| Unsur Analisis | Uraian |
|---|---|
| **Siapa yang mengalaminya** | Administrator sistem dan petugas audit keamanan TI yang harus memeriksa ribuan baris log otentikasi login SSH/Active Directory setiap minggu. |
| **Bagaimana diselesaikan sekarang** | Menggunakan script grep/regex atau filter manual di software spreadsheet. |
| **Mengapa cara sekarang tidak memadai** | Pola serangan yang tersebar atau anomali non-sekuensial sulit tertangkap oleh regex statis tanpa aturan yang sangat rumit. |
| **Bukti keberhasilan sistem** | Sistem mampu mengelompokkan anomali login ke dalam kategori risiko (rendah/sedang/tinggi) beserta ringkasan bukti waktu kejadian. |
| **Sumber dokumen sah yang dimiliki** | File log server uji sintetis (Apache/Auth.log tiruan). |
| **Satu alasan mengapa AI mungkin BUKAN jawabannya** | Log berukuran gigabyte jauh lebih efisien diproses menggunakan SIEM berbasis algoritma deterministik (Elasticsearch/Splunk) daripada dikirim ke model bahasa besar yang memakan biaya token sangat besar. |

---

### Calon Persoalan 3: Generator Panduan Onboarding Karyawan Baru Lintas Divisi
| Unsur Analisis | Uraian |
|---|---|
| **Siapa yang mengalaminya** | Karyawan baru yang kebingungan memahami hak akses aplikasi, aturan cuti, dan perangkat kerja yang sesuai dengan divisinya. |
| **Bagaimana diselesaikan sekarang** | Membaca dokumen buku saku karyawan (employee handbook) setebal 80 halaman saat hari pertama orientasi. |
| **Mengapa cara sekarang tidak memadai** | Informasi tersebar di berbagai bab dan kebijakan spesifik per divisi sering terlewatkan. |
| **Bukti keberhasilan sistem** | Karyawan dapat menanyakan checklist persiapan kerja divisi tertentu dan memperoleh daftar periksa personal yang akurat. |
| **Sumber dokumen sah yang dimiliki** | Panduan onboarding fiktif perusahaan. |
| **Satu alasan mengapa AI mungkin BUKAN jawabannya** | Sebagian besar alur onboarding cukup disajikan melalui formulir checklist statis di portal intranet tanpa memerlukan penalaran model generatif. |

---

## 4. Urutan Prioritas dan Keputusan Final

1. **Peringkat 1: Asisten Bantuan Mandiri Service Desk IT (*KnowDesk AI*)**
2. **Peringkat 2:** Generator Panduan Onboarding Karyawan Baru
3. **Peringkat 3:** Analisis Otomatis Audit Log Akses Server IT

**Alasan Memilih Calon Persoalan 1 untuk Dipertahankan hingga Minggu 16:**
Persoalan bantuan mandiri helpdesk IT menuntut dialog interaktif alami (menerjemahkan keluhan awam menjadi istilah teknis), memiliki batas benar-salah yang tegas berdasarkan dokumen SOP resmi, memungkinkan integrasi tool nyata (*search article*, *draft ticket*), serta memiliki batasan etika dan *guardrails* yang kaya (keamanan kata sandi, batas kewenangan bantuan).

---

## 5. Tantangan Wajib — Penggunaan AI Generatif pada Persoalan yang Salah

**Contoh Nyata di Lingkungan Kampus / Organisasi:**  
Penggunaan chatbot AI generatif publik untuk menghitung sisa masa studi mahasiswa dan memvalidasi kelayakan yudisium berdasarkan salinan transkrip nilai.

**Mengapa Pendekatan Ini Salah:**
1. **Deterministik vs Probabilistik:** Kelayakan yudisium dan batas SKS adalah formula hukum akademik yang memiliki jawaban biner pasti (Lolos / Belum Lolos). Model AI bersifat probabilistik dan rentan salah hitung angka SKS (halusinasi kalkulasi).
2. **Risiko Fatalitas:** Kesalahan interpretasi satu mata kuliah prasyarat dapat merugikan mahasiswa secara hukum akademik tanpa pertanggungjawaban yang jelas.
3. **Solusi yang Seharusnya Digunakan:** Sistem Informasi Akademik (SIAKAD) berbasis query basis data relasional (SQL) atau mesin aturan bisnis (*business rules engine*) deterministik dengan query terindeks, yang bekerja dalam hitungan milidetik dengan biaya operasional Rp 0 per eksekusi.
