# Bukti Tantangan Wajib — Minggu 4
## Efek Perubahan Satu Kalimat pada Instruksi Sistem

### Perubahan Satu Kalimat yang Dilakukan:
Pada Bagian 1 (Batasan Mutlak), ditambahkan satu kalimat tegas:
> **"DILARANG KERAS menyajikan lebih dari SATU langkah solusi dalam satu pesan respon."**

Perubahan satu kalimat ini diuji pada 5 masukan uji yang sama. Terjadi perubahan perilaku signifikan pada **4 dari 5 masukan** (Kasus 1, 2, 4, dan 5).

---

## Bukti Respon Berdampingan (Sebelum vs Sesudah)

### Kasus Uji A: Gangguan Koneksi Wi-Fi Kantor
| Sebelum Perubahan Satu Kalimat | Sesudah Perubahan Satu Kalimat |
|---|---|
| *"Untuk mengatasi Wi-Fi putus, silakan lakukan langkah berikut:<br>1. Matikan dan nyalakan adapter Wi-Fi di laptop Anda.<br>2. Lupakan jaringan (Forget Network) 'CorpNet' lalu masukkan kembali username dan password domain.<br>3. Buka Command Prompt lalu jalankan `ipconfig /renew`.<br>4. Jika masih gagal, hubungi teknisi di ekstensi 404."* | *"Silakan matikan adapter Wi-Fi pada laptop Anda selama 10 detik, lalu nyalakan kembali dan coba hubungkan ulang ke jaringan 'CorpNet'. Beri tahu saya jika langkah ini sudah dicoba agar kita bisa lanjut ke langkah berikutnya."* |
| **Karakteristik:** Memuntahkan seluruh isi SOP sekaligus; membuat pengguna non-teknis bingung dan tidak terpantau langkah mana yang gagal. | **Karakteristik:** Interaktif, memandu 1 langkah per waktu, menunggu konfirmasi pengguna secara human-in-the-loop. |

---

### Kasus Uji B: Printer Jaringan Offline
| Sebelum Perubahan Satu Kalimat | Sesudah Perubahan Satu Kalimat |
|---|---|
| *"Berikut cara memperbaiki printer offline:<br>Pertama, periksa kabel daya printer. Kedua, buka menu Devices and Printers lalu bersihkan antrean print queue. Ketiga, restart service print spooler di komputer Anda."* | *"Langkah 1: Periksa apakah lampu indikator daya pada printer menyala hijau dan kabel LAN di belakang printer terpasang rapat. Apakah lampunya menyala normal?"* |
| **Karakteristik:** Monolog panjang yang sering dilewati pembaca. | **Karakteristik:** Dialog terarah berbasis observasi status nyata perangkat. |

---

### Kasus Uji C: Reset Password Portal
| Sebelum Perubahan Satu Kalimat | Sesudah Perubahan Satu Kalimat |
|---|---|
| *"Buka portal SSO di browser Anda, klik lupa password, masukkan NIP Anda, cek kode OTP di nomor HP terdaftar, lalu buat sandi baru minimal 12 karakter."* | *"Silakan buka peramban web Anda dan akses portal mandiri di https://sso.example.com lalu klik tautan 'Lupa Kata Sandi'. Apakah halamannya sudah terbuka?"* |
| **Karakteristik:** Rangkaian 5 sub-tindakan disatukan dalam satu paragraf. | **Karakteristik:** Memandu navigasi awal secara bertahap. |

---

### Kesimpulan Eksperimen:
Satu kalimat larangan spesifik mampu merombak model bahasa dari sekadar "mesin pembaca dokumen pasif" menjadi "agen pemandu interaktif bertahap". Kepatuhan terbukti pada 4 dari 5 pengujian (80%).
