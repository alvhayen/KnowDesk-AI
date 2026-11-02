# Panduan Pengerjaan dan Pengumpulan Tugas Mingguan (Minggu 1 – 7)
## Proyek: KnowDesk AI — Asisten Bantuan Mandiri IT Service Desk
**Mata Kuliah:** Kapita Selekta: AI Engineering | Ganjil 2026/2027  
**Dosen:** Aidil Saputra Kirsan, S.ST., M.Tr.Kom.  
**Konfigurasi Parameter Peserta:** $K = 3$ (Dokumen KB: 8, Kasus Uji: 15, Tool: 3, Mode Keluaran: 1 Standar)

---

## 📌 Ringkasan Ketentuan Pengumpulan Dosen

Sesuai instruksi perkuliahan, setiap minggu tugas dikumpulkan dalam bentuk satu berkas arsip terkompresi:
```
<NIM>-m<minggu>.zip
```
*(Contoh: `1201230045-m1.zip`, `1201230045-m2.zip`, dst.)*

### 📦 Isi Wajib di dalam Berkas ZIP:
1. **Artefak Produk (Kumulatif)**:
   - Berkas hasil kerja teknis (kode, prompt, skema, rancangan, atau dokumen spesifikasi) yang bertambah setiap minggunya (pekerjaan minggu lalu tidak dibuang, melainkan menjadi fondasi minggu ini).
2. **`catatan-proses.md`**:
   - Wajib menggunakan format kanonik **Lampiran C**.
   - **Maksimal 2 halaman**. Tulisan padat, jujur, dan dapat ditelusuri.
   - Kolom prediksi pada tahap `BREAK` wajib terisi sebelum eksperimen dijalankan.
3. **Folder `bukti/`**:
   - Berisi rekaman terminal, log keluaran JSON, tabel pengujian, dan tangkapan layar verifikasi bahwa sistem benar-benar bekerja sesuai skenario.

---

## 🗂️ Struktur Direktori `Tugas Mingguan/`

Folder ini telah disiapkan secara terstruktur untuk Tugas 1 sampai dengan Tugas 7:

