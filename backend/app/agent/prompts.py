"""Pemuat instruksi sistem prompt runtime (agents.md §2 R8, §7).

Prompt disimpan dalam direktori instruksi/vN.md dan dimuat saat runtime.
Dilarang menggunakan prompt panjang inline di dalam kode Python.
"""

from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INSTRUCTION_DIR = BASE_DIR / "instruksi"


@lru_cache(maxsize=4)
def load_system_prompt(version: str = "v1") -> str:
    """Memuat prompt sistem dari file instruksi/v{N}.md."""
    prompt_file = INSTRUCTION_DIR / f"{version}.md"
    if not prompt_file.is_file():
        # Fallback jika dijalankan dari subdirektori lain
        alt_file = BASE_DIR.parent / "instruksi" / f"{version}.md"
        if alt_file.is_file():
            prompt_file = alt_file
        else:
            raise FileNotFoundError(f"File instruksi sistem tidak ditemukan: {prompt_file}")

    return prompt_file.read_text(encoding="utf-8")


def format_context_prompt(
    system_prompt: str,
    kb_context: str | None = None,
    user_message: str | None = None,
) -> str:
    """Membungkus data dokumen dan masukan pengguna dengan delimiter higienis (agents.md §7)."""
    parts = [system_prompt]

    if kb_context:
        # Escape tag penutup di dalam konteks KB
        escaped_kb = kb_context.replace("</konteks_kb>", "&lt;/konteks_kb&gt;")
        parts.append(f"\n<konteks_kb>\n{escaped_kb}\n</konteks_kb>")

    if user_message:
        # Escape tag penutup di dalam pesan pengguna
        escaped_user = user_message.replace("</pesan_pengguna>", "&lt;/pesan_pengguna&gt;")
        parts.append(f"\n<pesan_pengguna>\n{escaped_user}\n</pesan_pengguna>")

    return "\n".join(parts)
