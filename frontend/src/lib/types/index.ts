/**
 * Definisi tipe data aplikasi frontend KnowDesk AI.
 * Turunan langsung dari kontrak skema OpenAPI backend (Keputusan K14).
 */

import type { components } from "./api";

export type ChatRequest = components["schemas"]["ChatRequest"];
export type ChatResponse = components["schemas"]["ChatResponse"];
export type DraftTicket = components["schemas"]["DraftTicket"];
export type SumberKutipan = components["schemas"]["SumberKutipan"];
export type TicketConfirmRequest = components["schemas"]["TicketConfirmRequest"];

export interface MessageItem {
  id: string;
  sender: "user" | "assistant";
  text: string;
  response?: ChatResponse;
  timestamp: Date;
}
