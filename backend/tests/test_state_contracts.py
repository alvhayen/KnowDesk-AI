"""Unit test untuk validasi kontrak skema API dan state machine (agents.md §3 K3, K4, K6, K17, §6.2, §6.3)."""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.schemas.contracts import (
    ChatRequest,
    ChatResponse,
    SumberKutipan,
    TicketConfirmRequest,
)
from app.schemas.state import SessionStatus, is_tool_allowed
from app.schemas.tools import (
    CANONICAL_TOOLS,
    DraftTicketArgs,
    GetArticleArgs,
    SearchKbArgs,
)

# --- 1. Uji Kontrak ChatRequest ---


def test_chat_request_valid():
    """ChatRequest dengan field sah harus lolos validasi."""
    req = ChatRequest(
        session_id="550e8400-e29b-41d4-a716-446655440000",
        message="Wi-Fi kantor tidak bisa tersambung",
        confirmation="belum",
    )
    assert req.message == "Wi-Fi kantor tidak bisa tersambung"
    assert req.confirmation == "belum"


def test_chat_request_rejection_legacy_confirmation():
    """Nilai konfirmasi_tiket atau tolak_tiket harus ditolak keras sesuai Aturan K4."""
    with pytest.raises(ValidationError):
        ChatRequest(
            message="Tes pesan",
            confirmation="konfirmasi_tiket",  # Dihapus per K4
        )

    with pytest.raises(ValidationError):
        ChatRequest(
            message="Tes pesan",
            confirmation="tolak_tiket",  # Dihapus per K4
        )


def test_chat_request_max_length_guard():
    """Pesan melebihi 1000 karakter harus ditolak oleh Input Guard Pydantic."""
    with pytest.raises(ValidationError):
        ChatRequest(message="a" * 1001)

    with pytest.raises(ValidationError):
        ChatRequest(message="")  # Pesan kosong dilarang


# --- 2. Uji Kontrak ChatResponse ---


def test_chat_response_valid():
    """ChatResponse lengkap harus lolos validasi."""
    res = ChatResponse(
        session_id="550e8400-e29b-41d4-a716-446655440000",
        tipe_respons="langkah_solusi",
        pesan="Langkah pertama: lupakan jaringan Wi-Fi kantor.",
        sumber=[
            SumberKutipan(
                article_id="KB-001",
                section="Bagian 3",
                judul="Panduan Troubleshooting Koneksi Wi-Fi Kantor",
                kutipan="Lupakan jaringan kantor",
            )
        ],
        langkah_saat_ini=1,
        langkah_total_tersedia=4,
        keyakinan="tinggi",
        memerlukan_konfirmasi=True,
    )
    assert res.tipe_respons == "langkah_solusi"
    assert res.langkah_saat_ini == 1
    assert len(res.sumber) == 1


def test_chat_response_rejection_invalid_fields():
    """ChatResponse harus menolak tipe_respons atau keyakinan yang tidak sah."""
    with pytest.raises(ValidationError):
        ChatResponse(
            session_id="123",
            tipe_respons="respons_palsu",  # Tidak sah
            pesan="Halo",
        )

    with pytest.raises(ValidationError):
        ChatResponse(
            session_id="123",
            tipe_respons="langkah_solusi",
            pesan="Halo",
            langkah_saat_ini=5,  # Melebihi batas maksimal 4 langkah
        )


# --- 3. Uji Kontrak TicketConfirmRequest ---


def test_ticket_confirm_request_valid():
    """TicketConfirmRequest hanya menerima confirm atau cancel (K4)."""
    req_confirm = TicketConfirmRequest(action="confirm", ticket_id="TK-001")
    assert req_confirm.action == "confirm"

    req_cancel = TicketConfirmRequest(action="cancel")
    assert req_cancel.action == "cancel"

    with pytest.raises(ValidationError):
        TicketConfirmRequest(action="approve")  # Tindakan tak dikenal


# --- 4. Uji Definisi Tool Kanonik (K6, §6.3, §7) ---


def test_canonical_tools_count_and_descriptions():
    """Harus tepat ada 3 tool kanonik dan memuat panduan kapan dipakai/tidak."""
    assert len(CANONICAL_TOOLS) == 3
    tool_names = [t["function"]["name"] for t in CANONICAL_TOOLS]
    assert set(tool_names) == {"search_kb", "get_article", "draft_ticket"}

    for t in CANONICAL_TOOLS:
        desc = t["function"]["description"]
        assert "KAPAN DIPAKAI:" in desc
        assert "KAPAN TIDAK DIPAKAI:" in desc


def test_tool_args_validation():
    """Argumen tool harus divalidasi ketat oleh Pydantic."""
    # search_kb
    valid_search = SearchKbArgs(query="koneksi wifi putus")
    assert valid_search.query == "koneksi wifi putus"

    with pytest.raises(ValidationError):
        SearchKbArgs(query="ab")  # Terlalu pendek

    # get_article
    valid_get = GetArticleArgs(article_id="KB-001")
    assert valid_get.article_id == "KB-001"

    with pytest.raises(ValidationError):
        GetArticleArgs(article_id="KB-9999")  # Pola ID salah

    # draft_ticket
    valid_ticket = DraftTicketArgs(
        judul="Koneksi Wi-Fi Rusak",
        deskripsi="Pengguna sudah mencoba 4 langkah tetapi belum berhasil.",
        langkah_dicoba=["Langkah 1", "Langkah 2"],
        prioritas="sedang",
        kategori="jaringan",
    )
    assert valid_ticket.prioritas == "sedang"


# --- 5. Uji Penegakan Allowlist State Machine (Lapis 3, §6.3) ---


def test_tool_allowlist_enforcement():
    """Tool draft_ticket wajib ditolak di state selain ESCALATING (§6.3)."""
    # draft_ticket DITOLAK di idle, clarifying, guiding, resolved
    assert not is_tool_allowed(SessionStatus.IDLE, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.CLARIFYING, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.RETRIEVING, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.GUIDING, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.AWAITING_CONFIRM, "draft_ticket")
    assert not is_tool_allowed(SessionStatus.RESOLVED, "draft_ticket")

    # draft_ticket HANYA DIIZINKAN di escalating
    assert is_tool_allowed(SessionStatus.ESCALATING, "draft_ticket")

    # search_kb diizinkan di idle dan clarifying
    assert is_tool_allowed(SessionStatus.IDLE, "search_kb")
    assert is_tool_allowed(SessionStatus.CLARIFYING, "search_kb")

    # get_article diizinkan di retrieving
    assert is_tool_allowed(SessionStatus.RETRIEVING, "get_article")
