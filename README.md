# KnowDesk AI — Asisten Bantuan Mandiri Service Desk IT

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SvelteKit](https://img.shields.io/badge/SvelteKit-Svelte_5-FF3E00?style=flat-square&logo=svelte&logoColor=white)](https://svelte.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter_API-6366F1?style=flat-square)](https://openrouter.ai/)
[![Architecture](https://img.shields.io/badge/Architecture-Deterministic--First_RAG-success?style=flat-square)](#arsitektur-sistem)
[![Academic Scope](https://img.shields.io/badge/Academic_Scope-K%20%3D%203-blueviolet?style=flat-square)](#konteks-akademik-dan-lingkup-k--3)

> **KnowDesk AI** adalah sistem asisten *self-service IT Service Desk* berbasis **AI Agentik** dan **Grounded Hybrid RAG** yang dirancang untuk memandu staf kantor non-teknis menyelesaikan insiden IT minor secara mandiri, aman, dan bertahap tanpa membebani teknisi helpdesk.

---

## 📌 Daftar Isi

1. [Ringkasan Eksekutif](#-ringkasan-eksekutif)
2. [Konteks Akademik dan Lingkup K = 3](#-konteks-akademik-dan-lingkup-k--3)
3. [Mengapa AI Generatif (Bukan Rule-Based Biasa)](#-mengapa-ai-generatif-bukan-rule-based-biasa)
4. [Arsitektur Sistem & Alur Data](#-arsitektur-sistem--alur-data)
5. [Prinsip Desain & 5 Lapis Pertahanan (Guardrails)](#-prinsip-desain--5-lapis-pertahanan-guardrails)
6. [Tech Stack](#-tech-stack)
7. [Struktur Direktori Repositori](#-struktur-direktori-repositori)
8. [Panduan Instalasi & Menjalankan Sistem](#-panduan-instalasi--menjalankan-sistem)
9. [Konfigurasi Lingkungan (`.env`)](#-konfigurasi-lingkungan-env)
10. [Spesifikasi API & Kontrak Data](#-spesifikasi-api--kontrak-data)
11. [Knowledge Base & Pipeline Ingestion](#-knowledge-base--pipeline-ingestion)
12. [Pengujian, Evaluasi, dan Kalibrasi](#-pengujian-evaluasi-dan-kalibrasi)
13. [Aturan Rekayasa & Keputusan Kanonik (R1–R18 & K1–K19)](#-aturan-rekayasa--keputusan-kanonik-r1r18--k1k19)
14. [Etika, Keamanan Data, dan Batasan Sistem](#-etika-keamanan-data-dan-batasan-sistem)

---

## 🚀 Ringkasan Eksekutif

KnowDesk AI **bukanlah chatbot pencari artikel umum** atau tiruan ChatGPT. Sistem ini beroperasi sebagai **pemandu pemecahan masalah bertahap (*interactive troubleshooter*)**:

1. **Mengklarifikasi Gejala Ambigu:** Jika pengguna melapor *"komputer saya rusak"* atau *"internet tidak bisa"*, agen tidak langsung menebak atau mencari acak, melainkan mengajukan klarifikasi singkat (maksimum 2 kali per sesi).
2. **Pencarian Hibrida Deterministik:** Menggabungkan *lexical search* (BM25) dan *semantic search* (Cosine similarity dari embedding vektor) yang digabung dengan *Reciprocal Rank Fusion (RRF)*.
3. **Gerbang Kepastian Berbasis Ambang (*Deterministic Gatekeeper*):** Kode memverifikasi nilai cosine similarity top-1 terhadap ambang batas minimal (`RAG_MIN_COSINE`). Bila tidak relevan, sistem jujur menyatakan *"panduan tidak ditemukan"* dan tidak berhalusinasi dari pengetahuan umum model.
4. **Penyampaian Bertahap & Human-in-the-Loop:** Solusi disajikan **satu langkah per giliran pesan** dengan kutipan persis (*exact substring quote*) dari SOP resmi. Sistem menunggu konfirmasi pengguna (*"Masalah teratasi"* vs *"Masih bermasalah"*).
5. **Eskalasi Terkendali Satu Jalur:** Bila seluruh langkah habis (maksimum 4 langkah) atau solusi gagal, agen menyusun draf tiket IT. Tiket **hanya sah terkirim** setelah dikonfirmasi pengguna melalui endpoint eksplisit (`/api/ticket/confirm`).

---

## 🎓 Konteks Akademik dan Lingkup K = 3

Proyek ini dibangun untuk mata kuliah **Kapita Selekta: AI Engineering (Ganjil 2026/2027)** dengan kode peserta **K = 3**. Lingkup kuantitatif wajib yang diturunkan:

| Unsur Lingkup | Rumus Acuan | Target Wajib (K = 3) | Realisasi Implementasi |
|---|---|---|---|
| **Dokumen Rujukan KB** | `5 + (K mod 4)` | **8 dokumen** | 8 dokumen markdown sintetis kanonik (`KB-001` s/d `KB-008`) |
| **Kasus Uji Evaluasi** | `12 + (K mod 6)` | **15 kasus** | 15 kasus uji kanonik (`set-uji/15_kasus_uji.json`) |
| **Tool Wajib Agen** | `2 + (K mod 2)` | **3 tool** | `search_kb`, `get_article`, `draft_ticket` |
| **Mode Keluaran** | `K ganjil` | **1 mode standar** | Teks polos terstruktur + verifikasi sumber sitasi |

---

## 💡 Mengapa AI Generatif (Bukan Rule-Based Biasa)

| Kebutuhan Masalah | Solusi Konvensional (Formulir/Pencarian Kata Kunci) | Keunggulan KnowDesk AI (Generative AI + Agentik) |
|---|---|---|
| **Ambiguitas Bahasa Alami** | Gagal jika kata kunci tidak cocok persis (*"laptop tidak bisa internetan"* vs *"troubleshoot wifi"*). | Memahami maksud pengguna, meminta klarifikasi kontekstual, dan memetakan ke dokumen SOP yang tepat. |
| **Panduan Langkah demi Langkah** | Pengguna disodori dokumen PDF/wiki panjang yang malas dibaca staf kantor non-teknis. | Mengekstraksi dan menyajikan satu langkah terpandu per waktu dalam bahasa Indonesia sederhana tanpa jargon rumit. |
| **Penentuan Eskalasi Masalah** | Rule-based kaku sering salah kategori atau langsung membuat tiket duplikat. | Merangkum seluruh jejak interaksi dan langkah yang sudah gagal dicoba ke dalam ringkasan draf tiket terstruktur. |

---

## 🏛️ Arsitektur Sistem & Alur Data

KnowDesk AI mengadopsi arsitektur **3-Tier Client-Server** dengan pemisahan tegas antara antarmuka, orkestrasi logika, dan persistensi data.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PENGGUNA (Web Browser)                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST / JSON
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (SvelteKit + TypeScript)                  │
│                                                                        │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐   │
│   │  ChatBox     │   │  StepGuide   │   │  TicketModal             │   │
│   │  (Percakapan)│   │  (Indikator) │   │  (Konfirmasi Eskalasi)   │   │
│   └──────────────┘   └──────────────┘   └──────────────────────────┘   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ /api/chat & /api/ticket/confirm
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      BACKEND (Python + FastAPI)                        │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Lapis 1: Input Guardrail (Sanitasi, batas 1000 char, injeksi)     │  │
│  └────────────────────────────────┬─────────────────────────────────┘  │
│                                   ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ AGENT ORCHESTRATOR (Native Loop: Nalar → Tindak → Amati → Nilai) │  │
│  │ - Tanpa LangChain/LangGraph (Arsitektur minimalis & terkendali)  │  │
│  │ - Session Manager & State Machine (MySQL Persistence)            │  │
│  │ - Execution Limit Guard (Maks 4 langkah, maks 2 klarifikasi)     │  │
│  └───────┬────────────────────────┬─────────────────────────┬───────┘  │
│          │                        │                         │          │
│          ▼                        ▼                         ▼          │
│  ┌───────────────┐       ┌─────────────────┐       ┌────────────────┐  │
│  │ `search_kb`   │       │ `get_article`   │       │ `draft_ticket` │  │
│  │ Hybrid Search │       │ Ambil konten    │       │ Buat tiket     │  │
│  │ BM25 + Cosine │       │ langkah aktif   │       │ status 'draft' │  │
│  └───────┬───────┘       └─────────────────┘       └────────────────┘  │
│          │                                                             │
│          ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ RAG PIPELINE (Gerbang Deterministik Top-1 Cosine >= Ambang)      │  │
│  └────────────────────────────────┬─────────────────────────────────┘  │
│                                   ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Lapis 4: Output Guardrail (Skema JSON, Verifikasi Substring)      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────┬────────────────────────┘
                            │                   │
           ┌────────────────┴────────┐ ┌────────┴──────────────┐
           ▼                         ▼ ▼                       ▼
┌─────────────────────┐    ┌────────────────────┐    ┌───────────────────┐
│     MySQL 8 DB      │    │  OpenRouter API    │    │  Audit & Log      │
│ · articles & chunks │    │ · Chat LLM         │    │ · agent_traces    │
│ · sessions & tickets│    │ · Text Embedding   │    │ · pricing.json    │
└─────────────────────┘    └────────────────────┘    └───────────────────┘
```

### Siklus Agen (Agentic Loop)
Agen dieksekusi secara manual tanpa pustaka *black-box*:
1. **NALAR (Reason):** LLM mengevaluasi status sesi dan pesan pengguna di dalam pembungkus XML delimiter yang aman (`<konteks_kb>`, `<pesan_pengguna>`).
2. **TINDAK (Act):** LLM memanggil function call resmi (`search_kb`, `get_article`, `draft_ticket`) yang wewenangnya divalidasi oleh kode.
3. **AMATI (Observe):** Kode mengeksekusi tool dan mengembalikan data terstruktur ke model.
4. **NILAI (Evaluate):** Kode memastikan jawaban lolos *Output Guard* sebelum dikembalikan ke antarmuka pengguna.

---

## 🛡️ Prinsip Desain & 5 Lapis Pertahanan (Guardrails)

| Lapis Pertahanan | Mekanisme & Penegakan Kode |
|---|---|
| **Lapis 1: Input Guard** | Validasi masukan pengguna maksimum 1000 karakter, sanitasi tag berbahaya, dan deteksi dini pola serangan *prompt injection*. |
| **Lapis 2: System Prompt & Boundary** | Prompt sistem terversi (`v1.md`) menggunakan pemisah data tegas (`<konteks_kb>`, `<pesan_pengguna>`). Tag penutup di-escape untuk mencegah manipulasi konteks. |
| **Lapis 3: Hak Akses Basis Data** | Pemisahan pengguna database: `knowdesk_ingest` (akses tulis artikel & chunk) vs `knowdesk_app` (hanya baca artikel, tanpa hak `DROP` atau `ALTER`). |
| **Lapis 4: Output Guard & Grounding** | Verifikasi kepatuhan skema JSON, memastikan `article_id` cocok dengan sesi, dan **memvalidasi kutipan teks adalah substring asli** dari dokumen rujukan. |
| **Lapis 5: Pembatas Eksekusi & Biaya** | Pembatasan sesi: maks 4 langkah solusi, maks 2 klarifikasi, batas pemanggilan LLM per giliran, serta pencatatan token aktual per permintaan. |

---

## 💻 Tech Stack

### Backend
- **Bahasa:** Python 3.11+
- **Framework Web:** FastAPI (asynchronous ASGI) & Uvicorn
- **Validasi Data:** Pydantic v2 & `pydantic-settings`
- **Konektor Database:** `aiomysql` (Async connection pooling tanpa ORM berat)
- **Algoritma RAG:** `rank-bm25` (BM25Okapi) + NumPy (Cosine Similarity) + Reciprocal Rank Fusion (RRF)
- **HTTP Client:** `httpx` (Asynchronous HTTP)
- **Pengujian & Linting:** `pytest`, `pytest-asyncio`, `ruff`

### Frontend
- **Framework:** SvelteKit (Svelte 5 runes mode)
- **Bahasa:** TypeScript
- **Styling:** Tailwind CSS v4
- **Komponen Ikon:** `lucide-svelte`
- **Tipografi:** `@fontsource-variable/onest`, `@fontsource-variable/schibsted-grotesk`

### Basis Data & Eksternal
- **RDBMS:** MySQL 8 (Engine: InnoDB, Charset: `utf8mb4_unicode_ci`)
- **Penyedia Model AI:** OpenRouter API (Chat Completion + Embeddings)

---

## 📂 Struktur Direktori Repositori

```text
KnowDesk AI/
├── .env.example                 # Template konfigurasi environment (R2)
├── README.md                    # Dokumentasi utama proyek
├── Agent Guide/                 # Dokumen panduan spesifikasi dan desain
│   ├── PRD.md                   # Product Requirements Document
│   ├── agents.md                # Panduan kanonik coding agent & aturan keras
│   ├── architecture.md          # Dokumen arsitektur teknis lengkap
│   └── designsystem.md          # Standar desain antarmuka & styling UI
├── AI Engineering Guide/        # Modul kuliah & panduan akademik
├── knowledge_base/              # 8 Dokumen SOP IT sintetis kanonik (Markdown + Frontmatter)
│   ├── KB-001-troubleshoot-wifi.md
│   ├── KB-002-reset-password-email.md
│   ├── KB-003-konfigurasi-vpn.md
│   ├── KB-004-printer-jaringan.md
│   ├── KB-005-teams-outlook.md
│   ├── KB-006-akses-shared-drive.md
│   ├── KB-007-keamanan-akun-2fa.md
│   └── KB-008-troubleshoot-erp.md
├── set-uji/                     # Dataset evaluasi sistem
│   ├── 15_kasus_uji.json        # 15 kasus uji kanonik (dibekukan dengan testset-v1)
│   └── dev_set.json             # 20 dataset tuning ambang batas RAG
├── bukti/                       # Bukti eksekusi nyata, log, & hasil evaluasi
│   ├── kalibrasi-ambang-devset.json
│   └── smoke-test-fondasi.json
├── backend/                     # Layanan Backend FastAPI
│   ├── requirements.txt         # Dependensi Python
│   ├── app/
│   │   ├── main.py              # Entry point aplikasi FastAPI & konfigurasi CORS
│   │   ├── config.py            # Pembaca konfigurasi .env (Pydantic Settings)
│   │   ├── db.py                # Wrapper async pool MySQL & operasi database
│   │   ├── agent/               # Orkestrator agen manual (NALAR-TINDAK-AMATI-NILAI)
│   │   ├── guardrails/          # Lapis 1 (Input Guard) & Lapis 4 (Output Guard)
│   │   ├── llm/                 # Klien OpenRouter API & pencatatan token usage
│   │   ├── rag/                 # Chunker deterministik, Embedder, Retriever & RRF
│   │   ├── routes/              # Endpoint REST API (/chat, /ticket/confirm)
│   │   └── schemas/             # Kontrak data Pydantic (contracts.py, state.py)
│   ├── config/                  # Tabel tarif harga model (pricing.json)
│   ├── instruksi/               # Prompt sistem terversi (v1.md, CATATAN.md)
│   ├── migrations/              # Berkas SQL DDL & manajemen hak pengguna
│   │   ├── 001_initial.sql      # Skema tabel (articles, chunks, sessions, tickets, traces)
│   │   └── 002_users.sql        # Hak akses least privilege (knowdesk_app & knowdesk_ingest)
│   ├── scripts/                 # Skrip CLI (migrasi, ingestion KB, kalibrasi ambang)
│   └── tests/                   # Rangkaian pengujian otomatis pytest & smoke tests
└── frontend/                    # Aplikasi Antarmuka SvelteKit
    ├── package.json             # Dependensi npm & skrip frontend
    ├── vite.config.ts           # Konfigurasi Vite & SvelteKit
    ├── openapi.json             # Skema OpenAPI sinkron dari backend
    └── src/
        ├── app.html             # Shell HTML utama
        ├── lib/
        │   ├── components/      # Komponen UI (ChatBox, StepGuide, TicketModal)
        │   ├── stores/          # State manajemen percakapan klien (chat.ts)
        │   ├── styles/          # Konfigurasi tema warna & desain token
        │   └── types/           # Deklarasi tipe TypeScript
        └── routes/
            ├── +layout.svelte   # Layout global aplikasi
            └── +page.svelte     # Halaman utama chat interaktif
```

---

## ⚡ Panduan Instalasi & Menjalankan Sistem

### 1. Prasyarat Sistem
- **Python:** Versi 3.11 atau lebih baru
- **Node.js:** Versi 20.x atau lebih baru (disertai `npm`)
- **MySQL Server:** Versi 8.0+ aktif pada port 3306
- **Kunci API OpenRouter:** Akun aktif di [OpenRouter](https://openrouter.ai/)

### 2. Kloning & Pengaturan Lingkungan
Salin berkas konfigurasi `.env.example` menjadi `.env` pada root direktori:

```bash
# Salin konfigurasi
cp .env.example .env
```

Buka berkas `.env` dan lengkapi nilai kredensial:
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
CHAT_MODEL=meta-llama/llama-3.1-8b-instruct
EMBEDDING_MODEL=openai/text-embedding-3-small
MYSQL_PASSWORD=password_mysql_anda
```

### 3. Setup Basis Data MySQL
Jalankan inisialisasi basis data dan migrasi skema tabel:

```bash
# Masuk ke MySQL root untuk inisialisasi database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS knowdesk_ai DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Jalankan migrasi DDL dan pembuatan pengguna hak akses
mysql -u root -p knowdesk_ai < backend/migrations/001_initial.sql
mysql -u root -p knowdesk_ai < backend/migrations/002_users.sql
```
*(Atau gunakan runner otomatis Python: `python backend/scripts/run_migrations.py`)*

### 4. Setup Backend Python & Ingestion Knowledge Base

```bash
# 1. Buka folder backend dan buat virtual environment
cd backend
python -m venv venv

# Aktivasi venv:
# Di Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Di Linux/macOS:
source venv/bin/activate

# 2. Pasang dependensi
pip install -r requirements.txt

# 3. Jalankan Ingestion 8 Dokumen KB ke MySQL (Chunking & Vektor Embedding)
python scripts/ingest_kb.py

# 4. Jalankan Smoke Test Infrastruktur (Verifikasi Koneksi LLM & DB)
python tests/run_smoke_tests.py

# 5. Jalankan Server API FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API akan aktif pada: `http://localhost:8000` (Dokumentasi Swagger di `http://localhost:8000/docs`).

### 5. Setup Frontend SvelteKit

Buka terminal baru:

```bash
# Masuk ke direktori frontend
cd frontend

# Pasang dependensi npm
npm install

# Jalankan development server
npm run dev
```
Antarmuka web akan aktif pada: `http://localhost:5173`.

---

## ⚙️ Konfigurasi Lingkungan (`.env`)

Seluruh batasan sistem dikendalikan terpusat melalui variabel lingkungan (Aturan **R6**):

| Variabel | Tipe Data | Nilai Default | Keterangan |
|---|---|---|---|
| `OPENROUTER_API_KEY` | String | *Wajib diisi* | Kunci autentikasi OpenRouter API |
| `CHAT_MODEL` | String | *User defined* | Model LLM pembuat keputusan (misal: `meta-llama/llama-3.1-8b-instruct`) |
| `EMBEDDING_MODEL` | String | *User defined* | Model vektor embedding (misal: `openai/text-embedding-3-small`) |
| `LLM_TEMPERATURE` | Float | `0.2` | Temperatur generasi untuk respons konsisten & deterministik |
| `LLM_MAX_TOKENS` | Integer | `700` | Batas maksimum token keluaran agar JSON tidak terpotong (K18) |
| `AGENT_MAX_STEPS` | Integer | `4` | Batas langkah solusi maksimal per sesi sebelum eskalasi tiket |
| `AGENT_MAX_CLARIFICATIONS` | Integer | `2` | Batas pertanyaan klarifikasi maksimal per sesi |
| `RAG_MIN_COSINE` | Float | `0.25` – `0.35` | Ambang batas kemiripan kosinus minimal gerbang retrieval (K1) |
| `RAG_HIGH_COSINE` | Float | `0.40` – `0.55` | Ambang kemiripan kategori keyakinan "tinggi" |
| `RAG_RRF_K` | Integer | `60` | Konstanta peredam Reciprocal Rank Fusion |
| `INPUT_MAX_CHARS` | Integer | `1000` | Batas panjang masukan pengguna di Lapis 1 Input Guard |
| `MYSQL_HOST` | String | `localhost` | Host database MySQL |
| `MYSQL_USER` | String | `knowdesk_app` | Pengguna database aplikasi runtime (Least Privilege) |
| `MYSQL_DATABASE` | String | `knowdesk_ai` | Nama basis data operasional |

---

## 📡 Spesifikasi API & Kontrak Data

### 1. `POST /api/chat`
Endpoint utama untuk interaksi multi-turn antara pengguna dan agen.

**Request Payload:**
```json
{
  "session_id": "c1f7a0b2-3e4d-4e9b-b0b2-7a8b9c0d1e2f",
  "message": "Wi-Fi kantor saya tiba-tiba terputus dan tidak bisa konek",
  "confirmation": null
}
```
*Catatan:* `confirmation` dapat bernilai `null`, `"berhasil"`, `"belum"`, atau `"minta_tiket"` (K3).

**Response Body:**
```json
{
  "session_id": "c1f7a0b2-3e4d-4e9b-b0b2-7a8b9c0d1e2f",
  "tipe_respons": "langkah_solusi",
  "pesan": "Silakan lupakan jaringan Kantor-Utama di pengaturan Wi-Fi laptop Anda, lalu coba sambungkan kembali menggunakan akun domain Anda.",
  "sumber": [
    {
      "article_id": "KB-001",
      "section": "Bagian 2: Langkah Pemecahan Masalah",
      "judul": "Panduan Mengatasi Masalah Koneksi Wi-Fi Kantor",
      "kutipan": "Lupakan jaringan (Forget Network) 'Kantor-Utama' pada daftar Wi-Fi yang tersimpan"
    }
  ],
  "langkah_saat_ini": 1,
  "langkah_total_tersedia": 4,
  "keyakinan": "tinggi",
  "memerlukan_konfirmasi": true
}
```

### 2. `POST /api/ticket/confirm`
Satu-satunya jalur sah pengiriman tiket eskalasi ke teknisi (Aturan **R4 & K4**).

**Request Payload:**
```json
{
  "ticket_id": "TK-20261011-001",
  "action": "confirm"
}
```
*Opsi `action`:* `"confirm"` (kirim tiket & tutup sesi) atau `"cancel"` (batalkan tiket).

### 3. `GET /api/session/{session_id}`
Mengambil riwayat sesi, log percakapan, status aktif, dan data draf tiket terkait untuk audit.

### 4. `GET /api/health`
Pemeriksaan kesiapan operasional server backend dan koneksi pool basis data.

---

## 📚 Knowledge Base & Pipeline Ingestion

KnowDesk AI dilengkapi dengan **8 dokumen sintetis resmi** berformat Markdown dengan metadata YAML Front Matter (K19):

1. **`KB-001`**: *Panduan Mengatasi Masalah Koneksi Wi-Fi Kantor*
2. **`KB-002`**: *Prosedur Reset Kata Sandi Akun Email Kantor dan SSPR*
3. **`KB-003`**: *Panduan Konfigurasi dan Penanganan Masalah Koneksi VPN Kantor*
4. **`KB-004`**: *Penanganan Masalah Printer Jaringan Kantor*
5. **`KB-005`**: *Mengatasi Masalah Sinkronisasi Microsoft Outlook dan Microsoft Teams*
6. **`KB-006`**: *Akses dan Pemulihan Shared Drive Jaringan Perusahaan*
7. **`KB-007`**: *Autentikasi Dua Faktor (2FA) dan Keamanan Akun Pengguna*
8. **`KB-008`**: *Penanganan Masalah Login dan Akses Sistem ERP Internal*

### Karakteristik Pipeline Ingestion (`ingest_kb.py`)
- **Chunking Deterministik:** Dokumen dipotong per bagian (`## Bagian N`) dan langkah (`### Langkah N`). Satu langkah solusi di dokumen tepat dipetakan menjadi unit interaksi agen (K8).
- **Idempotensi Database:** Memakai pola `ON DUPLICATE KEY UPDATE` agar eksekusi ulang tidak menduplikasi data atau merusak referensi asing.
- **Isolasi Hak Akses:** Ingestion dijalankan di bawah akun khusus `knowdesk_ingest` sesuai aturan *Least Privilege* (§11).

---

## 🧪 Pengujian, Evaluasi, dan Kalibrasi

Proyek ini dibangun dengan standar pengujian ketat tanpa klaim tanpa bukti (Aturan **R9**):

### 1. Menjalankan Uji Otomatis (Pytest)
```bash
cd backend
pytest tests/ -v
```

Cakupan pengujian otomatis:
- `test_env_parity.py`: Memvalidasi keselarasan parameter di `.env.example` dan `config.py`.
- `test_chunker_deterministic.py`: Memverifikasi parser chunk dokumen menghasilkan output identik.
- `test_state_contracts.py`: Memastikan transisi state mesin sesi memenuhi kontrak Pydantic.
- `test_db_integration.py`: Pengujian transaksi basis data asinkron (CRUD sesi, tiket, jejak trace).
- `test_eval_set_valid.py`: Validasi integritas skema 15 kasus uji evaluasi.

### 2. Kalibrasi Ambang Retrieval Dev Set (`calibrate_threshold.py`)
Sesuai aturan **R10**, ambang batas retrieval `RAG_MIN_COSINE` tidak ditebak sembarangan, melainkan dikalibrasi pada `set-uji/dev_set.json` (20 kueri uji independen):
- Menemukan nilai batas optimal (hasil kalibrasi: `0.25` - `0.35`) yang menghasilkan **0 False Positive pada kueri out-of-scope**.
- Hasil kalibrasi dicatat secara transparan di `bukti/kalibrasi-ambang-devset.json`.

### 3. Smoke Test Infrastruktur & Audit Biaya Riil
```bash
python backend/tests/run_smoke_tests.py
```
Skrip menguji *live endpoint* OpenRouter chat, embedding, dan konektivitas MySQL, lalu menghitung biaya pemakaian aktual dari `pricing.json` dan menyimpannya di `bukti/smoke-test-fondasi.json` (Aturan **R7**).

---

## 📜 Aturan Rekayasa & Keputusan Kanonik (R1–R18 & K1–K19)

### Ringkasan Aturan Keras (Hard Rules)
- **R1:** Tidak ada data atau dokumen internal perusahaan nyata (100% sintetis, fiktif "PT Contoh Sejahtera").
- **R2:** `.env` tidak pernah di-commit ke Git; kredensial tidak pernah bocor ke log atau respons.
- **R3:** Batas kewenangan tool ditegakkan di level kode Python, bukan sekadar instruksi prompt.
- **R4:** Tiket hanya dapat terkirim melalui endpoint `POST /api/ticket/confirm`.
- **R5:** Larangan menjawab dari pengetahuan umum LLM; jika tidak lolos retrieval, kembalikan `tidak_ditemukan`.
- **R7:** Wajib mencatat token aktual dari atribut `usage` respons OpenRouter (tanpa estimasi palsu).
- **R8:** Prompt dipisahkan ke berkas `backend/instruksi/vN.md` (dilarang string panjang inline di Python).
- **R11:** Tanpa framework orkestrasi berat (tidak menggunakan LangChain/LangGraph).

### Koreksi Kanonik Penting
- **K1:** Ambang minimal diterapkan pada **skor Top-1 Cosine Similarity**, bukan pada skor RRF.
- **K2 & K8:** Satu langkah adalah satu heading `### Langkah N`. Langkah ke-N ditampilkan terlebih dahulu sebelum opsi eskalasi.
- **K3 & K4:** Makna status konfirmasi diseragamkan (`berhasil`, `belum`, `minta_tiket`) dengan satu rute konfirmasi tiket.
- **K10:** Output guard memverifikasi bahwa kutipan sumber yang dihasilkan LLM benar-benar merupakan **substring eksak** dari teks dokumen rujukan.
- **K17:** LLM hanya bertugas menghasilkan pesan dan kutipan; metadata teknis (`keyakinan`, `judul`, `langkah_total`) dihitung langsung oleh kode backend.

---

## ⚖️ Etika, Keamanan Data, dan Batasan Sistem

1. **Pernyataan Data Fiktif:**
   Seluruh data karyawan, domain (`example.com`), prosedur, dan dokumen rujukan dalam knowledge base adalah data sintetis fiktif. Tidak ada data rahasia dari pihak manapun yang digunakan.
2. **Transparansi Sistem AI:**
   Antarmuka web secara eksplisit menampilkan pengumuman bahwa seluruh respons disusun oleh asisten AI dan mungkin memerlukan konfirmasi teknisi IT manusia.
3. **Pemisahan Wewenang (Human Oversight):**
   Agen tidak memiliki wewenang untuk menutup tiket secara sepihak atau mengubah konfigurasi sistem pengguna; seluruh tindakan bersifat asistif dengan konfirmasi manusia di setiap langkah (*Human-in-the-Loop*).

---

<div align="center">
  <sub>Dibangun untuk Proyek Kapita Selekta: AI Engineering (Ganjil 2026/2027) · Kode Peserta K = 3</sub>
</div>
