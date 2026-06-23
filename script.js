const projects = [
  {
    title: 'AI Troubleshooting Agent',
    description: 'LLM-style RAG assistant for diagnostics, root cause analysis, remediation, escalation, and session memory.',
    tech: 'FastAPI | RAG | Python | JavaScript',
    link: 'projects/01-ai-troubleshooting-agent/frontend/index.html'
  },
  {
    title: 'Agent Governance and Analytics Platform',
    description: 'Internal control plane for agent identity, owners, permissions, usage, cost, explainability, and automation value.',
    tech: 'FastAPI | Agent Registry | Analytics',
    link: 'projects/02-ai-governance-agent/frontend/index.html'
  },
  {
    title: 'AI-Powered Workflow Automation Agent',
    description: 'Enterprise workflow automation for onboarding, KYC, document processing, approvals, and voice interactions.',
    tech: 'CrewAI | n8n | FastAPI',
    link: 'projects/03-workflow-automation-agent/frontend/index.html'
  },
  {
    title: 'AI Risk & Fraud Sentinel Agent',
    description: 'Fraud monitoring platform with anomaly detection, risk rules, investigation workflows, and reporting.',
    tech: 'LangChain | Risk Rules | APIs',
    link: 'projects/04-risk-fraud-sentinel-agent/frontend/index.html'
  },
  {
    title: 'Medallion Architecture Data Warehouse',
    description: 'SQL data warehouse project using Bronze, Silver, and Gold layers for ingestion, transformation, analytics-ready models, and reporting.',
    tech: 'SQL | Data Warehouse | Medallion Architecture',
    link: 'https://github.com/Busola8/SQL-Data-Warehouse-project',
    cta: 'View repo',
    external: true
  },
  {
    title: 'Sales Forecasting ML Pipeline',
    description: 'Demand and revenue forecasting platform with orchestration, model monitoring, drift detection, and retraining.',
    tech: 'Airflow | Forecasting | MLOps',
    link: 'projects/05-sales-forecasting-ml-pipeline/frontend/index.html'
  }
];

const projectsGrid = document.getElementById('projects-grid');

projects.forEach((project) => {
  const card = document.createElement('article');
  card.className = 'project-card';
  card.innerHTML = `
    <div>
      <h3>${project.title}</h3>
      <p>${project.description}</p>
    </div>
    <div class="project-meta">
      <span>${project.tech}</span>
      <a href="${project.link}" ${project.external ? 'target="_blank" rel="noopener noreferrer"' : ''} aria-label="View project ${project.title}">${project.cta || 'View'}</a>
    </div>
  `;
  projectsGrid.appendChild(card);
});

const yearElement = document.getElementById('year');
if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
}
