# Hasil Pemotongan Manual 5 Chunk Pertama — Tugas 7
## Dokumen: `KB-001` (Panduan Troubleshooting Wi-Fi Kantor)

---

### Aturan Pemotongan Manual:
> *"Satu chunk dibatasi tepat pada satu unit sub-heading (`## Bagian` untuk latar belakang, dan `### Langkah N` untuk setiap tindakan solusi operasional)."*

---

### Tabel Analisis Kelayakan 5 Chunk Pertama

| # | Bagian Heading Dokumen | Isi Ringkas Teks Chunk | Apakah Dapat Dipahami Berdiri Sendiri? | Apa yang Hilang Jika Dibaca Terpisah Tanpa Metadata? |
|:--:|---|---|:--:|---|
| **1** | `## Bagian 1: Gejala Umum dan Diagnostik Awal` | Uraian tanda laptop gagal konek ke SSID 'CorpNet' (ikon silang merah, IP 169.254.x.x). | **Ya** | Nama dokumen SOP dan versi protokol jaringan. |
| **2** | `### Langkah 1: Restart Adapter Wi-Fi` | Instruksi mematikan tombol Wi-Fi laptop selama 10 detik lalu menyalakan kembali. | **Ya** | Nama SSID kantor yang harus dipilih saat menyambung ulang. |
| **3** | `### Langkah 2: Lupakan Jaringan dan Sambung Ulang` | Instruksi klik kanan nama SSID 'CorpNet' $\rightarrow$ Forget, lalu input user domain. | **Ya** | Prasyarat bahwa adapter Wi-Fi dalam kondisi aktif. |
| **4** | `### Langkah 3: Pembaruan Alamat IP DHCP` | Perintah CMD `ipconfig /release` dan `ipconfig /renew` untuk meminta alokasi IP baru. | **Ya** | Konteks bahwa langkah ini hanya berguna jika status Wi-Fi sudah connected tapi no internet. |
| **5** | `### Langkah 4: Verifikasi Sertifikat 802.1X` | Langkah membuka portal sertifikat internal di https://cert.example.com untuk perpanjangan. | **Ya** | Keterangan jenis error otentikasi yang memerlukan pembaruan sertifikat. |

### Kesimpulan Pengamatan:
Setiap chunk langkah solusi dapat dipahami berdiri sendiri asalkan sistem menyertakan metadata `article_id: KB-001` dan `judul: Panduan Troubleshooting Koneksi Wi-Fi Kantor`. Ini membuktikan bahwa strategi chunking berbasis heading Markdown jauh lebih superior dibandingkan pemotongan berbasis panjang karakter statis.
