# AI Troubleshooting Agent

An LLM-style troubleshooting assistant that demonstrates RAG, diagnostics, root cause analysis, remediation recommendations, escalation routing, and session memory.

## What It Includes

- FastAPI backend with `/api/troubleshoot`
- OpenAI-ready LLM integration using the Responses API
- OpenAI embeddings path with local RAG-style retrieval fallback
- Sample system logs and service metrics
- Root cause analysis and remediation recommendation engine
- Escalation decisioning for critical or low-confidence incidents
- Persistent SQLite session memory
- Demo bearer-token authentication and rate limiting
- Browser UI for incident investigation
- Unit tests for retrieval and diagnostic behavior
- Docker, Compose, pgvector schema, architecture notes, and case study

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

```text
frontend/index.html
```

The frontend checks `http://127.0.0.1:8001` first, then falls back to `http://127.0.0.1:8000`. Use `--port 8001` if port 8000 is already taken.

## Environment

Copy `.env.example` to `.env` and set values as needed.

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
AUTH_TOKENS=demo-analyst-token:analyst,demo-admin-token:admin
```

If `OPENAI_API_KEY` is empty, the app uses deterministic local RCA and TF-IDF retrieval. That keeps the demo runnable without paid API usage.

In PowerShell, quote the key:

```powershell
$env:OPENAI_API_KEY="sk-your-new-key"
```

Do not paste API keys into chat, source files, screenshots, or `.env.example`. If a key is exposed, revoke it and create a new one.

## Auth

The API allows anonymous local demo calls. For role-aware calls, send:

```bash
curl -X POST http://127.0.0.1:8000/api/troubleshoot \
  -H "Authorization: Bearer demo-analyst-token" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"payments-api has checkout timeouts and 503s\",\"severity\":\"high\"}"
```

## Docker

```bash
docker compose up --build
```

The Compose file includes PostgreSQL with pgvector so the project has a clear vector-database deployment path.

## Demo Prompt

```text
Checkout is timing out in payments-api and customers are seeing 503 errors. What is the likely root cause and what should the on-call team do?
```

## Real Integration Path

This demo keeps credentials and external systems out of the repo. In production, local retrieval can use OpenAI embeddings plus pgvector, Pinecone, Weaviate, or Elasticsearch. Sample logs and metrics can be replaced with Datadog, CloudWatch, Prometheus, Splunk, OpenTelemetry, or service APIs. Escalation can be connected to Jira, ServiceNow, Slack, Teams, PagerDuty, or email.

## Portfolio Notes

This is intentionally implemented as a runnable portfolio project, not a slide-only claim. The architecture mirrors an enterprise incident assistant while keeping the local version easy to run and explain.

See `ARCHITECTURE.md` and `CASE_STUDY.md` for the recruiter/interview narrative.
