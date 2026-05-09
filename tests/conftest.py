import os

# Minimal Airflow config for local unit tests (no real DB, no webserver)
os.environ.setdefault("AIRFLOW__CORE__UNIT_TEST_MODE", "True")
os.environ.setdefault("AIRFLOW_HOME", "/tmp/airflow_test")
os.environ.setdefault(
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
    "sqlite:////tmp/airflow_test/airflow.db",
)
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
