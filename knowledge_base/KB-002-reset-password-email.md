---
article_id: KB-002
judul: Prosedur Reset dan Pemulihan Password Email
kategori: email
status: published
asal: buatan sendiri (sintetis)
pola: portal self-service password reset (SSPR) helpdesk email korporat
tanggal: 2026-10-11
---

# Prosedur Reset dan Pemulihan Password Email

## Bagian 1: Gambaran Umum Kebijakan Password Email

Akun email resmi staf PT Contoh Sejahtera (fiktif) menggunakan format alamat `nama.pengguna@contoh.example.com`. Akun ini terintegrasi langsung dengan sistem Single Sign-On (SSO) perusahaan, sehingga kata sandi email berlaku sama untuk mengakses portal intranet, aplikasi HR, dan workstation kantor.

Demi menjaga keamanan aset informasi perusahaan, sistem menerapkan kebijakan kata sandi berikut:
1. **Masa Berlaku Sandi**: Kata sandi wajib diperbarui secara berkala setiap 90 hari kalender. Sistem akan mengirimkan notifikasi pengingat pembaruan sandi ke kotak masuk 14 hari sebelum masa kedaluwarsa.
2. **Kriteria Kompleksitas**: Kata sandi baru minimal terdiri dari 12 karakter, memuat minimal satu huruf besar (A-Z), satu huruf kecil (a-z), satu angka (0-9), serta satu karakter khusus/simbol (misalnya `@`, `#`, `$`, `%`, `*`).
3. **Riwayat Sandi (Password History)**: Pengguna tidak diperbolehkan menggunakan kembali 5 kata sandi terakhir yang pernah dipakai sebelumnya.
4. **Proteksi Penguncian Otomatis (Account Lockout)**: Jika terjadi kesalahan pengetikan kata sandi sebanyak 5 kali berturut-turut dalam kurun waktu 15 menit, akun akan dikunci secara otomatis selama 30 menit untuk mencegah upaya pembobolan brute-force.

Jika Anda lupa kata sandi atau akun terkunci akibat salah ketik sandi, Anda dapat melakukan pemulihan secara mandiri melalui portal Self-Service Password Reset (SSPR) tanpa perlu menunggu respons manual dari tim IT.

## Bagian 2: Prasyarat Pemulihan Akun Mandiri (SSPR)

Layanan reset kata sandi mandiri dapat digunakan dengan lancar apabila staf telah memenuhi prasyarat berikut:
- **Metode Verifikasi Terdaftar**: Nomor ponsel pribadi aktif telah terdaftar pada data kepegawaian HR atau aplikasi *Authenticator* telah tertaut pada profil akun staf di portal `https://profil.example.com`.
- **Akses Jaringan**: Perangkat yang digunakan harus terhubung ke jaringan internet yang stabil (bisa menggunakan koneksi seluler, Wi-Fi rumah, atau jaringan kantor).
- **Identitas Akun Valid**: Anda mengetahui nama pengguna lengkap (User ID) atau alamat email resmi perusahaan Anda.

Jika Anda belum pernah mendaftarkan nomor telepon pemulihan atau aplikasi autentikasi sebelumnya, Anda tidak dapat menyelesaikan verifikasi mandiri dan harus mengikuti prosedur eskalasi tiket pada Bagian 4.

## Bagian 3: Prosedur Langkah Reset Password Mandiri

Lakukan langkah-langkah di bawah ini untuk mereset kata sandi akun email Anda secara mandiri:

### Langkah 1: Buka Portal Pemulihan Akun Mandiri (SSPR)
1. Buka peramban web (Google Chrome, Microsoft Edge, atau Mozilla Firefox) di komputer atau ponsel Anda.
2. Akses alamat resmi portal pemulihan kata sandi PT Contoh Sejahtera di `https://sso.example.com/reset`.
3. Masukkan alamat email lengkap Anda (contoh: `budi.santoso@contoh.example.com`) pada kolom *User ID / Email*.
4. Masukkan kode captcha keamanan yang ditampilkan pada layar untuk memvalidasi bahwa permintaan bukan berasal dari bot otomatis.
5. Klik tombol **Next / Lanjut**.

