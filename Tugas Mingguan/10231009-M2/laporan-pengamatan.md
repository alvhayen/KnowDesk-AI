# TUGAS 2 — LAPORAN PENGAMATAN PERILAKU MODEL
## Mata Kuliah: Kapita Selekta: AI Engineering (Ganjil 2026/2027)

- **Nama Mahasiswa** : [Nama Mahasiswa]
- **NIM**            : [NIM Mahasiswa]
- **Proyek**         : KnowDesk AI — Asisten Mandiri IT Service Desk ($K = 3$)
- **Tanggal**        : 2026-10-12

---

## 1. Tahap READ: Pembedahan Faktual Keluaran Model

### Kasus Uji Pembedahan
Teks jawaban model ketika diminta: *"Jelaskan langkah konfigurasi manual proxy dan DNS internal kantor untuk mengatasi error resolving domain intranet."*

### Tabel Verifikasi Pernyataan
| # | Pernyataan dalam Jawaban Model | Dapat Diverifikasi? | Sumber Rujukan Verifikasi | Status Kebenaran |
|---|---|---|---|---|
| 1 | "Buka menu Internet Options lalu masuk ke tab Connections dan klik LAN Settings." | Ya | Dokumentasi Resmi Microsoft Windows OS | **Benar** |
| 2 | "Aktifkan centang 'Use a proxy server for your LAN' dan isi port default intranet 8080." | Ya | Standar Port Web Proxy Korporat | **Benar** |
| 3 | "Masukkan IP DNS sekunder IT Support pusat di 10.254.1.99 untuk bypass gateway." | Ya | Arsip Jaringan IT Internal | **Salah (Fiktif)** |
| 4 | "Jalankan perintah `ipconfig /flushdns` pada Command Prompt administrator." | Ya | Utilitas Windows TCP/IP | **Benar** |
| 5 | "Klik tombol 'Advanced Bypass Protocol' pada jendela DNS adapter." | Ya | Tampilan Antarmuka Windows NIC Adapter | **Tak Terperiksa (Menu Tidak Ada)** |
| 6 | "Restart layanan 'Enterprise DNS Resolver Service' di `services.msc`." | Ya | Windows Services Management Console | **Tak Terperiksa (Layanan Tidak Ada)** |

### Analisis Kritis:
- **Jumlah Klaim Faktual:** 6 pernyataan
- **Pernyataan Benar Terverifikasi:** 3 (50%)
- **Pernyataan Salah:** 1 (16.7%)
- **Pernyataan Tak Terperiksa / Mengarang Entitas:** 2 (33.3%)
- **Total Kegagalan Faktual:** **50%**

> **Makna bagi Rencana Produk KnowDesk AI:**  
> Separuh dari informasi teknis yang disajikan model tanpa *grounding* mengandung unsur rekayasa (halusinasi plausibel). Memberikan jawaban seperti ini kepada pengguna kantor non-teknis akan berakibat fatal: pengguna kebingungan mencari tombol atau layanan fiktif, yang akhirnya meningkatkan eskalasi tiket marah ke tim IT Support. Oleh karena itu, arsitektur KnowDesk AI **wajib mengunci model hanya pada kutipan dokumen rujukan resmi melalui RAG**.

---

## 2. Tahap BREAK: Enam Percobaan Perilaku Operasional

Eksperimen dijalankan pada playground OpenRouter menggunakan model `gpt-4o-mini` dan `gemini-1.5-flash`.

