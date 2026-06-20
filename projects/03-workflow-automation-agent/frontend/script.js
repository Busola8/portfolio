const form = document.getElementById('workflow-form');
const completion = document.getElementById('completion');
const statusText = document.getElementById('status');
const summary = document.getElementById('summary');
const queue = document.getElementById('queue');
const steps = document.getElementById('steps');
const outputs = document.getElementById('outputs');
const notes = document.getElementById('notes');
const apiBases = ['http://127.0.0.1:8021', 'http://127.0.0.1:8020'];

const requiredDocs = ['certificate_of_incorporation', 'director_id', 'proof_of_address'];

function splitList(value) {
  return value.split(',').map((item) => item.trim()).filter(Boolean);
}

function payload() {
  return {
    customer_name: document.getElementById('customer-name').value,
    customer_type: document.getElementById('customer-type').value,
    country: document.getElementById('country').value,
    risk_level: document.getElementById('risk-level').value,
    documents: splitList(document.getElementById('documents').value),
    requested_products: splitList(document.getElementById('products').value),
    voice_channel: document.getElementById('voice-channel').checked,
    sharepoint_folder: document.getElementById('sharepoint-folder').value,
  };
}

async function runWorkflow(body) {
  const request = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  };
  for (const apiBase of apiBases) {
    try {
      const response = await fetch(`${apiBase}/api/workflows/run`, request);
      if (response.ok) return response.json();
    } catch {
      // Try next endpoint.
    }
  }
  return staticWorkflow(body);
}

function step(agent, action, status, details) {
  return { agent, action, status, details };
}

function staticWorkflow(body) {
  const missing = requiredDocs.filter((doc) => !body.documents.includes(doc));
  const highRisk = ['high', 'critical'].includes(body.risk_level);
  const approvalRequired = missing.length > 0 || highRisk;
  const workflowSteps = [
    step('IntakeAgent', 'Capture onboarding request', 'completed', `Created onboarding case for ${body.customer_name} in ${body.country}.`),
    step('KYCAgent', 'Validate KYC requirements', missing.length ? 'review' : 'completed', missing.length ? `Missing documents: ${missing.join(', ')}.` : 'All required KYC documents are present.'),
    step('DocumentAgent', 'Create document workspace', 'completed', `Prepared SharePoint folder ${body.sharepoint_folder || '/Onboarding/Generated'}.`),
    step('ApprovalAgent', 'Route approval', approvalRequired ? 'pending' : 'auto-approved', approvalRequired ? 'Sent to Compliance Approval Queue.' : 'Customer qualifies for straight-through onboarding.'),
  ];
  if (body.voice_channel) {
    workflowSteps.push(step('VoiceAgent', 'Prepare voice follow-up', 'scheduled', 'Generated telephony script for customer status update.'));
  }
  workflowSteps.push(step('NotificationAgent', 'Notify stakeholders', 'completed', 'Sent workflow status to operations, compliance, and relationship manager channels.'));
  return {
    workflow_id: `static-${Date.now()}`,
    status: approvalRequired ? 'approval_required' : 'completed',
    approval_required: approvalRequired,
    assigned_queue: approvalRequired ? 'Compliance Approval Queue' : 'Operations Fulfillment',
    completion_percentage: approvalRequired ? 72 : 100,
    summary: `${body.customer_name} onboarding is ${approvalRequired ? 'waiting for compliance approval' : 'ready for fulfillment'}. Static demo mode is active.`,
    steps: workflowSteps,
    documents_created: ['onboarding_case.json', 'kyc_checklist.md', 'approval_summary.md'],
    notifications: ['Relationship manager notified', approvalRequired ? 'Compliance queue updated' : 'Operations notified of auto-approval'],
    n8n_replacement_notes: [
      'IntakeAgent maps to an n8n Webhook trigger.',
      'KYCAgent maps to document validation and API enrichment nodes.',
      'DocumentAgent maps to SharePoint create-folder/upload nodes.',
      'ApprovalAgent maps to an n8n Wait/approval workflow.',
      'VoiceAgent maps to Twilio or telephony integration nodes.',
    ],
  };
}

function render(data) {
  completion.textContent = `${data.completion_percentage}%`;
  statusText.textContent = data.status.replaceAll('_', ' ').toUpperCase();
  summary.textContent = data.summary;
  queue.innerHTML = `<div class="queue"><strong>Assigned queue</strong><p>${data.assigned_queue}</p></div>`;
  steps.innerHTML = data.steps.map((item) => `
    <div class="step status-${item.status}">
      <strong>${item.agent} | ${item.action}</strong>
      <p>${item.details}</p>
    </div>
  `).join('');
  outputs.innerHTML = [
    ...data.documents_created.map((item) => `<div class="output"><strong>Document</strong><p>${item}</p></div>`),
    ...data.notifications.map((item) => `<div class="output"><strong>Notification</strong><p>${item}</p></div>`),
  ].join('');
  notes.innerHTML = data.n8n_replacement_notes.map((item) => `<div class="note">${item}</div>`).join('');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  completion.textContent = '--';
  statusText.textContent = 'Running workflow...';
  summary.textContent = '';
  queue.innerHTML = '';
  steps.innerHTML = '';
  outputs.innerHTML = '';
  notes.innerHTML = '';
  render(await runWorkflow(payload()));
});