```text
Tugas Mingguan/
├── README.md                      <-- (File ini) Panduan operasional & rubrik penilaian
├── package-tugas.ps1              <-- Script otomatisasi pembuatan ZIP (<NIM>-m<N>.zip)
│
├── m1/                            <-- Tugas 1 — Peta Minat dan Calon Persoalan
│   ├── catatan-proses.md          <-- Catatan proses Lampiran C (maks. 2 halaman)
│   ├── peta-minat.md              <-- Luaran pemetaan persoalan IT Service Desk (K = 3)
│   └── bukti/
│       ├── README.md              <-- Panduan tangkapan layar/bukti
│       └── log-break-m1.md        <-- Log uji coba halusinasi & batas model
│
├── m2/                            <-- Tugas 2 — Laporan Pengamatan Perilaku Model
│   ├── catatan-proses.md          <-- Catatan proses Lampiran C
│   ├── laporan-pengamatan.md      <-- Luaran bedah token, suhu, dan halusinasi
│   └── bukti/
│       ├── README.md
│       └── log-break-m2.md        <-- Log komparasi suhu & fenomena lost-in-the-middle
│
├── m3/                            <-- Tugas 3 — Bukti Pemanggilan Model Pertama
│   ├── catatan-proses.md          <-- Catatan proses Lampiran C
│   ├── call_model.py              <-- Script mandiri pemanggilan model (aman API key)
│   ├── catatan-pemakaian.md       <-- Buku besar pemakaian token & biaya
│   ├── perbandingan-model.md      <-- Evaluasi komparatif 3 model OpenRouter
│   └── bukti/
│       ├── README.md
│       └── output_pemanggilan.json<-- Bukti respon payload mentah model gateway
│
├── m4/                            <-- Tugas 4 — Lembar Tema Proyek dan Prompt v1
│   ├── catatan-proses.md          <-- Catatan proses Lampiran C
│   ├── lembar-tema.md             <-- Formulir resmi Lampiran B (K = 3 terkunci)
│   ├── instruksi/
│   │   ├── v1.md                  <-- Prompt sistem awal (6 sumbu kanonik)
│   │   ├── v2.md                  <-- Prompt sistem revisi hasil evaluasi
│   │   └── CATATAN.md             <-- Riwayat perubahan prompt
│   └── bukti/
│       ├── README.md
│       ├── hasil-uji-5-kasus.md   <-- Bukti evaluasi 5 variasi input
│       └── tantangan-wajib-m4.md  <-- Bukti perubahan 1 kalimat (sebelum vs sesudah)
│
├── m5/                            <-- Tugas 5 — Prototipe Output Berformat Tetap
│   ├── catatan-proses.md          <-- Catatan proses Lampiran C
│   ├── skema-kontrak.md           <-- Spesifikasi kontrak Pydantic & JSON
│   ├── validator.py               <-- Kode validator skema & fallback 3-langkah
│   ├── instruksi/                 <-- Kumulatif prompt v1, v2, CATATAN.md
│   └── bukti/
│       ├── README.md
│       ├── uji-10-masukan.md      <-- Evaluasi 10 kasus uji integritas skema
│       └── uji-fallback-error.md  <-- Bukti mekanisme retry saat diserang malformed input
│
├── m6/                            <-- Tugas 6 — Prototipe Memanggil Tool
│   ├── catatan-proses.md          <-- Catatan proses Lampiran C
│   ├── spesifikasi-tool.md        <-- Kontrak 3 tool (search_kb, get_article, draft_ticket)
│   ├── tools_runner.py            <-- Eksekutor function calling dengan batas akses
│   ├── instruksi/                 <-- Prompt sistem terintegrasi tool
│   └── bukti/
│       ├── README.md
│       ├── trace-eksekusi-tool.md <-- Jejak eksekusi 1 putaran model memanggil tool
│       ├── uji-8-skenario-tool.md <-- Evaluasi pemilihan tool pada 8 variasi pertanyaan
│       └── tantangan-wajib-m6.md  <-- Bukti tuning deskripsi tool menyelesaikan salah pilih
│
└── m7/                            <-- Tugas 7 — Rancangan Alur RAG
    ├── catatan-proses.md          <-- Catatan proses Lampiran C
    ├── rancangan-rag.md           <-- 6 keputusan desain RAG, formula ambang, metadata
    ├── knowledge_base/            <-- Ringkasan 8 dokumen SOP kanonik (KB-001 s.d KB-008)
    ├── backend/                   <-- Kode pipeline chunker & retriever deterministik
    └── bukti/
        ├── README.md
        ├── chunking-manual-sample.md <-- Analisis chunking manual 5 bagian pertama
        ├── hasil-uji-ambang-rag.md   <-- Log kalibrasi cosine similarity & penolakan ungrounded
        └── tantangan-wajib-m7.md     <-- Analisis multi-dokumen RAG & mitigasi biaya
```

---

## ⚡ Cara Cepat Mengemas Berkas ZIP Pengumpulan

Anda dapat menggunakan script otomatisasi `package-tugas.ps1` yang tersedia di direktori ini.

### Cara 1: Menggunakan Script PowerShell (Sangat Disarankan)
Buka terminal PowerShell pada direktori `Tugas Mingguan/`:
```powershell
# Mengompres satu minggu tertentu (misal: NIM Anda 1201230045, Minggu 1)
.\package-tugas.ps1 -NIM "1201230045" -Minggu 1

# Mengompres seluruh minggu (1 sampai 7) sekaligus:
.\package-tugas.ps1 -NIM "1201230045" -All
```

### Cara 2: Perintah Manual PowerShell
Jika ingin mengompresi manual per folder:
```powershell
# Contoh untuk Minggu 1
Compress-Archive -Path ".\m1\*" -DestinationPath ".\1201230045-m1.zip" -Force
```

---

## 🎯 Panduan Detail & Checklist Tiap Tugas (Minggu 1 – 7)

### 1. Tugas 1 — Peta Minat dan Calon Persoalan (Minggu 1)
- **Target:** Membedakan batas AI Engineering vs ML vs DB konvensional, menghitung parameter $K=3$, dan merumuskan calon masalah IT Service Desk.
- **Artefak:**
  - `peta-minat.md`: Memuat profil $K=3$, tabel perbandingan 3 disiplin, bedah 3 calon persoalan (IT Support Helpdesk, Audit Log Akses, Penjadwalan Shift Teknisi), alasan mengapa IT Helpdesk dipilih, dan tantangan wajib (AI keliru dipakai untuk hitung kuota cuti/database deterministik).
  - `catatan-proses.md`: Refleksi tahap READ-BREAK-BUILD, prediksi BREAK terisi sebelum uji.
  - `bukti/`: Tangkapan layar/log model saat ditanya hal fiktif (halusinasi percaya diri).
