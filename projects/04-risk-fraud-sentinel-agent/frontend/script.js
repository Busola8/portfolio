const form = document.getElementById('fraud-form');
const riskScore = document.getElementById('risk-score');
const riskLevel = document.getElementById('risk-level');
const decision = document.getElementById('decision');
const alerts = document.getElementById('alerts');
const findings = document.getElementById('findings');
const trail = document.getElementById('trail');
const reports = document.getElementById('reports');
const apiBases = ['http://127.0.0.1:8031', 'http://127.0.0.1:8030'];

function payload() {
  return {
    transaction_id: document.getElementById('transaction-id').value,
    customer_id: document.getElementById('customer-id').value,
    account_age_days: Number(document.getElementById('account-age').value),
    amount: Number(document.getElementById('amount').value),
    currency: 'NGN',
    merchant: document.getElementById('merchant').value,
    channel: document.getElementById('channel').value,
    country: document.getElementById('country').value,
    hour: Number(document.getElementById('hour').value),
    device_trusted: document.getElementById('device-trusted').checked,
    prior_chargebacks: Number(document.getElementById('chargebacks').value),
    velocity_1h: Number(document.getElementById('velocity').value),
    customer_avg_amount: Number(document.getElementById('avg-amount').value),
  };
}

async function investigate(body) {
  const request = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  };
  for (const apiBase of apiBases) {
    try {
      const response = await fetch(`${apiBase}/api/investigate`, request);
      if (response.ok) return response.json();
    } catch {
      // Try next endpoint.
    }
  }
  return staticInvestigation(body);
}

function finding(rule, severity, points, message, recommendation) {
  return { rule, severity, points, message, recommendation };
}

function staticInvestigation(txn) {
  const result = [];
  if (txn.amount > txn.customer_avg_amount * 4) {
    result.push(finding('Amount anomaly', 'high', 28, 'Transaction is more than 4x the customer normal amount.', 'Hold transaction and request customer confirmation.'));
  }
  if (txn.velocity_1h >= 6) {
    result.push(finding('Velocity spike', 'high', 25, 'Customer has unusually high transaction frequency in the last hour.', 'Temporarily limit additional transfers and review session activity.'));
  }
  if (!txn.device_trusted) {
    result.push(finding('Untrusted device', 'medium', 16, 'Transaction originated from a new or untrusted device.', 'Trigger step-up authentication.'));
  }
  if (txn.country.toLowerCase() !== 'nigeria') {
    result.push(finding('Geo anomaly', 'medium', 18, 'Transaction country differs from expected Nigeria operating region.', 'Check travel profile and location history.'));
  }
  if (txn.hour < 5 && txn.amount > txn.customer_avg_amount * 2) {
    result.push(finding('Unusual time', 'medium', 12, 'High-value transaction occurred during an overnight window.', 'Queue for analyst review if combined with other risk signals.'));
  }
  if (txn.prior_chargebacks > 0) {
    result.push(finding('Chargeback history', 'medium', 10, 'Customer has previous chargeback or dispute history.', 'Review prior dispute patterns before release.'));
  }
  if (txn.account_age_days < 30 && txn.amount > 500000) {
    result.push(finding('New account high value', 'high', 22, 'New account is attempting a high-value transaction.', 'Require enhanced due diligence before processing.'));
  }
  if (result.length === 0) {
    result.push(finding('Baseline', 'low', 0, 'No major fraud indicators were detected.', 'Allow transaction and continue passive monitoring.'));
  }
  const score = Math.max(0, Math.min(100, result.reduce((sum, item) => sum + item.points, 0)));
  const level = score >= 75 ? 'critical' : score >= 45 ? 'high' : score >= 20 ? 'medium' : 'low';
  const action = score >= 75 ? 'block' : score >= 45 ? 'manual_review' : score >= 20 ? 'step_up_auth' : 'allow';
  return {
    case_id: `STATIC-${Date.now()}`,
    transaction_id: txn.transaction_id,
    risk_score: score,
    risk_level: level,
    decision: action,
    findings: result,
    investigation_steps: [
      'StaticDemo: backend unavailable, running browser-only fraud scoring',
      'RiskAgent: scored transaction using anomaly and rules engine',
      'InvestigationAgent: generated case summary and recommended decision',
      'ReportingAgent: prepared SharePoint report and voice briefing',
    ],
    alerts: action === 'block' ? ['Fraud operations alert', 'Transaction blocked'] : action === 'manual_review' ? ['Fraud analyst review required'] : ['No active alert required'],
    sharepoint_report: `/FraudReports/static-${txn.transaction_id}.md`,
    voice_briefing: `Static case for ${txn.transaction_id}. Recommended action: ${action.replaceAll('_', ' ')}.`,
  };
}

function render(data) {
  riskScore.textContent = data.risk_score;
  riskLevel.textContent = `${data.risk_level.toUpperCase()} risk`;
  decision.textContent = `Decision: ${data.decision.replaceAll('_', ' ')}`;
  alerts.innerHTML = data.alerts.map((item) => `<div class="alert">${item}</div>`).join('');
  findings.innerHTML = data.findings.map((item) => `
    <div class="finding severity-${item.severity}">
      <strong>${item.rule} | +${item.points}</strong>
      <p>${item.message}</p>
      <span>${item.recommendation}</span>
    </div>
  `).join('');
  trail.innerHTML = data.investigation_steps.map((item) => `<div class="trail-item">${item}</div>`).join('');
  reports.innerHTML = `
    <div class="report"><strong>SharePoint report</strong><p>${data.sharepoint_report}</p></div>
    <div class="report"><strong>Voice briefing</strong><p>${data.voice_briefing}</p></div>
  `;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  riskScore.textContent = '--';
  riskLevel.textContent = 'Scoring transaction...';
  decision.textContent = '';
  alerts.innerHTML = '';
  findings.innerHTML = '';
  trail.innerHTML = '';
  reports.innerHTML = '';
  render(await investigate(payload()));
});
