<script lang="ts">
  import type { ChatResponse, SumberKutipan } from "../types";
  import { sendMessage } from "../stores/chat";
  import { FileText, Check, ArrowRight, Ticket, ChevronDown, ChevronUp } from "lucide-svelte";

  interface Props {
    response: ChatResponse;
    isLatest?: boolean;
  }

  let { response, isLatest = false }: Props = $props();

  let showQuotes = $state(false);

  function toggleQuotes() {
    showQuotes = !showQuotes;
  }

  function handleSolved() {
    sendMessage("", "berhasil");
  }

  function handleUnsolved() {
    sendMessage("", "belum");
  }

  function handleRequestTicket() {
    sendMessage("", "minta_tiket");
  }
</script>

<div class="mt-3 rounded border border-[var(--color-rule)] bg-[var(--color-surface)] p-4 shadow-sm text-left">
  <!-- Header: Badge Langkah Terverifikasi (K8) -->
  <div class="flex items-center justify-between pb-2 border-b border-[var(--color-rule)]">
    <div class="flex items-center gap-2">
      <span class="inline-flex items-center justify-center font-mono text-xs font-semibold px-2 py-0.5 rounded bg-[var(--color-paper-2)] text-[var(--color-ink)] border border-[var(--color-rule)]">
        Langkah {response.langkah_saat_ini} dari {response.langkah_total_tersedia}
      </span>
      {#if response.keyakinan === "tinggi"}
        <span class="text-xs text-[var(--color-accent)] font-medium">Keyakinan Tinggi</span>
      {:else if response.keyakinan === "rendah"}
        <span class="text-xs text-[var(--color-warn)] font-medium">Keyakinan Rendah</span>
      {/if}
    </div>
  </div>

  <!-- Isi Pesan Langkah (Teks Polos Anti-XSS: Tidak menggunakan @html) -->
  <div class="py-3 text-[var(--color-ink)] text-sm leading-relaxed whitespace-pre-wrap select-text">
    {response.pesan}
  </div>

  <!-- Sumber Kutipan Dokumen (K10, §9.6) -->
  {#if response.sumber && response.sumber.length > 0}
    <div class="mt-2 pt-2 border-t border-[var(--color-rule)] text-xs">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-1.5 text-[var(--color-muted)]">
          <FileText size={14} class="shrink-0" />
          <span>Sumber:</span>
          {#each response.sumber as s}
            <span class="font-mono bg-[var(--color-paper-2)] px-1.5 py-0.5 rounded border border-[var(--color-rule)] text-[var(--color-ink)]">
              {s.article_id} · {s.section}
            </span>
          {/each}
        </div>
        <button
          type="button"
          class="flex items-center gap-1 text-[var(--color-accent)] hover:underline focus:outline-none cursor-pointer py-1"
          onclick={toggleQuotes}
          aria-expanded={showQuotes}
        >
          {showQuotes ? "Sembunyikan kutipan" : "Lihat kutipan"}
          {#if showQuotes}
            <ChevronUp size={14} />
          {:else}
            <ChevronDown size={14} />
          {/if}
        </button>
      </div>

      {#if showQuotes}
        <div class="mt-2 space-y-1.5 p-2.5 rounded bg-[var(--color-paper)] border border-[var(--color-rule)]">
          {#each response.sumber as s}
            <div>
              <p class="font-medium text-[var(--color-ink)]">{s.judul}</p>
              <blockquote class="italic text-[var(--color-muted)] pl-2 border-l border-[var(--color-rule)] mt-0.5">
                "{s.kutipan}"
              </blockquote>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}

  <!-- Tombol Konfirmasi Aksi (Hanya aktif untuk pesan langkah terakhir & memerlukan konfirmasi) -->
  {#if isLatest && response.memerlukan_konfirmasi}
    <div class="mt-4 pt-3 border-t border-[var(--color-rule)] flex flex-wrap gap-2">
      <button
        type="button"
        onclick={handleSolved}
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-[var(--color-accent)] text-[var(--color-on-accent)] hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer"
      >
        <Check size={14} />
        Masalah teratasi
      </button>

      <button
        type="button"
        onclick={handleUnsolved}
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-[var(--color-paper-2)] text-[var(--color-ink)] border border-[var(--color-rule-strong)] hover:bg-[var(--color-paper)] transition-colors cursor-pointer"
      >
        <ArrowRight size={14} />
        Masih bermasalah
      </button>

      <button
        type="button"
        onclick={handleRequestTicket}
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium text-[var(--color-muted)] hover:text-[var(--color-ink)] hover:bg-[var(--color-paper-2)] transition-colors cursor-pointer ml-auto"
      >
        <Ticket size={14} />
        Minta tiket teknisi
      </button>
    </div>
  {/if}
</div>