- **Bobot Nilai:** Syarat kelulusan fondasi Blok A & penguncian parameter lingkup.

### 2. Tugas 2 — Laporan Pengamatan Perilaku Model (Minggu 2)
- **Target:** Mengamati sifat bawaan token, pengaruh variasi temperatur ($0$ vs $1$), fenomena *lost-in-the-middle*, dan mitigasi halusinasi.
- **Artefak:**
  - `laporan-pengamatan.md`: Bedah 5 baris pernyataan model terhadap fakta, 6 percobaan BREAK, pengulangan 5x instruksi "JIKA TIDAK TAHU JAWAB TIDAK TAHU", perhitungan matematis biaya token 100 pengguna x 20 panggilan, dan formulasi prompt pengakuan ketidaktahuan.
  - `catatan-proses.md`: Refleksi tahap READ-BREAK-BUILD.
  - `bukti/`: Log terminal respon model pada variasi suhu dan letak injeksi informasi.
- **Bobot Nilai:** Komponen Tugas (5%).

### 3. Tugas 3 — Bukti Pemanggilan Model Pertama (Minggu 3)
- **Target:** Berhasil memanggil model via OpenRouter API / Gateway dari kode Python lokal, memisahkan credential API key ke `.env`, dan menginisialisasi buku besar pemakaian token.
- **Artefak:**
  - `call_model.py`: Script Python modular yang memuat konfigurasi dari `.env`, memanggil model gateway, mencatat token usage, dan menangani error secara elegan.
  - `catatan-pemakaian.md`: Buku besar pemakaian token & rupiah per panggilan.
  - `perbandingan-model.md`: Tabel perbandingan metrik 3 model (Model Kecil: DeepSeek V3/Llama-3-8B, Model Sedang: Gemini Flash, Model Besar: Claude Sonnet) dari segi latensi, biaya, dan relevansi.
  - `catatan-proses.md`: Laporan kendala dan keputusan arsitektural.
  - `bukti/`: JSON raw response pemanggilan pertama.
- **Bobot Nilai:** Evaluasi Lingkungan Kerja + **Kuis 1 (10% total)** di awal pertemuan.

### 4. Tugas 4 — Lembar Tema Proyek dan Prompt v1 (Minggu 4)
- **Target:** Mengunci tema proyek pada **Lampiran B**, merumuskan prompt sistem kanonik dengan 6 sumbu kepatuhan, dan mencatat evolusi v1 $\rightarrow$ v2.
- **Artefak:**
  - `lembar-tema.md`: Lembar resmi Lampiran B berisi deklarasi persoalan KnowDesk AI, 5 uji kriteria penolakan, target lingkup $K=3$ (8 dokumen KB, 15 kasus uji, 3 tools).
  - `instruksi/v1.md`: Instruksi sistem dengan pembagian 6 sumbu (Peran, Konteks, Tugas, Batasan, Contoh, Format) dan data tags (`<konteks_kb>`, `<pesan_pengguna>`).
  - `instruksi/v2.md`: Revisi instruksi yang memperketat format teks polos tanpa markdown bintang/bold.
  - `instruksi/CATATAN.md`: Tabel riwayat evolusi versi prompt.
  - `catatan-proses.md`: Refleksi tahap READ-BREAK-FIX-BUILD.
  - `bukti/`: Hasil uji perbandingan v1 vs v2 pada 5 input (2 khas, 2 batas, 1 penolakan), serta bukti tantangan wajib perubahan 1 kalimat.
- **Batas Kritis:** Tema **terkunci permanen** setelah minggu ini!

### 5. Tugas 5 — Prototipe Output Berformat Tetap (Minggu 5)
- **Target:** Memaksa model mengeluarkan format terstruktur (JSON/Pydantic) dengan field bukti kutipan persis (*exact quote*) dan opsi nilai "tidak dapat ditentukan", serta sistem fallback 3-langkah.
- **Artefak:**
  - `skema-kontrak.md`: Dokumentasi skema Pydantic `TroubleshootResponse` dan `ResolutionStep`.
  - `validator.py`: Script Python penguji schema validity dan fallback 3 langkah (Validasi $\rightarrow$ Retry dengan error prompt $\rightarrow$ Fail-safe ticket escalation).
  - `catatan-proses.md`: Refleksi READ-BREAK-FIX-BUILD.
  - `bukti/`: Tabel evaluasi 10 kasus uji masukan (termasuk adversarial attack & teks panjang) dan log eksekusi fallback mechanism.
