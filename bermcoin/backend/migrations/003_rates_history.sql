CREATE TABLE IF NOT EXISTS rates_history (
  id BIGSERIAL PRIMARY KEY,
  from_ccy TEXT NOT NULL,
  to_ccy TEXT NOT NULL,
  rate NUMERIC NOT NULL,
  source TEXT NOT NULL,
  is_interpolated BOOLEAN DEFAULT FALSE,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_rates_pair_time ON rates_history(from_ccy, to_ccy, recorded_at DESC);
