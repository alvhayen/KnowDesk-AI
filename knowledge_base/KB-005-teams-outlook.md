---
article_id: KB-005
judul: Panduan Penggunaan Microsoft Teams dan Outlook
kategori: aplikasi
status: published
asal: buatan sendiri (sintetis)
pola: catatan internal helpdesk aplikasi kolaborasi kantor (sengaja tidak rapi per §5.2)
tanggal: 2026-10-11
---

# Panduan Penggunaan Microsoft Teams dan Outlook

## Bagian 1: Deskripsi Masalah Teams serta Ms Outlook

Di lingkungan perkantoran PT Contoh Sejahtera (fiktif), staf menggunakan aplikasi tim (Microsoft Teams / MS Teams) untuk berkoordinasi, melakukan rapat online, dan obrolan harian, serta menggunakan Outlook (kadang disebut surel kantor atau webmail) untuk korespondensi formal dengan klien. Layanan ini terhubung ke paket Microsoft 365 korporat melalui akun SSO `user@contoh.example.com`.

Sering kali aplikasi tim dan surel kantor mengalami masalah sinkronisasi data antar server cloud dan komputer lokal. Karena software kolaborasi ini saling terintegrasi (misalnya kalender di chat tim membaca kalender dari mail client Outlook), gangguan pada salah satu program kerap merembet ke aplikasi lainnya.

Gejala umum yang kerap dilaporkan pengguna:
- Pesan obrolan di MS Teams bertuliskan *"Failed to send - Retry"* atau status rekan kerja selalu terlihat offline padahal sedang online di meja sebelah.
- Surel kantor (Outlook client) menampilkan tulisan *"Disconnected"* atau *"Trying to connect..."* di pojok kanan bawah jendela aplikasi.
- Jadwal undangan meeting baru yang diterima lewat email kantor tidak otomatis muncul di tab Kalender aplikasi tim.
- Kamera atau mikrofon laptop tidak terdeteksi saat bergabung ke panggilan rapat daring di MS Teams.
- Outlook macet (*Not Responding*) saat membuka lampiran file PDF atau spreadsheet berukuran lebih dari 10 MB.

## Bagian 2: Tindakan Awal dan Pengecekan Jaringan

Sebelum melakukan tindakan pembersihan berkas sistem yang lebih dalam, pastikan hal-hal berikut:
1. Pastikan peramban web Anda dapat membuka versi web dari kedua layanan tersebut melalui `https://portal.example.com` atau `https://teams.example.com`. Jika versi browser berjalan lancar, berarti gangguan terlokalisasi pada software desktop lokal komputer Anda.
2. Periksa apakah perangkat Anda terhubung ke internet kantor atau VPN bila bekerja dari luar gedung.
3. Pastikan waktu dan zona waktu sistem komputer Windows Anda cocok dengan zona waktu kantor (WIB / GMT+7), karena selisih waktu sistem lebih dari 5 menit dapat menggagalkan token autentikasi cloud.

Jika pemeriksaan awal menunjukkan koneksi normal namun software tim dan mail client tetap error, lakukan langkah perbaikan mandiri di Bagian 3.

## Bagian 3: Langkah Solusi Mandiri Teams dan Outlook

### Langkah 1: Tutup Paksa Aplikasi dari Task Manager
Sering kali aplikasi tim dan mail client masih menggantung di proses latar belakang (*background processes*) meskipun jendelanya telah ditutup:
1. Tekan tombol `Ctrl + Shift + Esc` secara bersamaan pada keyboard untuk membuka Task Manager Windows.
2. Cari nama proses **Microsoft Teams** atau **Teams.exe** pada tab *Processes*.
3. Klik kanan pada proses tersebut, lalu pilih **End task**.
4. Lakukan hal yang sama untuk proses bernama **Microsoft Outlook** atau **OUTLOOK.EXE**. Pastikan tidak ada lagi proses Outlook yang aktif di daftar latar belakang.
5. Tunggu sekitar 10 detik sebelum membuka kembali program untuk memastikan file memori dilepaskan sepenuhnya.

