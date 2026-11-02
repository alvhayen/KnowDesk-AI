"""Script kalibrasi ambang batas retrieval RAG berbasis Dev Set (agents.md §2 R10, §3 K1, §6.4).

Menganalisis distribusi cosine similarity top-1 empiris pada dataset dev_set.json:
- 10 kueri relevan (harus lolos gerbang)
- 5 kueri ambigu
- 5 kueri out-of-scope (harus ditolak gerbang)

Melakukan grid scan ambang (0.25 s.d. 0.65) dengan prinsip 'condong ke menolak' (§6.4)
untuk merekomendasikan nilai optimal RAG_MIN_COSINE dan RAG_HIGH_COSINE.
Hasil disimpan ke bukti/kalibrasi-ambang-devset.json.
"""

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import aiomysql
import httpx
import numpy as np

# Pastikan path backend terdaftar
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import Settings
from scripts.ingest_kb import get_chunk_embedding
from tests.smoke_test_openrouter import get_active_settings


def compute_cosine_similarity(query_vec: np.ndarray, doc_matrix: np.ndarray) -> np.ndarray:
    """Menghitung cosine similarity vectorized antara 1 kueri dan matriks chunk."""
    q_norm = np.linalg.norm(query_vec)
    d_norms = np.linalg.norm(doc_matrix, axis=1)
    q_norm = 1.0 if q_norm == 0 else q_norm
    d_norms = np.where(d_norms == 0, 1.0, d_norms)
    return np.dot(doc_matrix, query_vec) / (q_norm * d_norms)


