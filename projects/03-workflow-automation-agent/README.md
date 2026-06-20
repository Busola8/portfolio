# AI-Powered Workflow Automation Agent

Runnable enterprise workflow automation demo for customer onboarding, KYC, document handling, approvals, notifications, and voice follow-up.

## What It Includes

- FastAPI backend with `/api/workflows/run` and `/api/dashboard`
- CrewAI-style agent roles: Intake, KYC, Document, Approval, Voice, Notification
- n8n-style workflow sequence with local deterministic runner
- Customer onboarding and KYC workflow for Nigeria
- SharePoint/document-management simulation
- Approval routing and stakeholder notifications
- Browser UI with static fallback for GitHub Pages
- Tests and deployment files

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8021
```

Then open:

```text
frontend/index.html
```

## Recruiter Demo Mode

The browser UI includes a static workflow runner. If the FastAPI backend is not running or not yet deployed, recruiters can still run the onboarding workflow directly in the browser.

## n8n Integration Path

The local engine maps to n8n like this:

- Webhook trigger receives onboarding request.
- KYC validation nodes check documents and external APIs.
- SharePoint nodes create folders and upload documents.
- Wait/approval nodes pause for compliance review.
- Twilio/telephony nodes handle voice follow-up.
- Email/Teams/Slack nodes notify stakeholders.

## Production Path

- Replace local workflow engine with n8n workflow execution.
- Add PostgreSQL for workflow state.
- Add SharePoint/Microsoft Graph credentials.
- Add KYC provider API credentials.
- Add queueing for long-running approvals.
- Add audit trail and role-based access.
