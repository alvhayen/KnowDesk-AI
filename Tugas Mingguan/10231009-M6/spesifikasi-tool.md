# Spesifikasi dan Batas Kewenangan Tiga Tool Kanonik
## Proyek: KnowDesk AI (K = 3) — Tugas 6

---

## 1. Matriks Tiga Tool Wajib ($K = 3$)

| Nama Tool | Kegunaan Utama | Parameter Masukan | Keluaran (Output) | Kapan TIDAK Boleh Dipakai | Sifat Akses & Batas Kewenangan |
|---|---|---|---|---|---|
| `search_kb` | Mencari artikel panduan SOP berdasarkan query gejala masalah. | `query` (string, wajib, 3–100 karakter) | Daftar ringkasan artikel: `[{"article_id": "KB-001", "judul": "...", "score": 0.84}]` | **DILARANG** dipanggil jika pesan pengguna masih terlalu ambigu (misal hanya *"komputer rusak"*). Klarifikasi dulu gejalanya. | **Read-Only Otomatis**.<br>Hanya membaca indeks KB internal kantor. |
| `get_article` | Mengambil teks lengkap dan langkah solusi dari artikel tertentu. | `article_id` (string, pola: `^KB-00[1-8]$`) | Objek artikel lengkap memuat metadata, teks heading, dan langkah-langkah kanonik. | **DILARANG** dipanggil dengan ID sembarang sebelum dilakukan pencarian resmi melalui `search_kb`. | **Read-Only Otomatis**.<br>Hanya membaca file SOP lokal yang sah. |
| `draft_ticket` | Menyusun draf tiket eskalasi ke antrean teknisi IT Support tier-2. | `judul`, `deskripsi`, `langkah_dicoba`, `prioritas`, `kategori` | Objek draf tiket: `{"ticket_id": "TICKET-DRAFT-...", "status": "draft", "perlu_konfirmasi": true}` | **DILARANG** dipanggil sebelum dilakukan pencarian artikel dan sebelum ada langkah panduan mandiri yang gagal dicoba. | **Write-Action / Human-in-the-Loop**.<br>Tiket **TIDAK PERNAH** dikirim langsung ke database tanpa persetujuan eksplisit dari pengguna. |

---

## 2. Definisi Skema JSON Schema untuk Pemanggilan Model (Function Calling)

```json
[
  {
    "type": "function",
    "function": {
      "name": "search_kb",
      "description": "Mencari artikel panduan helpdesk IT berdasarkan kata kunci gejala masalah yang spesifik. Jangan gunakan tool ini jika gejala pengguna masih kabur atau belum jelas.",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "Kata kunci keluhan teknis (contoh: 'wifi putus', 'vpn authentication failed')."
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
      "description": "Mengambil isi artikel panduan IT resmi berdasarkan article_id hasil pencarian resmi (misal 'KB-001'). Jangan gunakan jika belum menemukan article_id yang sah.",
      "parameters": {
        "type": "object",
        "properties": {
          "article_id": {
            "type": "string",
            "description": "ID kanonik dokumen rujukan (contoh: 'KB-001', 'KB-002')."
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
      "description": "Menyusun draf tiket eskalasi ke teknisi IT jika semua langkah mandiri telah gagal dicoba atau artikel panduan tidak ditemukan. Dilarang memanggil tool ini sebelum dilakukan pencarian artikel terlebih dahulu.",
      "parameters": {
        "type": "object",
        "properties": {
          "judul": { "type": "string", "description": "Ringkasan insiden IT (maksimal 60 karakter)." },
          "deskripsi": { "type": "string", "description": "Uraian detail keluhan kendala." },
          "langkah_dicoba": { "type": "string", "description": "Langkah-langkah SOP yang sudah dicoba namun gagal." },
          "prioritas": { "type": "string", "enum": ["rendah", "sedang", "tinggi"] },
          "kategori": { "type": "string", "enum": ["jaringan", "email", "aplikasi", "perangkat", "lainnya"] }
        },
        "required": ["judul", "deskripsi", "langkah_dicoba", "prioritas", "kategori"]
      }
    }
  }
]
```

---

## 3. Kebijakan Keamanan dan Prinsip Human-in-the-Loop

1. **Prinsip Least Privilege:** Seluruh tool interaktif hanya memiliki hak akses baca terbatas pada direktori `knowledge_base/`. Tidak ada tool yang memiliki akses ke terminal shell sistem operasi, registry Windows, atau API eksekusi script jarak jauh.
2. **Pintu Gerbang Konfirmasi Pengguna:**  
   Penyusunan tiket oleh `draft_ticket` hanya menghasilkan status `"draft"`. Pengguna diberikan antarmuka konfirmasi modal pop-up:
   - *"Kirim Tiket Sekarang"* $\rightarrow$ Mengirim ke endpoint `/api/ticket/confirm`.
   - *"Batal / Coba Lagi"* $\rightarrow$ Membatalkan pembuatan tiket.
