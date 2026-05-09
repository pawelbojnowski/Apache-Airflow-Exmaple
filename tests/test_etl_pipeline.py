"""
Testy jednostkowe logiki ETL.

Dostep do funkcji taskow przez task.python_callable — dzieki temu testujemy
czysty Python bez uruchamiania Airflow.
"""
import os

import pytest
from airflow.models import DagBag

DAGS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "dags")


@pytest.fixture(scope="module")
def etl_tasks():
    dagbag = DagBag(dag_folder=DAGS_FOLDER, include_examples=False)
    dag = dagbag.dags["etl_pipeline"]
    return {
        "extract": dag.get_task("extract").python_callable,
        "transform": dag.get_task("transform").python_callable,
        "load": dag.get_task("load").python_callable,
    }


# --- extract ---

def test_extract_returns_list(etl_tasks):
    result = etl_tasks["extract"]()
    assert isinstance(result, list)


def test_extract_returns_four_records(etl_tasks):
    result = etl_tasks["extract"]()
    assert len(result) == 4


def test_extract_record_has_required_keys(etl_tasks):
    result = etl_tasks["extract"]()
    for record in result:
        assert {"id", "name", "age", "salary"} <= record.keys()


# --- transform ---

def test_transform_strips_and_capitalizes_name(etl_tasks):
    raw = [{"id": 1, "name": "  alice ", "age": 30, "salary": 5000}]
    result = etl_tasks["transform"](raw)
    assert result[0]["name"] == "Alice"


def test_transform_skips_negative_age(etl_tasks):
    raw = [{"id": 2, "name": "Bob", "age": -1, "salary": 7000}]
    result = etl_tasks["transform"](raw)
    assert result == []


def test_transform_skips_zero_age(etl_tasks):
    raw = [{"id": 2, "name": "Bob", "age": 0, "salary": 7000}]
    result = etl_tasks["transform"](raw)
    assert result == []


def test_transform_skips_missing_salary(etl_tasks):
    raw = [{"id": 4, "name": "Diana", "age": 28, "salary": None}]
    result = etl_tasks["transform"](raw)
    assert result == []


def test_transform_keeps_valid_records(etl_tasks):
    raw = [
        {"id": 1, "name": "Alice", "age": 30, "salary": 5000},
        {"id": 3, "name": "Charlie", "age": 25, "salary": 4500},
    ]
    result = etl_tasks["transform"](raw)
    assert len(result) == 2


def test_transform_empty_input(etl_tasks):
    result = etl_tasks["transform"]([])
    assert result == []


# --- extract -> transform (mini integracja) ---

def test_full_pipeline_drops_invalid_records(etl_tasks):
    """extract zwraca 4 rekordy, transform odrzuca BOB (age=-1) i Diane (salary=None)."""
    raw = etl_tasks["extract"]()
    clean = etl_tasks["transform"](raw)
    assert len(clean) == 2
    names = {r["name"] for r in clean}
    assert names == {"Alice", "Charlie"}
