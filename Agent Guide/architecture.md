# Architecture Document — KnowDesk AI

**Kapita Selekta: AI Engineering | Ganjil 2026/2027**
**Kode Peserta K = 3**

---

## Daftar Isi

1. [Gambaran Arsitektur](#1-gambaran-arsitektur)
2. [Diagram Arsitektur Sistem](#2-diagram-arsitektur-sistem)
3. [Komponen dan Tanggung Jawab](#3-komponen-dan-tanggung-jawab)
4. [Alur Data End-to-End](#4-alur-data-end-to-end)
5. [Frontend — Svelte + TypeScript](#5-frontend--svelte--typescript)
6. [Backend — Python + FastAPI](#6-backend--python--fastapi)
7. [Database — MySQL](#7-database--mysql)
8. [Pipeline RAG](#8-pipeline-rag)
9. [Agent Orchestrator](#9-agent-orchestrator)
10. [Tool Definitions](#10-tool-definitions)
11. [Integrasi OpenRouter API](#11-integrasi-openrouter-api)
12. [Guardrails Implementation](#12-guardrails-implementation)
13. [Struktur Direktori Proyek](#13-struktur-direktori-proyek)
14. [API Contract](#14-api-contract)
15. [Konfigurasi dan Environment](#15-konfigurasi-dan-environment)
16. [Strategi Chunking dan Indexing](#16-strategi-chunking-dan-indexing)
17. [State Management](#17-state-management)
18. [Observabilitas dan Logging](#18-observabilitas-dan-logging)
19. [Keputusan Arsitektur dan Pertukaran](#19-keputusan-arsitektur-dan-pertukaran)
20. [Deployment dan Development](#20-deployment-dan-development)

---

## 1. Gambaran Arsitektur

KnowDesk AI menggunakan arsitektur **client-server tiga lapis** dengan pemisahan tegas antara:

1. **Frontend (Svelte + TypeScript + Tailwind CSS)** — Antarmuka chat untuk pengguna
2. **Backend (Python + FastAPI)** — Orkestrasi agen, pipeline RAG, dan API
3. **Data (MySQL)** — Penyimpanan artikel, chunk, embedding, session state, dan tiket

**Prinsip arsitektur:**

| Prinsip | Implementasi |
|---|---|
| Deterministik di mana bisa | Retrieval (BM25 + cosine similarity) dihitung di Python, bukan oleh LLM |
| Model hanya untuk bahasa alami | LLM hanya dipanggil untuk: klarifikasi, penyusunan jawaban, keputusan eskalasi |
| Kewenangan ditegakkan di kode | Batas tool ada di endpoint API, bukan hanya di instruksi model |
| State di luar percakapan | Session state disimpan di MySQL, bukan di riwayat chat model |
| Hemat token | Konteks retrieval dibatasi 5 chunk; instruksi sistem dioptimalkan |

---

## 2. Diagram Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            PENGGUNA (Browser)                           │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ HTTP/WebSocket
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Svelte + TypeScript)                     │
│                                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │  ChatWindow  │  │ StepTracker  │  │ TicketForm  │  │  StatusBar   │  │
│  │  (percakapan │  │ (langkah     │  │ (draf tiket │  │ (indikator   │  │
│  │   real-time) │  │  saat ini)   │  │  + konfirm) │  │  proses)     │  │
│  └─────────────┘  └──────────────┘  └─────────────┘  └──────────────┘  │
│                                                                         │
│  Tailwind CSS · Dark Mode · Responsive                                  │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ REST API (JSON)
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      BACKEND (Python + FastAPI)                         │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                       API Layer (FastAPI)                          │ │
│  │  POST /chat · GET /session/{id} · POST /ticket/confirm            │ │
│  │  GET /articles · GET /health                                       │ │
│  └───────────────────────────┬────────────────────────────────────────┘ │
│                              │                                          │
│  ┌───────────────────────────▼────────────────────────────────────────┐ │
│  │                    LAPIS 1: Input Guardrails                       │ │
│  │  Validasi panjang · Sanitasi · Deteksi pola injection             │ │
│  └───────────────────────────┬────────────────────────────────────────┘ │
│                              │                                          │
│  ┌───────────────────────────▼────────────────────────────────────────┐ │
│  │                    AGENT ORCHESTRATOR                              │ │
│  │                                                                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │ │
│  │  │  NALAR   │→│  TINDAK  │→│  AMATI   │→│  NILAI            │  │ │
│  │  │ (LLM)   │  │ (Tool)   │  │ (Parse)  │  │ (selesai/lanjut) │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘  │ │
│  │                                                                    │ │
│  │  Session Manager · Step Counter · State Tracker                    │ │
│  └───────────────────────────┬────────────────────────────────────────┘ │
│                              │                                          │
│  ┌──────────┐  ┌──────────┐  │  ┌──────────────────────────────────┐   │
│  │search_kb │  │get_article│  │  │        draft_ticket              │   │
│  │(retrieval│  │(read-only│  │  │(draft-only, needs confirmation) │   │
│  │ hybrid)  │  │ published)│  │  └──────────────────────────────────┘   │
│  └─────┬────┘  └────┬─────┘  │                                          │
│        │            │        │                                          │
│  ┌─────▼────────────▼────────▼────────────────────────────────────────┐ │
│  │                    RAG PIPELINE                                    │ │
│  │                                                                    │ │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────────────────┐ │ │
│  │  │   BM25     │  │  Embedding │  │  Reciprocal Rank Fusion     │ │ │
│  │  │  (rank_bm25│  │  (cosine   │  │  (gabung skor, ambang 0.35)│ │ │
│  │  │   library) │  │  similarity)│  └──────────────────────────────┘ │ │
│  │  └────────────┘  └────────────┘                                    │ │
│  └───────────────────────────┬────────────────────────────────────────┘ │
│                              │                                          │
│  ┌───────────────────────────▼────────────────────────────────────────┐ │
│  │                   LAPIS 4: Output Guardrails                       │ │
│  │  Validasi JSON schema · Cek kutipan sumber · Retry jika gagal     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │    MySQL     │  │  OpenRouter  │  │   File       │
    │              │  │  API         │  │   System     │
    │ · articles   │  │              │  │              │
    │ · chunks     │  │ · Chat LLM   │  │ · logs/      │
    │ · embeddings │  │ · Embedding  │  │ · traces/    │
    │ · sessions   │  │   Model      │  │              │
    │ · tickets    │  │              │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 3. Komponen dan Tanggung Jawab

### 3.1. Frontend Layer

| Komponen | Tanggung Jawab | Teknologi |
|---|---|---|
| `ChatWindow` | Menampilkan percakapan, menerima input pengguna, render langkah-langkah solusi | Svelte component |
| `StepTracker` | Menampilkan progress langkah saat ini (1/4, 2/4, dst) | Svelte component |
| `TicketForm` | Menampilkan draf tiket, tombol konfirmasi/tolak | Svelte component |
| `StatusBar` | Indikator loading, status koneksi, info sesi | Svelte component |
| `ChatStore` | State management percakapan di client | Svelte store (writable) |

### 3.2. Backend Layer

| Komponen | Tanggung Jawab | File |
|---|---|---|
| `API Router` | Endpoint HTTP, validasi request, routing | `app/api/routes.py` |
| `Input Guard` | Validasi dan sanitasi input pengguna (Lapis 1) | `app/guardrails/input_guard.py` |
| `Agent Orchestrator` | Siklus nalar-tindak, manajemen state, kontrol langkah | `app/agent/orchestrator.py` |
| `RAG Pipeline` | Chunking, embedding, BM25, hybrid retrieval, RRF | `app/rag/pipeline.py` |
| `Tool Registry` | Definisi dan eksekusi tool | `app/tools/` |
| `LLM Client` | Komunikasi dengan OpenRouter API | `app/llm/client.py` |
| `Output Guard` | Validasi schema keluaran, retry logic (Lapis 4) | `app/guardrails/output_guard.py` |
| `Session Manager` | CRUD session state di MySQL | `app/session/manager.py` |

### 3.3. Data Layer

| Komponen | Tanggung Jawab | Penyimpanan |
|---|---|---|
| `Article Store` | CRUD artikel knowledge base | MySQL `articles` table |
| `Chunk Store` | Chunk + metadata + embedding vectors | MySQL `chunks` table |
| `Session Store` | State percakapan agentik | MySQL `sessions` table |
| `Ticket Store` | Draf dan tiket terkonfirmasi | MySQL `tickets` table |
| `Trace Logger` | Log langkah-langkah agen untuk diagnosis | File system `logs/traces/` |

---

## 4. Alur Data End-to-End

### 4.1. Alur Penyiapan (Sekali / Saat Dokumen Berubah)

```
Dokumen Markdown (8 file)
        │
        ▼
┌──────────────────┐
│  Chunking Engine │  Potong per subbab, overlap 50 kata
│  (Python script) │  Tambah metadata: article_id, section, title
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│  BM25  │ │ Embedding│  OpenRouter embedding API
│  Index │ │  Vectors │  Simpan ke MySQL (JSON column)
└────┬───┘ └────┬─────┘
     │          │
     ▼          ▼
┌──────────────────┐
│     MySQL        │
│  chunks table    │  chunk_id, article_id, content, section,
│                  │  bm25_tokens, embedding_vector, metadata
└──────────────────┘
```

### 4.2. Alur Menjawab (Setiap Pesan Pengguna)

```
Pesan pengguna
     │
     ▼
[Lapis 1: Input Guard]
     │ validasi panjang, sanitasi, deteksi injection
     ▼
[Session Manager] ── load/create session state dari MySQL
     │
     ▼
[Agent Orchestrator]
     │
     ├── Cek: apakah gejala sudah cukup spesifik?
     │   │
     │   ├── TIDAK → [LLM: generate pertanyaan klarifikasi]
     │   │           → return ke pengguna, tunggu respons
     │   │
     │   └── YA → [Tool: search_kb(query)]
     │             │
     │             ├── Hasil kosong (skor < 0.35)
     │             │   → [LLM: compose rejection message]
     │             │   → tawarkan buat tiket
     │             │
     │             └── Ada hasil (skor ≥ 0.35)
     │                 → [Tool: get_article(article_id)]
     │                 → [LLM: compose step-by-step from chunks]
     │                 → return langkah + kutipan + "Berhasil?"
     │
     ├── Cek: pengguna konfirmasi langkah berhasil?
     │   ├── YA & masalah selesai → session resolved
     │   ├── YA & belum selesai → lanjut langkah berikutnya
     │   └── TIDAK → lanjut langkah berikutnya
     │
     ├── Cek: batas 4 langkah tercapai?
     │   └── YA → [Tool: draft_ticket(...)]
     │            → tampilkan draf ke pengguna
     │            → tunggu konfirmasi
     │
     └── Update session state di MySQL
          │
          ▼
[Lapis 4: Output Guard]
     │ validasi JSON schema, cek kutipan sumber
     │ retry 1x jika gagal
     ▼
Response JSON ke Frontend
```

---

## 5. Frontend — Svelte + TypeScript

### 5.1. Struktur Komponen

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── ChatWindow.svelte        # Kontainer percakapan utama
│   │   │   ├── ChatMessage.svelte       # Satu bubble pesan (user/assistant)
│   │   │   ├── ChatInput.svelte         # Input field + send button
│   │   │   ├── StepTracker.svelte       # Progress langkah: ●●○○ (2/4)
│   │   │   ├── SourceCitation.svelte    # Kutipan sumber yang clickable
│   │   │   ├── TicketDraft.svelte       # Preview draf tiket + confirm/reject
│   │   │   ├── ClarificationPrompt.svelte # Pertanyaan klarifikasi dari sistem
│   │   │   ├── ConfirmationButton.svelte  # Tombol "Berhasil" / "Belum"
│   │   │   ├── StatusIndicator.svelte   # Loading, typing, error states
│   │   │   └── Header.svelte            # Branding, info session
│   │   ├── stores/
│   │   │   ├── chatStore.ts             # State percakapan: messages[], session
│   │   │   ├── sessionStore.ts          # Session ID, step count, status
│   │   │   └── uiStore.ts              # Theme, loading state, modals
│   │   ├── services/
│   │   │   └── api.ts                   # HTTP client ke backend
│   │   ├── types/
│   │   │   └── index.ts                 # TypeScript interfaces
│   │   └── utils/
│   │       └── formatters.ts            # Format pesan, tanggal, tiket
│   ├── routes/
│   │   └── +page.svelte                 # Halaman utama (single page)
│   ├── app.html                         # HTML template
│   └── app.css                          # Tailwind imports + custom styles
├── static/
│   └── favicon.svg
├── svelte.config.js
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── package.json
```

### 5.2. TypeScript Interfaces (Frontend)

```typescript
// types/index.ts

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: AssistantMetadata;
}

interface AssistantMetadata {
  tipe_respons: 'klarifikasi' | 'langkah_solusi' | 'tidak_ditemukan' | 'draf_tiket' | 'tiket_terkirim';
  langkah_saat_ini: number;
  langkah_total_tersedia: number;
  sumber: SourceCitation[];
  memerlukan_konfirmasi: boolean;
  keyakinan: 'tinggi' | 'sedang' | 'rendah' | 'tidak_dapat_ditentukan';
  draf_tiket?: DraftTicket;
}

interface SourceCitation {
  article_id: string;
  section: string;
  judul: string;
  kutipan: string;
}

interface DraftTicket {
  ticket_id: string;
  judul: string;
  deskripsi: string;
  langkah_dicoba: string[];
  prioritas: 'rendah' | 'sedang' | 'tinggi';
  kategori: 'jaringan' | 'email' | 'aplikasi' | 'perangkat' | 'lainnya';
}

interface SessionState {
  session_id: string;
  status: 'clarifying' | 'solving' | 'escalating' | 'resolved' | 'closed';
  langkah_saat_ini: number;
  langkah_maks: number;
}

interface ChatRequest {
  session_id?: string;
  message: string;
  confirmation?: 'berhasil' | 'belum' | 'konfirmasi_tiket' | 'tolak_tiket';
}

interface ChatResponse {
  session_id: string;
  message: ChatMessage;
  session_state: SessionState;
}
```

### 5.3. Komponen Kunci: ChatWindow

```
┌─────────────────────────────────────────┐
│  ┌─────────────────────────────────┐    │
│  │  Header                         │    │
│  │  KnowDesk AI · Session #abc123 │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  StepTracker                    │    │
│  │  Langkah 2 dari 4  ●●○○        │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  ChatMessage (user)             │    │
│  │  "Password email saya salah"    │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  ChatMessage (assistant)        │    │
│  │  Langkah 1: Buka portal...     │    │
│  │  ┌──────────────────────────┐   │    │
│  │  │ SourceCitation           │   │    │
│  │  │ 📄 KB-003, Bagian 2      │   │    │
│  │  └──────────────────────────┘   │    │
│  │  ┌──────────────────────────┐   │    │
│  │  │ ConfirmationButton       │   │    │
│  │  │ [✓ Berhasil] [✗ Belum]   │   │    │
│  │  └──────────────────────────┘   │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  ChatInput                      │    │
│  │  [Ketik masalah Anda...] [↑]    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## 6. Backend — Python + FastAPI

### 6.1. Struktur Direktori Backend

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                       # FastAPI app, CORS, startup events
│   ├── config.py                     # Settings from .env (pydantic-settings)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                 # Semua endpoint API
│   │   └── schemas.py                # Pydantic request/response models
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Siklus nalar-tindak utama
│   │   ├── prompts.py                # System prompt dan template
│   │   └── state.py                  # Session state dataclass
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── pipeline.py               # Orchestrate retrieval pipeline
│   │   ├── bm25.py                   # BM25 indexing dan scoring
│   │   ├── embedder.py               # Embedding via OpenRouter
│   │   ├── chunker.py                # Chunking engine (per subbab)
│   │   └── ranker.py                 # RRF fusion dan threshold filtering
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py               # Tool registry + definitions
│   │   ├── search_kb.py              # search_kb implementation
│   │   ├── get_article.py            # get_article implementation
│   │   └── draft_ticket.py           # draft_ticket implementation
│   │
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── input_guard.py            # Lapis 1: validasi input
│   │   └── output_guard.py           # Lapis 4: validasi output
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   └── client.py                 # OpenRouter API client
│   │
│   ├── session/
│   │   ├── __init__.py
│   │   └── manager.py                # Session CRUD di MySQL
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py             # MySQL connection pool (aiomysql)
│   │   ├── models.py                 # SQLAlchemy / raw SQL models
│   │   └── migrations/               # Schema migrations
│   │       └── 001_initial.sql
│   │
│   └── logging/
│       ├── __init__.py
│       └── tracer.py                 # Trace logger untuk langkah agen
│
├── scripts/
│   ├── ingest_documents.py           # Chunking + embedding + store ke MySQL
│   ├── seed_articles.py              # Load 8 artikel dummy ke database
│   └── run_test_suite.py             # Jalankan 15 kasus uji
│
├── knowledge_base/
│   ├── KB-001-troubleshoot-wifi.md
│   ├── KB-002-reset-password-email.md
│   ├── KB-003-konfigurasi-vpn.md
│   ├── KB-004-printer-jaringan.md
│   ├── KB-005-teams-outlook.md
│   ├── KB-006-akses-shared-drive.md
│   ├── KB-007-keamanan-akun-2fa.md
│   └── KB-008-troubleshoot-erp.md
│
├── tests/
│   ├── test_cases/
│   │   └── test_suite_15.json        # 15 kasus uji + jawaban acuan
│   ├── test_retrieval.py
│   ├── test_agent.py
│   ├── test_guardrails.py
│   └── test_tools.py
│
├── logs/
│   └── traces/                       # Trace langkah agen per session
│
├── .env.example                      # Template environment variables
├── .gitignore                        # .env, __pycache__, logs/
├── requirements.txt
└── README.md
```

### 6.2. Pydantic Schemas (Backend)

```python
# app/api/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., max_length=1000)
    confirmation: Optional[Literal[
        "berhasil", "belum", "konfirmasi_tiket", "tolak_tiket"
    ]] = None

class SourceCitation(BaseModel):
    article_id: str
    section: str
    judul: str
    kutipan: str

class DraftTicket(BaseModel):
    ticket_id: str
    judul: str
    deskripsi: str
    langkah_dicoba: list[str]
    prioritas: Literal["rendah", "sedang", "tinggi"]
    kategori: Literal["jaringan", "email", "aplikasi", "perangkat", "lainnya"]

class AssistantMessage(BaseModel):
    tipe_respons: Literal[
        "klarifikasi", "langkah_solusi", "tidak_ditemukan",
        "draf_tiket", "tiket_terkirim"
    ]
    pesan: str
    langkah_saat_ini: int = 0
    langkah_total_tersedia: int = 0
    sumber: list[SourceCitation] = []
    memerlukan_konfirmasi: bool = True
    keyakinan: Literal["tinggi", "sedang", "rendah", "tidak_dapat_ditentukan"]
    draf_tiket: Optional[DraftTicket] = None

class SessionState(BaseModel):
    session_id: str
    status: Literal[
        "clarifying", "solving", "escalating", "resolved", "closed"
    ]
    langkah_saat_ini: int
    langkah_maks: int = 4

class ChatResponse(BaseModel):
    session_id: str
    message: AssistantMessage
    session_state: SessionState
```

---

## 7. Database — MySQL

### 7.1. Entity-Relationship Diagram

```
┌────────────────┐       ┌────────────────────┐
│   articles     │       │      chunks        │
├────────────────┤       ├────────────────────┤
│ id (PK)        │───1:N─│ id (PK)            │
│ article_id     │       │ article_id (FK)    │
│ title          │       │ section_number     │
│ content        │       │ section_title      │
│ category       │       │ content            │
│ status         │       │ bm25_tokens (JSON) │
│ created_at     │       │ embedding (JSON)   │
│ updated_at     │       │ metadata (JSON)    │
└────────────────┘       └────────────────────┘

┌────────────────────┐       ┌────────────────────┐
│    sessions        │       │     tickets        │
├────────────────────┤       ├────────────────────┤
│ id (PK)            │       │ id (PK)            │
│ session_id (UQ)    │───1:N─│ session_id (FK)    │
│ status             │       │ ticket_id (UQ)     │
│ gejala_awal        │       │ judul              │
│ gejala_terklarifikasi│     │ deskripsi          │
│ langkah_saat_ini   │       │ langkah_dicoba (JSON)│
│ langkah_selesai (JSON)│    │ prioritas          │
│ artikel_dipakai (JSON)│    │ kategori           │
│ chunks_retrieved (JSON)│   │ status             │
│ conversation_history (JSON)││ confirmed_at      │
│ created_at         │       │ created_at         │
│ updated_at         │       └────────────────────┘
└────────────────────┘

┌────────────────────┐
│   agent_traces     │
├────────────────────┤
│ id (PK)            │
│ session_id (FK)    │
│ step_number        │
│ action_type        │
│ tool_called        │
│ tool_params (JSON) │
│ tool_result (JSON) │
│ reasoning          │
│ decision           │
│ tokens_used        │
│ created_at         │
└────────────────────┘
```

### 7.2. DDL — Schema SQL

```sql
-- 001_initial.sql

CREATE TABLE articles (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    article_id      VARCHAR(20) NOT NULL UNIQUE,
    title           VARCHAR(255) NOT NULL,
    content         LONGTEXT NOT NULL,
    category        ENUM('jaringan','email','aplikasi','perangkat','lainnya') NOT NULL,
    status          ENUM('draft','published','archived') NOT NULL DEFAULT 'published',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_status (status),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE chunks (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    article_id      VARCHAR(20) NOT NULL,
    section_number  INT NOT NULL,
    section_title   VARCHAR(255) NOT NULL,
    content         TEXT NOT NULL,
    bm25_tokens     JSON NOT NULL,
    embedding       JSON NOT NULL,            -- vector as JSON array of floats
    metadata        JSON DEFAULT NULL,

    FOREIGN KEY (article_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    INDEX idx_article (article_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sessions (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    session_id              VARCHAR(36) NOT NULL UNIQUE,
    status                  ENUM('clarifying','solving','escalating','resolved','closed')
                            NOT NULL DEFAULT 'clarifying',
    gejala_awal             TEXT DEFAULT NULL,
    gejala_terklarifikasi   TEXT DEFAULT NULL,
    langkah_saat_ini        INT NOT NULL DEFAULT 0,
    langkah_selesai         JSON DEFAULT NULL,
    artikel_dipakai         JSON DEFAULT NULL,
    chunks_retrieved        JSON DEFAULT NULL,
    conversation_history    JSON DEFAULT NULL,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tickets (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    session_id      VARCHAR(36) NOT NULL,
    ticket_id       VARCHAR(20) NOT NULL UNIQUE,
    judul           VARCHAR(255) NOT NULL,
    deskripsi       TEXT NOT NULL,
    langkah_dicoba  JSON NOT NULL,
    prioritas       ENUM('rendah','sedang','tinggi') NOT NULL DEFAULT 'sedang',
    kategori        ENUM('jaringan','email','aplikasi','perangkat','lainnya') NOT NULL,
    status          ENUM('draft','confirmed','cancelled') NOT NULL DEFAULT 'draft',
    confirmed_at    DATETIME DEFAULT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE agent_traces (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    session_id      VARCHAR(36) NOT NULL,
    step_number     INT NOT NULL,
    action_type     ENUM('nalar','tindak','amati','nilai') NOT NULL,
    tool_called     VARCHAR(50) DEFAULT NULL,
    tool_params     JSON DEFAULT NULL,
    tool_result     JSON DEFAULT NULL,
    reasoning       TEXT DEFAULT NULL,
    decision        VARCHAR(100) DEFAULT NULL,
    tokens_used     INT DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_step (session_id, step_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 7.3. Keputusan: Mengapa Embedding di JSON Column

| Alternatif | Kelebihan | Kekurangan | Keputusan |
|---|---|---|---|
| **Vector DB terpisah (Pinecone, Weaviate)** | Pencarian vektor cepat, fitur khusus | Infra tambahan, overkill untuk 8 dokumen ± 50 chunk | ❌ Ditolak |
| **MySQL JSON column + cosine di Python** | Sederhana, satu database, cukup untuk skala ini | Tidak skala ke ribuan dokumen | ✅ Dipilih |
| **pgvector (PostgreSQL)** | Native vector search | Ganti database engine, fitur belum perlu | ❌ Ditolak |

**Alasan:** Dengan ± 50 chunk dari 8 dokumen, menghitung cosine similarity di Python untuk semua chunk memakan waktu < 10ms. Menambah infrastruktur vector database untuk ini adalah over-engineering yang tidak memberikan manfaat, dan justru mempersulit deployment.

---

## 8. Pipeline RAG

### 8.1. Chunking Engine

```python
# Pseudocode: app/rag/chunker.py

def chunk_document(article: Article) -> list[Chunk]:
    """
    Memotong dokumen per subbab/bagian (bukan per karakter).
    Setiap chunk mempertahankan konteks satu prosedur utuh.

    Keputusan:
    - Per subbab, bukan per N karakter → karena SOP punya struktur
      alami per langkah/prosedur yang menjadi unit makna.
    - Overlap 50 kata → mencegah terpotongnya kalimat di batas subbab.
    - Metadata disematkan → article_id, section_number, section_title
      memungkinkan kutipan sumber yang presisi.
    """
    sections = split_by_headers(article.content)  # Split di ## headers
    chunks = []

    for i, section in enumerate(sections):
        chunk_content = section.text

        # Tambah overlap dari section sebelumnya (50 kata terakhir)
        if i > 0:
            overlap = get_last_n_words(sections[i-1].text, n=50)
            chunk_content = overlap + "\n" + chunk_content

        chunks.append(Chunk(
            article_id=article.article_id,
            section_number=i + 1,
            section_title=section.title,
            content=chunk_content,
            metadata={
                "article_title": article.title,
                "category": article.category,
            }
        ))

    return chunks
```

### 8.2. Hybrid Retrieval

```python
# Pseudocode: app/rag/pipeline.py

def search(query: str, max_results: int = 5) -> list[ScoredChunk]:
    """
    Hybrid retrieval: BM25 + Embedding, digabung dengan RRF.

    Mengapa hybrid:
    - BM25 menangkap kecocokan eksak ("error 0x80070005")
    - Embedding menangkap makna ("internet putus" ≈ "koneksi terputus")
    - RRF menggabungkan tanpa perlu normalisasi skor

    Deterministik: skor dihitung di Python, bukan oleh LLM.
    """

    # 1. BM25 scoring (deterministik)
    bm25_results = bm25_search(query, all_chunks)  # rank_bm25 library
    bm25_ranked = rank_results(bm25_results)

    # 2. Embedding similarity (deterministik setelah embedding dihitung)
    query_embedding = get_embedding(query)  # OpenRouter embedding API
    embedding_results = cosine_similarity_search(query_embedding, all_chunk_embeddings)
    embedding_ranked = rank_results(embedding_results)

    # 3. Reciprocal Rank Fusion
    fused = reciprocal_rank_fusion(bm25_ranked, embedding_ranked, k=60)

    # 4. Threshold filtering (ambang 0.35)
    filtered = [chunk for chunk in fused if chunk.score >= 0.35]

    # 5. Return top-N
    return filtered[:max_results]


def reciprocal_rank_fusion(
    bm25_ranked: list, embedding_ranked: list, k: int = 60
) -> list[ScoredChunk]:
    """
    RRF score = Σ (1 / (k + rank_i)) untuk setiap ranking system.

    Mengapa RRF:
    - Tidak perlu normalisasi skor (BM25 dan cosine punya skala beda)
    - Sederhana, deterministik, well-studied
    - k=60 adalah default yang terbukti robust
    """
    scores = {}
    for rank, chunk in enumerate(bm25_ranked):
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank + 1)
    for rank, chunk in enumerate(embedding_ranked):
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank + 1)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### 8.3. Keputusan Retrieval

| Keputusan | Nilai | Alasan | Alternatif yang ditolak |
|---|---|---|---|
| Metode retrieval | Hybrid BM25 + Embedding | BM25 sendiri gagal pada sinonim; embedding sendiri gagal pada istilah teknis eksak | BM25 saja, embedding saja |
| Fusion | RRF (k=60) | Tidak perlu normalisasi skor; sederhana dan deterministik | Weighted sum (perlu tuning bobot), CombMNZ |
| Ambang skor | 0.35 | Dikalibrasi pada tahap development; di bawah 0.35 umumnya tidak relevan | Tanpa ambang (selalu return top-N, risiko jawaban palsu) |
| Jumlah chunk (N) | Maks 5 | Cukup untuk prosedur multi-langkah; lebih dari 5 = token terbuang | 3 (terlalu sedikit untuk prosedur tersebar), 10 (token mahal) |

---

## 9. Agent Orchestrator

### 9.1. State Machine

```
                   ┌─────────────────────┐
                   │                     │
                   ▼                     │
            ┌─────────────┐              │
  start ──► │ CLARIFYING  │◄─── masukan ambigu
            └──────┬──────┘              │
                   │ gejala cukup jelas  │ maks 2 putaran
                   ▼                     │
            ┌─────────────┐              │
            │   SOLVING   │──────────────┘
            └──────┬──────┘    langkah gagal & < 4 langkah
                   │
          ┌────────┼────────────────┐
          │        │                │
          ▼        ▼                ▼
    ┌──────────┐ ┌──────────┐ ┌──────────────┐
    │ RESOLVED │ │ESCALATING│ │   CLOSED     │
    │ (selesai)│ │(buat     │ │ (user tutup) │
    └──────────┘ │ draf)    │ └──────────────┘
                 └────┬─────┘
                      │ user konfirmasi
                      ▼
                ┌──────────┐
                │  CLOSED  │
                │(tiket    │
                │ terkirim)│
                └──────────┘
```

### 9.2. Orchestrator Logic

```python
# Pseudocode: app/agent/orchestrator.py

class AgentOrchestrator:
    MAX_STEPS = 4
    MAX_CLARIFICATIONS = 2

    async def process_message(
        self, session: SessionState, user_message: str
    ) -> AssistantMessage:
        """
        Siklus nalar-tindak utama.

        Agentik pada: keputusan klarifikasi/pencarian/eskalasi
        Workflow pada: retrieval, validasi, state update
        """

        # NALAR: Apakah perlu klarifikasi?
        if session.status == "clarifying":
            if session.clarification_count >= self.MAX_CLARIFICATIONS:
                session.status = "solving"
            elif self._needs_clarification(user_message):
                question = await self._generate_clarification(user_message)
                session.clarification_count += 1
                return AssistantMessage(
                    tipe_respons="klarifikasi",
                    pesan=question,
                    memerlukan_konfirmasi=True,
                )
            else:
                session.gejala_terklarifikasi = user_message
                session.status = "solving"

        # TINDAK: Cari di knowledge base
        if session.status == "solving":
            # Tool: search_kb (deterministik)
            chunks = await search_kb(session.gejala_terklarifikasi)

            if not chunks:  # Tidak ada yang lolos ambang
                return AssistantMessage(
                    tipe_respons="tidak_ditemukan",
                    pesan="Informasi untuk masalah ini tidak tersedia "
                          "di knowledge base kami. Apakah Anda ingin saya "
                          "buatkan tiket untuk teknisi?",
                    memerlukan_konfirmasi=True,
                    keyakinan="tidak_dapat_ditentukan",
                )

            # Tool: get_article
            article = await get_article(chunks[0].article_id)

            # LLM: Susun langkah dari chunks
            step = await self._compose_step(
                chunks, article, session.langkah_saat_ini + 1
            )

            session.langkah_saat_ini += 1

            # NILAI: Batas langkah tercapai?
            if session.langkah_saat_ini >= self.MAX_STEPS:
                session.status = "escalating"
                # Tool: draft_ticket
                draft = await draft_ticket(session)
                return AssistantMessage(
                    tipe_respons="draf_tiket",
                    pesan="Saya sudah mencoba 4 langkah penyelesaian. "
                          "Berikut draf tiket untuk teknisi:",
                    draf_tiket=draft,
                    memerlukan_konfirmasi=True,
                )

            return step

        # Handle konfirmasi tiket
        if session.status == "escalating":
            if user_message == "konfirmasi_tiket":
                await confirm_ticket(session.draft_ticket_id)
                session.status = "closed"
                return AssistantMessage(
                    tipe_respons="tiket_terkirim",
                    pesan=f"Tiket #{session.ticket_id} telah dikirim.",
                    memerlukan_konfirmasi=False,
                )
```

### 9.3. Mengapa Bercabang, Bukan Multi-Agen

| Pertanyaan | Jawaban |
|---|---|
| Apakah urutan langkah tidak dapat ditentukan di muka? | Sebagian besar bisa: retrieval → compose → confirm. Yang tidak: keputusan klarifikasi vs pencarian |
| Biaya terburuk kalau agen berputar? | 4 × pemanggilan LLM + 1 draf tiket. Terbatas oleh MAX_STEPS di kode |
| Kalau langkah salah, dapatkah dibatalkan? | Ya — langkah solusi hanya teks panduan, tidak mengubah apa pun |
| Bagaimana menguji sesuatu yang jalannya berbeda? | State machine memiliki jalur terbatas dan deterministik pada retrieval |

**Keputusan:** Satu agent dengan branching (klarifikasi / solusi / eskalasi), BUKAN multi-agent. Alasan: kompleksitas multi-agent tidak terbayar pada alur yang jalannya terbatas — dan alur ini memang terbatas (maks 2 klarifikasi + maks 4 langkah + 1 eskalasi).

---

## 10. Tool Definitions

### 10.1. Tool Schema untuk LLM

```python
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": (
                "Mencari chunk relevan di knowledge base IT berdasarkan "
                "deskripsi masalah pengguna. Mengembalikan maksimal 5 chunk "
                "teks beserta skor relevansi dan sumber artikel. "
                "Pakai setelah gejala pengguna cukup spesifik. "
                "JANGAN pakai jika pengguna belum mendeskripsikan masalah "
                "(masih perlu klarifikasi). "
                "Tool ini HANYA MEMBACA, tidak mengubah knowledge base."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Deskripsi masalah IT yang sudah cukup spesifik"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Jumlah maksimal hasil (default: 5, maks: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_article",
            "description": (
                "Mengambil satu artikel lengkap dari knowledge base berdasarkan "
                "ID artikel. Hanya mengembalikan artikel berstatus 'published'. "
                "Pakai setelah search_kb menemukan chunk relevan, untuk "
                "mendapatkan konteks lengkap artikel. "
                "JANGAN pakai untuk artikel yang statusnya bukan published. "
                "Tool ini HANYA MEMBACA."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "article_id": {
                        "type": "string",
                        "description": "ID artikel (contoh: KB-003)"
                    }
                },
                "required": ["article_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "draft_ticket",
            "description": (
                "Membuat DRAF tiket eskalasi ke teknisi IT. Berisi ringkasan "
                "masalah dan langkah yang sudah dicoba. "
                "Pakai saat masalah belum terselesaikan setelah 4 langkah, "
                "atau ketika jawaban tidak ditemukan di knowledge base. "
                "JANGAN pakai sebelum mencoba mencari solusi di knowledge base. "
                "Tool ini HANYA MEMBUAT DRAF — tiket TIDAK terkirim sampai "
                "pengguna mengonfirmasi."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "judul": {
                        "type": "string",
                        "description": "Ringkasan masalah dalam satu kalimat"
                    },
                    "deskripsi": {
                        "type": "string",
                        "description": "Deskripsi lengkap masalah dan konteksnya"
                    },
                    "langkah_dicoba": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Daftar langkah yang sudah dicoba pengguna"
                    },
                    "prioritas": {
                        "type": "string",
                        "enum": ["rendah", "sedang", "tinggi"],
                        "description": "Tingkat prioritas berdasarkan dampak masalah"
                    },
                    "kategori": {
                        "type": "string",
                        "enum": ["jaringan", "email", "aplikasi", "perangkat", "lainnya"],
                        "description": "Kategori masalah IT"
                    }
                },
                "required": ["judul", "deskripsi", "langkah_dicoba", "prioritas", "kategori"]
            }
        }
    }
]
```

### 10.2. Penegakan Kewenangan di Kode

```python
# app/tools/search_kb.py
async def search_kb(query: str, max_results: int = 5) -> list[dict]:
    """
    Penegakan Lapis 3:
    - max_results dibatasi di parameter (maks 5), bukan di instruksi
    - Timeout 5 detik untuk mencegah hang
    - Hanya membaca dari chunks table — TIDAK ADA operasi write
    - Error dikembalikan jujur, bukan hasil kosong
    """
    if max_results > 5:
        max_results = 5  # Hard cap di kode, bukan instruksi

    try:
        results = await rag_pipeline.search(query, max_results)
        return [chunk.to_dict() for chunk in results]
    except TimeoutError:
        return {"error": "Pencarian knowledge base timeout. Coba lagi."}
    except Exception as e:
        return {"error": f"Gagal mencari: {str(e)}"}


# app/tools/get_article.py
async def get_article(article_id: str) -> dict:
    """
    Penegakan Lapis 3:
    - Filter status='published' di query SQL, bukan di instruksi
    - Artikel non-published mengembalikan error eksplisit
    """
    article = await db.fetch_one(
        "SELECT * FROM articles WHERE article_id = %s AND status = 'published'",
        (article_id,)
    )
    if not article:
        return {"error": f"Artikel {article_id} tidak ditemukan atau tidak dipublikasikan."}
    return article.to_dict()


# app/tools/draft_ticket.py
async def draft_ticket(
    judul: str, deskripsi: str, langkah_dicoba: list[str],
    prioritas: str, kategori: str, session_id: str
) -> dict:
    """
    Penegakan Lapis 3:
    - Status SELALU 'draft' — tidak ada parameter untuk langsung confirm
    - Tidak ada fungsi auto-send di tool ini
    - Konfirmasi terpisah di endpoint /ticket/confirm (Lapis 5)
    """
    ticket_id = generate_ticket_id()  # TK-XXXX

    await db.execute(
        """INSERT INTO tickets
           (session_id, ticket_id, judul, deskripsi, langkah_dicoba,
            prioritas, kategori, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, 'draft')""",
        (session_id, ticket_id, judul, deskripsi,
         json.dumps(langkah_dicoba), prioritas, kategori)
    )

    return {
        "ticket_id": ticket_id,
        "draft_content": {
            "judul": judul,
            "deskripsi": deskripsi,
            "langkah_dicoba": langkah_dicoba,
            "prioritas": prioritas,
            "kategori": kategori,
        },
        "status": "draft"
    }
```

---

## 11. Integrasi OpenRouter API

### 11.1. LLM Client

```python
# Pseudocode: app/llm/client.py

class OpenRouterClient:
    """
    Satu client untuk semua pemanggilan model.
    Mengapa OpenRouter:
    - Satu kredensial, banyak model
    - Dapat berganti model tanpa ubah kode
    - Batas anggaran terpusat
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")  # Dari .env, BUKAN di kode
        self.base_url = "https://openrouter.ai/api/v1"
        self.chat_model = os.getenv("CHAT_MODEL", "meta-llama/llama-3.1-8b-instruct")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")

    async def chat_completion(
        self,
        messages: list[dict],
        tools: list[dict] = None,
        temperature: float = 0.2,     # Rendah: konsisten, deterministik
        max_tokens: int = 500,
    ) -> dict:
        """Temperature rendah karena tugas ini memerlukan konsistensi,
        bukan kreativitas. Batas token mencegah pembengkakan biaya."""
        ...

    async def get_embedding(self, text: str) -> list[float]:
        """Embedding untuk satu chunk atau query.
        Hasilnya disimpan di MySQL, tidak dihitung ulang tiap query."""
        ...
```

### 11.2. Strategi Model

| Pemanggilan | Model yang Disarankan | Alasan |
|---|---|---|
| Klarifikasi & komposisi jawaban | Model menengah (Llama 3.1 8B / setara) | Tugas penafsiran bahasa sedang; tidak perlu model besar |
| Keputusan eskalasi | Model yang sama | Keputusan biner (eskalasi/tidak) berdasarkan konteks terbatas |
| Embedding | text-embedding-3-small / setara | Embedding ringan, cukup untuk 8 dokumen |

**Catatan:** Model aktual ditentukan berdasarkan ketersediaan dan anggaran di OpenRouter. Perbandingan model murah vs mahal dilakukan di Minggu 14.

---

## 12. Guardrails Implementation

### 12.1. Lapis 1: Input Guard

```python
# app/guardrails/input_guard.py

class InputGuard:
    MAX_INPUT_LENGTH = 1000
    INJECTION_PATTERNS = [
        r"abaikan\s+instruksi",
        r"ignore\s+(previous|all)\s+instructions",
        r"system\s*prompt",
        r"kamu\s+sebenarnya\s+adalah",
    ]

    def validate(self, user_input: str) -> tuple[bool, str]:
        # Panjang
        if len(user_input) > self.MAX_INPUT_LENGTH:
            return False, "Pesan terlalu panjang. Maksimal 1000 karakter."

        # Sanitasi HTML/script tags
        cleaned = bleach.clean(user_input, tags=[], strip=True)

        # Deteksi pola injection (lapis terlemah — backup saja)
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                # Log untuk analisis, tapi JANGAN tolak langsung
                # (bisa false positive). Tandai sebagai flagged.
                log_suspicious_input(cleaned, pattern)

        return True, cleaned
```

### 12.2. Lapis 4: Output Guard

```python
# app/guardrails/output_guard.py

class OutputGuard:
    def validate(self, response: dict) -> tuple[bool, str]:
        # 1. Validasi JSON schema
        try:
            AssistantMessage.model_validate(response)
        except ValidationError as e:
            return False, f"Schema invalid: {e}"

        # 2. Cek kutipan sumber pada tipe langkah_solusi
        if response.get("tipe_respons") == "langkah_solusi":
            if not response.get("sumber"):
                return False, "Langkah solusi tanpa sumber tidak diperbolehkan."

        # 3. Cek bahwa pesan tidak mengandung instruksi sistem
        if self._contains_system_prompt(response.get("pesan", "")):
            return False, "Respons mengandung konten instruksi sistem."

        return True, ""

    async def validate_with_retry(self, llm_call, max_retries=1):
        """
        Penanganan kegagalan tiga langkah:
        1. Periksa keluaran terhadap skema
        2. Bila tidak sah → ulangi sekali dengan pesan error
        3. Bila masih tidak sah → kembalikan error standar
        """
        for attempt in range(max_retries + 1):
            response = await llm_call()
            valid, error = self.validate(response)
            if valid:
                return response
            if attempt < max_retries:
                # Retry dengan error message
                continue

        # Gagal setelah retry
        return self._fallback_error_response()
```

### 12.3. Tabel Guardrails Lengkap

| Lapis | Apa | Ditegakkan di | Kekuatan | Keterbatasan |
|---|---|---|---|---|
| 1 — Masukan | Validasi panjang, sanitasi, deteksi pola | Kode (`input_guard.py`) | Menangkap serangan kasar | Pattern matching tidak tangkap serangan halus |
| 2 — Instruksi | "Jawab HANYA dari konteks KB" | System prompt | Berfungsi sebagian besar waktu | Dapat ditembus oleh injection |
| 3 — Kewenangan | Tool hanya baca; draf tiket bukan kirim | Kode (tool implementations) | **Paling kuat** — tidak bergantung model | Butuh didesain sejak awal |
| 4 — Keluaran | Validasi JSON schema, cek kutipan sumber | Kode (`output_guard.py`) | Tangkap keluaran tak sah | Menambah latensi sedikit |
| 5 — Manusia | Tiket hanya terkirim setelah konfirmasi | Kode (endpoint terpisah) | **Paling kuat** untuk tindakan berdampak | Melambatkan alur |

---

## 13. Struktur Direktori Proyek (Lengkap)

```
knowdesk-ai/
│
├── frontend/                          # Svelte + TypeScript + Tailwind
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/            # UI components
│   │   │   ├── stores/                # Svelte stores
│   │   │   ├── services/              # API client
│   │   │   ├── types/                 # TypeScript interfaces
│   │   │   └── utils/                 # Formatters, helpers
│   │   ├── routes/                    # SvelteKit routes
│   │   ├── app.html
│   │   └── app.css
│   ├── static/
│   ├── svelte.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── package.json
│
├── backend/                           # Python + FastAPI
│   ├── app/
│   │   ├── api/                       # Endpoints + schemas
│   │   ├── agent/                     # Orchestrator + prompts + state
│   │   ├── rag/                       # BM25 + embedding + chunker + ranker
│   │   ├── tools/                     # search_kb, get_article, draft_ticket
│   │   ├── guardrails/                # Input + output guards
│   │   ├── llm/                       # OpenRouter client
│   │   ├── session/                   # Session manager
│   │   ├── db/                        # MySQL connection + migrations
│   │   └── logging/                   # Trace logger
│   ├── scripts/                       # Ingestion, seeding, test runner
│   ├── knowledge_base/                # 8 dokumen markdown
│   ├── tests/                         # Test suite
│   ├── logs/traces/                   # Agent traces
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   └── README.md
│
├── docs/                              # Dokumentasi proyek
│   ├── PRD.md                         # Product Requirements Document
│   ├── architecture.md                # Dokumen ini
│   ├── lembar-tema.md                 # Lembar tema proyek (Minggu 4)
│   ├── rancangan-sistem.md            # Rancangan sistem (UTS)
│   ├── rancangan-rag.md               # Rancangan alur RAG (Minggu 7)
│   ├── analisis-workflow-vs-agen.md   # Analisis komparatif (Minggu 10)
│   ├── guardrails.md                  # Guardrails + hasil uji serangan
│   ├── laporan-evaluasi.md            # Laporan evaluasi (Minggu 14)
│   └── kajian-risiko.md               # Kajian risiko + pernyataan etis
│
├── instruksi/                         # Versi instruksi sistem
│   ├── v1.md
│   ├── v2.md
│   └── CATATAN.md                     # Log perubahan instruksi
│
├── set-uji/                           # Set uji lengkap
│   └── test_suite_15.json
│
├── catatan-proses/                    # Catatan proses mingguan
│   ├── minggu-01.md
│   └── ...
│
├── catatan-pemakaian.md               # Log biaya token sejak Minggu 3
├── refleksi.md                        # Refleksi akhir semester
├── .gitignore
└── README.md
```

---

## 14. API Contract

### 14.1. Endpoints

| Method | Path | Deskripsi | Auth |
|---|---|---|---|
| `POST` | `/api/chat` | Kirim pesan pengguna, terima respons agen | - |
| `GET` | `/api/session/{session_id}` | Ambil state sesi saat ini | - |
| `POST` | `/api/ticket/confirm` | Konfirmasi pengiriman draf tiket | - |
| `GET` | `/api/articles` | Daftar semua artikel KB (untuk debug/admin) | - |
| `GET` | `/api/health` | Health check | - |

### 14.2. POST /api/chat

**Request:**
```json
{
  "session_id": "uuid-string atau null untuk sesi baru",
  "message": "Saya tidak bisa connect Wi-Fi kantor",
  "confirmation": null
}
```

**Response (klarifikasi):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "tipe_respons": "klarifikasi",
    "pesan": "Untuk membantu Anda, saya perlu tahu lebih detail:\n1. Apakah Wi-Fi kantor muncul di daftar jaringan?\n2. Apakah ada pesan error tertentu?",
    "langkah_saat_ini": 0,
    "langkah_total_tersedia": 0,
    "sumber": [],
    "memerlukan_konfirmasi": true,
    "keyakinan": "tidak_dapat_ditentukan",
    "draf_tiket": null
  },
  "session_state": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "clarifying",
    "langkah_saat_ini": 0,
    "langkah_maks": 4
  }
}
```

**Response (langkah solusi):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "tipe_respons": "langkah_solusi",
    "pesan": "**Langkah 1:** Buka pengaturan Wi-Fi di komputer Anda. Klik ikon jaringan di taskbar, lalu pilih 'Network & Internet Settings'. Cari nama jaringan kantor 'OFFICE-WIFI' dan klik 'Forget'. Setelah itu, cari kembali dan sambungkan ulang dengan memasukkan password.",
    "langkah_saat_ini": 1,
    "langkah_total_tersedia": 3,
    "sumber": [
      {
        "article_id": "KB-001",
        "section": "Bagian 3",
        "judul": "Langkah Reset Koneksi Wi-Fi",
        "kutipan": "Buka Network & Internet Settings, pilih jaringan kantor, klik Forget, lalu sambungkan ulang."
      }
    ],
    "memerlukan_konfirmasi": true,
    "keyakinan": "tinggi",
    "draf_tiket": null
  },
  "session_state": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "solving",
    "langkah_saat_ini": 1,
    "langkah_maks": 4
  }
}
```

### 14.3. POST /api/ticket/confirm

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "ticket_id": "TK-0042",
  "action": "confirm"
}
```

**Response:**
```json
{
  "ticket_id": "TK-0042",
  "status": "confirmed",
  "message": "Tiket #TK-0042 telah dikirim ke teknisi. Teknisi akan menghubungi Anda."
}
```

---

## 15. Konfigurasi dan Environment

### 15.1. Environment Variables

```bash
# .env.example — JANGAN commit file .env yang sebenarnya

# OpenRouter API
OPENROUTER_API_KEY=your_api_key_here    # TIDAK PERNAH di kode, TIDAK PERNAH di repo
CHAT_MODEL=meta-llama/llama-3.1-8b-instruct
EMBEDDING_MODEL=openai/text-embedding-3-small

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=knowdesk
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=knowdesk_ai

# Application
APP_PORT=8000
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO

# RAG Configuration
RAG_CHUNK_OVERLAP=50
RAG_MAX_RESULTS=5
RAG_SCORE_THRESHOLD=0.35
RAG_RRF_K=60

# Agent Configuration
AGENT_MAX_STEPS=4
AGENT_MAX_CLARIFICATIONS=2
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=500
```

### 15.2. .gitignore

```gitignore
# Environment & secrets
.env
*.env.local

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node
node_modules/
dist/
.svelte-kit/

# Logs
logs/
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## 16. Strategi Chunking dan Indexing

### 16.1. Format Dokumen KB

```markdown
<!-- KB-001-troubleshoot-wifi.md -->

# Panduan Troubleshooting Koneksi Wi-Fi Kantor

**Article ID:** KB-001
**Kategori:** Jaringan
**Terakhir diperbarui:** 2026-10-01

## Bagian 1: Gejala Umum
[isi tentang gejala]

## Bagian 2: Langkah Diagnosis Awal
[isi tentang diagnosis]

## Bagian 3: Langkah Reset Koneksi Wi-Fi
[isi langkah-langkah]

## Bagian 4: Masalah Driver Wi-Fi
[isi tentang driver]

## Bagian 5: Kapan Harus Menghubungi Teknisi
[isi tentang eskalasi]
```

### 16.2. Proses Ingestion

```
1. Parse markdown → extract sections (split di ## headers)
2. Setiap section → satu chunk + overlap 50 kata dari section sebelumnya
3. Tokenize untuk BM25 (Bahasa Indonesia tokenizer)
4. Generate embedding via OpenRouter API
5. Store ke MySQL: content, bm25_tokens, embedding, metadata
```

---

## 17. State Management

### 17.1. Frontend State (Svelte Stores)

```typescript
// stores/chatStore.ts
import { writable } from 'svelte/store';

export const messages = writable<ChatMessage[]>([]);
export const sessionId = writable<string | null>(null);
export const sessionState = writable<SessionState | null>(null);
export const isLoading = writable<boolean>(false);
```

### 17.2. Backend State (MySQL Sessions)

| State | Di mana | Umur | Mengapa |
|---|---|---|---|
| Conversation messages | Frontend (Svelte store) + Backend (`conversation_history` JSON di `sessions`) | Per sesi | Frontend untuk display; backend untuk konteks LLM |
| Task state (langkah, status) | MySQL `sessions` table | Per sesi | Di luar percakapan, dapat diperiksa dan dipulihkan |
| Agent traces | MySQL `agent_traces` table + file `logs/traces/` | Permanen | Untuk diagnosis dan evaluasi Minggu 14 |
| Tickets | MySQL `tickets` table | Permanen | Bukti eskalasi |

---

## 18. Observabilitas dan Logging

### 18.1. Agent Traces

Setiap langkah agen dicatat ke `agent_traces` table dan file log:

```json
{
  "session_id": "550e8400...",
  "step_number": 2,
  "action_type": "tindak",
  "tool_called": "search_kb",
  "tool_params": {"query": "password email salah", "max_results": 5},
  "tool_result": {"chunks_found": 3, "top_score": 0.72},
  "reasoning": "Gejala sudah spesifik (password salah). Mencari di KB.",
  "decision": "lanjut ke get_article",
  "tokens_used": 245,
  "created_at": "2026-10-11T10:30:15"
}
```

### 18.2. Catatan Pemakaian Token

Setiap pemanggilan LLM dicatat untuk `catatan-pemakaian.md`:
- Tanggal, model, token masuk, token keluar, perkiraan biaya
- Diakumulasi mingguan sebagai bahan laporan biaya Minggu 14

---

## 19. Keputusan Arsitektur dan Pertukaran

| # | Keputusan | Alternatif yang Ditolak | Alasan Memilih | Pertukaran yang Diterima |
|---|---|---|---|---|
| 1 | **Embedding di MySQL JSON** bukan vector DB | Pinecone, Weaviate, pgvector | 8 dokumen ≈ 50 chunk; cosine di Python < 10ms. Infra tambahan = over-engineering | Tidak skala ke ribuan dokumen (tapi tidak perlu) |
| 2 | **Satu agent bercabang** bukan multi-agent | Multi-agent dengan spesialisasi | Alur terbatas (maks 2+4+1 langkah); multi-agent menambah kerumitan tanpa manfaat | Kurang fleksibel untuk alur yang benar-benar tak terduga |
| 3 | **BM25 + Embedding hybrid** bukan salah satu | BM25 saja, embedding saja | BM25 tangkap kata kunci eksak; embedding tangkap sinonim. Saling melengkapi | Kompleksitas retrieval lebih tinggi |
| 4 | **Session state di MySQL** bukan di memori | In-memory store (Redis), percakapan LLM | Persisten, dapat diperiksa, tidak hilang saat restart; trace untuk evaluasi | Latensi sedikit lebih tinggi (diabaikan untuk skala ini) |
| 5 | **Temperature 0.2** bukan 0 | Temperature 0 | 0.2 cukup konsisten tapi sedikit lebih alami; 0 terlalu kaku untuk penyusunan panduan | Keluaran tidak 100% identik antar-run (variance dilaporkan) |
| 6 | **Batas 4 langkah di kode** bukan di instruksi | Batas di system prompt | Kode tidak bisa dilanggar model; instruksi bisa | Kurang fleksibel jika suatu saat mau ubah per kasus |
| 7 | **Tailwind CSS** bukan vanilla CSS | Vanilla CSS | Request eksplisit; utility-first mempercepat iterasi UI | Dependensi build tambahan |
| 8 | **FastAPI** bukan Flask/Django | Flask, Django | Async native (cocok untuk LLM calls); auto OpenAPI docs; pydantic integration | Ekosistem middleware lebih kecil dari Django |

---

## 20. Deployment dan Development

### 20.1. Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd knowdesk-ai

# 2. Backend setup
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # Edit dengan kredensial Anda

# 3. Database setup
mysql -u root -p -e "CREATE DATABASE knowdesk_ai CHARACTER SET utf8mb4;"
mysql -u root -p knowdesk_ai < app/db/migrations/001_initial.sql

# 4. Ingest knowledge base
python scripts/seed_articles.py
python scripts/ingest_documents.py

# 5. Run backend
uvicorn app.main:app --reload --port 8000

# 6. Frontend setup (terminal baru)
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

### 20.2. Dependencies Utama

**Backend (requirements.txt):**
```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
aiomysql>=0.2.0
httpx>=0.24.0              # HTTP client untuk OpenRouter
rank-bm25>=0.2.2           # BM25 scoring
numpy>=1.24.0              # Cosine similarity
python-dotenv>=1.0.0
bleach>=6.0.0              # Input sanitization
```

**Frontend (package.json):**
```json
{
  "devDependencies": {
    "@sveltejs/kit": "latest",
    "@sveltejs/adapter-static": "latest",
    "svelte": "^4.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0",
    "autoprefixer": "latest",
    "postcss": "latest",
    "vite": "^5.0.0"
  }
}
```

### 20.3. Arsitektur untuk Demo UAS

Karena pengguna disimulasikan di depan kelas, deployment cukup:

```
Laptop mahasiswa
├── MySQL (localhost:3306)
├── FastAPI backend (localhost:8000)
└── Svelte frontend (localhost:5173)

Koneksi keluar:
└── OpenRouter API (https://openrouter.ai/api/v1) — memerlukan internet
```

Tidak memerlukan deployment ke cloud atau server eksternal.

---

## Catatan Penutup

Dokumen arsitektur ini dirancang untuk memenuhi seluruh kebutuhan lima lapisan Kapita Selekta: AI Engineering:

- **Lapisan 1 (Fondasi):** Tech stack dipilih dan lingkungan kerja disiapkan
- **Lapisan 2 (Kendali):** Skema keluaran JSON, instruksi sistem, tool definitions
- **Lapisan 3 (Grounding):** Pipeline RAG hybrid, chunking, ambang skor, perilaku penolakan
- **Lapisan 4 (Agentic):** Agent orchestrator, state machine, batas langkah, tool dengan kewenangan
- **Lapisan 5 (Kematangan):** Observability, trace logging, test suite, evaluasi metrik

Setiap keputusan arsitektur disertai **alasan** dan **alternatif yang ditolak**, karena yang dinilai pada mata kuliah ini adalah **alasan di balik keputusan**, bukan kecanggihan teknologinya.
