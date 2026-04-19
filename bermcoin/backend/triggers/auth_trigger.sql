-- Bermcoin Auth Triggers
-- BERMCOIN-BCK-TRG-00001 and BERMCOIN-BCK-TRG-00002

CREATE OR REPLACE FUNCTION handle_new_auth_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO members (id, email)
  VALUES (NEW.id, NEW.email)
  ON CONFLICT (email) DO UPDATE SET id = NEW.id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_auth_user();

CREATE OR REPLACE FUNCTION reset_monthly_nudges()
RETURNS TRIGGER AS $$
BEGIN
  IF date_trunc('month', NOW()) > date_trunc('month', OLD.last_nudge_reset) THEN
    NEW.nudges_this_month := 0;
    NEW.last_nudge_reset := date_trunc('month', NOW());
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS auto_reset_nudges ON members;
CREATE TRIGGER auto_reset_nudges
  BEFORE UPDATE ON members
  FOR EACH ROW EXECUTE FUNCTION reset_monthly_nudges();
