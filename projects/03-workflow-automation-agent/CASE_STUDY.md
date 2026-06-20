# Case Study: AI-Powered Workflow Automation Agent

## Problem

Customer onboarding, KYC checks, document collection, approvals, and status updates often move across email, shared drives, manual checklists, and disconnected systems. This slows onboarding and makes audit trails weak.

## Solution

This project implements an automation agent that coordinates onboarding through specialized workflow agents. It validates KYC documents, prepares document workspaces, routes approvals, schedules voice follow-up, and notifies stakeholders.

## Implemented Locally

- Onboarding workflow API
- Browser workflow console
- KYC document validation
- SharePoint folder simulation
- Approval routing
- Voice follow-up simulation
- Static fallback for public portfolio demo

## Production Replacements

| Area | Local Demo | Production |
| --- | --- | --- |
| Workflow runner | Python deterministic engine | n8n workflow execution |
| Agent roles | Local classes | CrewAI agents or task workers |
| Documents | Simulated SharePoint folder | Microsoft Graph / SharePoint |
| Approvals | Local status | n8n Wait node, ServiceNow, Jira |
| Voice | Script generation | Twilio or telephony provider |
| State | In-memory store | PostgreSQL |
