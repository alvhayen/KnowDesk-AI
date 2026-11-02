-- ==============================================================================
-- KnowDesk AI — 002_users.sql
-- Pemisahan Pengguna Basis Data & Penegakan Hak Akses Lapis 3 (agents.md §11)
-- ==============================================================================

-- 1. Buat User Basis Data (jika belum ada)
CREATE USER IF NOT EXISTS 'knowdesk_ingest'@'localhost' IDENTIFIED BY 'knowdesk_ingest_pass';
CREATE USER IF NOT EXISTS 'knowdesk_ingest'@'%' IDENTIFIED BY 'knowdesk_ingest_pass';

CREATE USER IF NOT EXISTS 'knowdesk_app'@'localhost' IDENTIFIED BY 'knowdesk_app_pass';
CREATE USER IF NOT EXISTS 'knowdesk_app'@'%' IDENTIFIED BY 'knowdesk_app_pass';

-- 2. Hak Akses User Ingestion (knowdesk_ingest)
-- Akses penuh DDL dan DML hanya pada tabel articles dan chunks
GRANT ALL PRIVILEGES ON knowdesk_ai.articles TO 'knowdesk_ingest'@'localhost';
GRANT ALL PRIVILEGES ON knowdesk_ai.articles TO 'knowdesk_ingest'@'%';
GRANT ALL PRIVILEGES ON knowdesk_ai.chunks TO 'knowdesk_ingest'@'localhost';
GRANT ALL PRIVILEGES ON knowdesk_ai.chunks TO 'knowdesk_ingest'@'%';

-- 3. Hak Akses User Aplikasi Runtime (knowdesk_app)
-- HANYA hak SELECT pada articles & chunks (baca dokumen KB)
GRANT SELECT ON knowdesk_ai.articles TO 'knowdesk_app'@'localhost';
GRANT SELECT ON knowdesk_ai.articles TO 'knowdesk_app'@'%';
GRANT SELECT ON knowdesk_ai.chunks TO 'knowdesk_app'@'localhost';
GRANT SELECT ON knowdesk_ai.chunks TO 'knowdesk_app'@'%';

-- Hak SELECT, INSERT, UPDATE pada sessions, tickets, dan agent_traces
-- Penegakan Aturan §11: Dilarang keras hak DROP atau ALTER
GRANT SELECT, INSERT, UPDATE ON knowdesk_ai.sessions TO 'knowdesk_app'@'localhost';
GRANT SELECT, INSERT, UPDATE ON knowdesk_ai.sessions TO 'knowdesk_app'@'%';
GRANT SELECT, INSERT, UPDATE ON knowdesk_ai.tickets TO 'knowdesk_app'@'localhost';
GRANT SELECT, INSERT, UPDATE ON knowdesk_ai.tickets TO 'knowdesk_app'@'%';
GRANT SELECT, INSERT, UPDATE ON knowdesk_ai.agent_traces TO 'knowdesk_app'@'localhost';
GRANT SELECT, INSERT, UPDATE ON knowdesk_ai.agent_traces TO 'knowdesk_app'@'%';

FLUSH PRIVILEGES;
