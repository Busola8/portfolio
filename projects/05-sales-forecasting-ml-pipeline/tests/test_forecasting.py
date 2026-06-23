from app.forecasting import ForecastingPipeline
from app.models import ForecastRequest


def test_pipeline_returns_requested_horizon():
    result = ForecastingPipeline().run(ForecastRequest(horizon_months=4))

    assert len(result.forecast) == 4
    assert result.metrics.selected_model
    assert result.tasks[0].task_id == "extract_sales_data"


def test_retraining_branch_respects_threshold():
    result = ForecastingPipeline().run(ForecastRequest(drift_threshold=0.01, retrain_if_drift=True))

    assert result.metrics.drift_detected is True
    assert result.metrics.retraining_triggered is True
    assert result.tasks[-1].status == "queued"
