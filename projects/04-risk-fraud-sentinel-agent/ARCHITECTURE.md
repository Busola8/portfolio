# Architecture

```text
Transaction Event / API Input
  |
  v
FastAPI Fraud Sentinel API
  |
  |-- RiskAgent: anomaly and rule scoring
  |-- ContextAgent: customer, device, geography, velocity
  |-- InvestigationAgent: decision and case summary
  |-- ReportingAgent: SharePoint report and voice briefing
  |
  v
Case Store / Dashboard
```

The local demo uses deterministic rules so the behavior is explainable. A production version would add streaming ingestion, feature storage, ML anomaly models, analyst feedback, and persistent case management.
