# Agent Governance and Analytics Platform

A runnable internal platform for managing AI agents as company assets: identity, ownership, department, permissions, tool access, auditability, usage, cost, human intervention, time saved, and automation value.

## Product Idea

As a company scales from a few agents to dozens or hundreds, the hard problem shifts from building agents to governing and measuring them. This platform acts like an HR system and analytics dashboard for agents.

It answers questions like:

- Which agents exist, and who owns them?
- Which department uses each agent?
- Which tools and permissions does each agent have?
- Which agents are actually being used?
- Which agents create value, save time, or cost too much?
- Which tasks still require humans?
- Can we explain agent decisions after the fact?
- What percentage of work is automated across the company?

## What It Includes

- FastAPI backend with `/api/evaluate` and `/api/dashboard`
- Agent registry model for owner, department, region, permissions, and tools
- Multi-agent governance workflow inspired by LangGraph
- Usage analytics: completed tasks, interventions, automation percentage, time saved, token cost
- Governance checks for PII, retention, human review, audit logging, tool access, and explainability
- SQLite audit storage locally with PostgreSQL schema for production
- Demo bearer-token roles
- Executive dashboard UI
- Tests for policy scoring, value analytics, orchestration, storage, and API behavior

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8011
```

Then open:

```text
frontend/index.html
```

## Recruiter Demo Mode

The browser UI includes a static fallback evaluator. If the FastAPI backend is not running, the dashboard still works on GitHub Pages by calculating governance risk, value score, automation percentage, and findings directly in the browser.

Use the backend for the full API/audit-store version. Use the static fallback for public portfolio viewing.

## Demo Auth

```text
Authorization: Bearer demo-governance-token
```

## Portfolio Agent Examples

The platform can govern the same agent portfolio being built here:

- AI Troubleshooting Agent
- AI Governance Agent
- AI-Powered Workflow Automation Agent
- AI Risk & Fraud Sentinel Agent
- Medallion Architecture Data Warehouse
- Sales Forecasting ML Pipeline

The default region is Nigeria.

## Production Path

The local version uses deterministic agents so the project runs without paid services. In production:

- Replace local orchestration with LangGraph state graph nodes.
- Use PostgreSQL for agent registry, audit, permission, and analytics tables.
- Connect live usage events from agent runtimes, workflow systems, and model gateways.
- Add identity-provider JWT validation and role-based access control.
- Track token spend from OpenAI/Azure OpenAI/model gateway billing data.
- Add alerting to Slack, Teams, email, PagerDuty, or ServiceNow.
- Add OpenTelemetry traces and governance evidence exports.
