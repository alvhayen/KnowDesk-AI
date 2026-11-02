"""Orchestrator utama alur bantuan KnowDesk AI (agents.md §2 R3, R4, R11, §3 K2, K6, K8, K10, §6.1, §6.2).

Implementasi loop agen mandiri tanpa framework pihak ketiga (R11).
Menegakkan allowlist tool per state (R3), verifikasi substring kutipan (K10),
dan menampilkan langkah ke-4 sebelum eskalasi tiket (K2).
"""

import json
import logging
import uuid
from typing import Any

from app.agent.messages import (
    MSG_BATAS_LANGKAH,
    MSG_SELESAI,
    MSG_TIDAK_DITEMUKAN,
)
from app.agent.prompts import format_context_prompt, load_system_prompt
from app.config import Settings
from app.db import Database, db
from app.guardrails.input_guard import validate_and_sanitize_input
from app.guardrails.output_guard import OutputGuardError, validate_source_quotes
from app.llm.client import LLMClient
from app.rag.chunker import chunk_markdown_article
from app.rag.retriever import search_knowledge_base
from app.schemas.contracts import (
    ChatRequest,
    ChatResponse,
    DraftTicket,
    SumberKutipan,
)
from app.schemas.state import SessionStatus, is_tool_allowed
from app.schemas.tools import SEARCH_KB_TOOL

logger = logging.getLogger(__name__)


class ToolExecutionError(ValueError):
    """Pengecualian saat tool dipanggil di luar kewenangan status sesi (Aturan R3)."""



