# Bukti Penanganan Kegagalan 3 Langkah — Tugas 5

Pengujian memicu kegagalan format secara sengaja untuk membuktikan sistem tidak mengalami crash:

---

### Skenario Uji 1: Penanganan String Malformed (Bukan JSON)
- **Masukan Mentah Simulasi Model:**  
  `"Tentu! Ini hasil analisis saya: Kategori Masalah: Jaringan, Tingkat: Mendesak Sekali, Bukti: Pengguna bilang kabel putus."`
- **Eksekusi Penanganan:**
  1. *Langkah 1 (Validasi):* Gagal dengan `json.JSONDecodeError` (Teks bukan format JSON valid).
  2. *Langkah 2 (Retry dengan Error Correction):* Sistem memanggil retry dengan pesan galat skema.
  3. *Langkah 3 (Fallback Deterministic):* Sistem secara deterministik menghasilkan payload aman:
     ```json
     {
       "dapat_ditentukan": "tidak",
       "kategori": "lainnya",
       "tingkat_urgensi": "sedang",
       "langkah_ke": 1,
       "total_langkah": 1,
       "pesan": "Sistem mengalami kendala saat memformat panduan secara otomatis. Kami menyarankan untuk membuat draf tiket eskalasi ke teknisi IT.",
       "tindakan_berikutnya": "eskalasi_tiket",
       "sumber": []
     }
     ```
- **Hasil:** Aplikasi web tetap berjalan stabil, pengguna mendapatkan tawaran pembuatan tiket eskalasi yang jelas dan sopan tanpa melihat pesan error kode teknis.

---

### Skenario Uji 2: Penanganan Kutipan Falsifikasi (Kasus C pada Tahap FIX)
- **Masukan Mentah Simulasi Model:**  
  JSON valid secara sintaksis, namun medan `kutipan` berisi teks karangan:  
  `"kutipan": "pengguna disarankan membongkar casing printer dan memeriksa roda gear"` (Teks ini tidak ada di `KB-004`).
- **Eksekusi Penanganan:**
  - Fungsi `verify_exact_substring()` mendeteksi bahwa string tersebut tidak ditemukan di dalam dokumen rujukan resmi.
  - Respon ditolak pada Lapis 1 dan dialihkan ke fallback eskalasi tiket.
- **Hasil:** Mencegah instruksi berbahaya/karangan sampai ke tangan staf kantor.
