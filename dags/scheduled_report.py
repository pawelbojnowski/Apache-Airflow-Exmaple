from datetime import datetime

from airflow.decorators import dag, task
from airflow.models import Variable


@dag(
    dag_id="scheduled_report",
    schedule="0 8 * * 1",  # Every Monday at 08:00 UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example", "report"],
    access_control={
        "Admin": {"can_read", "can_edit", "can_delete"},
        "Op":    {"can_read", "can_edit", "can_dag_run"},
        "User":  {"can_read", "can_dag_run"},
        "Viewer": {"can_read"},
    },
)
def scheduled_report():
    @task
    def collect_data(logical_date=None) -> dict:
        # Simulate querying metrics for the past week
        report_date = logical_date or datetime.utcnow()
        data = {
            "week": report_date.strftime("%Y-W%W"),
            "total_orders": 342,
            "revenue": 18750.50,
            "new_users": 87,
            "churn_rate": 0.032,
        }
        print(f"Collected data for week {data['week']}: {data}")
        return data

    @task
    def generate_report(data: dict) -> str:
        report = (
            f"Weekly Report — {data['week']}\n"
            f"{'=' * 35}\n"
            f"Total orders : {data['total_orders']}\n"
            f"Revenue      : ${data['revenue']:,.2f}\n"
            f"New users    : {data['new_users']}\n"
            f"Churn rate   : {data['churn_rate']:.1%}\n"
        )
        print(report)
        return report

    @task
    def send_report(report: str):
        # In production: send via email / Slack / S3
        # recipient = Variable.get("report_recipient", default_var="team@example.com")
        print("Sending report...")
        print(report)
        print("Report sent successfully")

    data = collect_data()
    report = generate_report(data)
    send_report(report)


scheduled_report()
