<script lang="ts">
  import ChatBox from "$lib/components/ChatBox.svelte";
  import StepGuide from "$lib/components/StepGuide.svelte";
  import TicketModal from "$lib/components/TicketModal.svelte";
  import type { ChatResponse, DraftTicket, MessageItem } from "$lib/types";
  import { AlertTriangle, CheckCircle2, Layers } from "lucide-svelte";

  const isDev = import.meta.env.DEV;

  const mockStepResponse: ChatResponse = {
    session_id: "demo-session-step",
    status: "langkah_solusi",
    pesan: "Langkah 1: Matikan sambungan Wi-Fi pada perangkat Anda selama 10 detik, lalu sambungkan kembali ke SSID resmi kantor.",
    langkah_saat_ini: 1,
    langkah_total_tersedia: 4,
    memerlukan_konfirmasi: true,
    sumber: [
      {
        article_id: "KB-001",
        judul: "Troubleshooting Koneksi Wi-Fi Kantor",
        skor_rrf: 0.88,
        kutipan: "Langkah awal jika gagal tersambung adalah me-restart adapter jaringan perangkat."
      }
    ],
    keyakinan: "tinggi",
    biaya_usd: 0.00015
  };

  const mockDraftTicket: DraftTicket = {
    ticket_id: "TIK-20261019-01",
    judul: "Koneksi Wi-Fi Lantai 2 Terputus Berulang",
    kategori: "Jaringan",
    prioritas: "sedang",
    deskripsi: "Pengguna sudah menjalankan langkah troubleshooting 1 hingga 4. Adapter tetap menolak autentikasi RADIUS kantor.",
    status: "draf"
  };

  const mockSelesaiResponse: ChatResponse = {
    session_id: "demo-session-selesai",
    status: "selesai",
    pesan: "Masalah koneksi Wi-Fi berhasil diselesaikan pada langkah ke-2. Sesi bantuan mandiri ini telah ditutup dengan sukses.",
    langkah_saat_ini: 2,
    langkah_total_tersedia: 4,
    memerlukan_konfirmasi: false,
    sumber: [],
    keyakinan: "tinggi",
    biaya_usd: 0.0001
  };

  const idleMessages: MessageItem[] = [];

  const conversationMessages: MessageItem[] = [
    {
      id: "msg-1",
      sender: "user",
      text: "Wi-Fi di laptop saya sering putus saat pindah ke ruang rapat lantai 2.",
      timestamp: new Date()
    },
    {
      id: "msg-2",
      sender: "assistant",
      text: "Baik, mari kita periksa konfigurasi adapter Wi-Fi Anda terlebih dahulu.",
      response: mockStepResponse,
      timestamp: new Date()
    }
  ];

  const solvedMessages: MessageItem[] = [
    {
      id: "msg-s1",
      sender: "user",
      text: "Saya sudah lupa kata sandi email kantor dan akun terkunci.",
      timestamp: new Date()
    },
    {
      id: "msg-s2",
      sender: "assistant",
      text: "Selesai",
      response: mockSelesaiResponse,
      timestamp: new Date()
    }
  ];
</script>

<svelte:head>
  <title>Galeri Desain Komponen (Dev) — KnowDesk AI</title>
</svelte:head>

