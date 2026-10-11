# Catatan Asal Dokumen Knowledge Base (KB) Sintetis

- **Tanggal Penyusunan:** 2026-10-11
- **Status Data:** 100% Sintetis / Fiktif (Kepatuhan Aturan R1 & K5)
- **Entitas Fiktif:** PT Contoh Sejahtera (fiktif)
- **Domain Rujukan:** Seluruh URL menggunakan `example.com`

---

## 1. Matriks Dokumen Knowledge Base (K = 3)

| ID | Nama Berkas | Judul Dokumen | Kategori | Pola Acuan & Karakteristik | Status Kebersihan Data |
|---|---|---|---|---|---|
| KB-001 | `KB-001-troubleshoot-wifi.md` | Panduan Troubleshooting Koneksi Wi-Fi Kantor | jaringan | Pola panduan helpdesk enterprise Wi-Fi 802.1X WPA2/WPA3 | Bersih, langkah kanonik 1–4 lengkap |
| KB-002 | `KB-002-reset-password-email.md` | Prosedur Reset dan Pemulihan Password Email | email | Pola panduan portal Self-Service Password Reset (SSPR) & SSO | Bersih, langkah kanonik 1–4 lengkap (Koreksi K5) |
| KB-003 | `KB-003-konfigurasi-vpn.md` | Panduan Konfigurasi VPN untuk Akses Jarak Jauh | jaringan | Pola panduan remote access SSL-VPN client korporat | Bersih, langkah kanonik 1–4 lengkap (Koreksi K5) |
| KB-004 | `KB-004-printer-jaringan.md` | Panduan Instalasi dan Troubleshooting Printer Jaringan | perangkat | Pola panduan pengelolaan Print Server & Windows Spooler | Bersih, langkah kanonik 1–4 lengkap |
| KB-005 | `KB-005-teams-outlook.md` | Panduan Penggunaan Microsoft Teams dan Outlook | aplikasi | Pola catatan internal helpdesk kolaborasi kantor | **Sengaja tidak rapi (§5.2):** istilah dicampur (*Teams*, *MS Teams*, *aplikasi tim*, *surel kantor*), Langkah 4 minim rincian tombol |
| KB-006 | `KB-006-akses-shared-drive.md` | Prosedur Permintaan Akses Folder Bersama | lainnya | Pola panduan network shared drive SMB/CIFS & Credential Manager | Bersih, langkah kanonik 1–4 lengkap |
| KB-007 | `KB-007-keamanan-akun-2fa.md` | Panduan Keamanan Akun dan Autentikasi Dua Faktor | lainnya | Pola panduan MFA/2FA TOTP Authenticator korporat | Bersih, langkah kanonik 1–4 lengkap |
| KB-008 | `KB-008-troubleshoot-erp.md` | Panduan Troubleshooting Aplikasi ERP (Modul Dasar) | aplikasi | Pola catatan troubleshoot aplikasi ERP/FinOps internal | **Sengaja tidak rapi (§5.2):** istilah dicampur (*ERP*, *FinOps*, *portal operasional*), Langkah 4 minim instruksi penyamaran |

---

## 2. Kepatuhan Format Kanonik (§5.2 & K8)

1. **YAML Front Matter**: Setiap file memuat metadata terstruktur `article_id`, `judul`, `kategori`, `status: published`, `asal: buatan sendiri (sintetis)`, `pola`, dan `tanggal`.
2. **Struktur Chunking**: Setiap bagian menggunakan format `## Bagian N: ...` yang memudahkan pemisahan chunk deterministik pada pipeline RAG.
3. **Penghitungan Langkah (K8)**: Setiap unit solusi menggunakan format heading kanonik `### Langkah N: <Nama Langkah>` sehingga jumlah langkah dan penomoran dapat dihitung secara deterministik oleh kode orchestrator.
4. **Bagian Eskalasi**: Seluruh dokumen memiliki bagian wajib *"Kapan Harus Menghubungi Teknisi IT"*.