- **Bobot Nilai:** Bagian dari Luaran Blok B (10%).

### 6. Tugas 6 — Prototipe Memanggil Tool (Minggu 6)
- **Target:** Mengimplementasikan Function Calling untuk 3 tool wajib $K=3$ (`search_kb`, `get_article`, `draft_ticket`) dengan batas akses tertulis dan mitigasi error transparan.
- **Artefak:**
  - `spesifikasi-tool.md`: Definisi skema JSON Schema tiap tool, penjelasan kapan *TIDAK BOLEH* dipanggil, dan deklarasi *Human-in-the-Loop* (tiket tidak dikirim sebelum disetujui pengguna).
  - `tools_runner.py`: Script eksekusi tool dengan penanganan error jujur.
  - `catatan-proses.md`: Refleksi READ-BREAK-FIX-BUILD.
  - `bukti/`: Trace 1 siklus pemanggilan tool, hasil pengujian 8 variasi pertanyaan, dan bukti tantangan wajib penyelesaian salah pilih tool murni lewat penyempurnaan deskripsi.
- **Bobot Nilai:** Pengumpulan Luaran Blok B (10%) + **Kuis 2 (10% total)** di awal pertemuan.

### 7. Tugas 7 — Rancangan Alur RAG (Minggu 7)
- **Target:** Menyusun blueprint arsitektur RAG grounded untuk 8 dokumen KB, menentukan strategi chunking hierarkis berbasis heading Markdown, formula ambang similarity, dan set 10 pertanyaan uji.
- **Artefak:**
  - `rancangan-rag.md`: Dokumen blueprint komprehensif berisi 6 keputusan desain RAG berlandaskan alasan teknis, penentuan ambang batas cosine similarity, format sitasi persis, dan penanganan pertanyaan di luar sumber.
  - `knowledge_base/`: Ringkasan 8 dokumen SOP IT sintetis kanonik (`KB-001` s/d `KB-008`).
  - `catatan-proses.md`: Refleksi READ-BREAK-FIX-BUILD.
  - `bukti/`: Analisis chunking manual 5 sampel, pengujian kueri di luar dokumen (memastikan model tidak berhalusinasi), dan analisis tantangan wajib multi-dokumen retrieval.
- **Batas Kritis:** Menjadi fondasi utama bahan presentasi **UTS (Minggu 8)**!

---

## ⚖️ Rubrik Penilaian Dosen yang Wajib Diperhatikan

Setiap luaran mingguan dinilai dengan proporsi tetap:
1. **Rancangan dan Alasannya (35%)**:
   - Dosen menilai *mengapa* keputusan diambil dan *alternatif apa yang ditolak*. Jangan hanya menulis kode/prompt tanpa argumen!
2. **Bukti Sistem Bekerja (25%)**:
   - Bukti wajib menyertakan masukan persis dan keluaran model. Melaporkan kegagalan secara jujur dinilai penuh; mengklaim sukses tanpa bukti dinilai 0.
3. **Catatan Proses (25%)**:
   - Kolom prediksi di tahap `BREAK` harus terisi sebelum mencoba. Catat secara transparan apa yang diubah dari bantuan AI (kolom "yang saya ubah" tidak boleh "tidak ada"). Maksimal 2 halaman.
4. **Tantangan Wajib (15%)**:
   - Kerjakan tantangan khusus pada modul minggu bersangkutan. Jika gagal, tuliskan analisis mengapa pendekatan yang dicoba belum berhasil.

---

## ⚠️ Checklist Final Sebelum Mengunggah ke Portal Kuliah

- [ ] Nama berkas zip tepat: `<NIM>-m<minggu>.zip` (semua huruf kecil).
- [ ] Di dalam zip langsung terlihat file `catatan-proses.md`, folder `bukti/`, dan file artefak produk (tidak bersarang di dalam folder ganda).
- [ ] `catatan-proses.md` tidak melebihi 2 halaman dan nama/NIM sudah diganti dari placeholder.
- [ ] Tidak ada API key atau kredensial rahasia yang tidak sengaja terunggah di dalam kode atau catatan log!
- [ ] Seluruh butir daftar periksa mandiri pada minggu bersangkutan telah diverifikasi.
