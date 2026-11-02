# Spesifikasi Skema dan Kontrak Keluaran Terstruktur
## Proyek: KnowDesk AI (K = 3) — Tugas 5

---

## 1. Definisi Kontrak Data Pydantic

Sistem mewajibkan seluruh respon pemecahan masalah mematuhi skema kontrak berikut:

```python
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class SumberSitasi(BaseModel):
    article_id: str = Field(
        ..., 
        description="ID unik dokumen SOP rujukan kanonik (contoh: 'KB-001').",
        pattern=r"^KB-00[1-8]$"
    )
    section: str = Field(
        ..., 
        description="Nama heading bagian di dokumen rujukan (contoh: 'Bagian 2')."
    )
    kutipan: str = Field(
        ..., 
        description="Cuplikan teks asli yang persis (exact substring) dari dokumen rujukan."
    )

class TroubleshootResponse(BaseModel):
    dapat_ditentukan: Literal["ya", "tidak"] = Field(
        ..., 
        description="Status apakah keluhan dapat ditentukan solusinya dari basis pengetahuan."
    )
    kategori: Literal["jaringan", "email", "aplikasi", "perangkat", "lainnya"] = Field(
        ..., 
        description="Kategori domain masalah IT dalam daftar nilai tertutup."
    )
    tingkat_urgensi: Literal["rendah", "sedang", "tinggi"] = Field(
        ..., 
        description="Tingkat urgensi insiden berdasarkan dampaknya ke operasional kantor."
    )
    langkah_ke: int = Field(
        ..., 
        ge=1, le=4, 
        description="Nomor urut langkah pemecahan masalah yang sedang disajikan (1 sampai 4)."
    )
    total_langkah: int = Field(
        ..., 
        ge=1, le=4, 
        description="Total perkiraan langkah penyelesaian dari dokumen SOP."
    )
    pesan: str = Field(
        ..., 
        description="Teks panduan langkah kepada pengguna dalam bahasa Indonesia polos tanpa markdown."
    )
    tindakan_berikutnya: Literal["tunggu_konfirmasi", "eskalasi_tiket", "selesai"] = Field(
        ..., 
        description="Instruksi alur selanjutnya bagi frontend."
    )
    sumber: List[SumberSitasi] = Field(
        default_factory=list,
        description="Daftar rujukan kutipan persis. Wajib terisi jika dapat_ditentukan bernilai 'ya'."
    )
```

---

## 2. Aturan Ketat Validasi Kontrak

1. **Daftar Nilai Tertutup (*Closed-Set Enums*):**  
   - `kategori` hanya boleh: `jaringan`, `email`, `aplikasi`, `perangkat`, `lainnya`.
   - `tingkat_urgensi` hanya boleh: `rendah`, `sedang`, `tinggi`.
   - `dapat_ditentukan` hanya boleh: `ya` atau `tidak`.
2. **Kondisi `dapat_ditentukan == 'tidak'`:**  
   Bila informasi tidak ditemukan di dokumen, medan `sumber` harus berupa daftar kosong `[]`, `langkah_ke` bernilai 1, dan `tindakan_berikutnya` diset ke `eskalasi_tiket`.
3. **Validasi Kutipan Persis (*Exact Substring Verification*):**  
   Fungsi validator memverifikasi bahwa string `kutipan` benar-benar ada di dalam teks dokumen sumber:
   $$\text{kutipan} \in \text{Teks Dokumen}(KB\text{-}XXX)$$
   Jika tidak cocok (berbeda 1 huruf sekalipun), respon ditolak sebagai cacat grounding.

---

## 3. Penanganan Kegagalan Tiga Langkah (*Three-Step Fallback*)

Untuk mencegah kegagalan parser merusak aplikasi, sistem menerapkan arsitektur pertahanan 3 lapis:

```text
┌────────────────────────────────────────────────────────┐
│ 1. Uji Validasi Skema (Pydantic ValidationError Check) │
└───────────────────────────┬────────────────────────────┘
                            │
               ┌────────────┴────────────┐
             [Valid]                  [Invalid]
               │                         │
               ▼                         ▼
        Teruskan ke Frontend     ┌──────────────────────────────────────────────────┐
                                 │ 2. Retry Otomatis (1 Kali)                       │
                                 │    Kirim ulang prompt + pesan kesalahan validasi │
                                 │    ke model gateway                              │
                                 └──────────────────────────┬───────────────────────┘
                                                            │
                                               ┌────────────┴────────────┐
                                             [Valid]                  [Tetap Gagal]
                                               │                         │
                                               ▼                         ▼
                                        Teruskan ke Frontend     ┌────────────────────────────────────────┐
                                                                 │ 3. Fail-Safe Deterministic Fallback    │
                                                                 │    Catat log error, buat objek aman    │
                                                                 │    status 'dapat_ditentukan: tidak'    │
                                                                 │    tawarkan tiket eskalasi ke teknisi  │
                                                                 └────────────────────────────────────────┘
```
