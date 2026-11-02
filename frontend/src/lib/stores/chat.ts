/**
 * Svelte store untuk pengelolaan state percakapan agentik KnowDesk AI (K4, K17).
 */

import { writable, get } from "svelte/store";
import type {
  ChatRequest,
  ChatResponse,
  DraftTicket,
  MessageItem,
  TicketConfirmRequest,
} from "../types";

export interface ChatState {
  sessionId: string | null;
  messages: MessageItem[];
  currentStep: number;
  totalSteps: number;
  status: string;
  activeDraftTicket: DraftTicket | null;
  isLoading: boolean;
  errorMessage: string | null;
}

const initialState: ChatState = {
  sessionId: null,
  messages: [],
  currentStep: 0,
  totalSteps: 0,
  status: "idle",
  activeDraftTicket: null,
  isLoading: false,
  errorMessage: null,
};

export const chatStore = writable<ChatState>(initialState);

const API_BASE = "http://localhost:8000/api";

export async function sendMessage(
  messageText: string,
  confirmation?: "berhasil" | "belum" | "minta_tiket"
): Promise<void> {
  const state = get(chatStore);

  // Jangan kirim jika sedang memuat atau pesan kosong
  if (state.isLoading || (!messageText.trim() && !confirmation)) return;

  const userMsg: MessageItem = {
    id: `usr-${Date.now()}`,
    sender: "user",
    text: messageText || (confirmation === "berhasil" ? "Masalah teratasi" : confirmation === "belum" ? "Masih bermasalah" : "Minta tiket teknisi"),
    timestamp: new Date(),
  };

  chatStore.update((s) => ({
    ...s,
    messages: [...s.messages, userMsg],
    isLoading: true,
    errorMessage: null,
  }));

  try {
    const payload: ChatRequest = {
      session_id: state.sessionId,
      message: messageText || (confirmation ?? "Lanjut"),
      confirmation,
    };

    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData?.detail?.pesan || `Galat HTTP ${res.status}`);
    }

    const data: ChatResponse = await res.json();

    const assistantMsg: MessageItem = {
      id: `ast-${Date.now()}`,
      sender: "assistant",
      text: data.pesan,
      response: data,
      timestamp: new Date(),
    };

    chatStore.update((s) => ({
      ...s,
      sessionId: data.session_id,
      messages: [...s.messages, assistantMsg],
      currentStep: data.langkah_saat_ini,
      totalSteps: data.langkah_total_tersedia,
      status: data.tipe_respons,
      activeDraftTicket: data.draf_tiket ?? s.activeDraftTicket,
      isLoading: false,
      errorMessage: null,
    }));
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Terjadi kendala koneksi ke server.";
    chatStore.update((s) => ({
      ...s,
      isLoading: false,
      errorMessage: errorMsg,
    }));
  }
}

export async function confirmTicket(
  ticketId: string,
  action: "confirm" | "cancel",
  catatan?: string
): Promise<void> {
  chatStore.update((s) => ({ ...s, isLoading: true, errorMessage: null }));

  try {
    const payload: TicketConfirmRequest = {
      ticket_id: ticketId,
      action,
      catatan,
    };

    const res = await fetch(`${API_BASE}/ticket/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData?.detail?.pesan || `Galat HTTP ${res.status}`);
    }

    const data: ChatResponse = await res.json();

    const assistantMsg: MessageItem = {
      id: `ast-conf-${Date.now()}`,
      sender: "assistant",
      text: data.pesan,
      response: data,
      timestamp: new Date(),
    };

    chatStore.update((s) => ({
      ...s,
      messages: [...s.messages, assistantMsg],
      activeDraftTicket: null,
      status: "closed",
      isLoading: false,
      errorMessage: null,
    }));
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Gagal mengonfirmasi tiket.";
    chatStore.update((s) => ({
      ...s,
      isLoading: false,
      errorMessage: errorMsg,
    }));
  }
}

export function resetSession(): void {
  chatStore.set(initialState);
}

export function dismissError(): void {
  chatStore.update((s) => ({ ...s, errorMessage: null }));
}

