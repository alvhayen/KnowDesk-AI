---
article_id: KB-006
judul: Prosedur Permintaan Akses Folder Bersama
kategori: lainnya
status: published
asal: buatan sendiri (sintetis)
pola: panduan pengelolaan network shared drive SMB/CIFS enterprise
tanggal: 2026-10-11
---

# Prosedur Permintaan Akses Folder Bersama

## Bagian 1: Kebijakan Penyimpanan Data di Shared Drive

PT Contoh Sejahtera (fiktif) menyediakan penyimpanan terpusat berbasis server Network Attached Storage (NAS) yang dapat diakses oleh staf melalui protokol SMB pada jalur jaringan `\\nas.example.com\shared`. Folder bersama ini digunakan untuk pertukaran dokumen antar-divisi, pengarsipan laporan keuangan, dan kolaborasi proyek internal.

Struktur folder bersama diatur berdasarkan izin grup Active Directory:
- **Folder Departemen** (contoh: `\\nas.example.com\shared\Keuangan`, `\\nas.example.com\shared\SDM`): Hanya staf yang menjadi anggota departemen terkait yang memiliki hak baca (*Read*) dan tulis (*Write*).
- **Folder Publik Perusahaan** (`\\nas.example.com\shared\Publik`): Seluruh staf aktif memiliki hak baca dan unggah file sementara (file otomatis dibersihkan setiap 30 hari).
- **Folder Proyek Lintas Divisi**: Diberikan berdasarkan persetujuan manajer proyek terkait.

Setiap staf diwajibkan menggunakan akun domain kantor saat mengakses shared drive. Demi alasan keamanan dan pencegahan kebocoran data, akses dari luar kantor hanya diizinkan apabila staf terhubung melalui VPN resmi kantor.

## Bagian 2: Gejala Galat Akses Folder Bersama

Staf kerap mengalami kendala saat mencoba membuka shared drive melalui Windows File Explorer, antara lain:
1. Muncul jendela peringatan bertuliskan *"Windows cannot access \\nas.example.com\shared. You do not have permission to access this resource (Error 0x80070005 - Access is denied)"*.
2. Kotak dialog *Enter Network Credentials* terus muncul berulang kali meskipun username dan kata sandi yang dimasukkan sudah benar.
3. Muncul pesan galat *"The network path was not found (Error 0x80070035)"*, menandakan sistem Windows gagal menghubungi server NAS kantor.
4. Ikon drive yang sudah dipetakan (misal Drive `Z:`) di File Explorer menampilkan tanda silang merah (*Disconnected Network Drive*).
5. File di dalam folder bersama dapat dibuka (*Read*), namun gagal disimpan saat diedit (*Read-only error*).

Ikuti langkah-langkah di Bagian 3 untuk memverifikasi izin dan memetakan kembali shared drive ke komputer Anda.

## Bagian 3: Langkah Pemetaan dan Pemeriksaan Akses Drive

### Langkah 1: Periksa Izin Akses Melalui Portal Self-Service Permintaan Data
Sebelum melakukan perbaikan teknis pada Windows, pastikan akun Anda memang telah memiliki izin resmi untuk folder yang dituju:
1. Buka browser web di komputer kantor Anda, lalu akses portal izin internal di `https://akses.example.com`.
2. Masuk menggunakan akun SSO Anda (`nama.pengguna@contoh.example.com`).
3. Pilih menu **Cek Izin Folder Saya**, lalu cari nama folder departemen yang ingin Anda buka.
4. Jika status izin masih berstatus *Pending Approval* atau *Belum Terdaftar*, ajukan permintaan penambahan grup dengan memilih tombol **Request Access** dan sebutkan alasan kebutuhan kerja serta nama manajer pemberi persetujuan.
5. Jika status izin sudah tertulis *Active / Disetujui*, lanjutkan ke Langkah 2.

