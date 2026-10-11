"""Runner orkestrator smoke test infrastruktur M0 fondasi.

Menjalankan pengujian:
1. OpenRouter Chat Completion + Tool Calling
2. OpenRouter Embedding
3. MySQL Connectivity
Menghitung estimasi biaya aktual dari usage riil (R7) menggunakan backend/config/pricing.json,
serta menyimpan bukti terstruktur ke bukti/smoke-test-fondasi.json.
"""

import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Setup path
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from tests.smoke_test_mysql import execute_mysql_smoke
from tests.smoke_test_openrouter import (
    execute_openrouter_chat_smoke,
    execute_openrouter_embedding_smoke,
    get_active_settings,
)


def load_pricing() -> dict:
    pricing_file = backend_dir / "config" / "pricing.json"
    if pricing_file.is_file():
        with open(pricing_file, "r", encoding="utf-8") as f:
            return json.load(f).get("models", {})
    return {}


def calculate_cost(model_name: str, usage: dict, pricing_table: dict) -> dict:
    model_pricing = pricing_table.get(model_name, {})
    in_rate = model_pricing.get("biaya_input_per_token", 0.0)
    out_rate = model_pricing.get("biaya_output_per_token", 0.0)

    prompt_tokens = usage.get("prompt_tokens") or 0
    completion_tokens = usage.get("completion_tokens") or 0

    cost_usd = (prompt_tokens * in_rate) + (completion_tokens * out_rate)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost_usd": round(cost_usd, 8),
        "rates_found": bool(model_pricing),
    }


async def run_all_smoke_tests():
    settings = get_active_settings()
    pricing_table = load_pricing()
    timestamp = datetime.now(UTC).isoformat()

    print(f"[{timestamp}] Memulai Smoke Test Infrastruktur KnowDesk AI (K=3)...")

    # 1. Chat Smoke Test
    print("-> Menguji OpenRouter Chat + Tool Call...")
    chat_result = await execute_openrouter_chat_smoke(settings)
    if chat_result.get("status") == "passed" and "usage" in chat_result:
        chat_result["calculated_cost"] = calculate_cost(
            settings.CHAT_MODEL, chat_result["usage"], pricing_table
        )

    # 2. Embedding Smoke Test
    print("-> Menguji OpenRouter Embedding (K15)...")
    embed_result = await execute_openrouter_embedding_smoke(settings)
    if embed_result.get("status") == "passed" and "usage" in embed_result:
        embed_result["calculated_cost"] = calculate_cost(
            settings.EMBEDDING_MODEL, embed_result["usage"], pricing_table
        )

    # 3. MySQL Smoke Test
    print("-> Menguji MySQL Async Connectivity (aiomysql)...")
    mysql_result = await execute_mysql_smoke(settings)

    # Susun Laporan Bukti
    evidence_data = {
        "timestamp": timestamp,
        "fase": "M0 Fondasi (Fase 2)",
        "openrouter": {
            "chat_model": settings.CHAT_MODEL,
            "embedding_model": settings.EMBEDDING_MODEL,
            "chat_smoke": chat_result,
            "embedding_smoke": embed_result,
        },
        "mysql": mysql_result,
    }

    # Simpan ke bukti/smoke-test-fondasi.json
    evidence_path = root_dir / "bukti" / "smoke-test-fondasi.json"
    save_evidence_report(evidence_data, evidence_path)

    print(f"\n[SELESAI] Hasil disimpan ke {evidence_path}")
    print(f"- Chat Status     : {chat_result.get('status')}")
    print(f"- Embedding Status: {embed_result.get('status')}")
    print(f"- MySQL Status    : {mysql_result.get('status')}")

    return evidence_data


def save_evidence_report(evidence_data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evidence_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(run_all_smoke_tests())

