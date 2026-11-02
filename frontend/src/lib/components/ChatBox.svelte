<script lang="ts">
  import type { MessageItem } from "../types";
  import StepGuide from "./StepGuide.svelte";
  import TicketModal from "./TicketModal.svelte";
  import { User, Bot, Loader2 } from "lucide-svelte";
  import { tick } from "svelte";

  interface Props {
    messages: MessageItem[];
    isLoading?: boolean;
  }

  let { messages, isLoading = false }: Props = $props();

  let chatContainer: HTMLDivElement | null = $state(null);

  // Auto-scroll saat pesan bertambah
  $effect(() => {
    if (messages.length > 0 || isLoading) {
      tick().then(() => {
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      });
    }
  });
</script>

<div
  bind:this={chatContainer}
  class="flex-1 overflow-y-auto p-4 space-y-4 max-w-[var(--chat-max)] mx-auto w-full select-text"
  role="log"
  aria-live="polite"
>
  {#if messages.length === 0}
    <!-- Tampilan Awal / Welcome State (§9.12) -->
    <div class="py-8 text-left space-y-3">
      <h2 class="text-xl md:text-2xl font-bold tracking-tight text-[var(--color-ink)]">
        Ada masalah IT kantor? Ceritakan gejalanya.
      </h2>
      <p class="text-sm text-[var(--color-muted)] leading-relaxed max-w-[50ch]">
        KnowDesk memandu Anda langkah demi langkah menyelesaikan kendala minor secara mandiri, dan menyiapkan draf tiket resmi jika diperlukan bantuan teknisi.
      </p>
      <div class="pt-2 text-xs text-[var(--color-muted)] flex items-center gap-2">
        <span class="inline-block w-2 h-2 rounded-full bg-[var(--color-accent)]"></span>
        <span>Sistem siap membantu kendala Wi-Fi, Reset Password, VPN, Printer, Teams/Outlook, Shared Drive, dan ERP.</span>
      </div>
    </div>
  {:else}
    {#each messages as msg, index (msg.id)}
      {@const isLatest = index === messages.length - 1}

      {#if msg.sender === "user"}
        <!-- Gelembung Pesan Pengguna (Rata Kanan, Bersih) -->
        <div class="flex justify-end gap-2 items-start pl-8">
          <div class="bg-[var(--color-paper-2)] border border-[var(--color-rule-strong)] text-[var(--color-ink)] rounded px-3.5 py-2 text-sm max-w-[80%] whitespace-pre-wrap leading-relaxed">
            <!-- ANTI-XSS: Selalu dirender teks polos murni {msg.text}, DILARANG @html -->
            {msg.text}
          </div>
          <div class="w-7 h-7 rounded bg-[var(--color-paper-2)] border border-[var(--color-rule)] flex items-center justify-center text-[var(--color-muted)] shrink-0">
            <User size={14} />
          </div>
        </div>
      {:else}
        <!-- Gelembung Pesan Asisten KnowDesk (Rata Kiri) -->
        <div class="flex justify-start gap-2 items-start pr-8">
          <div class="w-7 h-7 rounded bg-[var(--color-accent)] text-[var(--color-on-accent)] flex items-center justify-center shrink-0 mt-0.5">
            <Bot size={14} />
          </div>

          <div class="flex-1 max-w-[90%]">
            {#if msg.response?.tipe_respons === "langkah_solusi"}
              <!-- Render Komponen Langkah Terstruktur & Terverifikasi -->
              <StepGuide response={msg.response} {isLatest} />
            {:else if msg.response?.tipe_respons === "draf_tiket" && msg.response.draf_tiket}
              <!-- Render Komponen Formulir Tiket Satu Jalur -->
              <div class="text-sm text-[var(--color-ink)] whitespace-pre-wrap leading-relaxed mb-2">
                {msg.text}
              </div>
              <TicketModal ticket={msg.response.draf_tiket} isInteractive={isLatest} />
            {:else}
              <!-- Pesan Asisten Polos (Klarifikasi, Tidak Ditemukan, Tiket Terkirim, Selesai) -->
              <div class="bg-[var(--color-surface)] border border-[var(--color-rule)] text-[var(--color-ink)] rounded px-4 py-3 text-sm leading-relaxed shadow-sm">
                <!-- ANTI-XSS: Selalu dirender teks polos murni {msg.text}, DILARANG @html -->
                <p class="whitespace-pre-wrap">{msg.text}</p>
              </div>
            {/if}
          </div>
        </div>
      {/if}
    {/each}
  {/if}

  <!-- Indikator Loading Skeleton / Memuat Jawaban (§9.10) -->
  {#if isLoading}
    <div class="flex justify-start gap-2 items-start pr-8">
      <div class="w-7 h-7 rounded bg-[var(--color-accent)] text-[var(--color-on-accent)] flex items-center justify-center shrink-0">
        <Bot size={14} />
      </div>
      <div class="bg-[var(--color-surface)] border border-[var(--color-rule)] rounded px-4 py-3 max-w-[60%] space-y-2 shadow-sm">
        <div class="flex items-center gap-2 text-xs text-[var(--color-muted)]">
          <Loader2 size={13} class="animate-spin text-[var(--color-accent)]" />
          <span>Menyusun panduan langkah…</span>
        </div>
        <div class="space-y-1.5 pt-1">
          <div class="h-2.5 bg-[var(--color-paper-2)] rounded w-48 animate-pulse"></div>
          <div class="h-2.5 bg-[var(--color-paper-2)] rounded w-36 animate-pulse"></div>
        </div>
      </div>
    </div>
  {/if}
</div>
