# Case Study

## Problem

Sales and revenue planning needs forecasts that are repeatable, explainable, monitored, and retrained when demand patterns shift.

## Solution

This project implements an end-to-end forecasting pipeline. Apache Airflow coordinates ingestion, feature preparation, training, evaluation, publishing, drift monitoring, and retraining. FastAPI exposes the pipeline output, and the frontend presents the DAG run in a recruiter-friendly interface.

## Why Airflow Matters

Forecasting is not just a model. It is an operational process that needs schedules, dependencies, retries, artifacts, monitoring, and retraining decisions. The included DAG shows that orchestration structure explicitly.

## Outcome

The demo produces a forecast, model metrics, drift score, and retraining decision in one run. It is lightweight enough for portfolio viewing while still mapping to a realistic MLOps production architecture.
