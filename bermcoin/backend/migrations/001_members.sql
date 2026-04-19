CREATE TABLE IF NOT EXISTS members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_customer_id TEXT UNIQUE,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free','standard','pro')),
  status TEXT DEFAULT 'active' CHECK (status IN ('active','cancelled','paused')),
  telegram_user_id TEXT,
  whatsapp_number TEXT,
  preferred_channels TEXT[] DEFAULT ARRAY['telegram','email'],
  affiliate_ref TEXT,
  language TEXT DEFAULT 'en',
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  cancelled_at TIMESTAMPTZ,
  stripe_subscription_id TEXT,
  nudges_this_month INT DEFAULT 0,
  last_nudge_reset TIMESTAMPTZ DEFAULT date_trunc('month', NOW())
);
