# Log Eksperimen Tahap BREAK — Minggu 2

- **Target Pengujian:** Stabilitas Suhu, Pemenggalan Token, Atensi Konteks
- **Model:** `gpt-4o-mini` (API Gateway)
- **Tanggal:** 2026-10-12

---

### Eksperimen 1: Suhu 0.0 (3x Eksekusi)
**Prompt:**  
`Ekstrak hanya nama subnet mask dan gateway dari teks: "Komputer kantor diatur dengan IP 192.168.10.45, subnet mask 255.255.255.0, default gateway 192.168.10.1."`

- **Run 1:** Subnet mask: 255.255.255.0, Default gateway: 192.168.10.1
- **Run 2:** Subnet mask: 255.255.255.0, Default gateway: 192.168.10.1
- **Run 3:** Subnet mask: 255.255.255.0, Default gateway: 192.168.10.1
*Catatan:* Keluaran 100% deterministik.

---

### Eksperimen 2: Suhu 1.0 (3x Eksekusi)
**Prompt:**  
`Jelaskan mengapa pengguna harus mengganti password secara berkala dalam satu paragraf pendek.`

- **Run 1:** Mengganti kata sandi secara berkala meminimalkan jendela kerentanan jika kredensial Anda sempat bocor tanpa disadari...
- **Run 2:** Ibarat mengganti gembok pintu rumah, rotasi kata sandi rutin mencegah akses pihak tak berwenang yang mungkin mengoleksi hash lawas...
- **Run 3:** Keamanan siber menuntut peremajaan autentikasi secara konstan; sandi yang statis selama berbulan-bulan menjadi sasaran empuk serangan brute-force...
*Catatan:* Ide sama, namun variasi metafora dan struktur kalimat sangat divergen.

---

### Eksperimen 3: Pemotongan Batas Token Keluaran (`max_tokens = 20`)
**Prompt:**  
`Tuliskan panduan langkah demi langkah cara menghubungkan laptop Windows ke Wi-Fi korporat.`

- **Keluaran Mentah:**  
  `1. Klik ikon Wi-Fi di sudut kanan taskbar. 2. Pilih SSID jaringan kantor "CorpNet". 3. Masukkan user`
*Catatan:* Respon terpotong secara kasar pada kata "user". Model tidak dapat "meringkas di detik terakhir" karena tidak mengetahui kapan token limit terpicu dari luar.

---

### Eksperimen 6: Eksperimen "Lost in the Middle"
**Bahan:** Teks artikel IT berdurasi 3.000 kata (SOP troubleshooting jaringan).
**Fakta Kunci yang Disisipkan:**  
`"PIN darurat teknisi untuk membuka kunci server lantai 3 adalah 8832."`

- **Skenario A (Disisipkan di Paragraf 1):**  
  Tanya: *Berapa PIN darurat teknisi server lantai 3?*  
  Hasil: Model menjawab tepat: **8832**.
- **Skenario B (Disisipkan di Bagian Tengah / Paragraf 14 dari 28):**  
  Tanya: *Berapa PIN darurat teknisi server lantai 3?*  
  Hasil: Model menjawab: *"Informasi mengenai PIN darurat teknisi lantai 3 tidak disebutkan dalam dokumen panduan troubleshooting."* (GAGAL / TERLEWATKAN).
- **Skenario C (Disisipkan di Paragraf Terakhir):**  
  Tanya: *Berapa PIN darurat teknisi server lantai 3?*  
  Hasil: Model menjawab tepat: **8832**.
