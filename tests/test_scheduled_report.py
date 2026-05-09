"""
Testy jednostkowe DAGa scheduled_report.
"""
import os
from datetime import datetime

import pytest
from airflow.models import DagBag

DAGS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "dags")


@pytest.fixture(scope="module")
def report_tasks():
    dagbag = DagBag(dag_folder=DAGS_FOLDER, include_examples=False)
    dag = dagbag.dags["scheduled_report"]
    return {
        "collect_data": dag.get_task("collect_data").python_callable,
        "generate_report": dag.get_task("generate_report").python_callable,
        "send_report": dag.get_task("send_report").python_callable,
    }


SAMPLE_DATA = {
    "week": "2024-W10",
    "total_orders": 342,
    "revenue": 18750.50,
    "new_users": 87,
    "churn_rate": 0.032,
}


# --- collect_data ---

def test_collect_data_returns_dict(report_tasks):
    result = report_tasks["collect_data"](logical_date=datetime(2024, 3, 4))
    assert isinstance(result, dict)


def test_collect_data_has_required_keys(report_tasks):
    result = report_tasks["collect_data"](logical_date=datetime(2024, 3, 4))
    assert {"week", "total_orders", "revenue", "new_users", "churn_rate"} <= result.keys()


def test_collect_data_week_format(report_tasks):
    result = report_tasks["collect_data"](logical_date=datetime(2024, 3, 4))
    # format: YYYY-Www
    assert result["week"].startswith("2024-W")


# --- generate_report ---

def test_generate_report_returns_string(report_tasks):
    result = report_tasks["generate_report"](SAMPLE_DATA)
    assert isinstance(result, str)


def test_generate_report_contains_week(report_tasks):
    result = report_tasks["generate_report"](SAMPLE_DATA)
    assert "2024-W10" in result


def test_generate_report_contains_revenue(report_tasks):
    result = report_tasks["generate_report"](SAMPLE_DATA)
    assert "18,750.50" in result


def test_generate_report_contains_churn_as_percent(report_tasks):
    result = report_tasks["generate_report"](SAMPLE_DATA)
    assert "3.2%" in result


def test_generate_report_contains_orders(report_tasks):
    result = report_tasks["generate_report"](SAMPLE_DATA)
    assert "342" in result


# --- send_report ---

def test_send_report_runs_without_error(report_tasks, capsys):
    report_tasks["send_report"]("Test report content")
    captured = capsys.readouterr()
    assert "Test report content" in captured.out
