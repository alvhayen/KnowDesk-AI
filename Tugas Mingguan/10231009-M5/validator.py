"""
Kode Validator Skema dan Fallback 3-Langkah — KnowDesk AI (Minggu 5)
Mata Kuliah: Kapita Selekta: AI Engineering (Ganjil 2026/2027)

Fitur:
1. Validasi Pydantic terstruktur dengan closed-set enum
2. Pembersihan markdown codeblock ```json ... ```
3. Verifikasi kutipan persis (exact substring match)
4. Mekanisme fallback 3 langkah yang aman dari crash
"""

import json
import re
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError

# --- 1. Definisi Model Pydantic ---

class SumberSitasi(BaseModel):
    article_id: str = Field(..., pattern=r"^KB-00[1-8]$")
    section: str
    kutipan: str

class TroubleshootResponse(BaseModel):
    dapat_ditentukan: Literal["ya", "tidak"]
    kategori: Literal["jaringan", "email", "aplikasi", "perangkat", "lainnya"]
    tingkat_urgensi: Literal["rendah", "sedang", "tinggi"]
    langkah_ke: int = Field(..., ge=1, le=4)
    total_langkah: int = Field(..., ge=1, le=4)
    pesan: str
    tindakan_berikutnya: Literal["tunggu_konfirmasi", "eskalasi_tiket", "selesai"]
    sumber: List[SumberSitasi] = Field(default_factory=list)


# --- 2. Fungsi Sanitasi & Verifikasi Substring ---

MOCK_KB_001 = (
    "Panduan Troubleshooting Wi-Fi Kantor. Bagian 2: Langkah Solusi. "
    "Langkah 1: Matikan tombol Wi-Fi pada laptop Anda selama 10 detik, "
    "lalu nyalakan kembali dan coba hubungkan ulang ke SSID CorpNet."
)

def strip_markdown_blocks(raw_text: str) -> str:
    """Membersihkan pembungkus markdown ```json ... ``` jika model menyertakannya."""
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, raw_text)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

def verify_exact_substring(response: TroubleshootResponse, kb_text: str) -> bool:
    """Memastikan bahwa kutipan adalah substring persis dari dokumen rujukan."""
    if response.dapat_ditentukan == "tidak":
        return True
    for s in response.sumber:
        if s.kutipan not in kb_text:
            return False
    return True


# --- 3. Implementasi Fallback 3 Langkah ---

def process_model_output_with_fallback(raw_output: str, kb_text: str = MOCK_KB_001) -> Dict[str, Any]:
    """
    Eksekusi 3 Langkah:
    Langkah 1: Uji Validasi Skema
    Langkah 2: Bila Gagal, Simulasi Retry dengan pesan galat
    Langkah 3: Bila Masih Gagal, Kembalikan Fallback Terstruktur Aman
    """
    cleaned = strip_markdown_blocks(raw_output)
    
    # Langkah 1: Parsing & Validasi
    try:
        data = json.loads(cleaned)
        validated = TroubleshootResponse(**data)
        
        # Validasi Substring
        if not verify_exact_substring(validated, kb_text):
            raise ValueError("Kutipan teks bukan merupakan substring persis dari dokumen rujukan.")
            
        return {
            "status": "valid (Langkah 1)",
            "data": validated.model_dump(),
            "retry_occurred": False
        }
    except (json.JSONDecodeError, ValidationError, ValueError) as err1:
        # Langkah 2: Retry dengan koreksi (disimulasikan di sini)
        print(f"[LANGKAH 1 GAGAL] Error: {err1}. Memulai Langkah 2 (Retry dengan Error Correction)...")
        
        # Simulasi jika retry menghasilkan teks yang diperbaiki:
        simulated_retry_output = json.dumps({
            "dapat_ditentukan": "ya",
            "kategori": "jaringan",
            "tingkat_urgensi": "sedang",
            "langkah_ke": 1,
            "total_langkah": 3,
            "pesan": "Matikan tombol Wi-Fi pada laptop Anda selama 10 detik lalu nyalakan kembali.",
            "tindakan_berikutnya": "tunggu_konfirmasi",
            "sumber": [
                {
                    "article_id": "KB-001",
                    "section": "Bagian 2",
                    "kutipan": "Matikan tombol Wi-Fi pada laptop Anda selama 10 detik"
                }
            ]
        })
        
        try:
            retry_data = json.loads(simulated_retry_output)
            validated_retry = TroubleshootResponse(**retry_data)
            if verify_exact_substring(validated_retry, kb_text):
                return {
                    "status": "valid_after_retry (Langkah 2)",
                    "data": validated_retry.model_dump(),
                    "retry_occurred": True
                }
        except Exception as err2:
            pass

        # Langkah 3: Fail-Safe Fallback Terstruktur
        print("[LANGKAH 2 GAGAL] Mengaktifkan Langkah 3: Deterministic Fail-Safe Fallback.")
        fallback_obj = TroubleshootResponse(
            dapat_ditentukan="tidak",
            kategori="lainnya",
            tingkat_urgensi="sedang",
            langkah_ke=1,
            total_langkah=1,
            pesan="Sistem mengalami kendala saat memformat panduan secara otomatis. Kami menyarankan untuk membuat draf tiket eskalasi ke teknisi IT.",
            tindakan_berikutnya="eskalasi_tiket",
            sumber=[]
        )
        return {
            "status": "fail_safe_fallback (Langkah 3)",
            "data": fallback_obj.model_dump(),
            "retry_occurred": True,
            "log_error": str(err1)
        }


if __name__ == "__main__":
    print("=" * 60)
    print("  KNOWDESK AI — VALIDATOR SKEMA & PENANGANAN KEGAGALAN (M5)")
    print("=" * 60)

    # Uji 1: Output Valid Sempurna
    print("\n[UJI 1] Menguji Keluaran Valid Sempurna...")
    valid_sample = json.dumps({
        "dapat_ditentukan": "ya",
        "kategori": "jaringan",
        "tingkat_urgensi": "sedang",
        "langkah_ke": 1,
        "total_langkah": 3,
        "pesan": "Silakan matikan tombol Wi-Fi selama 10 detik lalu coba hubungkan ulang.",
        "tindakan_berikutnya": "tunggu_konfirmasi",
        "sumber": [{
            "article_id": "KB-001",
            "section": "Bagian 2",
            "kutipan": "Matikan tombol Wi-Fi pada laptop Anda selama 10 detik"
        }]
    })
    res1 = process_model_output_with_fallback(valid_sample)
    print(f"Hasil: {res1['status']} | Kategori: {res1['data']['kategori']}")

    # Uji 2: Output Rusak / Malformed JSON (Memicu Fallback)
    print("\n[UJI 2] Menguji Masukan Cacat (Format Tidak Sah)...")
    malformed_sample = "Tentu! Berikut analisisnya: kategori=jaringan, tingkat_urgensi=sangat-amat-penting"
    res2 = process_model_output_with_fallback(malformed_sample)
    print(f"Hasil: {res2['status']} | Tindakan: {res2['data']['tindakan_berikutnya']}")
    print("=" * 60)
