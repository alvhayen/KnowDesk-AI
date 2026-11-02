# CATATAN PROSES — MINGGU 7

Nama / NIM / K : [Nama Mahasiswa] / [NIM Mahasiswa] / K = 3  
Tanggal        : 2026-10-12  
Waktu yang saya habiskan minggu ini : 9 jam  

---

## 1. Yang saya kerjakan minggu ini
Saya menyusun cetak biru arsitektur RAG grounded untuk 8 dokumen SOP kanonik ($K = 3$), merumuskan dokumen komprehensif `rancangan-rag.md` dengan 6 keputusan teknis berlandaskan alasan eksplisit, melakukan pemotongan chunk manual pada dokumen rujukan, mengkalibrasi ambang batas kemiripan (*cosine similarity*), serta menyusun 10 kasus uji ground evaluasi sebagai persiapan menghadapi presentasi UTS Minggu 8.

## 2. Tahap READ
Yang saya amati :
Ketika memotong dokumen SOP `KB-001` (Wi-Fi) secara manual, pemotongan per unit langkah kanonik (`### Langkah N: ...`) menghasilkan unit informasi yang utuh dan dapat dipahami secara mandiri (*self-contained*), asalkan metadata judul dokumen dan nama bagian diikutsertakan.

Yang mengejutkan saya :
Jika dokumen dipotong secara arbitrer berbasis jumlah karakter tetap (misal per 500 huruf), kalimat krusial seperti alamat URL portal SSO atau perintah terminal terpotong di tengah-tengah kata, membuat embedding semantiknya melenceng jauh.

## 3. Tahap BREAK
| # | Percobaan | Prediksi saya | Hasil sebenarnya | Prediksi tepat? |
|---|---|---|---|---|
| 1 | Ukuran chunk sangat kecil (1 kalimat) | Retrieval sangat tepat sasaran | Chunk terambil tepat namun model bingung karena kehilangan konteks nama aplikasi | tidak |
| 2 | Ukuran chunk sangat besar (3 halaman) | Konteks lengkap dan jawaban bagus | Skor kemiripan menurun drastis dan biaya token melonjak 4 kali lipat | ya |
| 3 | Tanpa overlap vs dengan overlap 50 kata | Hasil sama persis | Pada chunking struktural per heading, overlap kata tidak menambah akurasi | ya |
| 4 | Pertanyaan memakai istilah non-baku ("laptop silang merah") | Pencarian gagal total | Embedding semantik berhasil menemukan chunk Wi-Fi meskipun kata kunci tidak ada | tidak |
| 5 | Pertanyaan yang jawabannya TIDAK ADA di dokumen | Retrieval mengembalikan skor 0 | Chunk terdekat tetap terambil dengan skor kemiripan 0.58 | tidak |

Prediksi saya yang paling MELESET : nomor 4 dan 5  
Apa yang salah dari cara saya berpikir sebelumnya :
Pada nomor 4, saya meremehkan kekuatan embedding vektor yang mampu menangkap asosiasi semantik bahasa gaul. Pada nomor 5, fungsi cosine similarity selalu menghasilkan skor terhadap vektor terdekat terlepas dari apakah dokumen relevan atau tidak. Jika tidak dipasang ambang batas minimum ($\ge 0.70$), sistem akan tetap menyodorkan chunk yang salah ke model.

## 4. Tahap FIX
Kesalahan yang saya temukan :
Pada rancangan RAG contoh yang cacat: (1) Chunking 2.000 huruf tanpa overlap memotong klausul pasal, (2) Tidak ada metadata nama perda/pasal, (3) Pencarian top-3 tanpa ambang batas memicu salah rujukan, dan (4) Instruksi yang membolehkan memakai pengetahuan umum jika konteks kurang.
Bagaimana saya membuktikan diagnosis itu, bukan sekadar menduganya :
Cacat nomor 4 adalah yang paling merugikan pengguna karena sistem beralih ke halusinasi bebas saat dokumen tidak memuat aturan, namun pengguna mengira itu pasal hukum daerah asli.

## 5. Tahap BUILD
Yang berhasil :
1. Dokumen blueprint arsitektur `rancangan-rag.md` selesai memuat 6 keputusan kanonik berlandaskan alasan kuat.
2. Formulasi ambang batas gerbang deterministik: $\text{Cosine Similarity} \ge 0.70$.
3. Komposisi 10 kasus uji evaluasi (6 single-doc, 2 multi-doc, 2 ungrounded) tersusun rapi.

