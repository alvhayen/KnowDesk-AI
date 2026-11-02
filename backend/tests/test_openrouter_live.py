"""Tes integrasi langsung OpenRouter API & validasi pencatatan biaya aktual (agents.md §2 R7, §3 K15, §12 M0).

Menguji secara live:
1. Panggilan chat completion aktual dengan function calling (search_kb).
2. Verifikasi metadata usage token riil dari API (bukan konstanta / mock).
3. Panggilan embedding riil / K15 multilingual fallback.
4. Validasi perhitungan biaya aktual berdasarkan pricing.json.
5. Integritas file bukti bukti/smoke-test-fondasi.json.
"""

import json
import sys
from pathlib import Path

import pytest

backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import Settings

from tests.smoke_test_openrouter import (
    calculate_token_cost,
    execute_openrouter_chat_smoke,
    execute_openrouter_embedding_smoke,
    get_active_settings,
)


@pytest.fixture(scope="module")
def active_settings() -> Settings:
    return get_active_settings()


@pytest.mark.asyncio
async def test_live_chat_completion_with_function_calling(active_settings: Settings):
    """Panggilan nyata chat completion OpenRouter wajib sukses dan mengeksekusi function calling."""
    result = await execute_openrouter_chat_smoke(active_settings)
    if result.get("status") == "skipped":
        pytest.skip(result.get("reason", "OpenRouter API call dilewati"))
    err_msg = str(result.get("error", "")).lower()
    if any(k in err_msg for k in ("timeout", "overloaded", "502", "500", "provider returned error", "internal server error")):
        pytest.skip(f"OpenRouter upstream provider sedang mengalami gangguan sementara: {result.get('error')}")

    assert result["status"] == "passed", f"Panggilan chat gagal: {result.get('error')}"
    assert result["status_code"] == 200
    assert result["supports_tool_calls"] is True

    # Verifikasi tool yang dipanggil adalah search_kb
    tool_names = [call.get("function", {}).get("name") for call in result.get("tool_calls", [])]
    assert "search_kb" in tool_names

    # Verifikasi pencatatan token riil dari respons API (Aturan R7)
    usage = result["usage"]
    assert usage["prompt_tokens"] > 0
    assert usage["completion_tokens"] > 0
    assert usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"]
    assert result["latency_ms"] > 0


@pytest.mark.asyncio
async def test_live_embedding_and_k15(active_settings: Settings):
    """Panggilan nyata embedding OpenRouter / Fallback K15 wajib menghasilkan vektor embedding."""
    result = await execute_openrouter_embedding_smoke(active_settings)
    assert result["status"] == "passed", f"Embedding gagal: {result.get('error')}"
    assert result["embedding_dimension"] > 0
    assert result["usage"]["prompt_tokens"] > 0


def test_token_cost_calculation():
    """Perhitungan biaya harus membaca tarif pricing.json dan menghitung dengan akurat."""
    mock_usage = {"prompt_tokens": 300, "completion_tokens": 50, "total_tokens": 350}
    cost_info = calculate_token_cost("meta-llama/llama-3.1-8b-instruct", mock_usage)

    assert cost_info["rates_found"] is True
    assert cost_info["prompt_tokens"] == 300
    assert cost_info["completion_tokens"] == 50
    # 300 * 0.000000055 + 50 * 0.000000055 = 350 * 5.5e-8 = 1.925e-5 USD
    assert cost_info["cost_usd"] == pytest.approx(1.925e-05, rel=1e-4)
    assert cost_info["cost_idr"] == pytest.approx(1.925e-05 * 16000, rel=1e-4)


def test_smoke_evidence_file_integrity():
    """File bukti smoke-test-fondasi.json wajib berstatus 'success' dengan timestamp aktual."""
    evidence_path = root_dir / "bukti" / "smoke-test-fondasi.json"
    assert evidence_path.is_file(), "File bukti/smoke-test-fondasi.json tidak ditemukan"

    with open(evidence_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("status") == "success"
    assert "timestamp" in data
    assert data["openrouter"]["chat_smoke"]["status"] == "passed"
    assert data["openrouter"]["embedding_smoke"]["status"] == "passed"
    assert data["mysql"]["status"] == "passed"
    assert data["total_pemakaian_dan_biaya"]["total_tokens"] > 0
