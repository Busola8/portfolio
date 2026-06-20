CREATE TABLE IF NOT EXISTS ai_governance_audits (
  audit_id TEXT PRIMARY KEY,
  agent_name TEXT NOT NULL,
  department TEXT,
  owner TEXT,
  score INTEGER NOT NULL,
  value_score INTEGER,
  automation_percentage NUMERIC,
  estimated_hours_saved NUMERIC,
  risk_level TEXT NOT NULL,
  alert_required BOOLEAN NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ai_governance_audits_risk_idx
ON ai_governance_audits (risk_level, created_at DESC);