### Langkah 2: Hapus Berkas Cache Teams pada Direktori AppData
Penumpukan data cache obrolan yang korup sering menyebabkan MS Teams gagal memuat pesan baru atau menampilkan layar putih (*white screen*):
1. Tekan tombol `Windows + R` pada keyboard untuk membuka kotak dialog Run.
2. Salin dan tempel perintah jalur direktori berikut, lalu tekan Enter:
   ```text
   %appdata%\Microsoft\Teams
   ```
3. Di dalam folder yang terbuka, pilih seluruh file dan folder (tekan `Ctrl + A`).
4. Hapus seluruh isi folder tersebut (tekan tombol `Delete`). Jika ada file yang memunculkan peringatan *"File In Use"*, lewati file tersebut (*Skip*).
5. Untuk Teams versi baru (New Teams), buka dialog Run kembali lalu buka `%localappdata%\Packages\MSTeams_8wekyb3d8bbwe\LocalCache` dan bersihkan isi folder tersebut.
6. Buka kembali aplikasi tim dan login ulang jika diminta.

### Langkah 3: Jalankan Outlook dalam Safe Mode untuk Nonaktifkan Add-in
Add-in pihak ketiga yang rusak kerap menyebabkan surel kantor hang saat dibuka:
1. Tekan tombol `Windows + R` pada keyboard.
2. Ketik perintah berikut ke dalam kotak Run, lalu tekan Enter:
   ```cmd
   outlook.exe /safe
   ```
3. Jika Outlook berhasil terbuka tanpa kendala dalam mode aman (*Safe Mode*), klik menu **File -> Options -> Add-ins**.
4. Pada bagian bawah jendela, pilih **COM Add-ins** pada menu drop-down *Manage*, lalu klik tombol **Go...**.
5. Hapus tanda centang pada add-in yang mencurigakan atau add-in non-standar (seperti add-in antivirus pihak ketiga), lalu klik **OK**.
6. Tutup Outlook dan buka kembali secara normal tanpa parameter safe mode.

### Langkah 4: Perbaiki Profil Akun Melalui Account Settings
*(Catatan: Langkah ini dapat bervariasi bergantung pada versi instalasi software mail client kantor Anda)*
1. Buka aplikasi Outlook Anda.
2. Klik menu **File**, lalu pilih tombol **Account Settings** dan klik kembali opsi di dalamnya.
3. Pilih nama akun surel kantor Anda yang terdaftar pada tab email.
4. Klik tombol perbaikan akun untuk menyinkronkan ulang data dari server. Tunggu proses verifikasi server selesai lalu restart aplikasi.

## Bagian 4: Kapan Harus Menghubungi Teknisi IT

Hubungi tim IT Helpdesk apabila Anda mengalami kondisi berikut:
1. **Mailbox Penuh di Sisi Server (Quota Exceeded)**: Kotak masuk Anda telah melebihi batas kuota server 50 GB dan pesan mental dengan kode galat *554 5.2.2 mailbox full*.
2. **Lisensi Microsoft 365 Dinonaktifkan**: Muncul spanduk merah di bagian atas aplikasi bertuliskan *"Unlicensed Product"* atau *"Your license has expired"*, yang menandakan perlunya perpanjangan lisensi akun oleh administrator IT.
3. **Penyimpanan Berkas Data OST Korup Total**: Outlook gagal memuat file `outlook.ost` dan menampilkan pesan galat fatal database tidak dapat dipulihkan secara otomatis.
4. **Masalah Izin Delegasi Kalender**: Anda tidak dapat mengakses kalender atasan atau kalender ruang rapat bersama meskipun telah mendapatkan persetujuan email resmi.

Saat mengajukan laporan kendala ke IT, sertakan screenshot kode galat spesifik dan informasi apakah masalah ini juga terjadi saat membuka versi web di browser.