### Langkah 2: Verifikasi Identitas Melalui Kode OTP atau Authenticator
Pilih salah satu metode verifikasi dua langkah yang sebelumnya telah Anda daftarkan:
1. **Opsi SMS OTP**: Pilih opsi *"Kirim SMS ke nomor telepon saya (berakhiran XXXX)"*. Tunggu pesan SMS masuk berisi 6 digit kode keamanan dari pengirim resmi `CONTOH-AUTH`.
2. **Opsi Aplikasi Authenticator**: Pilih opsi *"Gunakan kode verifikasi dari aplikasi mobile"*, lalu buka aplikasi autentikator di ponsel Anda dan masukkan 6 digit token yang sedang berlaku.
3. Ketikkan 6 digit kode verifikasi tersebut ke dalam formulir portal SSPR pada batas waktu 3 menit.
4. Klik tombol **Verifikasi**. Jika kode cocok, portal akan mengalihkan Anda ke halaman pembuatan kata sandi baru.

### Langkah 3: Buat Kata Sandi Baru Sesuai Standar Keamanan
1. Pada halaman pembuatan sandi baru, ketikkan kata sandi baru Anda pada kolom **New Password**.
2. Pastikan indikator kekuatan sandi berubah menjadi hijau (*Strong*) dengan memenuhi syarat minimal 12 karakter, kombinasi huruf besar, huruf kecil, angka, dan simbol unik.
3. Ketikkan kembali kata sandi yang persis sama pada kolom **Confirm New Password**.
4. Klik tombol **Submit / Simpan**.
5. Tunggu pesan konfirmasi muncul di layar: *"Kata sandi Anda telah berhasil diperbarui dan akun Anda telah aktif kembali."*

### Langkah 4: Perbarui Kata Sandi di Aplikasi Email dan Browser
Setelah kata sandi SSO berhasil diubah di portal pusat, seluruh sesi login pada aplikasi lokal harus diperbarui:
1. Buka aplikasi Microsoft Outlook atau aplikasi email di perangkat kerja Anda.
2. Saat muncul jendela pop-up bertuliskan *"Need Password"* atau *"Authentication Required"*, masukkan kata sandi baru yang baru saja Anda buat.
3. Lakukan hal yang sama pada aplikasi email di ponsel pintar kerja Anda.
4. Jika browser Anda menyimpan kata sandi lama secara otomatis (*Autofill*), perbarui kredensial tersimpan di menu pengaturan browser agar akun tidak terkunci kembali akibat pengisian otomatis sandi lama.
5. Kirim satu email uji coba ke alamat email rekan kerja untuk memastikan proses kirim dan terima email telah berfungsi normal kembali.

## Bagian 4: Kapan Harus Menghubungi Teknisi IT

Staf wajib menghubungi teknisi IT Helpdesk apabila mengalami kondisi di bawah ini:
1. **Nomor Ponsel Pemulihan Tidak Aktif / Berubah**: Nomor telepon yang terdaftar pada sistem SSPR adalah nomor lama yang sudah hangus atau hilang, sehingga kode OTP verifikasi tidak dapat diterima.
2. **Status Akun Ditangguhkan (Suspended / Disabled)**: Portal menampilkan pesan galat *"Your account has been suspended by an administrator. Please contact your IT Helpdesk."* Hal ini biasanya terjadi jika ada indikasi aktivitas mencurigakan atau perubahan status kepegawaian.
3. **Looping Halaman Login**: Setelah berhasil mereset sandi dan mencoba login, browser terus-menerus dialihkan kembali ke halaman input sandi tanpa pesan galat apa pun (indikasi masalah sinkronisasi profil server Exchange/SSO).
4. **Permintaan Penggantian Email Primary Alias**: Terjadi perubahan nama resmi staf atau mutasi divisi yang memerlukan penyesuaian alamat email utama.

Saat melaporkan kendala ke IT Helpdesk, sebutkan Nomor Induk Karyawan (NIK), unit kerja, dan lampirkan foto kartu identitas karyawan (ID Card) untuk proses verifikasi identitas resmi sebelum reset manual dilakukan teknisi.
