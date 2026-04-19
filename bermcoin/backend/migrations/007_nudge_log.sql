CREATE TABLE IF NOT EXISTS nudge_log (
  id BIGSERIAL PRIMARY KEY,
  watch_id BIGINT REFERENCES rate_watches(id),
  user_id UUID REFERENCES members(id),
  from_ccy TEXT,
  to_ccy TEXT,
  rate_at_nudge NUMERIC,
  estimated_receive NUMERIC,
  channels_fired TEXT[],
  sources_confirmed INT DEFAULT 1,
  rate_verified BOOLEAN DEFAULT TRUE,
  fired_at TIMESTAMPTZ DEFAULT NOW()
);
