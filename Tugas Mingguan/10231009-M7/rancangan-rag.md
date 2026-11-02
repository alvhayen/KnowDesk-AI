# TUGAS 7 — RANCANGAN ALUR RAG (GROUNDING)
## Arsitektur Temu-Kembali Berbasis Bukti untuk Bantuan Mandiri IT Helpdesk
**Mata Kuliah:** Kapita Selekta: AI Engineering (Ganjil 2026/2027)  
**Proyek:** KnowDesk AI ($K = 3$)

---

## 1. Daftar Dokumen Rujukan Resmi ($K = 3 \rightarrow 8$ Dokumen)

Seluruh dokumen disusun dalam format Markdown sintetis kanonik dengan metadata YAML front matter:

| # | ID Dokumen | Judul Dokumen SOP | Kategori | Asal & Kepatuhan Data | Halaman Setara | Status Kelayakan |
|:--:|---|---|---|---|:--:|:--:|
| 1 | `KB-001` | Panduan Troubleshooting Koneksi Wi-Fi Kantor | `jaringan` | Sintetis Mandiri (PT Contoh Sejahtera) | 4 | **Sah & Bersih** |
| 2 | `KB-002` | Prosedur Reset dan Pemulihan Password Email | `email` | Sintetis Mandiri (PT Contoh Sejahtera) | 3 | **Sah & Bersih** |
| 3 | `KB-003` | Panduan Konfigurasi VPN untuk Akses Jarak Jauh | `jaringan` | Sintetis Mandiri (PT Contoh Sejahtera) | 3 | **Sah & Bersih** |
| 4 | `KB-004` | Panduan Instalasi dan Troubleshooting Printer Jaringan | `perangkat` | Sintetis Mandiri (PT Contoh Sejahtera) | 3 | **Sah & Bersih** |
| 5 | `KB-005` | Panduan Penggunaan Microsoft Teams dan Outlook | `aplikasi` | Sintetis Mandiri (Sengaja semi-rapi §5.2) | 3 | **Sah & Bersih** |
| 6 | `KB-006` | Prosedur Permintaan Akses Folder Bersama | `lainnya` | Sintetis Mandiri (PT Contoh Sejahtera) | 3 | **Sah & Bersih** |
| 7 | `KB-007` | Panduan Keamanan Akun dan Autentikasi Dua Faktor | `lainnya` | Sintetis Mandiri (PT Contoh Sejahtera) | 3 | **Sah & Bersih** |
| 8 | `KB-008` | Panduan Troubleshooting Aplikasi ERP (Modul Dasar) | `aplikasi` | Sintetis Mandiri (Sengaja semi-rapi §5.2) | 3 | **Sah & Bersih** |

---

## 2. Enam Keputusan Desain Arsitektur RAG Berlandaskan Alasan

| # | Keputusan Desain | Nilai / Kebijakan yang Dipilih | Alasan Teknis & Pertimbangan Desain |
|:--:|---|---|---|
| **1** | **Ukuran Chunk (*Chunking Strategy*)** | Pemotongan Hierarkis Berbasis Heading Markdown (`## Bagian` dan `### Langkah`) | Dokumen SOP ditulis oleh manusia dalam unit gagasan utuh per langkah. Pemotongan tetap (misal per 500 karakter) akan memotong kalimat perintah terminal, URL SSO, atau parameter konfigurasi di tengah kata. |
| **2** | **Tumpang Tindih (*Overlap*)** | $0$ Karakter (Pemisahan Struktural Murni) | Karena batas chunk mengikuti struktur logis heading Markdown, setiap unit langkah bersifat mandiri (*self-contained*). Menambahkan overlap berbasis token kata justru menimbulkan duplikasi teks pada jendela konteks dan memboroskan token. |
| **3** | **Jumlah Chunk Terambil ($N$ / Top-K)** | $K = 3$ Chunk Teratas | 3 chunk memberikan cakupan konteks yang cukup untuk membandingkan langkah awal dan prasyarat masalah, tanpa memicu fenomena *Lost in the Middle* atau menggelembungkan biaya token masukan. |
| **4** | **Ambang Kemiripan (*Similarity Threshold*)** | Cosine Similarity $\ge 0.70$ (pada model embedding dimensi 1536) | Eksperimen kalibrasi devset membuktikan bahwa kueri yang tidak ada di dokumen menghasilkan kemiripan semantik $0.45 - 0.62$. Ambang $0.70$ bertindak sebagai gerbang deterministik (*deterministic gatekeeper*) untuk menyaring kueri halusinasi. |
| **5** | **Metadata yang Disertakan Bersama Chunk** | `article_id`, `judul`, `section`, `langkah_ke`, `kategori` | Diperlukan agar sistem dapat memvalidasi kutipan persis (*exact substring quote*) dan menampilkan sitasi rujukan resmi di antarmuka pengguna frontend. |
| **6** | **Perilaku Jika Tidak Ditemukan** | Menolak Menjawab ("Panduan belum tersedia") dan Menawarkan Draf Tiket Eskalasi | **Keputusan Etis:** Sistem dilarang keras beralih ke pengetahuan umum model saat dokumen resmi tidak ada. Memberikan tebakan umum pada sistem enterprise menipu ekspektasi pengguna dan membahayakan kepatuhan keamanan TI. |

