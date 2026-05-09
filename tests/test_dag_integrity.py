"""
Testy integralności DAGów — sprawdzają, czy wszystkie DAGi ładują się bez błędów
i mają poprawną strukturę (harmonogram, liczba tasków, catchup).
"""
import os

import pytest
from airflow.models import DagBag

DAGS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "dags")


@pytest.fixture(scope="module")
def dagbag():
    return DagBag(dag_folder=DAGS_FOLDER, include_examples=False)


def test_no_import_errors(dagbag):
    assert dagbag.import_errors == {}, f"Bledy importu DAGow: {dagbag.import_errors}"


@pytest.mark.parametrize(
    "dag_id, expected_task_count",
    [
        ("hello_world", 2),
        ("etl_pipeline", 3),
        ("scheduled_report", 3),
        ("system_info", 4),
    ],
)
def test_dag_task_count(dagbag, dag_id, expected_task_count):
    dag = dagbag.dags.get(dag_id)
    assert dag is not None, f"DAG '{dag_id}' nie zostal znaleziony"
    assert len(dag.tasks) == expected_task_count, (
        f"DAG '{dag_id}': oczekiwano {expected_task_count} taskow, "
        f"jest {len(dag.tasks)}"
    )


@pytest.mark.parametrize(
    "dag_id",
    ["hello_world", "etl_pipeline", "scheduled_report", "system_info"],
)
def test_dag_catchup_disabled(dagbag, dag_id):
    dag = dagbag.dags.get(dag_id)
    assert dag.catchup is False, f"DAG '{dag_id}' powinien miec catchup=False"


@pytest.mark.parametrize(
    "dag_id, expected_tags",
    [
        ("hello_world", ["example"]),
        ("etl_pipeline", ["example", "etl"]),
        ("scheduled_report", ["example", "report"]),
        ("system_info", ["example", "bash"]),
    ],
)
def test_dag_tags(dagbag, dag_id, expected_tags):
    dag = dagbag.dags.get(dag_id)
    for tag in expected_tags:
        assert tag in dag.tags, f"DAG '{dag_id}' powinien miec tag '{tag}'"