class AgentOrchestrator:
    """Orchestrator loop alur percakapan agentik KnowDesk AI."""

    def __init__(
        self,
        database: Database | None = None,
        llm_client: LLMClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.db = database or db
        self.settings = settings or Settings()
        self.llm = llm_client or LLMClient(self.settings)

    async def process_turn(self, request: ChatRequest) -> ChatResponse:
        """Memproses satu giliran pesan chat pengguna secara deterministik dan agentik."""
        # Lapis 1: Input Guard
        sanitized_msg = validate_and_sanitize_input(
            request.message, max_chars=self.settings.INPUT_MAX_CHARS
        )

        # Muat atau buat sesi di database
        session_id = request.session_id or str(uuid.uuid4())
        session_row = await self.db.get_session(session_id)

        if not session_row:
            current_status = SessionStatus.IDLE
            current_step = 0
            clarification_count = 0
            artikel_terpilih = None
            draft_ticket_id = None
            await self.db.create_session(
                session_id=session_id,
                status=current_status.value,
                current_step=current_step,
                clarification_count=clarification_count,
            )
        else:
            current_status = SessionStatus(session_row["status"])
            current_step = session_row["current_step"]
            clarification_count = session_row["clarification_count"]
            artikel_terpilih = session_row["artikel_terpilih"]
            draft_ticket_id = session_row["draft_ticket_id"]

        # Tolak sesi yang sudah closed atau resolved (HTTP 409 per §6.1)
        if current_status in (SessionStatus.RESOLVED, SessionStatus.CLOSED):
            raise ValueError(f"Sesi {session_id} telah selesai ({current_status.value}). Tidak menerima pesan baru.")

        # --- KASUS 1: Pengguna Konfirmasi 'berhasil' (K3) ---
        if request.confirmation == "berhasil":
            await self.db.update_session(
                session_id=session_id,
                status=SessionStatus.RESOLVED.value,
                current_step=current_step,
                clarification_count=clarification_count,
                artikel_terpilih=artikel_terpilih,
                draft_ticket_id=draft_ticket_id,
            )
            await self.db.record_trace(
                trace_id=str(uuid.uuid4()),
                session_id=session_id,
                action_type="session_resolved",
                decision="Pengguna menandai masalah teratasi.",
            )
            return ChatResponse(
                session_id=session_id,
                tipe_respons="selesai",
                pesan=MSG_SELESAI,
                langkah_saat_ini=current_step,
                langkah_total_tersedia=current_step,
                keyakinan="tinggi",
                memerlukan_konfirmasi=False,
            )

        # --- KASUS 2: Pengguna Meminta Tiket Eksplisit 'minta_tiket' (K3, §6.2 #7) ---
        if request.confirmation == "minta_tiket":
            return await self._escalate_to_ticket(
                session_id=session_id,
                current_step=current_step,
                clarification_count=clarification_count,
                artikel_terpilih=artikel_terpilih,
                reason="Pengguna meminta eskalasi tiket.",
            )

        # --- KASUS 3: Sesi Sedang Dalam Tahap Solusi (GUIDING / AWAITING_CONFIRM) ---
        if current_status in (SessionStatus.GUIDING, SessionStatus.AWAITING_CONFIRM) and artikel_terpilih:
            article_row = await self.db.get_published_article(artikel_terpilih)
            if article_row:
                parsed_article = chunk_markdown_article(article_row["raw_content"])
                total_steps = parsed_article.langkah_total_tersedia

                # Cek jika pengguna menjawab 'belum' atau pesan teks lanjutan
                # K2: Langkah ke-4 ditampilkan sebelum eskalasi!
                next_step = current_step + 1

                if next_step <= min(self.settings.AGENT_MAX_STEPS, total_steps):
                    # Tampilkan langkah berikutnya (misal langkah 2, 3, atau 4)
                    return await self._present_step(
                        session_id=session_id,
                        parsed_article=parsed_article,
                        target_step=next_step,
                        clarification_count=clarification_count,
                        draft_ticket_id=draft_ticket_id,
                        keyakinan="tinggi",
                    )
                else:
                    # Langkah maksimal (4) atau seluruh langkah artikel sudah dicoba dan masih 'belum' -> Eskalasi!
                    return await self._escalate_to_ticket(
                        session_id=session_id,
                        current_step=current_step,
                        clarification_count=clarification_count,
                        artikel_terpilih=artikel_terpilih,
                        reason=f"Seluruh {current_step} langkah solusi telah dicoba namun belum teratasi.",
                        total_steps=total_steps,
                    )

        # --- KASUS 4: Sesi Awal atau Klarifikasi (IDLE / CLARIFYING) ---
        # Uji allowlist: draft_ticket dilarang sebelum retrieval (Aturan R3)
        return await self._handle_clarification_or_search(
            session_id=session_id,
            user_message=sanitized_msg,
            current_status=current_status,
            clarification_count=clarification_count,
        )

    async def _handle_clarification_or_search(
        self,
        session_id: str,
        user_message: str,
        current_status: SessionStatus,
        clarification_count: int,
    ) -> ChatResponse:
        """Memproses giliran awal: klarifikasi vs pencarian knowledge base (agents.md §6.2 #1)."""
        system_prompt = load_system_prompt("v1")

        # Cek batas klarifikasi (maksimal 2x per konfigurasi)
        force_search = clarification_count >= self.settings.AGENT_MAX_CLARIFICATIONS

        if force_search:
            # Klarifikasi telah mencapai batas maksimal, paksa eksekusi search_kb
            tool_choice = {"type": "function", "function": {"name": "search_kb"}}
            tools = [SEARCH_KB_TOOL]
        else:
            tool_choice = "auto"
            tools = [SEARCH_KB_TOOL]

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": format_context_prompt(
                    system_prompt="",
                    user_message=user_message,
                ),
            },
        ]

        llm_resp = await self.llm.chat_completion(
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )

        # Catat trace panggilan LLM
        await self.db.record_trace(
            trace_id=str(uuid.uuid4()),
            session_id=session_id,
            action_type="llm_clarify_turn",
            prompt_tokens=llm_resp.prompt_tokens,
            completion_tokens=llm_resp.completion_tokens,
            model=llm_resp.model,
            latency_ms=llm_resp.latency_ms,
            decision=llm_resp.content[:200] if llm_resp.content else "Tool call requested",
        )

        # Periksa apakah LLM memanggil search_kb
        search_call = next(
            (tc for tc in llm_resp.tool_calls if tc.get("function", {}).get("name") == "search_kb"),
            None,
        )

        if not search_call and not force_search:
            # LLM memilih memberikan pertanyaan klarifikasi teks
            new_clarification_count = clarification_count + 1
            await self.db.update_session(
                session_id=session_id,
                status=SessionStatus.CLARIFYING.value,
                current_step=0,
                clarification_count=new_clarification_count,
            )
            return ChatResponse(
                session_id=session_id,
                tipe_respons="klarifikasi",
                pesan=llm_resp.content or "Bisa tolong jelaskan lebih spesifik kendala perangkat atau aplikasi yang Anda alami?",
                sumber=[],
                langkah_saat_ini=0,
                langkah_total_tersedia=0,
                keyakinan="tidak_dapat_ditentukan",
                memerlukan_konfirmasi=False,
            )

        # Eksekusi search_kb
        query = user_message
        if search_call:
            try:
                args = json.loads(search_call["function"]["arguments"])
                query = args.get("query", user_message)
            except (json.JSONDecodeError, KeyError, TypeError):
                query = user_message

        # Validasi allowlist kode (Aturan R3)
        if not is_tool_allowed(SessionStatus.CLARIFYING, "search_kb") and not is_tool_allowed(SessionStatus.IDLE, "search_kb"):
            raise ToolExecutionError("Pemanggilan search_kb ditolak oleh allowlist status sesi.")

        search_res = await search_knowledge_base(query, database=self.db, settings=self.settings)

        # Catat trace eksekusi tool search_kb
        await self.db.record_trace(
            trace_id=str(uuid.uuid4()),
            session_id=session_id,
            action_type="tool_execution",
            tool_called="search_kb",
            parameters={"query": query},
            decision=f"Top article: {search_res.top_article_id}, top score: {search_res.top_score}, passed: {search_res.passed_gate}",
        )

        if not search_res.passed_gate or not search_res.top_article_id:
            # Tidak ada artikel yang lolos gerbang ambang batas (K1 & §6.2 #2)
            await self.db.update_session(
                session_id=session_id,
                status=SessionStatus.CLARIFYING.value,
                current_step=0,
                clarification_count=clarification_count,
            )
            return ChatResponse(
                session_id=session_id,
                tipe_respons="tidak_ditemukan",
                pesan=MSG_TIDAK_DITEMUKAN,
                sumber=[],
                langkah_saat_ini=0,
                langkah_total_tersedia=0,
                keyakinan="tidak_dapat_ditentukan",
                memerlukan_konfirmasi=True,
            )

        # Artikel relevan ditemukan! Ambil isi artikel dan mulai Langkah 1 (K7 & K8)
        article_row = await self.db.get_published_article(search_res.top_article_id)
        if not article_row:
            return ChatResponse(
                session_id=session_id,
                tipe_respons="tidak_ditemukan",
                pesan=MSG_TIDAK_DITEMUKAN,
                sumber=[],
                langkah_saat_ini=0,
                langkah_total_tersedia=0,
                keyakinan="tidak_dapat_ditentukan",
                memerlukan_konfirmasi=True,
            )

        parsed_article = chunk_markdown_article(article_row["raw_content"])
        return await self._present_step(
            session_id=session_id,
            parsed_article=parsed_article,
            target_step=1,
            clarification_count=clarification_count,
            draft_ticket_id=None,
            keyakinan=search_res.keyakinan,
        )

    async def _present_step(
        self,
        session_id: str,
        parsed_article: Any,
        target_step: int,
        clarification_count: int,
        draft_ticket_id: str | None,
        keyakinan: str,
    ) -> ChatResponse:
        """Menyusun dan memvalidasi penyajian langkah ke-N kepada pengguna (Keputusan K8 & K10)."""
        step_info = parsed_article.get_step(target_step)
        if not step_info:
            # Langkah tidak ditemukan di dokumen, eskalasi
            return await self._escalate_to_ticket(
                session_id=session_id,
                current_step=target_step - 1,
                clarification_count=clarification_count,
                artikel_terpilih=parsed_article.article_id,
                reason="Langkah panduan dokumen telah habis.",
                total_steps=parsed_article.langkah_total_tersedia,
            )

        step_text = step_info.content
        system_prompt = load_system_prompt("v1")

        # Instruksi ke LLM untuk menyusun pesan ramah + kutipan
        user_prompt = (
            f"Sajikan Langkah {target_step} berikut kepada pengguna secara ramah dan terstruktur.\n"
            f"Judul Langkah: {step_info.title}\n"
            f"Isi Dokumen Langkah:\n{step_text}\n\n"
            "Wajib sertakan sumber kutipan yang merupakan cuplikan substring persis dari teks dokumen langkah."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": format_context_prompt(
                    system_prompt="",
                    kb_context=step_text,
                    user_message=user_prompt,
                ),
            },
        ]

        llm_resp = await self.llm.chat_completion(
            messages=messages,
            temperature=self.settings.LLM_TEMPERATURE,
        )

        # Catat trace
        await self.db.record_trace(
            trace_id=str(uuid.uuid4()),
            session_id=session_id,
            action_type="step_generation",
            prompt_tokens=llm_resp.prompt_tokens,
            completion_tokens=llm_resp.completion_tokens,
            model=llm_resp.model,
            latency_ms=llm_resp.latency_ms,
            decision=f"Langkah {target_step} artikel {parsed_article.article_id}",
        )

        # Parse JSON keluaran model atau ekstrak pesan & sumber
        parsed_output = self._parse_model_output(
            llm_resp.content,
            parsed_article.article_id,
            step_info,
        )

        # Lapis 4: Output Guard — Verifikasi substring kutipan (Keputusan K10)
        try:
            validate_source_quotes(
                sumber_list=parsed_output["sumber"],
                expected_article_id=parsed_article.article_id,
                step_content=step_text,
            )
        except OutputGuardError as og_err:
            logger.warning("Output guard mendeteksi kutipan tidak valid: %s. Melakukan perbaikan fallback.", og_err)
            # Normalisasi fallback kutipan dari potongan pertama teks langkah asli (anti halusinasi)
            first_sentence = step_text.split(".")[0].strip() or step_info.title
            parsed_output["sumber"] = [
                SumberKutipan(
                    article_id=parsed_article.article_id,
                    section=f"Langkah {target_step}",
                    judul=parsed_article.judul,
                    kutipan=first_sentence,
                )
            ]

        # Isi metadata oleh kode per K17
        for s in parsed_output["sumber"]:
            s.judul = parsed_article.judul

        # Update sesi di database
        await self.db.update_session(
            session_id=session_id,
            status=SessionStatus.AWAITING_CONFIRM.value,
            current_step=target_step,
            clarification_count=clarification_count,
            artikel_terpilih=parsed_article.article_id,
            draft_ticket_id=draft_ticket_id,
        )

        return ChatResponse(
            session_id=session_id,
            tipe_respons="langkah_solusi",
            pesan=parsed_output["pesan"],
            sumber=parsed_output["sumber"],
            langkah_saat_ini=target_step,
            langkah_total_tersedia=parsed_article.langkah_total_tersedia,
            keyakinan=keyakinan,  # type: ignore[arg-type]
            memerlukan_konfirmasi=True,
        )

    async def _escalate_to_ticket(
        self,
        session_id: str,
        current_step: int,
        clarification_count: int,
        artikel_terpilih: str | None,
        reason: str,
        total_steps: int | None = None,
    ) -> ChatResponse:
        """Membuat draf tiket eskalasi teknisi IT (agents.md §3 K2, K4, §6.2 #6)."""
        ticket_id = f"TK-{uuid.uuid4().hex[:6].upper()}"
        article_title = "Kendala IT Pengguna"
        category = "lainnya"

        if artikel_terpilih:
            art = await self.db.get_published_article(artikel_terpilih)
            if art:
                article_title = art["judul"]
                category = art["kategori"]

        steps_tried = [f"Langkah {i}" for i in range(1, current_step + 1)] if current_step > 0 else ["Pencarian mandiri belum menemukan solusi"]

        draft_ticket = DraftTicket(
            ticket_id=ticket_id,
            judul=f"Eskalasi: {article_title}",
            deskripsi=f"Masalah belum teratasi setelah mencoba panduan. Catatan: {reason}",
            langkah_dicoba=steps_tried,
            prioritas="sedang",
            kategori=category if category in ("jaringan", "email", "aplikasi", "perangkat", "lainnya") else "lainnya",  # type: ignore[arg-type]
        )

        # Simpan draf tiket ke database MySQL (status 'draft', belum terkirim per R4 & K4)
        await self.db.create_ticket(
            ticket_id=ticket_id,
            session_id=session_id,
            summary=draft_ticket.deskripsi,
            steps_tried=steps_tried,
            category=draft_ticket.kategori,
            status="draft",
        )

        # Update sesi
        await self.db.update_session(
            session_id=session_id,
            status=SessionStatus.ESCALATING.value,
            current_step=current_step,
            clarification_count=clarification_count,
            artikel_terpilih=artikel_terpilih,
            draft_ticket_id=ticket_id,
        )

        # Catat trace
        await self.db.record_trace(
            trace_id=str(uuid.uuid4()),
            session_id=session_id,
            action_type="draft_ticket_created",
            tool_called="draft_ticket",
            parameters=draft_ticket.model_dump(),
            decision=f"Draf tiket {ticket_id} dibuat, menunggu konfirmasi pengguna via POST /api/ticket/confirm.",
        )

        header_msg = MSG_BATAS_LANGKAH.format(n=current_step) if current_step >= self.settings.AGENT_MAX_STEPS else "Berikut draf tiket bantuan untuk teknisi IT:"

        return ChatResponse(
            session_id=session_id,
            tipe_respons="draf_tiket",
            pesan=f"{header_msg} {draft_ticket.judul}. Silakan konfirmasi untuk mengirimkan tiket.",
            sumber=[],
            langkah_saat_ini=current_step,
            langkah_total_tersedia=total_steps or current_step,
            keyakinan="sedang",
            memerlukan_konfirmasi=True,
            draf_tiket=draft_ticket,
        )

    def _parse_model_output(
        self,
        raw_text: str,
        article_id: str,
        step_info: Any,
    ) -> dict[str, Any]:
        """Mengurai respons LLM menjadi format terstruktur (pesan dan daftar SumberKutipan)."""
        try:
            # Bersihkan blok code markdown jika ada
            clean = raw_text.strip()
            clean = clean.removeprefix("```json")
            clean = clean.removeprefix("```")
            clean = clean.removesuffix("```")
            data = json.loads(clean.strip())
            pesan = data.get("pesan", step_info.content)
            raw_sumber = data.get("sumber", [])
            sumber = []
            for s in raw_sumber:
                sumber.append(
                    SumberKutipan(
                        article_id=s.get("article_id", article_id),
                        section=s.get("section", f"Langkah {step_info.step_number}"),
                        judul="",  # Diisi kode per K17
                        kutipan=s.get("kutipan", ""),
                    )
                )
            return {"pesan": pesan, "sumber": sumber}
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            # Fallback jika model menghasilkan teks polos langsung
            first_sentence = step_info.content.split(".")[0].strip() or step_info.title
            return {
                "pesan": raw_text.strip() or step_info.content,
                "sumber": [
                    SumberKutipan(
                        article_id=article_id,
                        section=f"Langkah {step_info.step_number}",
                        judul="",
                        kutipan=first_sentence,
                    )
                ],
            }
