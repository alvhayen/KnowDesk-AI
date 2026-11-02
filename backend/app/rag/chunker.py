"""Engine chunking deterministik dokumen Knowledge Base (agents.md §3 K8, K19, §5.1, §5.2, §6.4).

Prinsip:
1. Parsing metadata YAML front matter secara ringan tanpa dependensi parser berat (K19).
2. Membagi dokumen per `## Bagian N:` sebagai unit chunk dengan overlap 50 kata (§6.4).
3. Mendeteksi heading `### Langkah N:` secara deterministik untuk menghitung langkah_total_tersedia (K8).
4. Menjaga integritas data: Dilarang memodifikasi atau 'membersihkan' teks KB-005 dan KB-008 (§5.2).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StepInfo:
    """Representasi langkah solusi individual dalam dokumen KB."""

    step_number: int
    title: str
    content: str
    heading: str


@dataclass
class DocumentChunk:
    """Potongan unit chunk per bagian dokumen untuk retrieval RAG."""

    chunk_id: str
    article_id: str
    section_number: int
    section_title: str
    chunk_text: str
    step_number: int | None = None
    step_numbers: list[int] = field(default_factory=list)
    steps: list[StepInfo] = field(default_factory=list)


@dataclass
class ParsedArticle:
    """Dokumen artikel lengkap setelah diurai front matter, chunk, dan langkahnya."""

    article_id: str
    judul: str
    kategori: str
    status: str
    asal: str
    raw_content: str
    pola: str | None = None
    tanggal: str | None = None
    chunks: list[DocumentChunk] = field(default_factory=list)
    steps: list[StepInfo] = field(default_factory=list)
    langkah_total_tersedia: int = 0

    def get_step(self, step_number: int) -> StepInfo | None:
        """Mengambil detail langkah solusi spesifik berdasarkan nomor urut (1-indexed)."""
        for s in self.steps:
            if s.step_number == step_number:
                return s
        return None

    def get_step_text(self, step_number: int) -> str | None:
        """Mengambil teks solusi langkah ke-N saja untuk dikirim ke LLM (Aturan K8)."""
        step = self.get_step(step_number)
        return step.content if step else None


def parse_yaml_front_matter(content: str) -> tuple[dict[str, str], str]:
    """Mengekstraksi metadata YAML front matter di awal file markdown."""
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        return {}, content

    yaml_block = match.group(1)
    body = content[match.end():]
    metadata: dict[str, str] = {}

    for line in yaml_block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            metadata[key.strip()] = val.strip()

    return metadata, body


def extract_steps_from_text(text: str) -> list[StepInfo]:
    """Mendeteksi heading `### Langkah N:` secara deterministik dan mengekstrak teksnya (K8)."""
    step_pattern = re.compile(r"^###\s+Langkah\s+(\d+):\s*(.*?)$", re.MULTILINE)
    matches = list(step_pattern.finditer(text))
    if not matches:
        return []

    steps: list[StepInfo] = []
    for i, m in enumerate(matches):
        step_num = int(m.group(1))
        title = m.group(2).strip()
        heading = m.group(0).strip()

        start_idx = m.end()
        end_idx = matches[i + 1].start() if (i + 1 < len(matches)) else len(text)
        step_content = text[start_idx:end_idx].strip()

        steps.append(
            StepInfo(
                step_number=step_num,
                title=title,
                content=step_content,
                heading=heading,
            )
        )
    return steps


def chunk_markdown_article(raw_markdown: str, overlap_words: int = 50) -> ParsedArticle:
    """Memecah teks artikel markdown menjadi unit chunk per `## Bagian N:` dan daftar langkah.

    Args:
        raw_markdown: Teks lengkap markdown termasuk front matter.
        overlap_words: Jumlah kata overlap dari bagian sebelumnya (default: 50 kata per §6.4).

    Returns:
        ParsedArticle dengan metadata, list chunk, dan list langkah terhitung.
    """
    metadata, body = parse_yaml_front_matter(raw_markdown)

    article_id = metadata.get("article_id", "KB-UNKNOWN")
    judul = metadata.get("judul", "Tanpa Judul")
    kategori = metadata.get("kategori", "lainnya")
    status = metadata.get("status", "published")
    asal = metadata.get("asal", "buatan sendiri (sintetis)")
    pola = metadata.get("pola")
    tanggal = metadata.get("tanggal")

    # Temukan seluruh heading '## Bagian N: ...'
    section_pattern = re.compile(r"^##\s+Bagian\s+(\d+):\s*(.*?)$", re.MULTILINE)
    section_matches = list(section_pattern.finditer(body))

    chunks: list[DocumentChunk] = []
    all_article_steps: list[StepInfo] = []

    # Ekstrak seluruh langkah yang ada di seluruh badan artikel
    all_article_steps = extract_steps_from_text(body)
    total_steps = len(all_article_steps)

    prev_section_words: list[str] = []

    for i, match in enumerate(section_matches):
        sec_num = int(match.group(1))
        sec_title_name = match.group(2).strip()
        full_sec_title = f"Bagian {sec_num}: {sec_title_name}"

        start_pos = match.end()
        end_pos = section_matches[i + 1].start() if (i + 1 < len(section_matches)) else len(body)
        raw_sec_text = body[start_pos:end_pos].strip()

        # Ekstrak langkah-langkah yang berada di dalam bagian ini
        sec_steps = extract_steps_from_text(raw_sec_text)
        sec_step_numbers = [s.step_number for s in sec_steps]

        # Terapkan overlap kata dari bagian sebelumnya (agents.md §6.4)
        if overlap_words > 0 and prev_section_words:
            overlap_prefix = " ".join(prev_section_words[-overlap_words:])
            chunk_text = f"{overlap_prefix}\n\n{raw_sec_text}"
        else:
            chunk_text = raw_sec_text

        # Simpan kata-kata dari bagian murni (tanpa overlap sebelumnya) untuk bagian berikutnya
        prev_section_words = raw_sec_text.split()

        # Tentukan step_number representatif untuk kolom tabel MySQL:
        # Jika bagian memuat 1 langkah saja -> step_number langkah tersebut.
        # Jika bagian memuat beberapa langkah (misal Bagian 3) -> step_number pertama atau None.
        rep_step_num = sec_step_numbers[0] if len(sec_step_numbers) == 1 else (sec_step_numbers[0] if sec_step_numbers else None)

        chunk_id = f"{article_id}-chunk-{sec_num}"
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                article_id=article_id,
                section_number=sec_num,
                section_title=full_sec_title,
                chunk_text=chunk_text,
                step_number=rep_step_num,
                step_numbers=sec_step_numbers,
                steps=sec_steps,
            )
        )

    return ParsedArticle(
        article_id=article_id,
        judul=judul,
        kategori=kategori,
        status=status,
        asal=asal,
        pola=pola,
        tanggal=tanggal,
        raw_content=raw_markdown,
        chunks=chunks,
        steps=all_article_steps,
        langkah_total_tersedia=total_steps,
    )


def parse_article_file(file_path: Path | str, overlap_words: int = 50) -> ParsedArticle:
    """Membaca berkas markdown dari disk dan menguraikannya menjadi ParsedArticle."""
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    return chunk_markdown_article(content, overlap_words=overlap_words)
