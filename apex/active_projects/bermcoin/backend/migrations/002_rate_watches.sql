CREATE TABLE IF NOT EXISTS rate_watches (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES members(id) ON DELETE CASCADE,
  from_ccy TEXT NOT NULL,
  to_ccy TEXT NOT NULL,
  target_rate NUMERIC NOT NULL,
  send_amount NUMERIC,
  send_ccy TEXT,
  channels TEXT[] DEFAULT ARRAY['telegram','email'],
  status TEXT DEFAULT 'looking' CHECK (status IN ('looking','on_hold','paused_limit','removed')),
  nudges_this_month INT DEFAULT 0,
  total_nudges INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_nudge_at TIMESTAMPTZ
);
