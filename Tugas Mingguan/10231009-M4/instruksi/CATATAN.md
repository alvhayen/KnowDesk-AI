# Catatan Perubahan Instruksi Sistem (Prompts)

| Versi | Tanggal | Yang Diubah | Alasan | Akibat yang Teramati |
|---|---|---|---|---|
| **v1** | 2026-10-11 | Penyusunan draf awal instruksi dengan 6 sumbu arsitektural lengkap, pembatas XML, pembatasan format JSON, dan deklarasi 3 tool kanonik. | Menetapkan fondasi operasional agen untuk tugas helpdesk IT (Aturan R8). | Model merespons secara terarah, namun masih sesekali menggunakan markdown bold dan memuntahkan 2 langkah sekaligus jika konteks memuat beberapa instruksi. |
| **v2** | 2026-10-12 | 1. Mempertegas larangan tanda bintang `**` dan heading pada teks pesan.<br>2. Menambahkan aturan wajib dialog klarifikasi gejala ambigu sebelum pencarian.<br>3. Menambahkan medan `langkah_ke` dan `total_langkah` pada format JSON.<br>4. Memperkuat klausul penolakan injeksi pada delimiter tag. | Hasil evaluasi 5 masukan uji pada Tugas 4 dan tantangan wajib satu kalimat. | Model 100% konsisten memberikan 1 langkah per pesan, tidak membocorkan instruksi saat diserang prompt injection, dan menghasilkan teks polos yang mudah dirender frontend. |