---

## 3. Format Konteks yang Dikirimkan ke Model

Konteks diinjeksi menggunakan penanda pembatas (*delimiter tags*) XML yang bersih dari instruksi operasional:

```xml
<konteks_kb>
[DOKUMEN 1]
article_id: KB-001
judul: Panduan Troubleshooting Koneksi Wi-Fi Kantor
section: Bagian 2: Langkah Solusi Mandiri
langkah_ke: 1
teks:
Matikan adapter Wi-Fi di laptop Anda selama 10 detik lalu nyalakan kembali. Coba sambungkan ulang ke SSID 'CorpNet'. Jika diminta kata sandi, gunakan akun domain Windows Anda.

[DOKUMEN 2]
article_id: KB-001
judul: Panduan Troubleshooting Koneksi Wi-Fi Kantor
section: Bagian 2: Langkah Solusi Mandiri
langkah_ke: 2
teks:
Lupakan jaringan (Forget Network) 'CorpNet' melalui menu Wi-Fi Settings. Setelah itu, klik kembali nama SSID dan pilih opsi 'Connect automatically'.
</konteks_kb>
```

---

## 4. Instruksi Sistem Versi RAG Grounded

```markdown
Anda adalah KnowDesk AI, asisten helpdesk IT internal PT Contoh Sejahtera.
Tugas Anda adalah mendampingi staf kantor menyelesaikan kendala IT hanya berdasarkan informasi di dalam <konteks_kb>.

ATURAN GROUNDING MUTLAK:
1. Jawab HANYA menggunakan informasi yang tercantum secara eksplisit di dalam <konteks_kb>. Dilarang menggunakan pengetahuan umum internet.
2. Jika <konteks_kb> kosong atau tidak memuat solusi dari kendala yang ditanyakan, katakan dengan jujur: "Panduan untuk kendala ini belum tersedia di basis pengetahuan resmi kami. Apakah Anda ingin saya buatkan draf tiket eskalasi ke teknisi IT?"
3. Sajikan HANYA SATU langkah pertama dalam satu pesan. Jangan berikan langkah selanjutnya sebelum pengguna mengonfirmasi.
4. Sertakan kutipan teks asli yang persis (substring) pada medan 'kutipan' di objek keluaran JSON. Dilarang mengubah satu huruf pun dari kutipan dokumen.
```

---

## 5. Sepuluh Kasus Uji Evaluasi Grounding

