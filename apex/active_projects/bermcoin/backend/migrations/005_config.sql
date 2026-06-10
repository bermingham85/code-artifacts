CREATE TABLE IF NOT EXISTS config (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  last_verified TIMESTAMPTZ DEFAULT NOW(),
  verified_by TEXT DEFAULT 'system',
  source_url TEXT,
  next_check TIMESTAMPTZ,
  confidence TEXT DEFAULT 'confirmed' CHECK (confidence IN ('confirmed','interpolated','uncertain'))
);
