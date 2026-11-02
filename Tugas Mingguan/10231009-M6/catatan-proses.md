# CATATAN PROSES — MINGGU 6

Nama / NIM / K : [Nama Mahasiswa] / [NIM Mahasiswa] / K = 3  
Tanggal        : 2026-10-12  
Waktu yang saya habiskan minggu ini : 8 jam  

---

## 1. Yang saya kerjakan minggu ini
Saya mengimplementasikan mekanisme pemanggilan perkakas eksternal (*Function Calling / Tool Use*) untuk 3 tool wajib $K = 3$ (`search_kb`, `get_article`, `draft_ticket`). Saya menyusun spesifikasi `spesifikasi-tool.md` dengan batas kewenangan tertulis, membuat script `tools_runner.py` dengan penanganan pesan error jujur, melakukan trace 1 siklus eksekusi tool, serta menguji ketepatan pemilihan tool pada 8 variasi pertanyaan.

## 2. Tahap READ
Yang saya amati :
Model bahasa sebenarnya tidak pernah "menjalankan" tool atau mengakses database secara langsung. Model hanya menghasilkan token string berstruktur khusus yang meminta sistem pemanggil untuk mengeksekusi sebuah fungsi. Sistem kitalah yang memegang kendali eksekusi dan memutuskan apakah permintaan tersebut sah dijalankan.

Yang mengejutkan saya :
Ketika hasil eksekusi tool dikembalikan ke model, model sering kali tergoda menambahkan kalimat kesimpulan sendiri yang tidak ada di dalam data pengembalian tool. Memeriksa kesetiaan (*faithfulness*) jawaban akhir terhadap data mentah tool adalah titik evaluasi yang sangat krusial.

## 3. Tahap BREAK
| # | Percobaan | Prediksi saya | Hasil sebenarnya | Prediksi tepat? |
|---|---|---|---|---|
| 1 | Deskripsi tool dikaburkan jadi 1 kata ("mencari") | Model tetap memilih dengan benar | Model salah memilih tool atau memanggilnya pada pertanyaan umum | tidak |
| 2 | Sediakan 2 tool dengan fungsi tumpang tindih | Model memanggil keduanya acak | Model bingung dan sering memanggil tool yang parameternya lebih sedikit | ya |
| 3 | Tool sengaja dibuat mengembalikan pesan error eksplisit | Model menyampaikan pesan error ke user | Model membaca pesan error dan menawarkan alternatif tiket IT | ya |
| 4 | Tool mengembalikan hasil kosong `[]` tanpa pesan error | Model tahu data tidak ada | Model berhalusinasi menyatakan informasi tidak tersedia di dunia | tidak |
| 5 | Tanya salam atau pertanyaan percakapan santai | Model tetap memanggil tool cari | Model langsung merespons ramah tanpa memanggil tool apa pun | ya |
| 6 | Pertanyaan membutuhkan 2 tool berurutan (search -> get) | Model memanggil 2 tool sekaligus | Model memanggil `search_kb` dulu, menunggu respon, baru memanggil `get_article` | ya |

Prediksi saya yang paling MELESET : nomor 1 dan 4  
Apa yang salah dari cara saya berpikir sebelumnya :
Pada nomor 1, deskripsi tool adalah prompt semantik bagi model; jika kabur, model menebak secara acak. Pada nomor 4, mengembalikan array kosong tanpa pesan galat membuat model mengira pencarian berhasil dan mengarang alasan ketiadaan data.

## 4. Tahap FIX
Kesalahan yang saya temukan :
Pada 3 tool contoh tahap FIX (`cari_data`, `cari_peraturan`, `hitung`): deskripsinya bertumpang tindih ("mencari informasi" vs "mencari peraturan dan data") sehingga kueri tentang ketentuan zonasi industri memicu tool yang salah.
Bagaimana saya membuktikan diagnosis itu, bukan sekadar menduganya :
Menguji kueri "ketentuan zonasi Kariangau"; sistem memanggil `cari_data` alih-alih `cari_peraturan`.
Perbaikan yang dilakukan :
Menulis ulang deskripsi ketiga tool secara tegas dengan batasan kapan tool TIDAK boleh digunakan.

## 5. Tahap BUILD
Yang berhasil :
1. Tiga tool kanonik $K = 3$ (`search_kb`, `get_article`, `draft_ticket`) berhasil dirangkai pada `tools_runner.py`.
2. Batas kewenangan tertulis diberlakukan: tool pembacaan berjalan otomatis, sedangkan pembuatan tiket memerlukan persetujuan eksplisit (*Human-in-the-Loop*).
3. Trace lengkap 1 putaran eksekusi tervalidasi 100% setia terhadap respon tool.

