from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="etl_pipeline",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example", "etl"],
    access_control={
        "Admin": {"can_read", "can_edit", "can_delete"},
        "Op":    {"can_read", "can_edit", "can_dag_run"},
        "User":  {"can_read", "can_dag_run"},
        "Viewer": {"can_read"},
    },
)
def etl_pipeline():
    @task
    def extract() -> list[dict]:
        # Simulate fetching raw data from a source (e.g. API, DB)
        raw_data = [
            {"id": 1, "name": "  Alice ", "age": 30, "salary": 5000},
            {"id": 2, "name": "BOB",      "age": -1, "salary": 7000},
            {"id": 3, "name": " Charlie", "age": 25, "salary": 4500},
            {"id": 4, "name": "Diana  ",  "age": 28, "salary": None},
        ]
        print(f"Extracted {len(raw_data)} records")
        return raw_data

    @task
    def transform(raw_data: list[dict]) -> list[dict]:
        cleaned = []
        for row in raw_data:
            # Strip whitespace from names
            row["name"] = row["name"].strip().title()
            # Drop records with invalid age or missing salary
            if row["age"] <= 0 or row["salary"] is None:
                print(f"Skipping invalid record: {row}")
                continue
            cleaned.append(row)
        print(f"Transformed: {len(raw_data)} → {len(cleaned)} records")
        return cleaned

    @task
    def load(clean_data: list[dict]):
        # Simulate writing to a data warehouse / database
        for row in clean_data:
            print(f"Loading record: {row}")
        print(f"Loaded {len(clean_data)} records successfully")

    raw = extract()
    clean = transform(raw)
    load(clean)


etl_pipeline()
