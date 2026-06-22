# Case Study: AI Risk & Fraud Sentinel Agent

## Problem

Fraud teams need to detect risky transactions quickly while keeping decisions explainable. Manual review is slow, and opaque risk scores are hard to defend.

## Solution

This project implements a fraud sentinel that scores each transaction using transparent anomaly and rule checks, generates an investigation trail, recommends an action, and prepares alert/report artifacts.

## Implemented Locally

- Transaction risk scoring
- Fraud rule findings
- Investigation case generation
- Alert recommendations
- SharePoint report path
- Voice briefing text
- Public static fallback

## Production Replacements

| Area | Local Demo | Production |
| --- | --- | --- |
| Transactions | Form/sample JSON | Banking APIs or event stream |
| Risk engine | Rules | Rules + ML anomaly model |
| Case store | In-memory | PostgreSQL/case management |
| Reporting | Simulated SharePoint path | Microsoft Graph/SharePoint |
| Alerts | UI list | Teams, Slack, email, PagerDuty |
| Voice | Text briefing | Telephony/voice agent integration |
