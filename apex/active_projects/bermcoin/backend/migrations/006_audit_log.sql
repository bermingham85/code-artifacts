CREATE TABLE IF NOT EXISTS audit_log (
  id BIGSERIAL PRIMARY KEY,
  config_key TEXT,
  old_value TEXT,
  new_value TEXT,
  source_urls TEXT[],
  changed_at TIMESTAMPTZ DEFAULT NOW(),
  changed_by TEXT DEFAULT 'auto'
);
