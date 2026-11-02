-- ==============================================================================
-- KnowDesk AI — 001_initial.sql
-- Migrasi DDL Skema Awal Basis Data (agents.md §3 K9, §4, §11)
-- ==============================================================================

-- 1. Tabel Artikel Knowledge Base
CREATE TABLE IF NOT EXISTS articles (
    article_id      VARCHAR(50) NOT NULL,
    judul           VARCHAR(255) NOT NULL,
    kategori        VARCHAR(50) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'published',
    asal            VARCHAR(255) NOT NULL DEFAULT 'buatan sendiri (sintetis)',
    raw_content     LONGTEXT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (article_id),
    INDEX idx_articles_status (status),
    INDEX idx_articles_kategori (kategori)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Tabel Chunking Dokumen & Vektor Embedding
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id        VARCHAR(64) NOT NULL,
    article_id      VARCHAR(50) NOT NULL,
    section_title   VARCHAR(255) NOT NULL,
    chunk_text      TEXT NOT NULL,
    step_number     INT NULL DEFAULT NULL,
    embedding_json  JSON NOT NULL,
    PRIMARY KEY (chunk_id),
    INDEX idx_chunks_article (article_id),
    CONSTRAINT fk_chunks_article FOREIGN KEY (article_id)
        REFERENCES articles (article_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Tabel Sesi Bantuan & State Mesin
CREATE TABLE IF NOT EXISTS sessions (
    session_id          VARCHAR(64) NOT NULL,
    status              VARCHAR(30) NOT NULL DEFAULT 'clarifying',
    current_step        INT NOT NULL DEFAULT 0,
    clarification_count INT NOT NULL DEFAULT 0,
    artikel_terpilih    VARCHAR(50) NULL DEFAULT NULL,
    draft_ticket_id     VARCHAR(50) NULL DEFAULT NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id),
    INDEX idx_sessions_status (status),
    INDEX idx_sessions_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tabel Tiket Eskalasi IT
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id       VARCHAR(50) NOT NULL,
    session_id      VARCHAR(64) NOT NULL,
    user_id         VARCHAR(50) NULL DEFAULT NULL,
    category        VARCHAR(50) NOT NULL DEFAULT 'lainnya',
    summary         TEXT NOT NULL,
    steps_tried     JSON NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticket_id),
    INDEX idx_tickets_session (session_id),
    INDEX idx_tickets_status (status),
    CONSTRAINT fk_tickets_session FOREIGN KEY (session_id)
        REFERENCES sessions (session_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Tabel Jejak Keputusan & Audit Token Agent
CREATE TABLE IF NOT EXISTS agent_traces (
    trace_id            VARCHAR(64) NOT NULL,
    session_id          VARCHAR(64) NOT NULL,
    action_type         VARCHAR(50) NOT NULL,
    tool_called         VARCHAR(50) NULL DEFAULT NULL,
    parameters          JSON NULL DEFAULT NULL,
    decision            TEXT NULL DEFAULT NULL,
    prompt_tokens       INT NOT NULL DEFAULT 0,
    completion_tokens   INT NOT NULL DEFAULT 0,
    model               VARCHAR(100) NOT NULL DEFAULT '',
    latency_ms          INT NOT NULL DEFAULT 0,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trace_id),
    INDEX idx_traces_session (session_id),
    INDEX idx_traces_created (created_at),
    CONSTRAINT fk_traces_session FOREIGN KEY (session_id)
        REFERENCES sessions (session_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
