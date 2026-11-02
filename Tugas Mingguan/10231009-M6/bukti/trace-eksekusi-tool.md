# Trace Satu Putaran Eksekusi Tool — Tugas 6

Tracing jejak komputasi interaksi pemanggilan tool secara utuh:

---

| Tahap Alur | Isi Sebenarnya pada Pengujian | Evaluasi Keabsahan |
|---|---|---|
| **1. Pertanyaan Pengguna** | "Wi-Fi di laptop kantor saya mendadak putus dan tidak bisa konek ke CorpNet." | Gejala spesifik jaringan Wi-Fi. |
| **2. Tool Diminta Model** | `search_kb` | **Tepat** (Model memilih pencarian artikel rujukan terlebih dahulu). |
| **3. Parameter Diminta Model** | `{"query": "wifi putus corpnet"}` | **Masuk Akal & Relevan** (Mengekstrak kata kunci esensial). |
| **4. Eksekusi Sistem (Sisi Server)**| Sistem Python menjalankan fungsi `search_kb(query)` terhadap indeks lokal. | Eksekusi aman (read-only). |
| **5. Hasil Dikembalikan Tool** | `{"status": "success", "data": [{"article_id": "KB-001", "judul": "Panduan Troubleshooting Koneksi Wi-Fi Kantor"}]}` | Data faktual dari knowledge base. |
| **6. Tindak Lanjut Model** | Model meminta tool kedua: `get_article(article_id="KB-001")`. | Model merangkai alur sekuensial secara tepat. |
| **7. Hasil Dikembalikan Tool 2** | `{"status": "success", "langkah_1": "Matikan adapter Wi-Fi di laptop Anda selama 10 detik lalu nyalakan kembali."}` | Teks asli langkah kanonik SOP. |
| **8. Jawaban Akhir Model** | *"Silakan matikan adapter Wi-Fi pada laptop Anda selama 10 detik, lalu nyalakan kembali dan coba hubungkan ulang ke SSID 'CorpNet'."* | **Setia 100% pada hasil tool**. |

### Uji Kesetiaan Jawaban Akhir (*Faithfulness Check*):
- Jawaban akhir model diteliti kata demi kata terhadap string `langkah_1` dari kembalian tool.
- Tidak ditemukan penambahan instruksi fiktif (seperti menyuruh instalasi driver pihak ketiga atau membongkar laptop).
- Model setia menyajikan tepat satu langkah pertama dan menunggu konfirmasi pengguna.
