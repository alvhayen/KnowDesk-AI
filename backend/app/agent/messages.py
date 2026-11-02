"""Pesan templat deterministik sistem KnowDesk AI (agents.md §6.6).

Digunakan langsung oleh kode orchestrator tanpa memanggil LLM untuk menjamin
konsistensi, keandalan, dan penghematan biaya token.
"""

# Respon ketika artikel tidak ditemukan di Knowledge Base (cosine top-1 < ambang)
MSG_TIDAK_DITEMUKAN = (
    "Informasi untuk masalah ini tidak tersedia di panduan IT kami. "
    "Saya tidak akan menebak. Mau saya buatkan draf tiket untuk teknisi?"
)

# Header pemberitahuan batas langkah tercapai
MSG_BATAS_LANGKAH = "Saya sudah mencoba {n} langkah. Berikut draf tiket untuk teknisi:"

# Respon penutupan ketika masalah telah teratasi
MSG_SELESAI = "Masalah ditandai teratasi. Sesi ini selesai."

# Respon setelah tiket berhasil dikonfirmasi dan dikirim
MSG_TIKET_TERKIRIM = "Tiket {id} telah dikirim. Teknisi akan menghubungi Anda."

# Respon setelah draf tiket dibatalkan
MSG_TIKET_DIBATALKAN = "Draf tiket dibatalkan. Sesi ini ditutup."
