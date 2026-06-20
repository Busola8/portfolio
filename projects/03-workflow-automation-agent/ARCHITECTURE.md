# Architecture

```text
Browser UI / API Client
  |
  v
FastAPI Workflow API
  |
  |-- IntakeAgent
  |-- KYCAgent
  |-- DocumentAgent
  |-- ApprovalAgent
  |-- VoiceAgent
  `-- NotificationAgent
       |
       v
Workflow Store / Dashboard
```

The local workflow runner is intentionally deterministic. In production, each agent step maps to n8n nodes or CrewAI tasks, while FastAPI remains the API layer for workflow events, status, approvals, and dashboards.
