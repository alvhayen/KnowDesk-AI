# CATATAN PROSES — MINGGU 5

Nama / NIM / K : [Nama Mahasiswa] / [NIM Mahasiswa] / K = 3  
Tanggal        : 2026-10-12  
Waktu yang saya habiskan minggu ini : 8 jam  

---

## 1. Yang saya kerjakan minggu ini
Saya merancang kontrak data keluaran berformat tetap (JSON Schema & Pydantic), menyusun spesifikasi `skema-kontrak.md` dengan medan wajib kutipan persis (*exact substring quote*) dan opsi nilai `dapat_ditentukan: ya | tidak`, membuat kode penguji `validator.py` dengan penanganan kegagalan 3 langkah, serta menguji ketahanan skema pada 10 variasi masukan berbeda.

## 2. Tahap READ
Yang saya amati :
Ketika skema tidak memiliki nilai tertutup (*closed-set enum*), model menghasilkan berbagai variasi semantik liar untuk medan tingkat kepentingan (seperti "agak mendesak", "prioritas lumayan", "segera"). Medan bukti yang tidak mewajibkan kutipan langsung cenderung diisi ringkasan subjektif yang tidak dapat diverifikasi secara programatis.

Yang mengejutkan saya :
Keluaran C pada tahap FIX (bukti berupa ringkasan dalam tanda kurung *"tidak disebutkan eksplisit tetapi dapat disimpulkan..."*) adalah pelanggaran skema yang paling berbahaya karena format JSON-nya tampak valid dan lolos tipe data teks string, namun secara substansi menyembunyikan halusinasi murni.

## 3. Tahap BREAK
| # | Percobaan | Prediksi saya | Hasil sebenarnya | Prediksi tepat? |
|---|---|---|---|---|
| 1 | Kirim masukan string kosong | JSON error atau null | Model mengembalikan `dapat_ditentukan: tidak` dan meminta rincian keluhan | ya |
| 2 | Kirim masukan bahasa Inggris | Model membalas bahasa Inggris | JSON tetap valid, pesan diterjemahkan otomatis ke bahasa Indonesia | ya |
| 3 | Keluhan mencakup 2 kategori (jaringan & email) | Model error memecah format | Model memilih kategori primer (jaringan) dan mencatat isu email di pesan | ya |
| 4 | Masukan sepanjang 5 halaman | Model macet atau truncation | Jendela konteks penuh, respon terpotong di tengah kurung kurawal JSON | ya |
| 5 | Hilangkan daftar nilai sah pada tingkat urgensi (10x run) | Muncul 2-3 variasi kata | Muncul 7 variasi nilai berbeda ("urgent", "high", "mendesak", "prioritas 1", dll.) | tidak |
| 6 | Masukan berisi string injeksi skema format | Model terkecoh format palsu | Skema divalidasi oleh Pydantic; teks masukan tetap berada di nilai data | ya |

Prediksi saya yang paling MELESET : nomor 5  
Apa yang salah dari cara saya berpikir sebelumnya :
Saya mengira tanpa enum model akan konsisten memakai istilah umum "tinggi/sedang/rendah". Kenyataannya model menghasilkan 7 variasi kosakata berbeda dalam 10 kali run, membuktikan bahwa daftar nilai tertutup adalah keharusan mutlak dalam rekayasa perangkat lunak berbasis AI.

## 4. Tahap FIX
Kesalahan yang saya temukan :
Pada 4 keluaran rusak tahap FIX:
- A: Tercemar teks basa-basi pembuka di luar JSON blok.
- B: Kategori dan tingkat kepentingan melanggar tipe enum (dua nilai digabung).
- C: Bukti bukan kutipan langsung melainkan interpretasi tersirat (paling berbahaya).
- D: Panjang tindakan disarankan melebihi batas 20 kata.
Bagaimana saya membuktikan diagnosis itu, bukan sekadar menduganya :
Menjalankan fungsi validator Pydantic; parser menolak A, B, dan D secara otomatis. Kasus C lolos parser teks namun gagal saat dicocokkan dengan fungsi `substring_match()`.

