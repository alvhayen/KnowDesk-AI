"""
Kode Eksekutor Tool (Tools Runner) — KnowDesk AI (Minggu 6)
Mata Kuliah: Kapita Selekta: AI Engineering (Ganjil 2026/2027)

Fitur:
1. Implementasi 3 tool kanonik (K = 3): search_kb, get_article, draft_ticket
2. Batas kewenangan tertulis (read-only vs human-in-the-loop write)
3. Penanganan error jujur (tidak menyembunyikan ketiadaan data)
4. Simulasi putaran eksekusi tool calling terintegrasi
"""

import json
from typing import Dict, Any, List

# Basis Pengetahuan Mock Kanonik untuk Pengujian Luring
MOCK_KB_DATABASE = {
    "KB-001": {
        "judul": "Panduan Troubleshooting Koneksi Wi-Fi Kantor",
        "kategori": "jaringan",
        "langkah": [
            "Matikan adapter Wi-Fi di laptop Anda selama 10 detik lalu nyalakan kembali.",
            "Lupakan jaringan (Forget Network) 'CorpNet' lalu sambungkan ulang dengan kredensial domain.",
            "Jalankan pembaruan IP melalui Command Prompt: ipconfig /renew.",
            "Periksa apakah sertifikat otentikasi 802.1X Anda masih aktif di portal IT."
        ]
    },
    "KB-002": {
        "judul": "Prosedur Reset dan Pemulihan Password Email",
        "kategori": "email",
        "langkah": [
            "Buka peramban web dan akses portal mandiri SSO di https://sso.example.com.",
            "Pilih opsi 'Lupa Kata Sandi' dan masukkan NIP karyawan Anda.",
            "Masukkan kode OTP yang dikirimkan ke nomor WhatsApp terdaftar.",
            "Buat kata sandi baru minimal 12 karakter kombinasi huruf besar, angka, dan simbol."
        ]
    }
}


# --- Implementasi Tiga Tool Kanonik ---

def search_kb(query: str) -> Dict[str, Any]:
    """Mencari artikel KB berdasarkan kesamaan kata kunci (Read-Only)."""
    q = query.lower()
    hasil = []
    for art_id, art_data in MOCK_KB_DATABASE.items():
        if any(term in art_data["judul"].lower() or term in art_data["kategori"].lower() for term in q.split()):
            hasil.append({
                "article_id": art_id,
                "judul": art_data["judul"],
                "kategori": art_data["kategori"]
            })
            
    if not hasil:
        # Penanganan Error Jujur: Kembalikan status not found eksplisit
        return {
            "status": "not_found",
            "pesan_error": f"Tidak ditemukan dokumen panduan resmi untuk query '{query}'.",
            "data": []
        }
        
    return {
        "status": "success",
        "total_ditemukan": len(hasil),
        "data": hasil
    }


def get_article(article_id: str) -> Dict[str, Any]:
    """Mengambil rincian isi artikel resmi (Read-Only)."""
    art_id = article_id.strip().upper()
    if art_id not in MOCK_KB_DATABASE:
        # Penanganan Error Jujur: Jangan sembunyikan error
        return {
            "status": "error",
            "pesan_error": f"Artikel dengan ID '{art_id}' tidak terdaftar di knowledge base."
        }
    
    art = MOCK_KB_DATABASE[art_id]
    return {
        "status": "success",
        "article_id": art_id,
        "judul": art["judul"],
        "langkah_1": art["langkah"][0],
        "total_langkah": len(art["langkah"])
    }


def draft_ticket(judul: str, deskripsi: str, langkah_dicoba: str, prioritas: str, kategori: str) -> Dict[str, Any]:
    """Menyusun draf tiket eskalasi (Human-in-the-Loop: Belum disimpan ke database)."""
    # Validasi prioritas dan kategori tertutup
    if prioritas not in ["rendah", "sedang", "tinggi"]:
        return {"status": "error", "pesan_error": "Nilai prioritas tidak valid."}
        
    draf = {
        "ticket_draft_id": "DRAFT-2026-0042",
        "judul": judul[:60],
        "deskripsi": deskripsi,
        "langkah_dicoba": langkah_dicoba,
        "prioritas": prioritas,
        "kategori": kategori,
        "status": "MENUNGGU_KONFIRMASI_PENGGUNA",
        "keterangan": "Tiket belum dikirim ke teknisi. Butuh konfirmasi pengguna melalui tombol konfirmasi."
    }
    return {
        "status": "success",
        "data": draf
    }


# --- Eksekutor Pemanggil Dinamis ---

TOOL_DISPATCHER = {
    "search_kb": search_kb,
    "get_article": get_article,
    "draft_ticket": draft_ticket
}

def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Mengeksekusi tool yang diminta model dan mengembalikan string JSON ke model."""
    if tool_name not in TOOL_DISPATCHER:
        return json.dumps({
            "status": "error",
            "pesan_error": f"Tool '{tool_name}' tidak diizinkan atau tidak ditemukan."
        })
    func = TOOL_DISPATCHER[tool_name]
    try:
        res = func(**arguments)
        return json.dumps(res, ensure_ascii=False)
    except TypeError as e:
        return json.dumps({
            "status": "error",
            "pesan_error": f"Parameter tool tidak sesuai: {str(e)}"
        })


if __name__ == "__main__":
    print("=" * 60)
    print("  KNOWDESK AI — EKSEKUTOR TOOL DAN FUNCTION CALLING (M6)")
    print("=" * 60)

    # 1. Uji Tool 1: search_kb
    print("\n[1] Menjalankan Tool 'search_kb' dengan query 'wifi kantor'...")
    res_search = execute_tool_call("search_kb", {"query": "wifi kantor"})
    print(f"Hasil Tool:\n{res_search}")

    # 2. Uji Tool 2: get_article
    print("\n[2] Menjalankan Tool 'get_article' dengan ID 'KB-001'...")
    res_art = execute_tool_call("get_article", {"article_id": "KB-001"})
    print(f"Hasil Tool:\n{res_art}")

    # 3. Uji Penanganan Error Jujur: Artikel Tidak Ada
    print("\n[3] Menjalankan Tool 'get_article' dengan ID Fiktif 'KB-999'...")
    res_err = execute_tool_call("get_article", {"article_id": "KB-999"})
    print(f"Hasil Error Jujur:\n{res_err}")

    # 4. Uji Tool 3: draft_ticket (Human-in-the-Loop)
    print("\n[4] Menjalankan Tool 'draft_ticket'...")
    res_ticket = execute_tool_call("draft_ticket", {
        "judul": "Wi-Fi putus di laptop Asus",
        "deskripsi": "Pengguna telah mencoba restart adapter namun tetap gagal terhubung.",
        "langkah_dicoba": "Restart Wi-Fi adapter (KB-001 Langkah 1)",
        "prioritas": "sedang",
        "kategori": "jaringan"
    })
    print(f"Hasil Tool Tiket:\n{res_ticket}")
    print("=" * 60)
