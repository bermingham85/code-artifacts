CREATE TABLE IF NOT EXISTS affiliate_conversions (
  id BIGSERIAL PRIMARY KEY,
  affiliate_ref TEXT NOT NULL,
  member_id UUID REFERENCES members(id),
  plan TEXT,
  converted_at TIMESTAMPTZ DEFAULT NOW()
);
