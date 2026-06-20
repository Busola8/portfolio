# Case Study: AI Troubleshooting Agent

## Problem

SRE and support teams often investigate incidents by jumping across logs, metrics, runbooks, dashboards, and chat history. This slows root cause analysis and makes escalation inconsistent.

## Solution

This project implements a troubleshooting assistant that combines incident prompts, system logs, service metrics, retrieved runbook evidence, root cause analysis, remediation steps, escalation decisions, and multi-turn session memory.

## What Is Implemented

- FastAPI backend with typed request/response models
- OpenAI-ready LLM integration through the Responses API
- OpenAI embeddings path with local TF-IDF fallback
- SQLite persistent session memory
- Role-aware bearer token authentication for demo use
- In-memory rate limiting
- Structured telemetry events
- Datadog, Prometheus, and Splunk adapter boundaries
- Dockerfile and Compose configuration with pgvector
- Evaluation tests for retrieval quality and RCA behavior

## What Is Mocked Locally

| Area | Local Demo | Production Replacement |
| --- | --- | --- |
| Logs | `data/sample_logs.json` | Datadog, Splunk, CloudWatch, OpenTelemetry |
| Metrics | `data/metrics.json` | Prometheus, Datadog, CloudWatch |
| Vector search | TF-IDF fallback or OpenAI embeddings | pgvector or Pinecone |
| Auth | Demo bearer tokens | OAuth/OIDC, SSO, RBAC |
| Sessions | SQLite | PostgreSQL |
| Telemetry | JSON logs | OpenTelemetry, Datadog, Splunk |

## Productionization Plan

1. Add customer-specific log and metric queries.
2. Store runbook chunks and embeddings in pgvector or Pinecone.
3. Enable OpenAI with `OPENAI_API_KEY`.
4. Replace demo auth with identity-provider backed JWT validation.
5. Add Redis-backed rate limiting for multi-instance deployments.
6. Deploy through Docker/Kubernetes with managed secrets.
7. Track retrieval accuracy, RCA correctness, escalation precision, and user feedback.

## Interview Talking Points

- The system uses RAG to ground recommendations in operational runbooks.
- The deterministic RCA fallback keeps the app usable when the LLM is unavailable.
- Persistent sessions make multi-turn troubleshooting possible.
- The integration adapters separate product logic from vendor-specific observability APIs.
- The project is honest about mocked local data versus production integrations.
