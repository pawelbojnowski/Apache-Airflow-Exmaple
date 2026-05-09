import os
from datetime import datetime

import psycopg2
from airflow.decorators import dag, task


def _get_conn():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "postgres"),
        dbname=os.environ.get("POSTGRES_DB", "airflow"),
        user=os.environ.get("POSTGRES_USER", "airflow"),
        password=os.environ.get("POSTGRES_PASSWORD", "airflow"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
    )


@dag(
    dag_id="postgres_explorer",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example", "sql"],
    access_control={
        "Admin": {"can_read", "can_edit", "can_delete"},
        "Op":    {"can_read", "can_edit", "can_dag_run"},
        "User":  {"can_read"},
        "Viewer": {"can_read"},
    },
)
def postgres_explorer():

    @task
    def list_tables() -> list[str]:
        with _get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cur.fetchall()]

        print(f"\nFound {len(tables)} table(s) in public schema:")
        for t in tables:
            print(f"  - {t}")
        return tables

    @task
    def dump_table_data(tables: list[str]):
        with _get_conn() as conn, conn.cursor() as cur:
            for table in tables:
                cur.execute(f'SELECT COUNT(*) FROM "{table}"')  # noqa: S608
                count = cur.fetchone()[0]
                print(f"\n{'=' * 50}")
                print(f"Table: {table}  ({count} rows)")
                print("=" * 50)

                if count == 0:
                    print("  (empty)")
                    continue

                cur.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position;
                """, (table,))
                columns = [row[0] for row in cur.fetchall()]
                print("  Columns: " + ", ".join(columns))

                cur.execute(f'SELECT * FROM "{table}" LIMIT 5')  # noqa: S608
                rows = cur.fetchall()
                print(f"  Sample rows (max 5 of {count}):")
                for row in rows:
                    print(f"    {row}")

    tables = list_tables()
    dump_table_data(tables)


postgres_explorer()
