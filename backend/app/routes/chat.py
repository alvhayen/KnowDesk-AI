"""FastAPI Router untuk endpoint percakapan, konfirmasi tiket, dan sesi (agents.md §2 R4, §3 K4, §6.1, §6.3).

Menegakkan aturan:
- POST /api/chat: Menerima ChatRequest, validasi, orkestrasi agen, dan pengembalian ChatResponse.
- POST /api/ticket/confirm: Satu-satunya jalur sah pengiriman tiket ke teknisi (Aturan R4 & K4).
- GET /api/session/{id}: Mengambil status dan riwayat audit sesi.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agent.messages import MSG_TIKET_DIBATALKAN, MSG_TIKET_TERKIRIM
from app.agent.orchestrator import AgentOrchestrator
from app.db import db
from app.guardrails.input_guard import InputGuardError
from app.schemas.contracts import (
    ChatRequest,
    ChatResponse,
    TicketConfirmRequest,
)
from app.schemas.state import SessionStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chat & Tickets"])
orchestrator = AgentOrchestrator(database=db)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Kirim pesan pengguna ke orchestrator agen",
)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Memproses pesan percakapan pengguna dan mengembalikan respons bantuan agen."""
    try:
        response = await orchestrator.process_turn(request)
        return response
    except InputGuardError as ige:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"kode": "invalid_input", "pesan": str(ige)},
        ) from ige
    except ValueError as ve:
        # Sesi selesai / tertutup mengembalikan 409 Conflict per §6.1
        if "telah selesai" in str(ve) or "closed" in str(ve) or "resolved" in str(ve):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"kode": "session_terminated", "pesan": str(ve)},
            ) from ve
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"kode": "bad_request", "pesan": str(ve)},
        ) from ve
    except Exception as e:
        logger.exception("Kesalahan internal saat memproses giliran chat")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"kode": "internal_error", "pesan": "Terjadi kesalahan internal pada sistem agen."},
        ) from e


@router.post(
    "/ticket/confirm",
    response_model=ChatResponse,
    summary="Konfirmasi pengiriman atau pembatalan draf tiket (Satu Jalur Sah R4 & K4)",
)
async def confirm_ticket_endpoint(request: TicketConfirmRequest) -> ChatResponse:
    """Mengonfirmasi atau membatalkan draf tiket eskalasi ke teknisi IT."""
    ticket_id = request.ticket_id
    if not ticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"kode": "missing_ticket_id", "pesan": "Parameter ticket_id wajib disertakan."},
        )

    ticket_row = await db.get_ticket(ticket_id)
    if not ticket_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"kode": "ticket_not_found", "pesan": f"Tiket dengan ID {ticket_id} tidak ditemukan."},
        )

    session_id = ticket_row["session_id"]
    session_row = await db.get_session(session_id)
    current_step = session_row["current_step"] if session_row else 0

    if request.action == "confirm":
        # Perbarui status tiket menjadi 'confirmed' di database
        await db.update_ticket_status(ticket_id, "confirmed")

        # Tutup sesi terkait
        if session_row:
            await db.update_session(
                session_id=session_id,
                status=SessionStatus.CLOSED.value,
                current_step=current_step,
                clarification_count=session_row["clarification_count"],
                artikel_terpilih=session_row["artikel_terpilih"],
                draft_ticket_id=ticket_id,
            )

        # Catat trace audit
        await db.record_trace(
            trace_id=f"trc-conf-{ticket_id}",
            session_id=session_id,
            action_type="ticket_confirmed",
            decision=f"Tiket {ticket_id} disetujui pengguna dan dikirim ke sistem tiket IT.",
        )

        return ChatResponse(
            session_id=session_id,
            tipe_respons="tiket_terkirim",
            pesan=MSG_TIKET_TERKIRIM.format(id=ticket_id),
            sumber=[],
            langkah_saat_ini=current_step,
            langkah_total_tersedia=current_step,
            keyakinan="tinggi",
            memerlukan_konfirmasi=False,
        )

    elif request.action == "cancel":
        # Batalkan tiket
        await db.update_ticket_status(ticket_id, "cancelled")

        # Tutup sesi
        if session_row:
            await db.update_session(
                session_id=session_id,
                status=SessionStatus.CLOSED.value,
                current_step=current_step,
                clarification_count=session_row["clarification_count"],
                artikel_terpilih=session_row["artikel_terpilih"],
                draft_ticket_id=ticket_id,
            )

        # Catat trace audit
        await db.record_trace(
            trace_id=f"trc-canc-{ticket_id}",
            session_id=session_id,
            action_type="ticket_cancelled",
            decision=f"Draf tiket {ticket_id} dibatalkan oleh pengguna.",
        )

        return ChatResponse(
            session_id=session_id,
            tipe_respons="selesai",
            pesan=MSG_TIKET_DIBATALKAN,
            sumber=[],
            langkah_saat_ini=current_step,
            langkah_total_tersedia=current_step,
            keyakinan="tinggi",
            memerlukan_konfirmasi=False,
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"kode": "invalid_action", "pesan": f"Action '{request.action}' tidak sah."},
    )


@router.get(
    "/session/{session_id}",
    response_model=dict[str, Any],
    summary="Ambil status dan jejak audit sesi aktif",
)
async def get_session_endpoint(session_id: str) -> dict[str, Any]:
    """Mengambil informasi state sesi dan jejak keputusan audit."""
    session_row = await db.get_session(session_id)
    if not session_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"kode": "session_not_found", "pesan": f"Sesi dengan ID {session_id} tidak ditemukan."},
        )

    traces = await db.get_session_traces(session_id)
    ticket_data = None
    if session_row.get("draft_ticket_id"):
        ticket_data = await db.get_ticket(session_row["draft_ticket_id"])

    return {
        "session": session_row,
        "ticket": ticket_data,
        "traces_count": len(traces),
        "traces": traces,
    }
