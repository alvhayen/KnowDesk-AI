<script lang="ts">
  import { chatStore, sendMessage, resetSession, dismissError } from "../lib/stores/chat";
  import ChatBox from "../lib/components/ChatBox.svelte";
  import { Send, RotateCcw, AlertTriangle } from "lucide-svelte";

  let inputMessage = $state("");

  function handleSubmit(e?: SubmitEvent) {
    if (e) e.preventDefault();
    if (!inputMessage.trim() || $chatStore.isLoading) return;
    const msg = inputMessage.trim();
    inputMessage = "";
    sendMessage(msg);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function handleSuggestion(text: string) {
    sendMessage(text);
  }
</script>

<svelte:head>
  <title>KnowDesk AI — Bantuan Mandiri IT Kantor</title>
</svelte:head>

<div class="flex flex-col h-screen w-full bg-[var(--color-paper)] text-[var(--color-ink)]">
  <!-- Header Aplikasi (§9.11) -->
  <header class="h-[var(--header-h)] border-b border-[var(--color-rule)] px-4 flex items-center justify-between bg-[var(--color-surface)] shrink-0">
    <div class="flex items-center gap-2.5">
      <!-- Kotak aksen identitas 10x10 px (§8) -->
      <span class="w-2.5 h-2.5 rounded-[1px] bg-[var(--color-accent)] shrink-0"></span>
      <h1 class="font-extrabold text-base tracking-tight text-[var(--color-ink)]">
        KnowDesk
      </h1>
      <span class="text-xs text-[var(--color-muted)] font-normal hidden sm:inline">
        · Bantuan Mandiri IT
      </span>
    </div>

    <div class="flex items-center gap-3">
      <button
        type="button"
        onclick={resetSession}
        class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-[var(--color-muted)] hover:text-[var(--color-ink)] hover:bg-[var(--color-paper-2)] rounded border border-[var(--color-rule)] transition-colors cursor-pointer"
        title="Mulai percakapan baru"
      >
        <RotateCcw size={13} />
        Sesi baru
      </button>
    </div>
  </header>

  <!-- Kontainer Percakapan Utama -->
  <main class="flex-1 flex flex-col overflow-hidden relative">
    <ChatBox messages={$chatStore.messages} isLoading={$chatStore.isLoading} />

    <!-- Baris Contoh Saran Gejala (Tampil Hanya Saat Belum Ada Pesan) -->
    {#if $chatStore.messages.length === 0}
      <div class="p-4 max-w-[var(--chat-max)] mx-auto w-full pt-0 shrink-0">
        <p class="text-xs font-medium text-[var(--color-muted)] mb-2">Contoh kendala umum:</p>
        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            onclick={() => handleSuggestion("Wi-Fi kantor tidak bisa tersambung")}
            class="text-xs px-2.5 py-1.5 rounded bg-[var(--color-surface)] border border-[var(--color-rule)] hover:border-[var(--color-rule-strong)] text-[var(--color-ink)] transition-colors cursor-pointer"
          >
            Wi-Fi kantor tidak bisa tersambung
          </button>
          <button
            type="button"
            onclick={() => handleSuggestion("Lupa kata sandi email kantor dan akun terkunci")}
            class="text-xs px-2.5 py-1.5 rounded bg-[var(--color-surface)] border border-[var(--color-rule)] hover:border-[var(--color-rule-strong)] text-[var(--color-ink)] transition-colors cursor-pointer"
          >
            Lupa kata sandi email kantor
          </button>
          <button
            type="button"
            onclick={() => handleSuggestion("Printer tidak merespons di komputer")}
            class="text-xs px-2.5 py-1.5 rounded bg-[var(--color-surface)] border border-[var(--color-rule)] hover:border-[var(--color-rule-strong)] text-[var(--color-ink)] transition-colors cursor-pointer"
          >
            Printer tidak merespons
          </button>
          <button
            type="button"
            onclick={() => handleSuggestion("Tidak bisa VPN akses jarak jauh dari rumah")}
            class="text-xs px-2.5 py-1.5 rounded bg-[var(--color-surface)] border border-[var(--color-rule)] hover:border-[var(--color-rule-strong)] text-[var(--color-ink)] transition-colors cursor-pointer"
          >
            Akses VPN jarak jauh
          </button>
        </div>
      </div>
    {/if}

    <!-- Banner Galat Jika Terjadi Masalah Jaringan -->
    {#if $chatStore.errorMessage}
      <div class="max-w-[var(--chat-max)] mx-auto w-full px-4 mb-2 shrink-0">
        <div class="flex items-center gap-2 p-2.5 rounded bg-[var(--color-danger-soft)] text-[var(--color-danger)] border border-[var(--color-danger)] text-xs">
          <AlertTriangle size={15} class="shrink-0" />
          <span class="flex-1">{$chatStore.errorMessage}</span>
          <button
            type="button"
            onclick={dismissError}
            class="underline font-medium hover:opacity-80 cursor-pointer"
          >
            Tutup
          </button>
        </div>
      </div>
    {/if}

    <!-- Area Komposer Input Pesan (Sticky di Bawah) -->
    <div class="p-4 border-t border-[var(--color-rule)] bg-[var(--color-surface)] shrink-0">
      <form onsubmit={handleSubmit} class="max-w-[var(--chat-max)] mx-auto flex gap-2">
        <textarea
          bind:value={inputMessage}
          onkeydown={handleKeydown}
          placeholder="Tuliskan keluhan atau gejala masalah IT Anda..."
          rows={1}
          disabled={$chatStore.isLoading}
          class="flex-1 p-2.5 text-sm rounded border border-[var(--color-rule)] bg-[var(--color-paper)] text-[var(--color-ink)] placeholder-[var(--color-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)] resize-none"
        ></textarea>

        <button
          type="submit"
          disabled={$chatStore.isLoading || !inputMessage.trim()}
          class="inline-flex items-center justify-center px-4 rounded bg-[var(--color-accent)] text-[var(--color-on-accent)] hover:bg-[var(--color-accent-hover)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer shrink-0"
          aria-label="Kirim pesan"
        >
          <Send size={15} />
        </button>
      </form>

      <!-- Label Wajib Disclaimer AI (Aturan R16) -->
      <footer class="mt-2 text-center text-xs text-[var(--color-muted)] max-w-[var(--chat-max)] mx-auto">
        Jawaban disusun oleh AI dan dapat keliru. Konfirmasikan hasil per langkah.
      </footer>
    </div>
  </main>
</div>