### Langkah 2: Lakukan Pemetaan Ulang Network Drive (Map Network Drive)
Memetakan folder jaringan menjadi huruf drive lokal (seperti Drive `Z:`) mempermudah akses harian dan menyegarkan jalur SMB Windows:
1. Buka File Explorer (`Windows + E`), lalu klik kanan pada ikon **This PC** di panel navigasi sebelah kiri.
2. Pilih opsi **Map network drive...**.
3. Pada opsi **Drive**, pilih huruf drive yang belum terpakai (disarankan huruf **Z:**).
4. Pada kolom **Folder**, ketikkan jalur lengkap folder jaringan kantor:
   ```text
   \\nas.example.com\shared\NamaDepartemen
   ```
   *(Ganti `NamaDepartemen` dengan folder tujuan Anda, misal `Keuangan`)*.
5. Centang opsi **Reconnect at sign-in** dan centang **Connect using different credentials**.
6. Klik tombol **Finish**.

### Langkah 3: Bersihkan Kredensial Lama di Windows Credential Manager
Windows kerap menyimpan kredensial login jaringan lama yang kedaluwarsa sehingga menyebabkan penolakan autentikasi otomatis oleh server NAS:
1. Klik tombol **Start**, ketik **Credential Manager**, lalu tekan Enter.
2. Pilih tab **Windows Credentials**.
3. Gulir ke bawah pada bagian *Generic Credentials* atau *Windows Credentials*, lalu cari entri yang memuat nama `nas.example.com` atau alamat IP server NAS.
4. Klik tanda panah pada entri tersebut, lalu klik tombol **Remove** untuk menghapus kredensial yang tersimpan.
5. Tekan `Windows + R`, ketik `cmd`, lalu ketik perintah berikut untuk memutuskan seluruh sesi jaringan lama:
   ```cmd
   net use * /delete /y
   ```
6. Buka kembali jalur `\\nas.example.com\shared` dan masukkan username domain Anda dengan awalan domain (contoh: `CONTOH\nama.pengguna`) beserta kata sandi aktif Anda.

### Langkah 4: Uji Konektivitas Protokol SMB Melalui Command Prompt
Jika folder tetap tidak dapat dibuka, uji apakah jalur jaringan port SMB (port TCP 445) terhalang firewall lokal:
1. Buka Command Prompt Windows (`cmd`).
2. Lakukan uji ping ke server NAS kantor dengan mengetik:
   ```cmd
   ping nas.example.com
   ```
3. Pastikan waktu respons (*latency*) normal di bawah 10 ms dan tidak ada paket data yang hilang (*0% packet loss*).
4. Periksa apakah layanan Workstation Windows aktif dengan mengetik perintah:
   ```cmd
   sc query lanmanworkstation
   ```
5. Pastikan status layanan menunjukkan status `RUNNING`. Jika status `STOPPED`, ketik `net start lanmanworkstation` untuk menyalakannya kembali.

## Bagian 4: Kapan Harus Menghubungi Teknisi IT

Ajukan tiket bantuan ke tim teknisi IT apabila Anda menghadapi situasi berikut:
1. **Pemberian Izin Belum Masuk ke Token Keamanan**: Formulir izin di portal `akses.example.com` telah disetujui manajer lebih dari 24 jam kerja, namun token sesi login Windows tetap belum mencatat keanggotaan grup keamanan Active Directory Anda.
2. **Server NAS Sedang Mengalami Masalah File System**: Muncul galat *"The specified network name is no longer available"* atau *"I/O device error"* pada seluruh pengguna di lantai yang sama.
3. **Konflik File Locking**: File Excel atau dokumen Word di folder bersama terkunci oleh pengguna lain yang sudah tidak membuka file tersebut (*locked by another user ghost lock*), yang membutuhkan pelepasan sesi kunci (*open files unlock*) di konsol server NAS oleh administrator.
4. **Kebutuhan Kuota Penyimpanan Tambahan**: Kapasitas partisi folder bersama telah mencapai 95% sehingga seluruh staf departemen tidak dapat lagi menyimpan file baru.

Saat membuat tiket ke tim IT, cantumkan jalur lengkap folder yang ingin diakses (misal: `\\nas.example.com\shared\Keuangan\Laporan2026`) dan nomor referensi tiket persetujuan akses portal bila ada.