Yang tidak berhasil :
Pada pengujian awal, model sempat memanggil `draft_ticket` sebelum pengguna mencoba langkah apa pun; berhasil dicegah dengan mempertegas deskripsi bahwa tiket dilarang dibuat sebelum pencarian solusi dilakukan.

Keputusan rancangan yang saya ambil minggu ini, beserta alasannya :
| Keputusan | Alternatif yang saya tolak | Alasan memilih |
|---|---|---|
| Memisahkan pencarian ringkas (`search_kb`) dan pembacaan artikel penuh (`get_article`)| Menggabungkan langsung dalam 1 tool besar | Menghemat token masukan jendela konteks dengan tidak menarik artikel penuh jika belum relevan |
| Menolak pengiriman tiket otomatis | Agen langsung membuat tiket ke database helpdesk | Mencegah spam tiket palsu dan mematuhi batas kewenangan persetujuan manusia |

## 6. Tantangan wajib
Hasil :
Saya menemukan pertanyaan yang awalnya memicu salah pilih tool: *"Bisa tolong buatkan tiket perbaikan Wi-Fi karena dari tadi putus terus?"* Awalnya model langsung memanggil `draft_ticket`.
Saya memperbaikinya **hanya dengan mengubah deskripsi tool `draft_ticket`** (menambahkan: *"DILARANG memanggil tool ini sebelum dilakukan pencarian artikel solusi di search_kb"*). Setelah deskripsi diubah, model berbalik memanggil `search_kb("troubleshoot wifi")` terlebih dahulu.

## 7. Penggunaan AI minggu ini
| # | Untuk apa | Prompt (ringkas / pola Lampiran A) | Yang saya UBAH dari hasilnya | Bagaimana saya verifikasi |
|---|---|---|---|---|
| 1 | Desain spesifikasi tool | Pola Prompt 6.2.A: Perancang parameter tool | Menambahkan parameter `langkah_dicoba` pada tool tiket | Memeriksa kecocokan skema JSON |
| 2 | Variasi pertanyaan uji | Pola Prompt 6.2.B: 8 pertanyaan uji pemilihan tool | Menyesuaikan dengan ragam keluhan helpdesk IT kantor | Menguji pada script eksekutor |

Satu hal yang AI berikan dan ternyata KELIRU minggu ini :
AI menyarankan tool `execute_command_line` untuk menjalankan perintah perbaikan di komputer pengguna secara otomatis. Ini sangat berbahaya (risiko keamanan siber fatal); saya tolak sepenuhnya.

Bagian karya minggu ini yang paling sulit saya jelaskan bila ditanya :
Mengapa kegagalan tool nomor 4 (mengembalikan kosong diam-diam) lebih berbahaya daripada nomor 3 (mengembalikan error eksplisit) (penjelasannya: hasil kosong memicu halusinasi percaya diri, sedangkan error memicu jalur pemulihan terarah).

## 8. Pemakaian dan biaya
| Kegiatan | Model | Perkiraan token | Perkiraan biaya |
|---|---|---|---|
| Uji coba 8 skenario tool calling | google/gemini-flash | 16.500 token | Rp 760 |
Total minggu ini : Rp 760  
Total kumulatif  : Rp 2.590  

## 9. Daftar periksa mandiri
- [x] Trace satu putaran tool terisi lengkap, termasuk uji kesetiaan jawaban
- [x] Enam percobaan BREAK dengan prediksi lebih dulu
- [x] Analisis perbandingan nomor 3 dan 4 tertulis
- [x] Ketiga deskripsi tool tahap FIX ditulis ulang
- [x] Produk memanggil >= 1 tool dan hasilnya terbukti dipakai
- [x] Tiap tool punya batas kewenangan tertulis
- [x] Tantangan wajib disertai bukti sebelum-sesudah

## 10. Yang macet dan rencana minggu depan
Yang masih macet : Mengatur pemenggalan dokumen (*chunking*) dan perhitungan *embedding* vektor untuk pencarian dokumen SOP nyata.  
Apa yang sudah saya coba untuk mengatasinya : Membaca teori cosine similarity dan pemenggalan berbasis heading Markdown.  
Rencana konkret minggu depan : Merancang arsitektur alur RAG lengkap untuk 8 dokumen KB pada Tugas 7 sebagai persiapan UTS Minggu 8.
