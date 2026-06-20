# Architecture

```text
Browser UI
  |
  | POST /api/troubleshoot
  v
FastAPI API
  |
  |-- Auth + role context
  |-- Rate limiting
  |-- Session store
  |     |-- SQLite locally
  |     `-- PostgreSQL in production
  |
  |-- Diagnostics engine
  |     |-- Local sample logs/metrics
  |     |-- Datadog adapter
  |     |-- Prometheus adapter
  |     `-- Splunk adapter
  |
  |-- RAG retrieval
  |     |-- Local TF-IDF fallback
  |     |-- OpenAI embeddings
  |     |-- pgvector target schema
  |     `-- Pinecone-ready boundary
  |
  |-- RCA generation
  |     |-- Local deterministic fallback
  |     `-- OpenAI Responses API when OPENAI_API_KEY is set
  |
  `-- Telemetry
        |-- JSON structured logs locally
        `-- Datadog/OpenTelemetry/Splunk production path
```

## Why This Shape

The project is designed to run without paid credentials while exposing the same boundaries a production incident assistant needs. Local JSON data keeps the demo portable; OpenAI, vector databases, and observability systems are activated by environment variables or adapter implementations.

## Production Gaps Still To Close

- Replace demo bearer tokens with OAuth/OIDC.
- Move rate limiting from memory to Redis.
- Replace SQLite with PostgreSQL for multi-instance deployments.
- Implement concrete Datadog/Splunk/Prometheus queries for the target customer environment.
- Add OpenTelemetry traces across retrieval, diagnostics, and LLM calls.
- Add CI/CD, secret management, and deployment manifests.