## 5. Tahap BUILD
Yang berhasil :
1. Penyusunan Pydantic schema model `TroubleshootResponse` dan `ResolutionStep`.
2. Implementasi mekanisme fallback 3 langkah pada `validator.py`.
3. Pencapaian skor kepatuhan validasi skema 10 dari 10 masukan uji (100% sah).

Yang tidak berhasil :
Sempat menemui kegagalan parsing JSON ketika model membungkus objek dengan blok markdown ```json ... ```; diatasi dengan menambahkan fungsi ekstraksi regex sanitasi `strip_markdown_codeblock()`.

Keputusan rancangan yang saya ambil minggu ini, beserta alasannya :
| Keputusan | Alternatif yang saya tolak | Alasan memilih |
|---|---|---|
| Menerapkan validasi kutipan persis (*exact substring*) | Mengizinkan ringkasan semantik | Memastikan klaim teknis 100% berakar pada teks SOP kanonik |
| Penanganan kegagalan 3 langkah (Validasi $\rightarrow$ Retry $\rightarrow$ Fallback Tiket) | Mengabaikan error dan menampilkan teks apa adanya | Menjamin antarmuka frontend tidak pernah mengalami crash atau menampilkan JSON rusak |

## 6. Tantangan wajib
Hasil :
Saya berhasil mencapai target **10 dari 10 keluaran sah** pada pengujian sepuluh masukan beragam (termasuk masukan panjang, istilah bahasa asing, dan injeksi instruksi). Seluruh keluaran tervalidasi penuh oleh skema Pydantic.

## 7. Penggunaan AI minggu ini
| # | Untuk apa | Prompt (ringkas / pola Lampiran A) | Yang saya UBAH dari hasilnya | Bagaimana saya verifikasi |
|---|---|---|---|---|
| 1 | Merancang skema JSON | Pola Prompt 5.2.A: Perancang skema keluaran terstruktur | Menambahkan medan `dapat_ditentukan` dan `langkah_ke` | Validasi skema via Pydantic model |
| 2 | Membuat masukan pengacau | Pola Prompt 5.2.B: Pembangkit 10 masukan adversarial | Menyaring agar tetap relevan dengan konteks perangkat kantor | Menguji pada validator lokal |

Satu hal yang AI berikan dan ternyata KELIRU minggu ini :
AI menyarankan agar medan `sumber` diberi tipe data `Optional[str]` bebas. Saya ubah menjadi array of objects berisi `article_id`, `section`, dan `kutipan` agar dapat diverifikasi otomatis.

Bagian karya minggu ini yang paling sulit saya jelaskan bila ditanya :
Mengapa kasus C pada tahap FIX paling berbahaya (penjelasannya: kasus C adalah *silent failure* yang lolos validasi sintaksis JSON namun merusak integritas semantik grounding).

## 8. Pemakaian dan biaya
| Kegiatan | Model | Perkiraan token | Perkiraan biaya |
|---|---|---|---|
| Uji coba 10 kasus validasi skema | google/gemini-flash | 14.800 token | Rp 680 |
Total minggu ini : Rp 680  
Total kumulatif  : Rp 1.830  

## 9. Daftar periksa mandiri
- [x] Empat pertanyaan READ terjawab tanpa mencoba lebih dulu
- [x] Nomor 5 BREAK dijalankan 10 kali dan variasi nilainya dihitung (7 nilai berbeda)
- [x] Empat keluaran tak sah tahap FIX dianalisis, termasuk analisis kasus C
- [x] Skema produk memuat medan bukti dan nilai tak-dapat-ditentukan
- [x] Tabel sepuluh masukan uji terisi lengkap
- [x] Penanganan kegagalan tiga langkah ada dan terbukti bekerja
- [x] instruksi/CATATAN.md diperbarui

## 10. Yang macet dan rencana minggu depan
Yang masih macet : Menghubungkan model dengan tool fungsi Python eksternal secara dinamis (*Function Calling*).  
Apa yang sudah saya coba untuk mengatasinya : Membaca dokumentasi OpenAI/OpenRouter tools parameter.  
Rencana konkret minggu depan : Merancang 3 tool wajib ($K = 3$) dan batas kewenangan aksesnya pada Tugas 6.
