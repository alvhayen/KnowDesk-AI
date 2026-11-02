# Catatan Perubahan Instruksi Sistem (Prompts)

| Versi | Tanggal | Yang Diubah | Alasan | Akibat yang Teramati |
|---|---|---|---|---|
| **v1** | 2026-10-11 | Inisialisasi awal 6 sumbu instruksi helpdesk IT. | Fondasi sistem. | Model merespons terarah namun format output belum diikat enum tertutup. |
| **v2** | 2026-10-12 | Penambahan pembatasan format JSON ketat (Pydantic model sync), penegasan larangan markdown, dan integrasi field `dapat_ditentukan`. | Kebutuhan integrasi kontrak data terstruktur pada Tugas 5. | Parsing JSON mencapai 100% konsistensi pada 10 variasi input uji. |
