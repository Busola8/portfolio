const projects = [
  {
    title: 'AI Troubleshooting Agent',
    description: 'LLM-style RAG assistant for diagnostics, root cause analysis, remediation, escalation, and session memory.',
    tech: 'FastAPI | RAG | Python | JavaScript',
    link: 'projects/01-ai-troubleshooting-agent/frontend/index.html'
  },
  {
    title: 'AI Governance Agent',
    description: 'Multi-agent governance platform with audit storage, policy validation, risk checks, and executive dashboards.',
    tech: 'LangGraph | PostgreSQL | Dashboards',
    link: '#'
  },
  {
    title: 'AI-Powered Workflow Automation Agent',
    description: 'Enterprise workflow automation for onboarding, KYC, document processing, approvals, and voice interactions.',
    tech: 'CrewAI | n8n | FastAPI',
    link: '#'
  },
  {
    title: 'AI Risk & Fraud Sentinel Agent',
    description: 'Fraud monitoring platform with anomaly detection, risk rules, investigation workflows, and reporting.',
    tech: 'LangChain | Risk Rules | APIs',
    link: '#'
  },
  {
    title: 'Transaction Classification System',
    description: 'ML classification pipeline for banking transactions with preprocessing, model evaluation, retraining, and APIs.',
    tech: 'ML | NLP | FastAPI',
    link: '#'
  },
  {
    title: 'Sentiment Analysis System',
    description: 'BERT-based sentiment platform with fine-tuning, inference pipelines, metrics, and customer analytics integration.',
    tech: 'Transformers | NLP | APIs',
    link: '#'
  },
  {
    title: 'Medallion Architecture Data Warehouse',
    description: 'Bronze, Silver, and Gold data warehouse with ingestion, quality, lineage, monitoring, and governance.',
    tech: 'ETL | Data Quality | Governance',
    link: '#'
  },
  {
    title: 'Sales Forecasting ML Pipeline',
    description: 'Demand and revenue forecasting platform with orchestration, model monitoring, drift detection, and retraining.',
    tech: 'Airflow | Forecasting | MLOps',
    link: '#'
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
      <a href="${project.link}" aria-label="View project ${project.title}">View</a>
    </div>
  `;
  projectsGrid.appendChild(card);
});

const yearElement = document.getElementById('year');
if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
}
