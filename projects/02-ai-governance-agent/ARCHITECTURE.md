# Architecture

```text
Agent Runtime Events / Manual Registry Entry
  |
  v
FastAPI Agent Governance API
  |
  |-- AccessControl
  |-- RegistryAgent
  |     |-- identity, owner, department, region
  |     |-- permissions and tool access
  |
  |-- UsageAgent
  |     |-- tasks completed
  |     |-- human interventions
  |     |-- active users
  |     |-- token/model cost
  |     `-- estimated time saved
  |
  |-- PrivacyAgent
  |-- AccessAgent
  |-- ComplianceAgent
  |-- ExplainabilityAgent
  |-- RiskAgent
  |
  |-- Audit Store
  |     |-- SQLite locally
  |     `-- PostgreSQL in production
  |
  `-- Executive Dashboard
        |-- automation percentage
        |-- department value
        |-- high-risk agents
        |-- least/most active agents
        `-- cost and intervention metrics
```

The local orchestrator is deterministic and testable. In a production version, each named agent maps cleanly to a LangGraph node with shared state for the agent registry, policy findings, analytics metrics, and alert decisions.

## Production Tables

A production PostgreSQL version would split the current JSON audit payload into normalized tables:

- `agents`
- `agent_permissions`
- `agent_tools`
- `agent_usage_events`
- `agent_decision_traces`
- `agent_audits`
- `agent_department_value`

The local version keeps the payload compact so the portfolio demo is easy to run.
