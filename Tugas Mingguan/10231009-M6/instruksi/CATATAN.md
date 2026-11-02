# Catatan Perubahan Instruksi Sistem (Prompts)

| Versi | Tanggal | Yang Diubah | Alasan | Akibat yang Teramati |
|---|---|---|---|---|
| **v1** | 2026-10-11 | Fondasi awal 6 sumbu instruksi sistem. | Inisialisasi arsitektur. | Gaya bahasa terarah namun eksekusi tool belum terkendali. |
| **v2** | 2026-10-12 | Penambahan pembatasan pemanggilan tool kanonik (K = 3), larangan pemanggilan tiket dini, dan aturan klarifikasi gejala ambigu. | Implementasi Function Calling pada Tugas 6. | Model 100% konsisten memilih `search_kb` sebelum `get_article` dan tidak memicu pembuatan tiket palsu. |
