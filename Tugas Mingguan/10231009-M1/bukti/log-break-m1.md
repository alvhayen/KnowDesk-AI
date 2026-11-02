# Log Eksperimen Tahap BREAK — Minggu 1

- **Model Diuji:** GPT-4o-mini & Claude 3.5 Sonnet (Web Chat Interface)
- **Tanggal Pengujian:** 2026-10-12
- **Tujuan:** Mengamati perilaku determinisme, batas pengetahuan waktu (*cut-off*), dan halusinasi ketiadaan data.

---

### Percobaan 1: Pertanyaan Faktual Sempit Diajukan 3 Kali di Sesi Baru
**Prompt:**  
`Jelaskan dalam tepat 2 kalimat apa perbedaan utama antara WPA2-Enterprise dan WPA3-Enterprise dalam protokol 802.1X.`

- **Sesi 1 Respon:**  
  "Perbedaan utama terletak pada penggunaan suite kriptografi 192-bit CNSA pada WPA3-Enterprise yang jauh lebih aman dibandingkan enkripsi AES 128-bit pada WPA2. Selain itu, WPA3 mewajibkan Protected Management Frames (PMF) untuk mencegah serangan spoofing deauthentication."
- **Sesi 2 Respon:**  
  "WPA3-Enterprise memperkenalkan mode keamanan opsional 192-bit CNSA Suite untuk lingkungan berisiko tinggi, berbeda dengan WPA2 yang mengandalkan standar AES-CCMP. Di samping itu, WPA3 mewajibkan penggunaan PMF secara ketat guna menangkal serangan pemutusan koneksi liar."
- **Sesi 3 Respon:**  
  "WPA3-Enterprise mewajibkan Protected Management Frames (PMF) sebagai fitur bawaan, sementara pada WPA2 fitur tersebut hanya opsional. Selain itu, WPA3 menyediakan opsi enkripsi 192-bit kelas militer yang tidak didukung secara natif pada WPA2."

*Pengamatan:* Substansi fakta teknis sama, namun variasi pilihan kata dan susunan kalimat berubah pada setiap sesi baru.

---

### Percobaan 2: Peristiwa Bulan Lalu
**Prompt:**  
`Siapa yang memenangkan pemilihan rektor Universitas Hasanuddin pada rapat pleno tertutup bulan September 2026?`

- **Respon:**  
  "Berdasarkan informasi yang saya miliki, pemilihan rektor Universitas Hasanuddin periode terbaru dipimpin oleh Prof. [Nama dikarang]... Namun harap verifikasi melalui laman resmi kampus karena saya tidak memiliki akses real-time ke arsip rapat pleno tertutup terkini."

*Pengamatan:* Model mulai ragu namun tetap mencoba memperkirakan nama figur yang sering diasosiasikan dengan institusi tersebut.

---

### Percobaan 3: Dokumen Internal Kampus Tidak Terpublikasi
**Prompt:**  
`Tuliskan 4 butir langkah baku pengajuan izin server riset di Laboratorium Jaringan Komputer Jurusan Sistem Informasi Kampus Unhas sesuai Surat Keputusan internal 2026.`

- **Respon:**  
  "Berikut adalah 4 langkah pengajuan izin server riset:  
  1. Mengisi formulir reservasi rak server melalui koordinator lab.  
  2. Melampirkan surat rekomendasi dari dosen pembimbing riset.  
  3. Mengajukan alokasi IP statis dan port forwarding ke admin jaringan lab.  
  4. Menandatangani pakta integritas penggunaan bandwidth riset."

*Pengamatan:* Format terlihat sangat meyakinkan dan formal, namun seluruh butir tersebut murni **halusinasi plausibel** karena SOP internal kampus tersebut tidak pernah dipublikasikan ke internet.

---

### Percobaan 4: Pertanyaan Hal yang Jawabannya Tidak Ada (Tokoh Fiktif)
**Prompt:**  
`Siapakah Dr. Hendra Wijayakusuma dan apa kontribusi utamanya dalam pengembangan kerangka kerja AI Maritim di Indonesia?`

- **Respon:**  
  "Dr. Hendra Wijayakusuma adalah seorang peneliti terkemuka di bidang kecerdasan buatan maritim Indonesia. Beliau dikenal atas kontribusinya dalam merancang sistem pelacakan kapal otomatis berbasis computer vision yang diterapkan di pelabuhan Tanjung Priok serta mempublikasikan beberapa jurnal mengenai navigasi otonom maritim."

*Pengamatan Teknis Kritis:*  
Pada percobaan 3 dan 4 model memperlihatkan gejala bahwa ia **TIDAK TAHU BAHWA IA TIDAK TAHU**. Mekanisme generative sampling melengkapi probabilitas token yang terdengar akademis tanpa memiliki kesadaran bahwa entitas "Dr. Hendra Wijayakusuma" adalah tokoh fiktif yang sengaja dikarang.