def load_dev_set_queries(path: Path) -> list[dict]:
    """Membaca berkas dev set JSON secara sinkron."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_calibration_report(path: Path, data: dict) -> None:
    """Menyimpan berkas laporan hasil kalibrasi secara sinkron."""
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def load_chunk_embeddings_from_db(settings: Settings) -> list[dict]:
    """Mengambil seluruh data chunk dan embedding dari database MySQL."""
    conn = await aiomysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DATABASE,
        autocommit=True,
    )
    chunks_data = []
    async with conn.cursor() as cur:
        await cur.execute("SELECT chunk_id, article_id, section_title, embedding_json FROM chunks;")
        rows = await cur.fetchall()
        for r in rows:
            chunks_data.append({
                "chunk_id": r[0],
                "article_id": r[1],
                "section_title": r[2],
                "embedding": np.array(json.loads(r[3]), dtype=np.float32),
            })
    conn.close()
    return chunks_data


async def run_threshold_calibration(
    dev_set_path: Path | None = None,
    output_path: Path | None = None,
) -> dict:
    """Menjalankan pengujian kueri dev set dan kalibrasi ambang gerbang RAG."""
    if dev_set_path is None:
        dev_set_path = root_dir / "set-uji" / "dev_set.json"
    if output_path is None:
        output_path = root_dir / "bukti" / "kalibrasi-ambang-devset.json"

    settings = get_active_settings()
    dev_queries = load_dev_set_queries(dev_set_path)

    print("==================================================")
    print("KnowDesk AI — Kalibrasi Ambang Retrieval Dev Set")
    print(f"Dataset Dev Set : {dev_set_path.name} ({len(dev_queries)} kueri)")
    print(f"Database Target : {settings.MYSQL_DATABASE}")
    print("==================================================")

    # 1. Muat chunk dari database
    chunks = await load_chunk_embeddings_from_db(settings)
    if not chunks:
        print("[FATAL] Tabel chunks kosong. Jalankan ingest_kb.py terlebih dahulu.")
        return {}

    doc_matrix = np.stack([c["embedding"] for c in chunks])
    print(f"[OK] Memuat {len(chunks)} chunk embedding dari database (dimensi: {doc_matrix.shape[1]}).\n")

    # 2. Uji tiap kueri dev set terhadap basis data
    query_results = []
    relevant_scores = []
    ambiguous_scores = []
    oos_scores = []

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        for q in dev_queries:
            q_id = q["id"]
            kategori = q["kategori_kueri"]
            text = q["kueri"]
            target_article = q.get("target_article")

            vec, provider = await get_chunk_embedding(text, settings, http_client, dimension=doc_matrix.shape[1])
            q_vec = np.array(vec, dtype=np.float32)

            similarities = compute_cosine_similarity(q_vec, doc_matrix)
            top_idx = int(np.argmax(similarities))
            top_score = round(float(similarities[top_idx]), 4)
            top_chunk = chunks[top_idx]

            is_correct_article = (top_chunk["article_id"] == target_article) if target_article else None

            res_entry = {
                "id": q_id,
                "kategori": kategori,
                "kueri": text,
                "target_article": target_article,
                "top1_score": top_score,
                "top1_article": top_chunk["article_id"],
                "top1_chunk_id": top_chunk["chunk_id"],
                "top1_section": top_chunk["section_title"],
                "is_correct_article": is_correct_article,
                "embedding_provider": provider,
            }
            query_results.append(res_entry)

            if kategori == "relevan":
                relevant_scores.append(top_score)
            elif kategori == "ambigu":
                ambiguous_scores.append(top_score)
            elif kategori == "out_of_scope":
                oos_scores.append(top_score)

            mark = "[MATCH]" if is_correct_article else ("[REJECT]" if target_article is None else "[MISS]")
            print(f"[{q_id}] ({kategori:<12}) skor: {top_score:.4f} -> {top_chunk['article_id']} {mark}")

    # 3. Grid scan threshold 0.25 s.d. 0.65
    threshold_grid = [round(float(t), 2) for t in np.arange(0.25, 0.66, 0.05)]
    grid_evaluation = []

    for tau in threshold_grid:
        # Relevan (10): lolos gerbang jika skor >= tau
        tp = sum(1 for s in relevant_scores if s >= tau)
        fn = len(relevant_scores) - tp

        # Out-of-scope (5): ditolak jika skor < tau
        fp_oos = sum(1 for s in oos_scores if s >= tau)
        tn_oos = len(oos_scores) - fp_oos

        # Ambigu (5): idealnya ditolak jika terlalu umum
        fp_amb = sum(1 for s in ambiguous_scores if s >= tau)

        precision = round(tp / (tp + fp_oos), 4) if (tp + fp_oos) > 0 else 0.0
        recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0.0

        grid_evaluation.append({
            "threshold": tau,
            "tp_relevan": tp,
            "fn_relevan": fn,
            "fp_out_of_scope": fp_oos,
            "tn_out_of_scope": tn_oos,
            "fp_ambigu": fp_amb,
            "precision_vs_oos": precision,
            "recall": recall,
            "f1_score": f1,
        })

    # 4. Tentukan Rekomendasi Empiris:
    # Prinsip §6.4: 'condong ke menolak' -> pilih threshold terendah dengan FP_out_of_scope = 0
    safe_thresholds = [g for g in grid_evaluation if g["fp_out_of_scope"] == 0]
    if safe_thresholds:
        # Ambil threshold dengan F1 tertinggi di antara yang aman (FP = 0)
        recommended_min = max(safe_thresholds, key=lambda x: (x["f1_score"], x["recall"]))["threshold"]
    else:
        recommended_min = 0.35

    # RAG_HIGH_COSINE ditentukan dari persentil-75 atau batas atas skor kueri relevan
    median_rel = float(np.median(relevant_scores))
    recommended_high = round(max(recommended_min + 0.15, median_rel), 2)

    print("\n--------------------------------------------------")
    print("Hasil Grid Scan Ambang (Relevan vs Out-of-Scope):")
    print("--------------------------------------------------")
    print("Ambang | TP (Rel) | FP (OOS) | Precision | Recall | F1-Score")
    print("-------|----------|----------|-----------|--------|---------")
    for g in grid_evaluation:
        star = " *" if g["threshold"] == recommended_min else ""
        print(f" {g['threshold']:.2f}  |   {g['tp_relevan']:>2}/10   |   {g['fp_out_of_scope']:>2}/5    |  {g['precision_vs_oos']:.4f}   | {g['recall']:.4f} | {g['f1_score']:.4f}{star}")

    print("\n--------------------------------------------------")
    print("Statistik Skor Empiris:")
    print(f"- Kueri Relevan      : Min={min(relevant_scores):.4f}, Max={max(relevant_scores):.4f}, Mean={np.mean(relevant_scores):.4f}")
    print(f"- Kueri Ambigu       : Min={min(ambiguous_scores):.4f}, Max={max(ambiguous_scores):.4f}, Mean={np.mean(ambiguous_scores):.4f}")
    print(f"- Kueri Out-of-Scope : Min={min(oos_scores):.4f}, Max={max(oos_scores):.4f}, Mean={np.mean(oos_scores):.4f}")
    print("--------------------------------------------------")
    print("[REKOMENDASI EMPIRIS]")
    print(f"  RAG_MIN_COSINE  : {recommended_min:.2f} (Memisahkan kueri relevan dari out-of-scope)")
    print(f"  RAG_HIGH_COSINE : {recommended_high:.2f} (Batas kategori keyakinan tinggi)")
    print("--------------------------------------------------")

    report_data = {
        "timestamp": datetime.now(UTC).isoformat(),
        "dev_set_size": len(dev_queries),
        "rekomendasi": {
            "RAG_MIN_COSINE": recommended_min,
            "RAG_HIGH_COSINE": recommended_high,
            "alasan": f"Ambang {recommended_min:.2f} memberikan 0 FP pada kueri out-of-scope (kondisi aman per §6.4), dengan recall {next(g['recall'] for g in grid_evaluation if g['threshold'] == recommended_min):.2f}.",
        },
        "distribusi_skor": {
            "relevan": {
                "min": min(relevant_scores),
                "max": max(relevant_scores),
                "mean": round(float(np.mean(relevant_scores)), 4),
                "median": round(float(np.median(relevant_scores)), 4),
            },
            "ambigu": {
                "min": min(ambiguous_scores),
                "max": max(ambiguous_scores),
                "mean": round(float(np.mean(ambiguous_scores)), 4),
            },
            "out_of_scope": {
                "min": min(oos_scores),
                "max": max(oos_scores),
                "mean": round(float(np.mean(oos_scores)), 4),
            },
        },
        "grid_scan": grid_evaluation,
        "detail_kueri": query_results,
    }

    save_calibration_report(output_path, report_data)
    print(f"[SELESAI] Hasil kalibrasi dicatat di: {output_path}")
    return report_data


def main():
    parser = argparse.ArgumentParser(description="KnowDesk AI Retrieval Threshold Calibration")
    parser.add_argument("--dev-set", default=str(root_dir / "set-uji" / "dev_set.json"))
    parser.add_argument("--output", default=str(root_dir / "bukti" / "kalibrasi-ambang-devset.json"))

    args = parser.parse_args()
    asyncio.run(
        run_threshold_calibration(
            dev_set_path=Path(args.dev_set),
            output_path=Path(args.output),
        )
    )


if __name__ == "__main__":
    main()
