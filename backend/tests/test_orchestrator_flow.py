"""Unit test lengkap untuk alur Orchestrator, Guardrails, dan Router (agents.md §2 R3, R4, §3 K2, K3, K4, K10, §6.1, §6.2).

Mencakup pengujian wajib:
1. Batas klarifikasi (maks 2x per konfigurasi, pada giliran ke-3 dipaksa retrieval).
2. Langkah ke-4 tampil sebelum eskalasi pembuatan tiket (Keputusan K2).
3. Penolakan keras tool draft_ticket jika dipanggil mendahului retrieval (Aturan R3).
4. Output guard menolak kutipan halusinasi yang bukan substring dari teks langkah (Keputusan K10).
5. Konfirmasi tiket satu jalur via POST /api/ticket/confirm (Aturan R4 & Keputusan K4).
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agent.orchestrator import AgentOrchestrator
from app.config import Settings
from app.guardrails.output_guard import OutputGuardError, validate_source_quotes
from app.llm.client import LLMResponse
from app.schemas.contracts import (
    ChatRequest,
    SumberKutipan,
    TicketConfirmRequest,
)
from app.schemas.state import SessionStatus, is_tool_allowed

# =============================================================================
# 1. Uji Batas Klarifikasi (Maksimal 2x, agents.md §6.2 #1)
# =============================================================================


@pytest.mark.asyncio
async def test_clarification_limit_max_2():
    """Percakapan ambigu hanya boleh mengklarifikasi maksimal 2x, giliran berikutnya wajib retrieval."""
    mock_db = MagicMock()
    mock_db.record_trace = AsyncMock()

    # Giliran 1: Sesi baru (clarification_count = 0)
    mock_db.get_session = AsyncMock(
        return_value={
            "session_id": "sess-clarify-1",
            "status": "clarifying",
            "current_step": 0,
            "clarification_count": 0,
            "artikel_terpilih": None,
            "draft_ticket_id": None,
        }
    )
    mock_db.update_session = AsyncMock()

    mock_llm = MagicMock()
    # LLM memilih memberikan klarifikasi tanpa memanggil tool
    mock_llm.chat_completion = AsyncMock(
        return_value=LLMResponse(
            content="Apakah komputer Anda terhubung melalui kabel LAN atau Wi-Fi?",
            tool_calls=[],
            prompt_tokens=50,
            completion_tokens=20,
            total_tokens=70,
            model="mock-model",
            latency_ms=100,
            raw_response={},
        )
    )

    settings = Settings(
        CHAT_MODEL="mock",
        EMBEDDING_MODEL="mock",
        AGENT_MAX_CLARIFICATIONS=2,
    )
    orchestrator = AgentOrchestrator(
        database=mock_db,
        llm_client=mock_llm,
        settings=settings,
    )

    req1 = ChatRequest(
        session_id="sess-clarify-1",
        message="Komputer saya rusak tidak bisa internet",
    )
    res1 = await orchestrator.process_turn(req1)
    assert res1.tipe_respons == "klarifikasi"
    # Pastikan clarification_count bertambah jadi 1
    mock_db.update_session.assert_called_with(
        session_id="sess-clarify-1",
        status=SessionStatus.CLARIFYING.value,
        current_step=0,
        clarification_count=1,
    )

    # Giliran 2: clarification_count = 1 -> Masih boleh klarifikasi ke-2
    mock_db.get_session = AsyncMock(
        return_value={
            "session_id": "sess-clarify-1",
            "status": "clarifying",
            "current_step": 0,
            "clarification_count": 1,
            "artikel_terpilih": None,
            "draft_ticket_id": None,
        }
    )
    res2 = await orchestrator.process_turn(req1)
    assert res2.tipe_respons == "klarifikasi"

    # Giliran 3: clarification_count = 2 (sudah mencapai batas maksimal 2x)
    # Orchestrator WAJIB memaksakan tool_choice search_kb dan TIDAK boleh klarifikasi lagi!
    mock_db.get_session = AsyncMock(
        return_value={
            "session_id": "sess-clarify-1",
            "status": "clarifying",
            "current_step": 0,
            "clarification_count": 2,
            "artikel_terpilih": None,
            "draft_ticket_id": None,
        }
    )

    # Simulasikan hasil search_kb di mock_llm (dipaksa tool call search_kb)
    mock_llm.chat_completion = AsyncMock(
        return_value=LLMResponse(
            content="",
            tool_calls=[
                {
                    "function": {
                        "name": "search_kb",
                        "arguments": '{"query": "komputer rusak internet"}',
                    }
                }
            ],
            prompt_tokens=60,
            completion_tokens=25,
            total_tokens=85,
            model="mock-model",
            latency_ms=120,
            raw_response={},
        )
    )
    mock_db.get_all_chunks = AsyncMock(return_value=[])  # Hasil kosong -> tidak_ditemukan

    res3 = await orchestrator.process_turn(req1)
    # Pada giliran ke-3, respons TIDAK BOLEH klarifikasi lagi! (bisa tidak_ditemukan atau langkah)
    assert res3.tipe_respons != "klarifikasi"
    assert res3.tipe_respons == "tidak_ditemukan"


# =============================================================================
# 2. Uji Langkah ke-4 Tampil Sebelum Eskalasi (Keputusan Kanonik K2)
# =============================================================================


@pytest.mark.asyncio
async def test_step_4_displays_before_escalation_k2():
    """Langkah ke-4 wajib disajikan kepada pengguna, eskalasi hanya terjadi jika langkah 4 masih 'belum'."""
    raw_content = """---
