"""Unit test validasi integritas dataset 15 kasus uji (agents.md §8.1 Uji test_eval_set_valid).

Memastikan:
1. Dataset set-uji/15_kasus_uji.json berisi tepat 15 kasus (K=3).
2. Distribusi komposisi sesuai PRD §15 (6 khas, 4 klarifikasi, 3 tak berjawab, 2 injeksi).
3. Setiap artikel_target merujuk ke dokumen nyata di knowledge_base/ atau fixture K11.
"""

import json
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_available_kb_ids() -> set[str]:
    root = get_project_root()
    kb_dir = root / "knowledge_base"
    kb_ids = set()

    for md_file in kb_dir.glob("KB-*.md"):
        # Ekstrak article_id dari nama file atau front matter
        file_stem = md_file.stem
        # Format umum KB-001-xxx -> ambil KB-001
        parts = file_stem.split("-", 2)
        if len(parts) >= 2:
            article_id = f"{parts[0]}-{parts[1]}"
            kb_ids.add(article_id)

    return kb_ids


def test_eval_set_exists_and_count():
    """Dataset 15 kasus uji harus ada dan memuat tepat 15 item."""
    eval_file = get_project_root() / "set-uji" / "15_kasus_uji.json"
    assert eval_file.is_file(), f"Berkas {eval_file} tidak ditemukan"

    with open(eval_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    assert isinstance(cases, list)
    assert len(cases) == 15, f"Jumlah kasus uji harus tepat 15, ditemukan {len(cases)}"


def test_eval_set_composition():
    """Komposisi jenis kasus uji harus persis 6 khas, 4 klarifikasi, 3 tak berjawab, 2 injeksi."""
    eval_file = get_project_root() / "set-uji" / "15_kasus_uji.json"
    with open(eval_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    counts = {"khas": 0, "klarifikasi": 0, "tak_berjawab": 0, "injeksi": 0}
    for c in cases:
        jenis = c.get("jenis")
        assert jenis in counts, f"Jenis kasus tidak dikenal: {jenis}"
        counts[jenis] += 1

    assert counts["khas"] == 6, f"Kasus khas harus 6, ditemukan {counts['khas']}"
    assert counts["klarifikasi"] == 4, f"Kasus klarifikasi harus 4, ditemukan {counts['klarifikasi']}"
    assert counts["tak_berjawab"] == 3, f"Kasus tak berjawab harus 3, ditemukan {counts['tak_berjawab']}"
    assert counts["injeksi"] == 2, f"Kasus injeksi harus 2, ditemukan {counts['injeksi']}"


def test_eval_set_references_real_articles():
    """Setiap artikel_target yang tidak null harus merujuk ke artikel KB nyata atau fixture K11."""
    eval_file = get_project_root() / "set-uji" / "15_kasus_uji.json"
    fixture_file = get_project_root() / "backend" / "tests" / "fixtures" / "KB-TEST-injeksi.md"
    available_kbs = get_available_kb_ids()

    assert fixture_file.is_file(), "Fixture KB-TEST-injeksi.md harus ada untuk kasus injeksi K11"

    with open(eval_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    for c in cases:
        target = c.get("artikel_target")
        case_id = c.get("id")

        if target is not None:
            if target == "KB-TEST-injeksi":
                assert fixture_file.is_file(), f"Kasus {case_id} merujuk ke fixture yang tidak ada: {target}"
            else:
                assert target in available_kbs, f"Kasus {case_id} merujuk ke artikel yang tidak ada di KB: {target}"


def test_eval_set_required_fields():
    """Setiap item harus memuat seluruh field wajib dan kriteria evaluasi."""
    eval_file = get_project_root() / "set-uji" / "15_kasus_uji.json"
    with open(eval_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    for c in cases:
        assert "id" in c and c["id"].startswith("TC-")
        assert "jenis" in c
        assert "masukan" in c and len(c["masukan"]) > 0
        assert "jawaban_acuan" in c and len(c["jawaban_acuan"]) > 0
        assert "kriteria_evaluasi" in c and isinstance(c["kriteria_evaluasi"], dict)
