# Bukti Tantangan Wajib — Minggu 6
## Memperbaiki Pemilihan Tool Keliru HANYA dengan Mengubah Deskripsi Tool

---

### Masalah Awal: Salah Pilih Tool
Pada pengujian kueri pengguna:  
> *"Wi-Fi saya tidak bisa internetan dari tadi, tolong segera buatkan tiket perbaikan ya!"*

**Perilaku Awal Sistem:**  
Model langsung memanggil `draft_ticket(...)` karena menangkap kata kunci *"segera buatkan tiket"*, mengabaikan fakta bahwa pengguna belum pernah mencoba langkah panduan mandiri apa pun.

---

### Tindakan Perbaikan (Tanpa Mengubah Instruksi Sistem):
Saya **HANYA** mengubah string deskripsi tool `draft_ticket` pada spesifikasi JSON Schema:

- **Deskripsi Lama:**  
  `"Menyusun draf tiket eskalasi ke teknisi IT untuk kendala yang dialami pengguna."`
- **Deskripsi Baru (Diperbaiki):**  
  `"Menyusun draf tiket eskalasi ke teknisi IT jika seluruh langkah mandiri telah gagal dicoba atau artikel panduan tidak ditemukan. DILARANG memanggil tool ini jika pengguna baru pertama kali melaporkan masalah dan belum dilakukan pencarian artikel solusi di search_kb."`

---

## Bukti Sebelum vs Sesudah Berdampingan

| Kondisi | Deskripsi Tool `draft_ticket` | Aksi yang Dipilih Model | Evaluasi |
|---|---|---|:--:|
| **SEBELUM PERBAIKAN** | Deskripsi umum permisif tanpa larangan kondisi. | Memanggil `draft_ticket(judul="Wi-Fi tidak bisa internetan", ...)` | **SALAH** (Membuat tiket sebelum mencari panduan mandiri). |
| **SESUDAH PERBAIKAN** | Deskripsi dipertegas dengan larangan negatif eksplisit ("DILARANG memanggil sebelum search_kb"). | Memanggil `search_kb(query="wifi tidak bisa internetan")` | **BENAR** (Mengutamakan bantuan mandiri sesuai SOP). |

### Kesimpulan:
Deskripsi tool adalah prompt semantik primer bagi penentu rute (*tool router*) pada model bahasa besar. Menambahkan kalimat larangan negatif mengenai **kapan tool TIDAK BOLEH dipakai** adalah cara paling presisi untuk mencegah kekeliruan eksekusi fungsi tanpa perlu memperpanjang prompt sistem utama.