Yang tidak berhasil :
Pencarian murni Cosine similarity sempat kalah akurat pada kueri yang memuat kode error teknis spesifik (seperti `0x800CCC0E`); masalah ini diatasi pada arsitektur produk dengan menggabungkan *lexical search* (BM25) melalui Reciprocal Rank Fusion (RRF).

Keputusan rancangan yang saya ambil minggu ini, beserta alasannya :
| Keputusan | Alternatif yang saya tolak | Alasan memilih |
|---|---|---|
| Chunking berbasis struktur Heading Markdown | Chunking berbasis hitungan token tetap (500 token) | Struktur heading SOP adalah unit pemikiran manusia yang sudah tertata per langkah |
| Menolak menjawab jika skor kemiripan $< 0.70$ | Membiarkan model menjawab dari pengetahuan internet | Keputusan etis: integritas sistem enterprise menuntut kejujuran ketiadaan data |

## 6. Tantangan wajib
Hasil :
Untuk 2 kueri yang jawabannya tersebar di 2 dokumen berbeda (misal: "konfigurasi VPN saat Wi-Fi kantor bermasalah"):
- Mengambil Top-3 chunk tidak cukup karena slot top-3 didominasi oleh satu dokumen yang skor semantiknya tinggi, sehingga dokumen kedua terdepak.
- Dua solusi yang saya tawarkan:
  1. *Sub-query Decomposition*: Memecah kueri majemuk menjadi 2 kueri terpisah (Biaya: tambahan 1 pemanggilan LLM kecil $\approx \text{Rp } 0,40$).
  2. *Diverse Retrieval / Maximal Marginal Relevance (MMR)*: Penalti kemiripan antar dokumen yang terambil (Biaya: Rp 0, murni komputasi vektor di backend).

## 7. Penggunaan AI minggu ini
| # | Untuk apa | Prompt (ringkas / pola Lampiran A) | Yang saya UBAH dari hasilnya | Bagaimana saya verifikasi |
|---|---|---|---|---|
| 1 | Merancang set kasus uji | Pola Lampiran A Bagian C: 10 pertanyaan uji RAG | Menyesuaikan 2 kasus ungrounded khusus topik hardware kantor | Menguji pencarian pada 8 dokumen KB |
| 2 | Analisis kegagalan chunking | Pola Prompt 7.2: Evaluasi rancangan RAG cacat | Memperdalam analisis dampak etis klausul fallback bebas | Menelaah rubrik penilaian Lampiran H |

Satu hal yang AI berikan dan ternyata KELIRU minggu ini :
AI menyarankan menggunakan chunking besar 1.500 kata agar konteks tidak hilang. Ini keliru karena menurunkan resolusi kemiripan embedding dan memboroskan biaya token.

Bagian karya minggu ini yang paling sulit saya jelaskan bila ditanya :
Mengapa sistem tidak boleh beralih ke pengetahuan umum saat dokumen tidak ada (penjelasannya: itu adalah pelanggaran etika rekayasa kecerdasan buatan karena menipu ekspektasi pengguna korporat).

## 8. Pemakaian dan biaya
| Kegiatan | Model | Perkiraan token | Perkiraan biaya |
|---|---|---|---|
| Eksperimen embedding & kueri RAG | text-embedding-3-small & gemini-flash | 18.200 token | Rp 450 |
Total minggu ini : Rp 450  
Total kumulatif  : Rp 3.040  

## 9. Daftar periksa mandiri
- [x] Chunking manual dilakukan dan aturannya tertulis
- [x] Sepuluh pertanyaan uji tersusun sesuai komposisi
- [x] Lima percobaan BREAK dengan prediksi lebih dulu, nomor 5 dicatat nilai kemiripannya (0.58)
- [x] Keempat cacat rancangan ditemukan, termasuk yang paling merugikan pengguna
- [x] `rancangan-rag.md` lengkap enam bagian, setiap keputusan beralasan
- [x] Tantangan wajib terjawab dengan dua cara beserta biayanya

## 10. Yang macet dan rencana minggu depan
Yang masih macet : Mempersiapkan slide presentasi dan materi pembelaan desain untuk UTS Minggu 8.  
Apa yang sudah saya coba untuk mengatasinya : Membaca bank pertanyaan pertanggungjawaban pada Lampiran E.  
Rencana konkret minggu depan : Menyusun dokumen `rancangan-sistem.md` dan 8 slide presentasi UTS.
