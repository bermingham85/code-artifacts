CREATE TABLE IF NOT EXISTS churn_log (
  id BIGSERIAL PRIMARY KEY,
  member_id UUID REFERENCES members(id),
  plan TEXT,
  from_ccy TEXT,
  to_ccy TEXT,
  churned_at TIMESTAMPTZ DEFAULT NOW()
);