{#if !isDev}
  <div class="p-8 text-center text-[var(--color-muted)]">
    <p class="text-sm">Halaman galeri desain hanya tersedia pada mode pengembangan (development).</p>
  </div>
{:else}
  <div class="p-6 max-w-[var(--chat-max)] mx-auto space-y-10 text-[var(--color-ink)] bg-[var(--color-paper)]">
    <!-- Header Galeri -->
    <header class="pb-4 border-b border-[var(--color-rule)] space-y-1">
      <div class="flex items-center gap-2">
        <Layers size={18} class="text-[var(--color-accent)]" />
        <h1 class="text-lg font-bold tracking-tight text-[var(--color-ink)]">
          Galeri State Komponen Antarmuka
        </h1>
      </div>
      <p class="text-xs text-[var(--color-muted)]">
        Dokumentasi visual state komponen (designsystem.md §13.5). Khusus lingkungan pengembangan.
      </p>
    </header>

    <!-- State 1: Idle / Welcome State -->
    <section class="space-y-3">
      <div class="flex items-center justify-between pb-1 border-b border-[var(--color-rule)]">
        <h2 class="text-xs font-semibold tracking-wide uppercase text-[var(--color-muted)]">
          1. State Idle (ChatBox Kosong / Sambutan Awal)
        </h2>
        <span class="text-xs font-mono bg-[var(--color-paper-2)] px-2 py-0.5 rounded border border-[var(--color-rule)]">
          idle
        </span>
      </div>
      <div class="border border-[var(--color-rule)] rounded bg-[var(--color-surface)] p-2">
        <ChatBox messages={idleMessages} isLoading={false} />
      </div>
    </section>

    <!-- State 2: Loading State -->
    <section class="space-y-3">
      <div class="flex items-center justify-between pb-1 border-b border-[var(--color-rule)]">
        <h2 class="text-xs font-semibold tracking-wide uppercase text-[var(--color-muted)]">
          2. State Loading (Menunggu Respon AI & Skeleton)
        </h2>
        <span class="text-xs font-mono bg-[var(--color-paper-2)] px-2 py-0.5 rounded border border-[var(--color-rule)]">
          loading
        </span>
      </div>
      <div class="border border-[var(--color-rule)] rounded bg-[var(--color-surface)] p-2">
        <ChatBox messages={conversationMessages} isLoading={true} />
      </div>
    </section>

    <!-- State 3: Error State -->
    <section class="space-y-3">
      <div class="flex items-center justify-between pb-1 border-b border-[var(--color-rule)]">
        <h2 class="text-xs font-semibold tracking-wide uppercase text-[var(--color-muted)]">
          3. State Error (Banner Galat Jaringan / Batasan Sistem)
        </h2>
        <span class="text-xs font-mono bg-[var(--color-paper-2)] px-2 py-0.5 rounded border border-[var(--color-rule)]">
          error
        </span>
      </div>
      <div class="flex items-center gap-2 p-3 rounded bg-[var(--color-danger-soft)] text-[var(--color-danger)] border border-[var(--color-danger)] text-xs">
        <AlertTriangle size={15} class="shrink-0" />
        <span class="flex-1">Gagal menghubungi server basis data MySQL. Pastikan kontainer docker aktif di port 3307.</span>
        <span class="underline font-medium cursor-pointer">Tutup</span>
      </div>
    </section>

    <!-- State 4: Langkah Solusi -->
    <section class="space-y-3">
      <div class="flex items-center justify-between pb-1 border-b border-[var(--color-rule)]">
        <h2 class="text-xs font-semibold tracking-wide uppercase text-[var(--color-muted)]">
          4. State Langkah Solusi (StepGuide Komponen Terisolasi)
        </h2>
        <span class="text-xs font-mono bg-[var(--color-paper-2)] px-2 py-0.5 rounded border border-[var(--color-rule)]">
          langkah_solusi
        </span>
      </div>
      <StepGuide response={mockStepResponse} isLatest={true} />
    </section>

    <!-- State 5: Draf Tiket Eskalasi -->
    <section class="space-y-3">
      <div class="flex items-center justify-between pb-1 border-b border-[var(--color-rule)]">
        <h2 class="text-xs font-semibold tracking-wide uppercase text-[var(--color-muted)]">
          5. State Draf Tiket (TicketModal Pra-Konfirmasi Manusia / HITL)
        </h2>
        <span class="text-xs font-mono bg-[var(--color-paper-2)] px-2 py-0.5 rounded border border-[var(--color-rule)]">
          draf_tiket
        </span>
      </div>
      <TicketModal ticket={mockDraftTicket} isInteractive={false} />
    </section>

    <!-- State 6: Selesai / Masalah Teratasi -->
    <section class="space-y-3">
      <div class="flex items-center justify-between pb-1 border-b border-[var(--color-rule)]">
        <h2 class="text-xs font-semibold tracking-wide uppercase text-[var(--color-muted)]">
          6. State Selesai (Konfirmasi Masalah Teratasi)
        </h2>
        <span class="text-xs font-mono bg-[var(--color-paper-2)] px-2 py-0.5 rounded border border-[var(--color-rule)]">
          selesai
        </span>
      </div>
      <div class="p-4 rounded border border-[var(--color-rule)] bg-[var(--color-accent-soft)] text-[var(--color-ink)] flex items-start gap-3">
        <CheckCircle2 size={18} class="text-[var(--color-accent)] shrink-0 mt-0.5" />
        <div class="space-y-1">
          <p class="text-sm font-semibold text-[var(--color-accent)]">Kendala Berhasil Diatasi</p>
          <p class="text-xs text-[var(--color-muted)] leading-relaxed">
            {mockSelesaiResponse.pesan}
          </p>
        </div>
      </div>
    </section>
  </div>
{/if}
