# AI Risk & Fraud Sentinel Agent

Real-time fraud monitoring demo for banking transactions, with anomaly scoring, rules, investigation workflow, alerts, SharePoint-style reporting, and voice briefing simulation.

## What It Includes

- FastAPI backend with `/api/investigate`, `/api/monitor`, and `/api/dashboard`
- Rule-based fraud and anomaly scoring engine
- Investigation workflow with explainable findings
- Alert recommendations: allow, step-up auth, manual review, or block
- SharePoint report and voice briefing simulation
- Browser UI with static fallback for GitHub Pages
- Tests and deployment config

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8031
```

Then open:

```text
frontend/index.html
```

## Recruiter Demo Mode

The frontend includes browser-side fraud scoring. If the backend is offline, recruiters can still investigate a transaction and see risk score, findings, decision, alerts, and reports.

## Production Path

- Replace sample transaction input with banking API/event stream.
- Add model-based anomaly detection alongside the rules engine.
- Persist cases in PostgreSQL.
- Export reports to SharePoint.
- Connect alerts to Teams, Slack, email, or case management tools.
- Add audit logging and analyst feedback loops.
