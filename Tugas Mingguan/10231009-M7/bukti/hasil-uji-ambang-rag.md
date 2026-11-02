# Log Eksperimen Ambang Batas Kemiripan RAG — Tugas 7

- **Model Embedding:** `text-embedding-3-small` (1536 dimensi)
- **Metrik:** Cosine Similarity ($[-1.0, 1.0]$)
- **Koleksi Dokumen:** 8 Dokumen Sintetis Kanonik (`KB-001` s/d `KB-008`)

---

### Hasil Percobaan BREAK 1–5

| # | Percobaan | Prediksi Awal | Hasil Sebenarnya | Catatan Teknis |
|:--:|---|---|---|---|
| 1 | Chunking Sangat Kecil (1 Kalimat) | Retrieval sangat spesifik | Chunk terambil tepat, namun saat model menjawab ia kekurangan konteks prasyarat | Kehilangan konteks (*context fragmentation*). |
| 2 | Chunking Sangat Besar (Seluruh Dokumen) | Jawaban sangat lengkap | Skor kemiripan menurun karena rerata vektor menjadi encer (*diluted embedding*) | Pemborosan token masukan 4x lipat. |
| 3 | Tanpa Overlap vs Overlap 50 Kata | Overlap selalu lebih baik | Skor retrieval identik pada chunking per heading Markdown | Overlap mubazir pada batas semantik alami. |
| 4 | Kueri Bahasa Gaul ("laptop silang merah") | Pencarian gagal | **Lolos** (Cosine similarity = 0.76 terhadap `KB-001`) | Kemampuan semantik dense vector retrieval. |
| 5 | Kueri yang Jawabannya TIDAK ADA ("layar monitor pecah") | Skor similarity = 0 | **Chunk terdekat tetap terambil dengan skor 0.58** | **Temuan Krusial: Cosine similarity selalu mengembalikan tetangga terdekat.** |

---

### Eksperimen Kalibrasi Ambang Batas (Percobaan Nomor 5)
Ketika diuji dengan kueri di luar lingkup SOP:
- Kueri Uji A: *"Monitor saya layarnya retak dan bergaris ungu."*  
  $\rightarrow$ Chunk terambil: `KB-004` (Printer Jaringan) dengan skor **0.582**.
- Kueri Uji B: *"Bagaimana cara klaim kacamata kerja ke bagian HRD?"*  
  $\rightarrow$ Chunk terambil: `KB-007` (Keamanan Akun) dengan skor **0.461**.

### Penetapan Gerbang Ambang Deterministik:
$$\text{Threshold Minimal} = \mathbf{0.70}$$

- Jika $\text{Top-1 Score} \ge 0.70 \rightarrow$ Teruskan chunk ke jendela konteks `<konteks_kb>`.
- Jika $\text{Top-1 Score} < 0.70 \rightarrow$ **Blokir Retrieval**, jangan kirim teks dokumen apa pun, dan picu template jawaban penolakan: *"Panduan untuk kendala ini belum tersedia di basis pengetahuan resmi kami. Apakah Anda ingin saya buatkan draf tiket eskalasi ke teknisi IT?"*
