# designsystem.md — Sistem Desain KnowDesk AI

> Versi 1.0 · 11 Oktober 2026 · Tema **Arsip Pinus** · light only
> Untuk AI coding agent dan mahasiswa pemilik proyek. Aturan anti-slop diturunkan dari repo [Nutlope/hallmark](https://github.com/Nutlope/hallmark) (MIT; `SKILL.md` dan `references/anti-patterns.md`, `typography.md`, `color.md`, `genres/modern-minimal.md`). Hallmark dirancang untuk halaman, bukan aplikasi, jadi yang dipakai di sini adalah **disiplinnya** (token terkunci, 8 state, larangan font/warna/layout, gerbang uji), bukan katalog macrostructure halaman pemasaran.

---

## 0. Cara memakai

1. File ini adalah **sistem terkunci**. Agent tidak boleh memilih warna, font, radius, atau durasi di luar token yang ada. Butuh nilai baru → tambahkan sebagai token di `tokens.css` lebih dulu, lalu pakai namanya.
2. Setiap komponen harus memiliki **8 state**: default, hover, `:focus-visible`, active, disabled, loading, error, success (bila relevan, tulis alasan di komentar mengapa suatu state tidak berlaku).
3. Jalankan `npm run lint:design` (skrip di §13.4) sebelum menyatakan UI selesai.
4. Jika pengguna memasang skill Hallmark (`npx skills add nutlope/hallmark`), salin file ini ke root repo sebagai `design.md` agar Hallmark tunduk pada sistem ini. Menurut `SKILL.md`, `design.md` di root mengalahkan semua pilihan lain.
5. Konflik dengan `architecture.md`: file ini menang untuk UI (tema light, tanpa emoji, tanpa WebSocket; lihat `agents.md` K12).

---

## 1. Arah desain

| Aspek | Keputusan |
|---|---|
| Audiens | Staf kantor non-teknis yang sedang terhambat dan ingin cepat tuntas |
| Satu tugas | Menyelesaikan satu masalah IT lewat langkah yang bisa diikuti, atau tahu kapan harus meminta tiket |
| Nada | **Utilitarian**: tenang, terbaca, prosedural. Bukan "bersih dan modern" (itu bukan nada) |
| Konsep | **Arsip Pinus**: kertas arsip hangat, tinta hijau pinus, garis tipis seperti formulir kantor dan buku panduan servis |
| Genre | Modern-minimal yang dipanaskan: Geist-style sans diganti font langka, kartu bergaris tipis, tanpa pil, tanpa gradien |
| Tema | Light only. `color-scheme: light`. Tidak ada tombol tema gelap |

**Tiga gerakan khas** (yang membuat tampilan terasa dirancang, bukan dihasilkan):

1. **Slip langkah.** Setiap langkah solusi adalah blok bernomor dengan angka besar tabular di kolom kiri dan instruksi di kanan, dipisah garis tipis seperti lembar prosedur. Bukan bubble chat berlatar warna.
2. **Catatan kaki sumber.** Kutipan sumber tampil seperti catatan kaki: chip kode mono `KB-002 · Bagian 3`, judul bagian, lalu kutipan yang bisa dibuka.
3. **Draf tiket sebagai formulir.** Tiket tampil sebagai formulir berbaris garis tipis dengan label di kiri, bukan kartu ikon.

---

## 2. Larangan anti-slop (ringkasan, dengan pengganti)

Tiap baris adalah "tell" khas UI buatan AI. Satu saja sudah masalah; dua dalam satu layar berarti pasti terlihat otomatis.

| Dilarang | Mengapa terbaca AI | Gantinya di KnowDesk |
|---|---|---|
| Gradien ungu→biru/pink, gradien di hero atau teks (`background-clip: text`) | Tell paling dikenal | Permukaan solid; satu aksen hijau pinus |
| Inter, Roboto, Open Sans, Lato, Poppins, Montserrat, DM Sans, Nunito, Arial, Helvetica, `system-ui` sebagai satu-satunya font | Default semua LLM | Schibsted Grotesk + Onest + Spline Sans Mono (§4) |
| `#000`, `#fff` murni | Terasa datar dan sintetis | Kertas dan tinta bernuansa (§5) |
| Grid 3 kolom ikon-judul-teks; kartu ikon di kotak berwarna | Template universal | Daftar bergaris, ikon sejajar baris atau tanpa ikon |
| Kartu di dalam kartu | Bersarang tanpa arti | Satu lapis wadah |
| **Garis tepi tebal satu sisi** (`border-left: 4px`) pada kartu/kutipan | "Side-stripe card" | Garis tipis di semua sisi atau tanpa garis |
| Hero `100vh` serba tengah | Landing LLM standar | Welcome rata kiri setinggi isinya |
| Semua serba rata tengah | Terlalu simetris | Rata kiri; pesan pengguna rata kanan hanya sebagai penanda giliran |
| Emoji sebagai ikon (`✨ 🚀 ⚡ ✅`, juga `✓ ✗ ●`) | Rusak sistem tipografi, beda di tiap OS | Lucide, satu pustaka |
| Mencampur pustaka ikon | Stroke berbeda | Hanya Lucide, `stroke-width` 1.75 |
| `transition-all`, `hover:scale-105`, easing bouncy, kursor pengikut | Gerak generik | Transisi properti spesifik, `--ease-out` |
| Dot mengambang/blob aurora/orb | Dekorasi tanpa fungsi | Tidak ada dekorasi |
| Glow bayangan berwarna pada latar gelap; glassmorphism hiasan | | Tidak ada bayangan di kartu; garis tipis |
| Italic pada judul | Penanda "ingin terlihat editorial" | Judul selalu roman (`font-style: normal`) |
| Eyebrow huruf besar di tiap bagian; label kiri + judul kanan | Tic template editorial | Tidak ada eyebrow |
| Angka metrik buatan ("99,9%", "10× lebih cepat") | Fabrikasi | Tampilkan `—` atau jangan tampilkan |
| Chrome palsu (bingkai browser, ponsel, jendela kode) | Meniru OS | Tidak dipakai |
| Toast perayaan ("Berhasil!") untuk hal yang sudah terlihat | | Sukses diam; toast hanya untuk galat dan aksi yang efeknya tak terlihat |
| Dialog "Apakah Anda yakin?" untuk aksi yang bisa dibatalkan | | Aksi langsung; draf tiket **adalah** konfirmasinya |
| Titik tiga (`...`), tanda kutip lurus, `--` | Tanda belum disunting | `…`, kutip lengkung, `—` |
| Nama placeholder startup ("Acme", "Nexus", "Unleash", "Seamless") | | Nama konkret dan fiktif yang jelas |
| Animate-on-scroll di semua bagian | | Satu entrance pesan terbaru saja |

---

## 3. Layout aplikasi

**Satu halaman** (`+page.svelte`), tanpa landing page.

```
Desktop ≥ 1024 px                           Mobile < 1024 px
┌───────────────────────────────────────┐   ┌───────────────────────┐
│ Header (3.5rem)                       │   │ Header                │
├───────────────────────────┬───────────┤   ├───────────────────────┤
│ Percakapan                │ Ringkasan │   │ ▸ Ringkasan sesi      │ ← <details>
│ (maks 46rem, rata kiri)   │ sesi      │   ├───────────────────────┤
│                           │ (20rem)   │   │ Percakapan            │
├───────────────────────────┤           │   ├───────────────────────┤
│ Composer + pengungkapan AI│           │   │ Composer (menempel)   │
└───────────────────────────┴───────────┘   └───────────────────────┘
```

- Kolom percakapan dibatasi `--chat-max: 46rem`; panjang baris teks `--measure: 65ch`. Kolom ini **rata kiri**, tidak di tengah halaman.
- Panel samping berisi `StepTracker`, status sesi, daftar sumber yang dipakai, aksi "Buat tiket ke teknisi" dan "Sesi baru". Isinya dari state klien (store), bukan endpoint baru.
- Mobile: panel menjadi `<details>` di atas percakapan (ringkas: "Langkah 2 · maks. 4"). Composer menempel di bawah memakai `position: sticky`, bukan `fixed` dengan `100vw`.
- Breakpoint: 320, 375, 414, 768, 1024, 1280. Setiap emit diperiksa di empat lebar pertama.
- Skala z-index bernama: `--z-base: 0`, `--z-sticky: 10`, `--z-popover: 20`, `--z-toast: 30`. Tidak ada `z-index: 9999`.

---

## 4. Tipografi

### 4.1. Font (dua keluarga utama + satu outlier)

| Peran | Font | Sumber | Bobot | Dipakai untuk |
|---|---|---|---|---|
| Display | **Schibsted Grotesk** | `@fontsource-variable/schibsted-grotesk` | 700, 800 | Wordmark, judul welcome, nomor langkah, judul bagian |
| Body | **Onest** | `@fontsource-variable/onest` | 400, 500 | Semua teks UI dan isi pesan |
| Outlier | **Spline Sans Mono** | `@fontsource-variable/spline-sans-mono` | 400, 500 | **Hanya kode pengenal**: `KB-002 · Bagian 3` dan `TK-0042` |

- Dasar pemilihan: ketiganya ada di Google Fonts, gratis dan berlisensi terbuka, dan jarang dipilih secara default oleh generator UI dibanding Inter/Geist/Fraunces. Grotesk berkarakter (Schibsted) bertemu sans humanis yang lapang (Onest) dan mono bergaya kode kantor.
- Mono adalah **outlier**: hanya untuk identifier. Maksimal dua jenis tempat (chip sumber, ID tiket). Jangan dipakai untuk label, tombol, atau badge lain.
- Maksimal **tiga keluarga** di seluruh aplikasi. Bobot berbeda dari keluarga yang sama dihitung satu.
- Install: `npm i @fontsource-variable/schibsted-grotesk @fontsource-variable/onest @fontsource-variable/spline-sans-mono` (verifikasi nama paket dengan `npm search` sebelum dipakai [Kemungkinan Besar benar]). Self-host, tidak memanggil CDN, sehingga demo tetap jalan tanpa koneksi ke Google.
- Fallback: `ui-sans-serif, system-ui, sans-serif`. Bila terlihat CLS, tambahkan `size-adjust` pada font fallback.
- Fitur: `font-variant-numeric: tabular-nums` untuk angka (nomor langkah, jumlah karakter, ID). `font-display: swap` (sudah bawaan Fontsource).

### 4.2. Skala (rasio 1,25, dasar 16 px)

| Token | Ukuran | Line-height | Pemakaian |
|---|---|---|---|
| `--text-sm` | 0,875rem (14 px) | 1,5 | metadata, label, chip, catatan pengungkapan AI |
| `--text-base` | 1rem (16 px) | 1,6 | isi pesan, input, tombol |
| `--text-md` | 1,25rem (20 px) | 1,4 | judul langkah, judul bagian panel |
| `--text-lg` | 1,5625rem (25 px) | 1,25 | nomor langkah, judul welcome (mobile) |
| `--text-xl` | 1,953rem (31 px) | 1,15 | judul welcome (desktop) |

- Maksimal **lima ukuran** pada satu layar. Hierarki tambahan lewat bobot dan warna, bukan ukuran baru.
- Teks di bawah 14 px dilarang. Teks isi tidak pernah huruf kapital semua. Tidak ada rata kanan-kiri (justify).
- Display: `letter-spacing: -0.02em`, bobot 700–800, **tidak pernah italic**. Body: bobot 400, `line-height: 1.6`, `max-width: var(--measure)`.
- Judul welcome ≤ 7 kata dan ≤ 50 karakter.
- Aksen pada teks tidak memakai italic: tekanan lewat bobot 500 atau warna `--color-accent`.

---

## 5. Warna (OKLCH, dikunci)

Satu jangkar: **hijau pinus** (hue 160) di atas kertas hangat (hue 100). Netral diwarnai tipis ke arah jangkar. Aksen **≤ 3% dari area layar**.

| Token | Nilai | Peran |
|---|---|---|
| `--color-paper` | `oklch(97.5% 0.010 100)` | latar halaman |
| `--color-paper-2` | `oklch(94.5% 0.013 100)` | permukaan tenggelam: pesan pengguna, panel samping |
| `--color-surface` | `oklch(99% 0.006 100)` | permukaan terangkat: input, kartu sumber, draf tiket |
| `--color-rule` | `oklch(87% 0.012 100)` | garis tipis |
| `--color-rule-strong` | `oklch(76% 0.014 100)` | garis input saat aktif, batas tombol sekunder |
| `--color-muted` | `oklch(46% 0.012 100)` | teks sekunder |
| `--color-ink` | `oklch(21% 0.012 100)` | teks utama |
| `--color-accent` | `oklch(44% 0.105 160)` | tombol utama, tautan, tanda langkah aktif |
| `--color-accent-hover` | `oklch(38% 0.105 160)` | hover aksen |
| `--color-accent-soft` | `oklch(93.5% 0.030 160)` | latar terpilih/sukses |
| `--color-on-accent` | `oklch(97.5% 0.010 100)` | teks di atas aksen |
| `--color-focus` | `oklch(50% 0.140 160)` | cincin fokus |
| `--color-warn` / `--color-warn-soft` | `oklch(46% 0.110 70)` / `oklch(94.5% 0.050 85)` | peringatan |
| `--color-danger` / `--color-danger-soft` | `oklch(48% 0.160 27)` / `oklch(95% 0.030 27)` | galat |

- **Kontras** (perkiraan dari kecerahan OKLCH; **verifikasi dengan alat kontras sebelum rilis** [Menebak]): teks `--color-ink` dan `--color-muted` di atas `--color-paper` dan `--color-paper-2` ≥ 4,5:1; `--color-on-accent` di atas `--color-accent` ≥ 4,5:1; batas komponen ≥ 3:1.
- Status **tidak pernah hanya warna**: selalu disertai ikon dan teks (prioritas tiket "Tinggi", bukan hanya titik merah).
- Aksen bukan latar luas. Boleh untuk: tombol utama, tautan, tanda langkah aktif, cincin fokus. Tidak boleh untuk: latar bagian, banner besar, dekorasi.
- Dilarang: nilai warna di luar `tokens.css`, kelas warna bawaan Tailwind (`bg-gray-100`, `text-black`), kanal alfa sebagai definisi warna, gradien.

---

## 6. Spasi, bentuk, dan elevasi

| Token | Nilai |
|---|---|
| `--space-2xs` | 4 px |
| `--space-xs` | 8 px |
| `--space-sm` | 12 px |
| `--space-md` | 16 px |
| `--space-lg` | 24 px |
| `--space-xl` | 32 px |
| `--space-2xl` | 48 px |
| `--space-3xl` | 64 px |
| `--radius-sm` | 4 px (chip, kode) |
| `--radius-md` | 8 px (input, tombol, kartu) |

- Hanya dua radius. Tidak ada pil, tidak ada `rounded-2xl`, tidak ada lingkaran avatar.
- **Elevasi lewat garis dan lapisan warna**, bukan bayangan. Satu-satunya bayangan: `--shadow-pop` untuk toast dan popover (ketat dan gelap, bukan halo).
- Padding tidak seragam di semua bagian: percakapan lebih longgar vertikal, panel samping lebih rapat.

---

## 7. Gerak

| Token | Nilai | Pemakaian |
|---|---|---|
| `--dur-fast` | 100 ms | press, perubahan warna |
| `--dur-short` | 160 ms | entrance pesan, buka/tutup kutipan |
| `--dur-med` | 240 ms | panel `<details>` |
| `--ease-out` | `cubic-bezier(0.22, 1, 0.36, 1)` | standar |
| `--ease-in-out` | `cubic-bezier(0.65, 0, 0.35, 1)` | perubahan ukuran |

- Hanya animasikan `transform` dan `opacity`. Tidak ada `transition-all`; tulis properti secara eksplisit.
- **Satu** entrance: pesan terbaru muncul `opacity 0→1` dan `translateY(4px→0)` selama `--dur-short`. Pesan lama tidak bergerak. Tidak ada stagger.
- Indikator memuat: **skeleton tiga baris** di blok asisten, ditampilkan setelah jeda 150 ms dan bertahan minimal 300 ms (mencegah kedip). Tidak ada titik berlompatan atau spinner berputar besar.
- Cincin fokus muncul **instan**, tidak dianimasikan.
- `prefers-reduced-motion: reduce` → entrance menjadi crossfade ≤ 150 ms tanpa translasi; skeleton tanpa animasi.

---

## 8. Ikon dan identitas

- Satu pustaka: **Lucide** (`@lucide/svelte` untuk Svelte 5, `lucide-svelte` untuk Svelte 4; verifikasi). `stroke-width` 1.75; ukuran 16 px (di teks) dan 20 px (mandiri). Warna `currentColor`.
- Ikon yang dipakai: `Search`, `SearchX`, `ArrowUp`, `Check`, `X`, `CircleCheck`, `TriangleAlert`, `Info`, `ChevronDown`, `FileText`, `Ticket`, `RotateCcw`. Ikon tombol-saja wajib `aria-label`.
- **Wordmark:** "KnowDesk" dalam Schibsted Grotesk 800, `letter-spacing: -0.02em`, didahului kotak aksen 10 × 10 px (SVG sederhana, tanpa gradien, tanpa bentuk "kilau/sparkle"). Tidak ada logo AI generik (bintang, kilau, otak).
- Tidak ada ilustrasi dekoratif. Welcome hanya tipografi.

---

## 9. Komponen

Semua komponen memakai token dan 8 state. Nama mengikuti `architecture.md` §5.1.

### 9.1. Button

| Varian | Tampilan | Pemakaian |
|---|---|---|
| `primary` | latar `--color-accent`, teks `--color-on-accent` | satu per area: "Kirim", "Kirim tiket", "Masalah teratasi" |
| `secondary` | latar `--color-surface`, garis `--color-rule-strong`, teks `--color-ink` | "Masih bermasalah", "Batalkan draf" |
| `ghost` | tanpa latar, teks `--color-accent`, garis bawah saat hover | "Buat tiket ke teknisi", "Lihat kutipan" |

- Tinggi 2,5rem (40 px) di desktop, **2,75rem (44 px)** di pointer kasar. `white-space: nowrap`; label ≤ 3 kata dan tidak pernah tampil dua baris.
- State: hover (latar `--color-accent-hover` / garis lebih gelap), focus-visible (`outline: 2px solid var(--color-focus); outline-offset: 2px`, instan), active (`translateY(1px)`), disabled (latar `--color-paper-2`, teks `--color-muted`, `cursor: not-allowed`), loading (`aria-busy`, label berganti "Mengirim…", tombol terkunci), error (garis dan teks `--color-danger`, label "Coba lagi"), success (latar `--color-accent-soft`, ikon `Check`).

### 9.2. ChatInput (composer)

- `textarea` otomatis 1–4 baris, latar `--color-surface`, garis `--color-rule-strong`, `--radius-md`. `Enter` kirim, `Shift+Enter` baris baru. `maxlength` = 1000.
- Penghitung karakter muncul mulai 800 karakter (`812 / 1000`, `tabular-nums`), berubah `--color-danger` mulai 980.
- Disabled saat `escalating`, `resolved`, `closed`, atau saat memuat. Pada `resolved`/`closed` ganti isi composer dengan tombol "Sesi baru".
- Di bawahnya, selalu terlihat (R16): "Jawaban dibuat AI dari panduan IT simulasi dan bisa keliru. Bila langkah tidak cocok, minta tiket ke teknisi." (`--text-sm`, `--color-muted`).

### 9.3. ChatMessage

- **Asisten:** tanpa bubble. Kolom penuh, rata kiri. Baris judul kecil: kotak aksen 8 px + "KnowDesk" (`--text-sm`, bobot 500). Isi `pesan` dengan `white-space: pre-line`, `max-width: var(--measure)`.
- **Pengguna:** rata kanan, latar `--color-paper-2`, `--radius-md`, tanpa ekor, lebar maksimal 80%, teks `--color-ink`.
- Hanya pesan terbaru yang boleh punya aksi aktif. Pesan lama menampilkan hasil sebagai teks statis ("Dijawab: Masih bermasalah").
- Isi `pesan` dirender sebagai **teks polos**. Dilarang `{@html}`.

### 9.4. Slip langkah (`langkah_solusi`)

```
┌────────────────────────────────────────────────────────┐
│  2     Sambungkan ulang ke jaringan kantor             │  ← nomor: display 800, --text-lg, tabular-nums
│        Klik ikon jaringan di pojok kanan bawah, ...    │  ← pesan: body
│        ┌──────────────────────────────────────────┐    │
│        │ Sumber  KB-001 · Bagian 3                │    │  ← SourceCitation
│        └──────────────────────────────────────────┘    │
│        [ Masalah teratasi ]  [ Masih bermasalah ]      │
└────────────────────────────────────────────────────────┘
   garis tipis --color-rule di atas dan bawah slip
```

- Kolom nomor lebar tetap 2,5rem; isi di kolom kedua. Tidak berarti "label kiri + judul kanan" ala template: ini nomor urut prosedur yang memang ordinal.
- Judul langkah berasal dari `### Langkah N: judul` (dikirim kode), bukan dikarang model.

### 9.5. StepTracker

- Empat segmen persegi panjang (tinggi 4 px, jarak 4 px, radius 1 px): terisi `--color-accent` untuk langkah selesai, `--color-ink` untuk langkah aktif, `--color-rule` untuk sisa. Teks "Langkah 2 · maks. 4" di sampingnya.
- Aksesibilitas: `role="progressbar"` dengan `aria-valuemin=0`, `aria-valuemax`, `aria-valuenow`, dan `aria-label`. Bukan titik ●●○○.
- Bila langkah artikel kurang dari 4, segmen sisa berlabel "tidak tersedia" lewat `title` dan teks pendukung.

### 9.6. SourceCitation

- Wadah `--color-surface`, **garis tipis di semua sisi** (`1px solid var(--color-rule)`), `--radius-md`. Dilarang garis tebal satu sisi.
- Baris atas: kata "Sumber" (`--text-sm`, `--color-muted`), chip mono `KB-001 · Bagian 3` (`--radius-sm`, latar `--color-paper-2`), judul bagian (bobot 500).
- Kutipan tersembunyi secara default; tombol ghost "Lihat kutipan" (`aria-expanded`, `aria-controls`). Kutipan tampil dengan tanda kutip lengkung “…”, `--text-sm`.

### 9.7. ClarificationPrompt

- Tampil sebagai pesan asisten biasa. Pertanyaan bernomor (maks 2) dalam daftar `ol`. Bila `clarification_count` mendekati batas, tambahkan teks kecil "Pertanyaan {n} dari maks. 2".

### 9.8. Tidak ditemukan (`tidak_ditemukan`)

- Blok `--color-paper-2` bergaris tipis, ikon `SearchX` 20 px, judul "Belum ada panduan untuk ini" (`--text-md`, display 700), teks `messages.tidak_ditemukan`.
- Aksi: primary "Buat draf tiket", secondary "Ubah pertanyaan" (memfokuskan composer).

### 9.9. TicketDraft

- Formulir bergaris di `--color-surface`: baris-baris dengan label kiri (`--color-muted`, `--text-sm`, lebar 7rem) dan nilai kanan, dipisah `1px solid var(--color-rule)`. Di mobile, label di atas nilai.
- Baris: ID (mono, `TK-0042`), Judul, Kategori, **Prioritas** (teks + ikon, tidak hanya warna), Deskripsi, Langkah dicoba (`ol`).
- Header "Draf tiket · belum dikirim". Aksi: primary "Kirim tiket", secondary "Batalkan draf". Setelah terkirim: header berubah "Tiket terkirim", ikon `CircleCheck`, kedua tombol hilang. Tidak ada modal konfirmasi tambahan; formulir ini sudah konfirmasinya.

### 9.10. StatusIndicator dan galat

- Memuat: skeleton tiga baris (§7) dengan teks tersembunyi untuk pembaca layar "Menyusun jawaban…" (`aria-live="polite"`).
- Galat: banner `--color-danger-soft`, garis tipis `--color-danger`, ikon `TriangleAlert`, teks plain: "Layanan sedang tidak merespons. Pesan Anda belum diproses." + tombol secondary "Coba lagi". `role="alert"`. Banner tidak mendorong layout (muncul di slot composer).
- Peringatan keyakinan rendah: tampilkan teks "Panduan ini mungkin kurang tepat. Bila tidak cocok, minta tiket." pada pesan dengan `keyakinan` `rendah`.

### 9.11. Header

- Kiri: kotak aksen + wordmark. Kanan: tombol ghost "Sesi baru" (`RotateCcw`). Garis bawah `--color-rule`. Tinggi 3,5rem. Tanpa bayangan, tanpa blur backdrop. ID sesi tidak ditampilkan (hanya di log/dev).

### 9.12. Welcome (state kosong)

- Rata kiri, tanpa ilustrasi. Judul display: "Ada masalah IT? Ceritakan gejalanya." (`--text-xl` desktop, `--text-lg` mobile). Satu kalimat: "KnowDesk memandu langkah demi langkah dari panduan IT dan membuat tiket bila masalah belum selesai."
- Di bawahnya daftar contoh bergaris tipis (bukan kartu), tiap baris adalah tombol ghost rata kiri: "Wi-Fi kantor tidak bisa tersambung", "Printer tidak terdeteksi di komputer", "Lupa password email". Mengklik mengisi dan mengirim.

### 9.13. Panel Ringkasan Sesi

- Latar `--color-paper-2`, garis kiri tipis `1px` (bukan tebal). Judul bagian `--text-md`. Isi: StepTracker, status (teks: "Memahami masalah" / "Memandu langkah" / "Menunggu konfirmasi tiket" / "Selesai" / "Ditutup"), daftar sumber yang dipakai (chip mono), aksi "Buat tiket ke teknisi" (ghost, aktif bila minimal satu pencarian sudah terjadi).

---

## 10. Teks antarmuka (Bahasa Indonesia)

- Suara: tenang, langsung, satu kalimat per ide. Tanpa seruan berlebihan, tanpa "Oops", tanpa "Tentu!", tanpa "Mari kita…".
- Tombol: kata kerja pendek, **satu baris**: "Kirim", "Kirim tiket", "Batalkan draf", "Masalah teratasi", "Masih bermasalah", "Coba lagi", "Sesi baru".
- Galat selalu menyatakan apa yang terjadi, apakah pesan sudah diproses, dan apa yang bisa dilakukan.
- Kutip lengkung, elipsis `…`, tanda pisah `—`. Angka dan tanggal memakai format Indonesia (`1 Oktober 2026`).
- Placeholder composer: "Tulis masalah Anda…". Saat `solving`: "Ceritakan hasilnya, atau pakai tombol di atas…".

---

## 11. Responsif

Wajib benar pada **320 / 375 / 414 / 768 px** (dan 1280 px):

- Tidak ada scroll horizontal. `html, body { overflow-x: clip }` (bukan `hidden`). Jangan pakai `100vw`.
- Grid dengan konten memakai `minmax(0, 1fr)`, bukan `1fr` polos.
- Teks panjang tanpa spasi (URL, kode) memakai `overflow-wrap: anywhere`.
- Tombol dan tautan tidak pernah dua baris (`white-space: nowrap`); persingkat label bila perlu.
- Target sentuh ≥ 44 px pada `pointer: coarse`.
- Tinggi dinamis memakai `dvh`, bukan `vh`.

---

## 12. Aksesibilitas

- Urutan fokus mengikuti visual. `:focus-visible` pada semua elemen interaktif, kontras ≥ 3:1.
- Pesan baru diumumkan lewat region `aria-live="polite"`. Galat memakai `role="alert"`.
- Tombol konfirmasi adalah `<button>` sungguhan; kutipan memakai pola `aria-expanded`.
- Tidak ada aksi yang hanya muncul saat hover. Semua dapat dipakai dengan keyboard dan sentuh.
- Tidak menyampaikan informasi hanya dengan warna.

---

## 13. Implementasi

### 13.1. `src/lib/styles/tokens.css` (satu-satunya tempat nilai mentah)

Contoh ini untuk **Tailwind v4** (CSS-first). Jika scaffold memakai Tailwind v3, petakan token yang sama ke `theme.extend` di `tailwind.config.js` memakai `var(--color-…)`.

```css
/* KnowDesk · design tokens v1 · tema: Arsip Pinus
 * genre: utilitarian app (turunan aturan Hallmark) · paper hue 100 · accent hue 160 · light only
 * Satu-satunya berkas yang boleh memuat warna/font mentah.
 */
@theme static {
  --color-*: initial;
  --font-*: initial;
  --radius-*: initial;
  --shadow-*: initial;
  --ease-*: initial;
  --text-*: initial;

  --color-paper:         oklch(97.5% 0.010 100);
  --color-paper-2:       oklch(94.5% 0.013 100);
  --color-surface:       oklch(99%   0.006 100);
  --color-rule:          oklch(87%   0.012 100);
  --color-rule-strong:   oklch(76%   0.014 100);
  --color-muted:         oklch(46%   0.012 100);
  --color-ink:           oklch(21%   0.012 100);

  --color-accent:        oklch(44%   0.105 160);
  --color-accent-hover:  oklch(38%   0.105 160);
  --color-accent-soft:   oklch(93.5% 0.030 160);
  --color-on-accent:     oklch(97.5% 0.010 100);
  --color-focus:         oklch(50%   0.140 160);

  --color-warn:          oklch(46%   0.110 70);
  --color-warn-soft:     oklch(94.5% 0.050 85);
  --color-danger:        oklch(48%   0.160 27);
  --color-danger-soft:   oklch(95%   0.030 27);

  --font-display: "Schibsted Grotesk Variable", ui-sans-serif, system-ui, sans-serif;
  --font-body:    "Onest Variable", ui-sans-serif, system-ui, sans-serif;
  --font-mono:    "Spline Sans Mono Variable", ui-monospace, monospace;

  --radius-sm: 4px;
  --radius-md: 8px;

  --shadow-pop: 0 4px 12px oklch(21% 0.012 100 / 0.14);

  --ease-out:    cubic-bezier(0.22, 1, 0.36, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);

  --text-sm:   0.875rem;  --text-sm--line-height:   1.5;
  --text-base: 1rem;      --text-base--line-height: 1.6;
  --text-md:   1.25rem;   --text-md--line-height:   1.4;
  --text-lg:   1.5625rem; --text-lg--line-height:   1.25;
  --text-xl:   1.9531rem; --text-xl--line-height:   1.15;
}

:root {
  color-scheme: light;

  --space-2xs: 4px;  --space-xs: 8px;   --space-sm: 12px; --space-md: 16px;
  --space-lg: 24px;  --space-xl: 32px;  --space-2xl: 48px; --space-3xl: 64px;

  --dur-fast: 100ms; --dur-short: 160ms; --dur-med: 240ms;

  --measure: 65ch;
  --chat-max: 46rem;
  --panel-w: 20rem;
  --header-h: 3.5rem;

  --z-base: 0; --z-sticky: 10; --z-popover: 20; --z-toast: 30;
}
```

> `--shadow-pop` memuat kanal alfa karena ia bayangan (modifier), bukan warna palet. Itu satu-satunya pengecualian alfa.

### 13.2. `src/app.css`

```css
/* KnowDesk design system v1 · tema Arsip Pinus · stamp: jangan hapus baris ini */
@import 'tailwindcss';
@import './lib/styles/tokens.css';
@import '@fontsource-variable/schibsted-grotesk';
@import '@fontsource-variable/onest';
@import '@fontsource-variable/spline-sans-mono';

html, body { overflow-x: clip; }

body {
  background: var(--color-paper);
  color: var(--color-ink);
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: 1.6;
  font-weight: 400;
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3 {
  font-family: var(--font-display);
  font-style: normal;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
  overflow-wrap: anywhere;
  min-width: 0;
}

:where(button, a, input, textarea, summary):focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
  transition: none;
}

.num { font-variant-numeric: tabular-nums; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```

Urutan `@import` (Tailwind → tokens → font) harus berada di paling atas file sebelum aturan lain.

### 13.3. Contoh komponen dengan 8 state: `Button.svelte` (Svelte 5)

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  type Props = {
    variant?: 'primary' | 'secondary' | 'ghost';
    state?: 'idle' | 'loading' | 'error' | 'success';
    disabled?: boolean;
    type?: 'button' | 'submit';
    onclick?: (e: MouseEvent) => void;
    children: Snippet;
  };

  let { variant = 'primary', state = 'idle', disabled = false, type = 'button', onclick, children }: Props = $props();
</script>

<button
  class="btn"
  data-variant={variant}
  data-state={state}
  {type}
  disabled={disabled || state === 'loading'}
  aria-busy={state === 'loading'}
  {onclick}
>
  {@render children()}
</button>

<style>
  .btn {
    min-height: 2.5rem;
    padding: 0 var(--space-md);
    border-radius: var(--radius-md);
    border: 1px solid transparent;
    font: 500 var(--text-base) / 1 var(--font-body);
    white-space: nowrap;
    cursor: pointer;
    transition:
      background-color var(--dur-fast) var(--ease-out),
      border-color var(--dur-fast) var(--ease-out),
      color var(--dur-fast) var(--ease-out),
      transform var(--dur-fast) var(--ease-out);
  }
  @media (pointer: coarse) { .btn { min-height: 2.75rem; } }

  /* varian */
  .btn[data-variant='primary']   { background: var(--color-accent); color: var(--color-on-accent); }
  .btn[data-variant='secondary'] { background: var(--color-surface); color: var(--color-ink); border-color: var(--color-rule-strong); }
  .btn[data-variant='ghost']     { background: transparent; color: var(--color-accent); padding: 0 var(--space-xs); }

  /* hover (kelas .is-hover dipakai galeri /design untuk memaksa state) */
  .btn[data-variant='primary']:hover,   .btn[data-variant='primary'].is-hover   { background: var(--color-accent-hover); }
  .btn[data-variant='secondary']:hover, .btn[data-variant='secondary'].is-hover { border-color: var(--color-ink); }
  .btn[data-variant='ghost']:hover,     .btn[data-variant='ghost'].is-hover     { text-decoration: underline; }

  /* active */
  .btn:active, .btn.is-active { transform: translateY(1px); }

  /* focus-visible: gaya global di app.css; kelas .is-focus untuk galeri */
  .btn.is-focus { outline: 2px solid var(--color-focus); outline-offset: 2px; }

  /* disabled */
  .btn:disabled { background: var(--color-paper-2); color: var(--color-muted); border-color: var(--color-rule); cursor: not-allowed; }

  /* loading */
  .btn[data-state='loading'] { cursor: progress; }

  /* error */
  .btn[data-state='error'] { background: var(--color-danger-soft); color: var(--color-danger); border-color: var(--color-danger); }

  /* success */
  .btn[data-state='success'] { background: var(--color-accent-soft); color: var(--color-accent); border-color: var(--color-accent); }
</style>
```

Pada Svelte 4, gunakan `export let` dan `<slot />` dengan CSS yang sama.

### 13.4. Gerbang otomatis: `frontend/scripts/check-design.mjs`

Tambahkan di `package.json`: `"lint:design": "node scripts/check-design.mjs"`. Skrip memeriksa `src/` dan gagal (exit 1) bila ada pelanggaran.

```js
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, extname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const SRC = fileURLToPath(new URL('../src', import.meta.url));
const EXT = new Set(['.svelte', '.ts', '.css', '.html']);

const RULES = [
  { id: 'raw-color', skipTokens: true, msg: 'Warna mentah di luar tokens.css',
    re: /#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(|\boklch\(/g },
  { id: 'tailwind-default-palette', msg: 'Kelas warna bawaan Tailwind dilarang',
    re: /\b(?:bg|text|border|ring|fill|stroke|from|to|via)-(?:white|black|(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3})\b/g },
  { id: 'banned-font', msg: 'Font terlarang',
    re: /\b(?:Inter|Roboto|Open Sans|Lato|Poppins|Montserrat|Raleway|Work Sans|DM Sans|Nunito|Arial|Helvetica)\b/g },
  { id: 'transition-all', msg: 'transition-all dilarang', re: /transition-all|transition:\s*all\b/g },
  { id: 'gradient', msg: 'Gradien dilarang', re: /linear-gradient|radial-gradient|conic-gradient|bg-gradient-|bg-clip-text|background-clip:\s*text/g },
  { id: 'hover-scale', msg: 'hover:scale dilarang', re: /hover:scale-/g },
  { id: 'viewport-hero', msg: 'Hero 100vh / 100vw dilarang', re: /min-h-screen|min-height:\s*100d?vh|\b100vw\b/g },
  { id: 'emoji-icon', msg: 'Emoji/simbol sebagai ikon dilarang (pakai Lucide)',
    re: /[\u{1F300}-\u{1FAFF}\u2600-\u27BF\u2B50]/gu },
  { id: 'dark-mode', msg: 'Tema gelap tidak dipakai',
    re: /\bdark:|prefers-color-scheme:\s*dark/g },
  { id: 'side-stripe', msg: 'Garis tebal satu sisi dilarang',
    re: /\bborder-l-[2-9]\b|border-left:\s*[2-9]px/g },
  { id: 'italic-heading', msg: 'Judul tidak boleh italic', re: /<h[1-3][^>]*\bitalic\b/g },
  { id: 'z-index', msg: 'z-index bilangan besar dilarang', re: /z-index:\s*\d{3,}|z-\[\d{3,}\]/g },
  { id: 'html-raw', msg: '{@html} dilarang pada konten pesan', re: /\{@html\b/g },
  { id: 'straight-ellipsis', msg: 'Gunakan … bukan ... pada teks UI', re: />[^<{]*\.\.\.[^<{]*</g },
];

function* walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const s = statSync(p);
    if (s.isDirectory()) yield* walk(p);
    else if (EXT.has(extname(p))) yield p;
  }
}

let violations = 0;
for (const file of walk(SRC)) {
  const isTokens = basename(file) === 'tokens.css';
  const lines = readFileSync(file, 'utf8').split(/\r?\n/);
  lines.forEach((line, i) => {
    for (const r of RULES) {
      if (r.skipTokens && isTokens) continue;
      r.re.lastIndex = 0;
      if (r.re.test(line)) {
        violations++;
        console.error(`${file}:${i + 1}  [${r.id}] ${r.msg}\n    ${line.trim()}`);
      }
    }
  });
}

if (violations) {
  console.error(`\n${violations} pelanggaran desain.`);
  process.exit(1);
}
console.log('lint:design bersih.');
```

Catatan: aturan `raw-color` mengecualikan `tokens.css`; `--shadow-pop` ada di sana. Skrip ini heuristik, bukan pengganti tinjauan mata. Jika menolak pola yang sah, ubah pola di skrip dan catat alasannya, jangan menonaktifkan aturan.

### 13.5. Galeri state (dev-only)

Buat rute `src/routes/design/+page.svelte` yang menampilkan **setiap komponen dalam seluruh state** secara bertumpuk dan berlabel (memakai kelas `.is-hover`, `.is-focus`, `.is-active`). Rute ini dikecualikan dari build produksi (mis. `export const prerender = false` dan dicek `import.meta.env.DEV`). Gunanya: tinjauan visual cepat dan bahan tangkapan layar untuk dokumentasi.

---

## 14. Tinjauan mandiri sebelum UI dinyatakan selesai

Nilai 1–5 pada enam sumbu; nilai < 3 pada sumbu mana pun berarti revisi (diadaptasi dari "pre-emit self-critique" Hallmark). Catat skor di PR atau `catatan-proses/`.

| Sumbu | Pertanyaan |
|---|---|
| Filosofi | Apakah tampilan konsisten dengan "Arsip Pinus, utilitarian, tenang"? |
| Hierarki | Dalam lima detik, apakah jelas apa langkah sekarang dan apa aksinya? |
| Eksekusi | Semua state lengkap? Lulus `lint:design`? Benar di 320–1280 px? |
| Kekhususan | Apakah ada elemen yang bisa ditempel ke produk lain tanpa diubah? (Jika ya, itu generik.) |
| Menahan diri | Aksen ≤ 3%? Tidak ada dekorasi tanpa fungsi? Gerak minimal? |
| Variasi | Apakah slip langkah, catatan kaki sumber, dan formulir tiket masih terasa sebagai tiga gerakan yang berbeda? |

**Checklist cepat:**
- [ ] Tidak ada nilai warna/font di luar `tokens.css`
- [ ] Hanya tiga keluarga font; mono hanya untuk `KB-…` dan `TK-…`
- [ ] Tidak ada emoji; semua ikon Lucide
- [ ] Tidak ada gradien, bayangan kartu, pil, garis tebal satu sisi, atau italic judul
- [ ] Pengungkapan AI terlihat di bawah composer
- [ ] Teks UI: kutip lengkung, `…`, `—`, tidak ada tombol dua baris
- [ ] `lint:design` bersih; fokus keyboard terlihat; `prefers-reduced-motion` ditangani
- [ ] Tidak ada angka atau klaim buatan di UI
