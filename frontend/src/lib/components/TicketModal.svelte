<script lang="ts">
  import type { DraftTicket } from "../types";
  import { confirmTicket } from "../stores/chat";
  import { Ticket, Send, X, AlertCircle } from "lucide-svelte";

  interface Props {
    ticket: DraftTicket;
    isInteractive?: boolean;
  }

  let { ticket, isInteractive = true }: Props = $props();

  let notes = $state("");
  let isSubmitting = $state(false);

  async function handleConfirm() {
    if (isSubmitting) return;
    isSubmitting = true;
    try {
      await confirmTicket(ticket.ticket_id, "confirm", notes);
    } finally {
      isSubmitting = false;
    }
  }

  async function handleCancel() {
    if (isSubmitting) return;
    isSubmitting = true;
    try {
      await confirmTicket(ticket.ticket_id, "cancel");
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="mt-3 rounded border border-[var(--color-rule)] bg-[var(--color-surface)] p-4 shadow-sm text-left">
  <!-- Header Formulir Draf -->
  <div class="flex items-center justify-between pb-3 border-b border-[var(--color-rule)]">
    <div class="flex items-center gap-2">
      <Ticket size={18} class="text-[var(--color-accent)]" />
      <span class="font-semibold text-sm text-[var(--color-ink)]">Draf Tiket Bantuan IT</span>
      <span class="text-xs px-2 py-0.5 rounded bg-[var(--color-warn-soft)] text-[var(--color-warn)] font-medium">
        Belum dikirim
      </span>
    </div>
    <span class="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-[var(--color-paper-2)] text-[var(--color-ink)] border border-[var(--color-rule)]">
      {ticket.ticket_id}
    </span>
  </div>

  <!-- Rincian Formulir (Tabel Baris Tipis §9.9) -->
  <div class="py-3 space-y-2 text-xs">
    <div class="grid grid-cols-3 gap-2 py-1 border-b border-[var(--color-rule)]">
      <span class="text-[var(--color-muted)]">Judul Masalah</span>
      <span class="col-span-2 font-medium text-[var(--color-ink)]">{ticket.judul}</span>
    </div>

    <div class="grid grid-cols-3 gap-2 py-1 border-b border-[var(--color-rule)]">
      <span class="text-[var(--color-muted)]">Kategori IT</span>
      <span class="col-span-2 font-medium text-[var(--color-ink)] capitalize">{ticket.kategori}</span>
    </div>

    <div class="grid grid-cols-3 gap-2 py-1 border-b border-[var(--color-rule)]">
      <span class="text-[var(--color-muted)]">Tingkat Prioritas</span>
      <span class="col-span-2 font-medium text-[var(--color-ink)] capitalize">{ticket.prioritas}</span>
    </div>

    <div class="grid grid-cols-3 gap-2 py-1 border-b border-[var(--color-rule)]">
      <span class="text-[var(--color-muted)]">Langkah Dicoba</span>
      <div class="col-span-2 text-[var(--color-ink)]">
        <ol class="list-decimal list-inside space-y-0.5">
          {#each ticket.langkah_dicoba as step}
            <li>{step}</li>
          {/each}
        </ol>
      </div>
    </div>

    <div class="grid grid-cols-3 gap-2 py-1">
      <span class="text-[var(--color-muted)]">Deskripsi Ringkasan</span>
      <span class="col-span-2 text-[var(--color-ink)] leading-relaxed whitespace-pre-wrap">{ticket.deskripsi}</span>
    </div>
  </div>

  <!-- Catatan Tambahan Opsional (HITL) -->
  {#if isInteractive}
    <div class="mt-2 pt-2 border-t border-[var(--color-rule)]">
      <label for="ticket-notes" class="block text-xs font-medium text-[var(--color-muted)] mb-1">
        Catatan Tambahan untuk Teknisi (Opsional):
      </label>
      <textarea
        id="ticket-notes"
        bind:value={notes}
        rows={2}
        placeholder="Tuliskan detail tambahan lokasi, nomor kontak, dll..."
        class="w-full text-xs p-2 rounded border border-[var(--color-rule)] bg-[var(--color-paper)] text-[var(--color-ink)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)]"
      ></textarea>
    </div>

    <!-- Tombol Aksi Pengiriman (Satu Jalur Sah R4 & K4) -->
    <div class="mt-4 pt-3 border-t border-[var(--color-rule)] flex items-center justify-between gap-2">
      <div class="flex items-center gap-1.5 text-xs text-[var(--color-muted)]">
        <AlertCircle size={14} class="shrink-0" />
        <span>Tiket hanya diteruskan bila Anda menekan tombol konfirmasi.</span>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          onclick={handleCancel}
          disabled={isSubmitting}
          class="inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium bg-[var(--color-paper-2)] text-[var(--color-muted)] hover:text-[var(--color-ink)] border border-[var(--color-rule-strong)] transition-colors cursor-pointer disabled:opacity-50"
        >
          <X size={14} />
          Batalkan draf
        </button>

        <button
          type="button"
          onclick={handleConfirm}
          disabled={isSubmitting}
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-[var(--color-accent)] text-[var(--color-on-accent)] hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer disabled:opacity-50"
        >
          <Send size={14} />
          {isSubmitting ? "Mengirim..." : "Kirim tiket ke teknisi"}
        </button>
      </div>
    </div>
  {/if}
</div>