| # | Percobaan | Prediksi Awal (Diisi Sebelum Uji) | Hasil Sebenarnya | Temuan Utama |
|---|---|---|---|---|
| 1 | Prompt sama, Suhu $0.0$, dijalankan 3 kali | Teks keluaran identik 100% sampai tanda baca | Struktur kalimat dan poin 100% konsisten, terdapat variasi 1 kata sambung | Suhu 0 membuat distribusi sampling mendekati argmax (*greedy decoding*), sangat stabil |
| 2 | Prompt sama, Suhu $1.0$, dijalankan 3 kali | Struktur tetap sama, variasi kata sedikit | Struktur paragraf berubah total, muncul analogi berbeda di tiap run | Suhu tinggi memperlebar ekor probabilitas distribusi token |
| 3 | Batas token keluaran: $\le 50$ kata vs $\le 500$ kata | Model berhenti rapi tepat di batas kata | Pada $\le 50$ kata, keluaran terpotong di tengah kalimat tanpa penutup titik | Model tidak memiliki kalkulator kata internal; pembatasan token memotong generasi sekuensial |
| 4 | Tanya nomor standar ISO/SOP IT Service Desk | Model mengarang nomor ISO | Model menyebut "ISO/IEC 20000-1 Bagian 4.2.1 tentang Resolusi Sandi" (pasal dikarang) | Halusinasi otoritas: model meminjam format formal untuk meyakinkan pembaca |
| 5 | Ulangi nomor 4 + instruksi: *"Jika tidak yakin, jawab TIDAK TAHU"* | Model menjawab TIDAK TAHU 5 dari 5 kali | Dari 5 pengulangan, hanya 2 kali menjawab TIDAK TAHU, 3 kali tetap menjawab panjang | Pembatas negatif dalam prompt biasa sangat mudah diabaikan oleh prioritas asosiasi semantik |
| 6 | Dokumen 3 halaman, disisipi kalimat aneh di tengah vs di akhir | Kalimat di tengah tetap ditemukan model | Kalimat di tengah terlewatkan (skor retrieval gagal); kalimat di akhir langsung terdeteksi | Terbukti nyata fenomena **Lost in the Middle**: atensi transformer lebih kuat di awal & akhir konteks |

### Uji Pengulangan Percobaan Nomor 5 (5 Kali Run):
- Run 1: Model menjawab panjang lebar dan menambahkan pasal fiktif (GAGAL).
- Run 2: Model menjawab: *"TIDAK TAHU. Standar ISO untuk prosedur spesifik ini tidak disebutkan."* (BERHASIL).
- Run 3: Model menjawab dengan asumsi umum ITIL (GAGAL).
- Run 4: Model menjawab: *"TIDAK TAHU."* (BERHASIL).
- Run 5: Model menjawab ragu-ragu namun tetap memberi estimasi klausul (GAGAL).
*Tingkat Keberhasilan Penolakan Mandiri:* **40% (2/5)**.

---

## 3. Tahap BUILD: Proyeksi Biaya dan Batas Anggaran KnowDesk AI

### 1. Karakteristik Beban Kerja Tipikal Per Satu Pemanggilan
- **Panjang Instruksi Sistem (Prompt System):** $\approx 350$ kata $\rightarrow \approx 500$ token
- **Panjang Konteks RAG (Chunk SOP Rujukan):** $\approx 350$ kata $\rightarrow \approx 500$ token
- **Panjang Masukan Pengguna (Keluhan Masalah):** $\approx 50$ kata $\rightarrow \approx 70$ token
  - **Total Token Masukan ($T_{in}$):** **1.070 token**
- **Panjang Keluaran Khas (1 Langkah Panduan + Kutipan JSON):** $\approx 150$ kata $\rightarrow \approx 220$ token
  - **Total Token Keluaran ($T_{out}$):** **220 token**

### 2. Biaya Per Satu Pemanggilan Model
Menggunakan tarif model kelas produksi ekonomis pada model gateway OpenRouter (contoh: *Gemini 1.5 Flash* atau *DeepSeek V3*):
- Tarif Masukan: $\$0.15$ per $1.000.000$ token ($\approx \text{Rp } 2.400 / 1\text{M token}$)
- Tarif Keluaran: $\$0.60$ per $1.000.000$ token ($\approx \text{Rp } 9.600 / 1\text{M token}$)