article_id: KB-001
judul: Panduan Troubleshooting Koneksi Wi-Fi Kantor
kategori: jaringan
status: published
---
## Bagian 1: Pengenalan
### Langkah 1: Periksa sakelar Wi-Fi
Pastikan Wi-Fi aktif.
### Langkah 2: Lupakan jaringan kantor
Lupakan jaringan lalu sambung ulang.
### Langkah 3: Perbarui alamat IP
Jalankan ipconfig release dan renew.
### Langkah 4: Hubungkan ke jaringan cadangan
Gunakan SSID cadangan di ruang rapat.
"""
    mock_db = MagicMock()
    mock_db.record_trace = AsyncMock()
    mock_db.get_published_article = AsyncMock(
        return_value={
            "article_id": "KB-001",
            "judul": "Panduan Troubleshooting Koneksi Wi-Fi Kantor",
            "kategori": "jaringan",
            "raw_content": raw_content,
        }
    )
    mock_db.update_session = AsyncMock()
    mock_db.create_ticket = AsyncMock()

    mock_llm = MagicMock()
    mock_llm.chat_completion = AsyncMock(
        return_value=LLMResponse(
            content='{"pesan": "Gunakan SSID cadangan di ruang rapat.", "sumber": [{"article_id": "KB-001", "section": "Langkah 4", "kutipan": "Gunakan SSID cadangan di ruang rapat"}]}',
            tool_calls=[],
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="mock",
            latency_ms=200,
            raw_response={},
        )
    )

    settings = Settings(CHAT_MODEL="mock", EMBEDDING_MODEL="mock", AGENT_MAX_STEPS=4)
    orchestrator = AgentOrchestrator(database=mock_db, llm_client=mock_llm, settings=settings)

    # 1. Sesi berada di Langkah 3, pengguna menjawab 'belum'
    mock_db.get_session = AsyncMock(
        return_value={
            "session_id": "sess-step-4",
            "status": SessionStatus.AWAITING_CONFIRM.value,
            "current_step": 3,
            "clarification_count": 0,
            "artikel_terpilih": "KB-001",
            "draft_ticket_id": None,
        }
    )

    req_step3 = ChatRequest(
        session_id="sess-step-4",
        message="Langkah 3 sudah dicoba tapi masih belum bisa",
        confirmation="belum",
    )

    res_step4 = await orchestrator.process_turn(req_step3)

    # VERIFIKASI K2: Langkah ke-4 WAJIB TAMPIL (bukan draf tiket!)
    assert res_step4.tipe_respons == "langkah_solusi"
    assert res_step4.langkah_saat_ini == 4
    assert res_step4.draf_tiket is None
    assert res_step4.memerlukan_konfirmasi is True

    # 2. Pengguna berada di Langkah 4 dan menjawab 'belum' lagi -> BARU ESKALASI TIKET
    mock_db.get_session = AsyncMock(
        return_value={
            "session_id": "sess-step-4",
            "status": SessionStatus.AWAITING_CONFIRM.value,
            "current_step": 4,
            "clarification_count": 0,
            "artikel_terpilih": "KB-001",
            "draft_ticket_id": None,
        }
    )

    req_step4_belum = ChatRequest(
        session_id="sess-step-4",
        message="Tetap tidak bisa terhubung",
        confirmation="belum",
    )

    res_escalated = await orchestrator.process_turn(req_step4_belum)

    # VERIFIKASI: Setelah langkah 4 dicoba dan 'belum', baru membuat draf tiket
    assert res_escalated.tipe_respons == "draf_tiket"
    assert res_escalated.draf_tiket is not None
    assert res_escalated.draf_tiket.ticket_id.startswith("TK-")
    assert mock_db.create_ticket.called


# =============================================================================
# 3. Uji Penolakan draft_ticket Mendahului Retrieval (Aturan R3 & §6.3)
# =============================================================================


def test_draft_ticket_rejected_before_retrieval_r3():
    """Tool draft_ticket wajib ditolak keras oleh kode jika dipanggil pada state sebelum eskalasi."""
    # Penegakan allowlist kode:
    assert not is_tool_allowed(SessionStatus.IDLE, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.CLARIFYING, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.RETRIEVING, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.GUIDING, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.AWAITING_CONFIRM, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.RESOLVED, "draft_ticket")

    # Hanya diizinkan pada status ESCALATING
    assert is_tool_allowed(SessionStatus.ESCALATING, "draft_ticket")


# =============================================================================
# 4. Uji Output Guard Menolak Kutipan Halusinasi (Keputusan Kanonik K10)
# =============================================================================


def test_output_guard_rejects_hallucinated_quote_k10():
    """Output guard wajib menolak kutipan yang bukan substring dari teks dokumen yang dikirim ke model."""
    step_doc_text = (
        "Buka menu Pengaturan Jaringan pada laptop Anda. "
        "Pilih SSID Wi-Fi kantor dan klik Lupakan Jaringan. "
        "Nyalakan ulang adaptor Wi-Fi lalu sambungkan kembali."
    )

    # 1. Kutipan valid (ada di dalam teks langkah)
    valid_quotes = [
        SumberKutipan(
            article_id="KB-001",
            section="Bagian 3",
            judul="Wi-Fi Kantor",
            kutipan="klik Lupakan Jaringan",
        ),
        SumberKutipan(
            article_id="KB-001",
            section="Bagian 3",
            judul="Wi-Fi Kantor",
            kutipan="Nyalakan ulang adaptor Wi-Fi",
        ),
    ]
    assert validate_source_quotes(valid_quotes, "KB-001", step_doc_text) is True

    # 2. Kutipan halusinasi (teks mengarang / tidak ada di dokumen)
    hallucinated_quotes = [
        SumberKutipan(
            article_id="KB-001",
            section="Bagian 3",
            judul="Wi-Fi Kantor",
            kutipan="Ganti kabel fiber optic di router pusat kantor",  # HALUSINASI
        )
    ]
    with pytest.raises(OutputGuardError) as exc_info:
        validate_source_quotes(hallucinated_quotes, "KB-001", step_doc_text)
    assert "bukan substring" in str(exc_info.value) or "halusinasi" in str(exc_info.value)

    # 3. Artikel ID tidak cocok
    wrong_article_quotes = [
        SumberKutipan(
            article_id="KB-999",  # SALAH
            section="Bagian 3",
            judul="Wi-Fi Kantor",
            kutipan="klik Lupakan Jaringan",
        )
    ]
    with pytest.raises(OutputGuardError) as exc_info:
        validate_source_quotes(wrong_article_quotes, "KB-001", step_doc_text)
    assert "merujuk article_id 'KB-999'" in str(exc_info.value)


# =============================================================================
# 5. Uji Konfirmasi Tiket Satu Jalur & Penyelesaian Sesi (K3 & K4)
# =============================================================================


@pytest.mark.asyncio
async def test_session_success_confirmation_k3():
    """Pengguna memilih confirmation='berhasil' menyelesaikan sesi secara tuntas."""
    mock_db = MagicMock()
    mock_db.record_trace = AsyncMock()
    mock_db.get_session = AsyncMock(
        return_value={
            "session_id": "sess-success",
            "status": SessionStatus.AWAITING_CONFIRM.value,
            "current_step": 2,
            "clarification_count": 0,
            "artikel_terpilih": "KB-001",
            "draft_ticket_id": None,
        }
    )
    mock_db.update_session = AsyncMock()

    settings = Settings(CHAT_MODEL="mock", EMBEDDING_MODEL="mock")
    orchestrator = AgentOrchestrator(database=mock_db, settings=settings)

    req = ChatRequest(
        session_id="sess-success",
        message="Sudah bisa tersambung, terima kasih!",
        confirmation="berhasil",
    )
    res = await orchestrator.process_turn(req)

    assert res.tipe_respons == "selesai"
    assert "teratasi" in res.pesan
    assert res.memerlukan_konfirmasi is False
    mock_db.update_session.assert_called_with(
        session_id="sess-success",
        status=SessionStatus.RESOLVED.value,
        current_step=2,
        clarification_count=0,
        artikel_terpilih="KB-001",
        draft_ticket_id=None,
    )


@pytest.mark.asyncio
async def test_ticket_confirm_endpoint_flow_k4():
    """Menguji eksekusi endpoint konfirmasi tiket (POST /api/ticket/confirm)."""
    from app.routes.chat import confirm_ticket_endpoint

    mock_ticket = {
        "ticket_id": "TK-ABC123",
        "session_id": "sess-ticket-1",
        "status": "draft",
    }
    mock_session = {
        "session_id": "sess-ticket-1",
        "status": SessionStatus.ESCALATING.value,
        "current_step": 4,
        "clarification_count": 0,
        "artikel_terpilih": "KB-001",
        "draft_ticket_id": "TK-ABC123",
    }

    import app.routes.chat as chat_module

    chat_module.db.get_ticket = AsyncMock(return_value=mock_ticket)
    chat_module.db.get_session = AsyncMock(return_value=mock_session)
    chat_module.db.update_ticket_status = AsyncMock(return_value=True)
    chat_module.db.update_session = AsyncMock()
    chat_module.db.record_trace = AsyncMock()

    # 1. Konfirmasi tiket -> tiket_terkirim
    req_confirm = TicketConfirmRequest(ticket_id="TK-ABC123", action="confirm")
    res_confirm = await confirm_ticket_endpoint(req_confirm)
    assert res_confirm.tipe_respons == "tiket_terkirim"
    assert "TK-ABC123" in res_confirm.pesan
    chat_module.db.update_ticket_status.assert_called_with("TK-ABC123", "confirmed")

    # 2. Pembatalan tiket -> dibatalkan
    req_cancel = TicketConfirmRequest(ticket_id="TK-ABC123", action="cancel")
    res_cancel = await confirm_ticket_endpoint(req_cancel)
    assert res_cancel.tipe_respons == "selesai"
    assert "dibatalkan" in res_cancel.pesan
    chat_module.db.update_ticket_status.assert_called_with("TK-ABC123", "cancelled")
