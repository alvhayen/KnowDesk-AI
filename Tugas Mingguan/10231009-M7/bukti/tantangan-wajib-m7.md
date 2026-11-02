# Bukti Tantangan Wajib — Minggu 7
## Analisis dan Solusi Retrieval Multi-Dokumen (Dua Dokumen Tersebar)

---

### Masalah: Mengapa Mengambil Top-3 Chunk Mungkin TIDAK CUKUP
Dua kasus uji pada set evaluasi menuntut informasi yang tersebar di lebih dari satu dokumen:
- **Kasus 7:** Pengguna ingin membuka email Outlook dari rumah menggunakan koneksi VPN kantor (`KB-002` + `KB-003`).
- **Kasus 8:** Pengguna mengubah kata sandi SSO lalu mendapati akses Microsoft Teams dan VPN terputus (`KB-002` + `KB-003` + `KB-005`).

Ketika kueri Kasus 7 diajukan ke pipeline pencarian vektor standar:
- Kueri: *"Saya ingin akses email Outlook kantor dari laptop pribadi di rumah lewat VPN."*
- Kata kunci "VPN" dan "akses rumah" memiliki bobot dense vector yang sangat tinggi.
- **Hasil Top-3 Chunk:**
  1. `KB-003` Bagian 1 (Konfigurasi VPN) — Skor: 0.842
  2. `KB-003` Bagian 2 Langkah 1 (Unduh VPN Client) — Skor: 0.819
  3. `KB-003` Bagian 2 Langkah 2 (Input Gateway VPN) — Skor: 0.795
  4. `KB-002` Bagian 3 (Akses Webmail dari Luar Jaringan) — Skor: 0.768 *(TERDEPAK / TIDAK TERIKUT)*

**Dampak:**  
Model hanya menerima panduan VPN, sementara panduan mengenai URL webmail kantor tidak masuk ke konteks. Model terpaksa berhalusinasi atau memberikan jawaban setengah jadi.

---

### Dua Cara Alternatif Mengatasinya Beserta Biaya

#### 1. Solusi A: Dekomposisi Kueri (*Sub-Query Decomposition*)
- **Cara Kerja:**  
  Orkestrator LLM awal memecah kueri majemuk menjadi dua sub-kueri mandiri sebelum retrieval:
  - Sub-kueri 1: *"Cara mengaktifkan koneksi VPN kantor dari rumah"* $\rightarrow$ Mencari Top-2 chunk di `KB-003`.
  - Sub-kueri 2: *"Cara membuka email Outlook setelah terhubung jaringan internal"* $\rightarrow$ Mencari Top-2 chunk di `KB-002`.
- **Biaya:**
  - Tambahan 1 panggilan LLM model kecil (misal: Gemini Flash) untuk parsing kueri:
    - Input: $\approx 80 \text{ token} \times \text{Rp } 0,0024 = \text{Rp } 0,192$
    - Output: $\approx 35 \text{ token} \times \text{Rp } 0,0096 = \text{Rp } 0,336$
    - **Total Biaya Tambahan:** $\approx \mathbf{\text{Rp } 0,53 \text{ per interaksi kueri majemuk}}$.

#### 2. Solusi B: Diversifikasi Hasil Vektor (*Maximal Marginal Relevance / MMR*)
- **Cara Kerja:**  
  Algoritma pencarian vektor di backend tidak mengambil murni $k$-teratas berbasis kemiripan terhadap kueri, melainkan menerapkan formula MMR:
  $$\text{MMR} = \arg\max_{D_i \in R \setminus S} \left[ \lambda \cdot \text{Sim}(D_i, Q) - (1 - \lambda) \cdot \max_{D_j \in S} \text{Sim}(D_i, D_j) \right]$$
  Parameter $\lambda = 0.6$ memberi penalti pada chunk yang mirip dengan chunk yang sudah terpilih ($D_j$). Akibatnya, setelah chunk `KB-003` pertama terpilih, chunk `KB-003` lainnya mendapat penalti kebaruan sehingga chunk dari `KB-002` otomatis naik ke posisi 2.
- **Biaya:**
  - **Rp 0** (Nol Rupiah).
  - Tidak ada pemanggilan API LLM tambahan; murni kalkulasi matriks dot-product di memori server Python/FastAPI dalam waktu $< 2 \text{ ms}$.