| # | Tipe Kasus | Pertanyaan Uji Pengguna | Dokumen Target | Perilaku yang Diharapkan |
|:--:|---|---|---|---|
| 1 | **Tunggal** | "Bagaimana cara konek ulang ke Wi-Fi kantor kalau putus?" | `KB-001` | Mengambil langkah 1 (restart adapter Wi-Fi) + kutipan persis `KB-001`. |
| 2 | **Tunggal** | "Saya lupa sandi akun email Microsoft Outlook saya." | `KB-002` | Mengarahkan ke portal SSO mandiri + kutipan persis `KB-002`. |
| 3 | **Tunggal** | "VPN kantor saya muncul pesan authentication failed." | `KB-003` | Panduan periksa username domain dan sertifikat klien. |
| 4 | **Tunggal** | "Kertas printer di lantai 2 macet di dalam roll penarik." | `KB-004` | Panduan mematikan daya dan membuka baki paper jam `KB-004`. |
| 5 | **Tunggal** | "Bagaimana cara meminta hak akses ke folder bersama departemen finance?" | `KB-006` | Panduan mengisi form approval shared drive `KB-006`. |
| 6 | **Tunggal** | "Aplikasi ERP FinOps saya mendadak force close saat cetak invoice." | `KB-008` | Panduan hapus cache temporary ERP `KB-008`. |
| 7 | **Tersebar (Multi-Doc)** | "Saya mau buka email kantor dari rumah tapi koneksi internet saya harus lewat VPN kantor dulu." | `KB-002` & `KB-003` | Mengambil koneksi VPN dulu (`KB-003`), baru panduan akses webmail (`KB-002`). |
| 8 | **Tersebar (Multi-Doc)** | "Setelah ganti password email, akun saya di Teams dan VPN ikut bermasalah." | `KB-002`, `KB-003`, `KB-005` | Menjelaskan propagasi password SSO ke aplikasi turunan. |
| 9 | **Ungrounded (Ketiadaan Solusi)** | "Monitor komputer saya layarnya pecah bergaris ungu setelah terbentur meja." | *Tidak Ada (Hardware)* | **Menolak:** Menyatakan panduan tidak ada dan menawarkan tiket teknisi hardware. |
| 10| **Ungrounded (Ketiadaan Solusi)** | "Bagaimana cara mengajukan reimbursment pulsa internet bulanan?" | *Tidak Ada (Keuangan/HR)*| **Menolak:** Menyatakan panduan tidak tersedia di KB teknis. |

---

## 6. Bentuk Keluaran Terstruktur dengan Sitasi Rujukan

Setiap respon panduan memuat metadata sitasi rujukan yang dapat diklik (*verifiable source citation*):

```json
{
  "dapat_ditentukan": "ya",
  "kategori": "jaringan",
  "tingkat_urgensi": "sedang",
  "langkah_ke": 1,
  "total_langkah": 4,
  "pesan": "Silakan matikan adapter Wi-Fi di laptop Anda selama 10 detik lalu nyalakan kembali dan coba sambungkan ulang ke SSID 'CorpNet'.",
  "tindakan_berikutnya": "tunggu_konfirmasi",
  "sumber": [
    {
      "article_id": "KB-001",
      "judul_artikel": "Panduan Troubleshooting Koneksi Wi-Fi Kantor",
      "section": "Bagian 2: Langkah Solusi Mandiri",
      "kutipan": "Matikan adapter Wi-Fi di laptop Anda selama 10 detik lalu nyalakan kembali."
    }
  ]
}
```

---

## 7. Tantangan Wajib — Pengambilan Konteks Multi-Dokumen

### 1. Mengapa Mengambil Top-3 Chunk Mungkin TIDAK CUKUP:
Pada kasus nomor 7 dan 8 (pertanyaan yang jawabannya tersebar di 2 atau 3 dokumen berbeda), kueri pengguna sering kali memiliki kedekatan semantik yang lebih dominan ke salah satu dokumen (misal istilah "VPN" mendominasi kueri). Akibatnya, seluruh slot Top-3 chunk terisi oleh potongan dari dokumen VPN (`KB-003`), sementara potongan krusial dari dokumen email (`KB-002`) terdepak ke peringkat 4 atau 5. Hal ini menyebabkan model hanya menerima separuh informasi.

### 2. Dua Cara Alternatif Mengatasinya Beserta Biaya:

#### Solusi A: Dekomposisi Kueri (*Sub-Query Decomposition*)
- **Mekanisme:** Model orkestrator kecil membedah kueri majemuk menjadi dua kueri mandiri: (1) *"Cara koneksi VPN kantor dari rumah"*, dan (2) *"Akses webmail kantor lewat peramban"*. Sistem menjalankan retrieval terpisah untuk masing-masing kueri lalu menggabungkan chunk teratasnya.
- **Biaya:** Memerlukan 1 pemanggilan LLM ekstra untuk dekomposisi kueri ($\approx 100 \text{ token input} + 30 \text{ token output} \approx \mathbf{\text{Rp } 0,45 \text{ per kueri}}$).

#### Solusi B: Diversifikasi Hasil Vektor (*Maximal Marginal Relevance / MMR*)
- **Mekanisme:** Menggunakan algoritma MMR saat mengambil chunk dari indeks vektor. MMR menyeimbangkan antara relevansi terhadap kueri dan kebaruan (*diversity*) terhadap chunk yang sudah terambil sebelumnya, sehingga dokumen kedua tidak tereliminasi oleh variasi kalimat dokumen pertama.
- **Biaya:** **Rp 0** biaya LLM (murni kalkulasi aljabar linier komputasi vektor di memori server backend).
