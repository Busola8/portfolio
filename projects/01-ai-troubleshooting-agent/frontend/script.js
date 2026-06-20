const form = document.getElementById('troubleshoot-form');
const messageInput = document.getElementById('message');
const severityInput = document.getElementById('severity');
const rootCause = document.getElementById('root-cause');
const confidence = document.getElementById('confidence');
const remediation = document.getElementById('remediation');
const evidence = document.getElementById('evidence');
const memory = document.getElementById('memory');

let sessionId = null;
const apiBases = [
  'https://ai-troubleshooting-agent.onrender.com',
  'http://127.0.0.1:8001',
  'http://127.0.0.1:8000',
];

function setLoading() {
  rootCause.textContent = 'Analyzing logs, metrics, and retrieved runbooks...';
  confidence.textContent = '--';
  remediation.innerHTML = '';
  evidence.innerHTML = '';
  memory.innerHTML = '';
}

function renderResponse(data) {
  sessionId = data.session_id;
  rootCause.textContent = data.likely_root_cause;
  confidence.textContent = `${Math.round(data.confidence * 100)}%`;
  remediation.innerHTML = data.remediation_steps
    .map((step) => `<li>${step}</li>`)
    .join('');
  evidence.innerHTML = data.evidence
    .map(
      (item) => `
        <div class="evidence-item">
          <strong>${item.title}</strong>
          <span>${item.source} | score ${item.score}</span>
          <p>${item.excerpt}</p>
        </div>
      `,
    )
    .join('');
  memory.innerHTML = data.memory
    .map((turn) => `<div class="memory-item">${turn}</div>`)
    .join('');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  setLoading();

  try {
    let response = null;
    const payload = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: messageInput.value,
        severity: severityInput.value,
        session_id: sessionId,
      }),
    };

    for (const apiBase of apiBases) {
      try {
        response = await fetch(`${apiBase}/api/troubleshoot`, payload);
        if (response.ok) break;
      } catch {
        response = null;
      }
    }

    if (!response || !response.ok) {
      throw new Error('API unavailable');
    }

    renderResponse(await response.json());
  } catch (error) {
    rootCause.textContent = 'Could not reach the FastAPI backend. Start it with: uvicorn app.main:app --reload --port 8001';
    confidence.textContent = 'offline';
  }
});
