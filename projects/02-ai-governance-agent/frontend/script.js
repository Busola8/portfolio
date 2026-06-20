const form = document.getElementById('governance-form');
const score = document.getElementById('score');
const valueScore = document.getElementById('value-score');
const automation = document.getElementById('automation');
const hoursSaved = document.getElementById('hours-saved');
const risk = document.getElementById('risk');
const summary = document.getElementById('summary');
const findings = document.getElementById('findings');
const trace = document.getElementById('trace');
const alerts = document.getElementById('alerts');
const apiBases = [
  'https://ai-governance-agent-2mxy.onrender.com',
  'http://127.0.0.1:8011',
  'http://127.0.0.1:8010',
];

function splitList(value) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function agentPayload() {
  const agentName = document.getElementById('agent-name').value;
  return {
    agent: {
      agent_id: agentName.toLowerCase().replaceAll(' ', '-'),
      agent_name: agentName,
      owner: document.getElementById('owner').value,
      department: document.getElementById('department').value,
      model: 'gpt-4.1-mini',
      purpose: document.getElementById('purpose').value,
      permissions: splitList(document.getElementById('permissions').value),
      tools: splitList(document.getElementById('tools').value),
      data_classification: document.getElementById('data-classification').value,
      tasks_completed: Number(document.getElementById('tasks-completed').value),
      human_interventions: Number(document.getElementById('human-interventions').value),
      avg_minutes_saved_per_task: Number(document.getElementById('minutes-saved').value),
      monthly_token_cost_usd: Number(document.getElementById('token-cost').value),
      active_users: Number(document.getElementById('active-users').value),
      decisions_made: Number(document.getElementById('decisions-made').value),
      retention_days: Number(document.getElementById('retention-days').value),
      automated_decisioning: document.getElementById('automated-decisioning').checked,
      pii_used: document.getElementById('pii-used').checked,
      human_review: document.getElementById('human-review').checked,
      audit_logging: document.getElementById('audit-logging').checked,
      explainability_enabled: document.getElementById('explainability').checked,
      region: document.getElementById('region').value,
    },
  };
}

async function postEvaluation(payload) {
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer demo-governance-token',
    },
    body: JSON.stringify(payload),
  };
  for (const apiBase of apiBases) {
    try {
      const response = await fetch(`${apiBase}/api/evaluate`, options);
      if (response.ok) return response.json();
    } catch {
      // Try next API base.
    }
  }
  return staticEvaluation(payload.agent);
}

function staticFinding(agent, control, severity, message, recommendation, status = 'review') {
  return { agent, control, status, severity, message, recommendation };
}

