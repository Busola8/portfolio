const form = document.getElementById('pipeline-form');
const statusText = document.getElementById('status');
const summary = document.getElementById('summary');
const model = document.getElementById('model');
const mape = document.getElementById('mape');
const drift = document.getElementById('drift');
const retraining = document.getElementById('retraining');
const tasks = document.getElementById('tasks');
const forecast = document.getElementById('forecast');
const notes = document.getElementById('notes');
const apiBases = ['http://127.0.0.1:8041', 'http://127.0.0.1:8040'];

function payload() {
  return {
    horizon_months: Number(document.getElementById('horizon').value),
    drift_threshold: Number(document.getElementById('drift-threshold').value),
    retrain_if_drift: document.getElementById('retrain').checked,
  };
}

async function runPipeline(body) {
  const request = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  };
  for (const apiBase of apiBases) {
    try {
      const response = await fetch(`${apiBase}/api/pipeline/run`, request);
      if (response.ok) return response.json();
    } catch {
      // Try the next local backend, then browser demo mode.
    }
  }
  return staticPipeline(body);
}

function staticPipeline(body) {
  const driftScore = 0.21;
  const retrain = driftScore >= body.drift_threshold && body.retrain_if_drift;
  const months = ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10', '2026-11', '2026-12'];
  const base = 39200000;
  return {
    run_id: `static-${Date.now()}`,
    orchestration: 'Apache Airflow DAG: sales_forecasting_dag',
    status: retrain ? 'retraining_queued' : 'forecast_published',
    summary: `${body.horizon_months}-month revenue forecast published with seasonal_blend; drift score ${driftScore}. Static demo mode is active.`,
    tasks: [
      task('extract_sales_data', 'Airflow', 'success', 31, 'raw/sales/monthly_sales.json'),
      task('prepare_features', 'FeaturePipeline', 'success', 44, 'features/sales_features.parquet'),
      task('train_forecast_models', 'ModelTrainer', 'success', 88, 'models/sales_forecaster.pkl'),
      task('evaluate_models', 'Evaluator', 'success', 23, 'metrics/model_report.json'),
      task('publish_forecast', 'ForecastService', 'success', 18, 'forecasts/revenue_forecast.json'),
      task('monitor_drift', 'Monitoring', 'warning', 14, 'monitoring/drift_report.json'),
      task('trigger_retraining', 'Airflow', retrain ? 'queued' : 'skipped', 6, 'dags/sales_forecasting_dag.py'),
    ],
    metrics: {
      selected_model: 'seasonal_blend',
      mae: 1285000,
      mape: 0.082,
      drift_score: driftScore,
      drift_detected: true,
      retraining_triggered: retrain,
    },
    forecast: months.slice(0, body.horizon_months).map((month, index) => {
      const predicted = base + index * 1650000;
      return {
        month,
        predicted_revenue: predicted,
        lower_bound: predicted * 0.9,
        upper_bound: predicted * 1.1,
      };
    }),
    monitoring_notes: [
      'Apache Airflow DAG coordinates ingestion, feature preparation, model training, evaluation, publishing, drift monitoring, and retraining.',
      'Static demo mode keeps the project viewable on GitHub Pages without requiring recruiters to run Airflow.',
      retrain ? 'Drift threshold breached; retraining branch is queued.' : 'Drift threshold is tolerated for this run; no retraining branch was queued.',
    ],
  };
}

function task(task_id, owner, status, duration_seconds, artifact) {
  return { task_id, owner, status, duration_seconds, artifact };
}

function money(value) {
  return new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: 'NGN',
    maximumFractionDigits: 0,
  }).format(value);
}

function render(data) {
  statusText.textContent = data.status.replaceAll('_', ' ').toUpperCase();
  summary.textContent = data.summary;
  model.textContent = data.metrics.selected_model;
  mape.textContent = `${(data.metrics.mape * 100).toFixed(1)}%`;
  drift.textContent = data.metrics.drift_score.toFixed(2);
  retraining.textContent = data.metrics.retraining_triggered ? 'Queued' : 'No';
  tasks.innerHTML = data.tasks.map((item) => `
    <div class="task status-${item.status}">
      <strong>${item.task_id}</strong>
      <p>${item.owner} | ${item.duration_seconds}s</p>
      <span>${item.artifact}</span>
    </div>
  `).join('');
  forecast.innerHTML = data.forecast.map((item) => `
    <div class="forecast-row">
      <strong>${item.month}</strong>
      <span>${money(item.predicted_revenue)}</span>
      <small>${money(item.lower_bound)} - ${money(item.upper_bound)}</small>
    </div>
  `).join('');
  notes.innerHTML = data.monitoring_notes.map((item) => `<div class="note">${item}</div>`).join('');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  statusText.textContent = 'Running Airflow-style pipeline...';
  summary.textContent = '';
  tasks.innerHTML = '';
  forecast.innerHTML = '';
  notes.innerHTML = '';
  render(await runPipeline(payload()));
});
