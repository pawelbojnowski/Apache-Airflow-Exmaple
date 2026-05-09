from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="hello_world",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example"],
    access_control={
        "Admin": {"can_read", "can_edit", "can_delete"},
        "Op":    {"can_read", "can_edit", "can_dag_run"},
        "User":  {"can_read", "can_dag_run"},
        "Viewer": {"can_read"},
    },
)
def hello_world():
    @task
    def say_hello():
        print("Hello, World!")
        return "Hello, World!"

    @task
    def say_goodbye(message: str):
        print(f"Task received: {message}")
        print("Goodbye, World!")

    say_goodbye(say_hello())


hello_world()