function staticEvaluation(agent) {
  const results = [];
  if (agent.pii_used && agent.automated_decisioning && !agent.human_review) {
    results.push(staticFinding(
      'PrivacyAgent',
      'Human review',
      'critical',
      'Agent makes or supports decisions using PII without human review.',
      'Add human-in-the-loop approval for decisions that affect customers.',
      'fail',
    ));
  }
  if (agent.permissions.map((item) => item.toLowerCase()).includes('write')) {
    results.push(staticFinding(
      'AccessAgent',
      'Privileged access',
      'high',
      'Agent has write permissions and can affect operational systems.',
      'Scope credentials, require owner approval, and log every tool call.',
    ));
  }
  if (agent.decisions_made > 0 && !agent.explainability_enabled) {
    results.push(staticFinding(
      'ExplainabilityAgent',
      'Decision traceability',
      'high',
      'Agent decisions do not have explainability enabled.',
      'Store rationale, evidence, model version, prompt, and tool-call trace.',
      'fail',
    ));
  }
  if (!agent.audit_logging) {
    results.push(staticFinding(
      'AuditAgent',
      'Audit logging',
      'medium',
      'Agent activity is not fully logged for governance review.',
      'Enable redacted audit logging for prompts, outputs, and tool calls.',
      'fail',
    ));
  }
  if (agent.tasks_completed < 10 && agent.monthly_token_cost_usd > 100) {
    results.push(staticFinding(
      'ValueAgent',
      'Low adoption high cost',
      'medium',
      'Agent has low usage relative to model cost.',
      'Review adoption, expand the use case, or retire the agent.',
    ));
  }
  if (results.length === 0) {
    results.push(staticFinding(
      'ValueAgent',
      'Baseline governance',
      'low',
      'Agent meets baseline governance and value checks.',
      'Continue monitoring adoption, cost, and interventions.',
      'pass',
    ));
  }

  const totalWork = agent.tasks_completed + agent.human_interventions;
  const automationPercentage = totalWork === 0 ? 0 : (agent.tasks_completed / totalWork) * 100;
  const estimatedHoursSaved = (agent.tasks_completed * agent.avg_minutes_saved_per_task) / 60;
  const penalty = results.reduce((sum, item) => {
    const weights = { critical: 30, high: 22, medium: 12, low: 2 };
    return sum + (item.status === 'pass' ? 0 : weights[item.severity]);
  }, 0);
  const governanceScore = Math.max(0, Math.min(100, 100 - penalty));
  const valueScore = Math.max(
    0,
    Math.min(100, Math.round(60 + estimatedHoursSaved / 5 - agent.monthly_token_cost_usd / 20 - (100 - automationPercentage) / 8)),
  );
  const riskLevel = governanceScore < 55 ? 'critical' : governanceScore < 75 ? 'high' : governanceScore < 90 ? 'medium' : 'low';

  return {
    audit_id: `static-${Date.now()}`,
    agent_id: agent.agent_id,
    agent_name: agent.agent_name,
    department: agent.department,
    compliance_score: governanceScore,
    risk_level: riskLevel,
    alert_required: governanceScore < 75,
    value_score: valueScore,
    automation_percentage: Number(automationPercentage.toFixed(1)),
    estimated_hours_saved: Number(estimatedHoursSaved.toFixed(1)),
    executive_summary: `${agent.agent_name} in ${agent.department} scored ${governanceScore}/100 governance, ${valueScore}/100 value, and ${automationPercentage.toFixed(1)}% automation. Static demo mode is active.`,
    findings: results,
    workflow_trace: [
      'StaticDemo: backend unavailable, running browser-only evaluation',
      'RegistryAgent: reviewed identity, owner, department, permissions, and tools',
      'UsageAgent: calculated tasks, human interventions, cost, automation, and time saved',
      'RiskAgent: calculated governance risk and value score',
    ],
  };
}

function render(data) {
  score.textContent = data.compliance_score;
  valueScore.textContent = data.value_score;
  automation.textContent = `${data.automation_percentage}%`;
  hoursSaved.textContent = data.estimated_hours_saved;
  risk.textContent = `${data.risk_level.toUpperCase()} governance risk`;
  summary.textContent = data.executive_summary;
  alerts.innerHTML = data.alert_required
    ? '<div class="alert severity-high">Alert routed to Agent Governance Council.</div>'
    : '<div class="alert">No governance alert required.</div>';
  findings.innerHTML = data.findings
    .map(
      (finding) => `
        <div class="finding severity-${finding.severity}">
          <strong>${finding.agent} | ${finding.control}</strong>
          <p>${finding.message}</p>
          <span>${finding.recommendation}</span>
        </div>
      `,
    )
    .join('');
  trace.innerHTML = data.workflow_trace
    .map((item) => `<div class="trace-item">${item}</div>`)
    .join('');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  score.textContent = '--';
  valueScore.textContent = '--';
  automation.textContent = '--';
  hoursSaved.textContent = '--';
  risk.textContent = 'Evaluating agent...';
  summary.textContent = '';
  findings.innerHTML = '';
  trace.innerHTML = '';
  render(await postEvaluation(agentPayload()));
});
