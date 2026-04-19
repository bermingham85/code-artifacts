-- Bermcoin Row Level Security Policies
-- BERMCOIN-BCK-RLS-00001

ALTER TABLE members ENABLE ROW LEVEL SECURITY;
ALTER TABLE rate_watches ENABLE ROW LEVEL SECURITY;
ALTER TABLE nudge_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE affiliate_conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE churn_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE rates_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE config ENABLE ROW LEVEL SECURITY;
ALTER TABLE rate_cache ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "own_member_row" ON members;
CREATE POLICY "own_member_row" ON members FOR ALL USING (auth.uid() = id);

DROP POLICY IF EXISTS "own_watches" ON rate_watches;
CREATE POLICY "own_watches" ON rate_watches FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "own_nudges" ON nudge_log;
CREATE POLICY "own_nudges" ON nudge_log FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "public_rates" ON rates_history;
CREATE POLICY "public_rates" ON rates_history FOR SELECT USING (true);

DROP POLICY IF EXISTS "public_config" ON config;
CREATE POLICY "public_config" ON config FOR SELECT USING (true);

DROP POLICY IF EXISTS "public_cache" ON rate_cache;
CREATE POLICY "public_cache" ON rate_cache FOR SELECT USING (true);

-- n8n uses SUPABASE_SERVICE_ROLE_KEY
-- Service role bypasses RLS natively — no extra policy needed