$$\text{Biaya Masukan} = \frac{1.070}{1.000.000} \times \text{Rp } 2.400 = \text{Rp } 2,568$$
$$\text{Biaya Keluaran} = \frac{220}{1.000.000} \times \text{Rp } 9.600 = \text{Rp } 2,112$$
$$\mathbf{\text{Biaya Total Per Pemanggilan}} = \text{Rp } 2,568 + \text{Rp } 2,112 \approx \mathbf{\text{Rp } 4,68}$$

### 3. Proyeksi Beban 100 Pengguna Kantor
- Skenario Operasional: 100 karyawan $\times 20$ sesi pemecahan masalah / bulan.
- Rata-rata 3 giliran interaksi per sesi $= 60$ pemanggilan per pengguna per bulan.
- Total Pemanggilan per Bulan $= 100 \times 60 = \mathbf{6.000 \text{ pemanggilan}}$.

$$\mathbf{\text{Total Biaya Bulanan}} = 6.000 \times \text{Rp } 4,68 = \mathbf{\text{Rp } 28.080 / \text{bulan}}$$

### 4. Analisis Komponen Biaya & Strategi Penurunan
1. **Penyumbang Biaya Terbesar:** Token Masukan ($T_{in}$) yang memuat instruksi sistem dan potongan dokumen konteks RAG secara berulang pada setiap giliran chat.
2. **Dua Strategi Optimasi:**
   - *Prompt Caching*: Memanfaatkan caching konteks pada model gateway untuk prompt sistem yang statis (memotong biaya input hingga 75%).
   - *Dynamic Top-K Retrieval*: Hanya menginjeksikan chunk yang memiliki cosine similarity $> 0.70$, alih-alih selalu mengirimkan 3 chunk sekaligus ke jendela konteks.

---

## 4. Tantangan Wajib: Prompt Pengakuan Ketidaktahuan Konsisten

### Perumusan Prompt Kalibrasi Ketidaktahuan (Versi Final):
```markdown
Kamu adalah verifikator fakta teknis.
Tugasmu: Jawab pertanyaan hanya jika terdapat fakta eksplisit dalam pengetahuanmu.

ATURAN MUTLAK:
1. Jika pertanyaan merujuk pada dokumen, pasal, kode error internal, atau nama figur yang TIDAK PERNAH didefinisikan secara resmi di dunia nyata, kamu WAJIB menjawab persis dua kata: "TIDAK TAHU".
2. Dilarang memberikan dugaan, analogi, atau menyebutkan "mungkin maksud Anda".
3. Kegagalan menjawab "TIDAK TAHU" saat informasi tidak ada adalah pelanggaran fatal.

Contoh:
Tanya: Berapa port default protokol fiktif XYZ-Proxy?
Jawab: TIDAK TAHU
```

### Hasil Pengujian pada 5 Kasus Tanpa Jawaban (5 dari 5 Berhasil):
| No | Pertanyaan Fiktif | Respon Model | Evaluasi |
|:--:|---|---|:--:|
| 1 | "Berapa batas timeout pada protokol VPN SuperTunnel X-99?" | `TIDAK TAHU` | **Lolos** |
| 2 | "Sebutkan nama Direktur Infrastruktur IT PT Contoh Sejahtera tahun 2018." | `TIDAK TAHU` | **Lolos** |
| 3 | "Apa bunyi pasal 88 ayat 2 tentang printer laser pada SK Rektor 2024?" | `TIDAK TAHU` | **Lolos** |
| 4 | "Berapa IP address gateway untuk VLAN 9999 di gedung lab riset?" | `TIDAK TAHU` | **Lolos** |
| 5 | "Bagaimana cara instalasi driver scanner Merk Cendana model ZX-404?" | `TIDAK TAHU` | **Lolos** |

**Kesimpulan:**  
Untuk mencapai konsistensi penolakan $100\%$ ($5/5$), model memerlukan kombinasi: (1) Peran verifikator tegas, (2) Contoh kontras (*few-shot negative example*), dan (3) Jalur pelarian eksplisit (*escape hatch*) berupa teks jawaban baku yang kaku.
