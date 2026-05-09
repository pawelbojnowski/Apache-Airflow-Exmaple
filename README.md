# Apache Airflow Example

An example Apache Airflow project running locally via Docker Compose.
Uses **CeleryExecutor** + **PostgreSQL 15** + **Redis 7**.

## Requirements

- Docker + Docker Compose
- Python 3.x (only needed for manual key generation)

## Quick start

```bash
./run.sh
```

The script automatically:
1. Removes existing containers, volumes and networks
2. Cleans up the `logs/` directory and `.env` file
3. Copies `.env.example` → `.env` and generates `FERNET_KEY` and `SECRET_KEY`
4. Sets `AIRFLOW_UID`
5. Runs database migration, creates all users with roles and starts all services

### Example console output after running `./run.sh`

```
==> [DROP] Stopping and removing containers, volumes and networks...
==> [DROP] Removing temporary folders and .env file...
==> [CREATE] Creating Airflow directories...
==> [CREATE] Copying .env.example -> .env...
==> [CREATE] Checking for required Python package: cryptography...
==> [CREATE] Generating AIRFLOW_FERNET_KEY...
==> [CREATE] Generating AIRFLOW_SECRET_KEY...
==> [CREATE] Setting AIRFLOW_UID...
==> [CREATE] Initializing Airflow (DB migration + admin user)...
[+] Running 5/5
 ✔ Network apache-airflow-exmaple_default              Created
 ✔ Volume "apache-airflow-exmaple_postgres-db-volume"  Created
 ✔ Container apache-airflow-exmaple-postgres-1         Created
 ✔ Container apache-airflow-exmaple-redis-1            Created
 ✔ Container apache-airflow-exmaple-airflow-init-1     Created
Attaching to airflow-init-1
airflow-init-1  | DB: postgresql+psycopg2://airflow:***@postgres:5432/airflow
airflow-init-1  | Performing upgrade to the metadata database...
airflow-init-1  | Database migrating done!
airflow-init-1  | Added user admin
airflow-init-1  | User "admin" created with role "Admin"
airflow-init-1  | User "user_devops" created with role "Op"
airflow-init-1  | User "user_user" created with role "User"
airflow-init-1  | User "user_viewer" created with role "Viewer"
airflow-init-1 exited with code 0
==> [CREATE] Starting all services...
[+] Running 7/7
 ✔ Container apache-airflow-exmaple-redis-1              Healthy
 ✔ Container apache-airflow-exmaple-postgres-1           Healthy
 ✔ Container apache-airflow-exmaple-airflow-init-1       Exited
 ✔ Container apache-airflow-exmaple-airflow-scheduler-1  Started
 ✔ Container apache-airflow-exmaple-airflow-webserver-1  Started
 ✔ Container apache-airflow-exmaple-airflow-worker-1     Started
 ✔ Container apache-airflow-exmaple-airflow-triggerer-1  Started

Done. Airflow is running at http://localhost:8080

Users:
  admin       / admin        (Admin)
  user_devops / user_devops  (DevOps/Op)
  user_user   / user_user    (User)
  user_viewer / user_viewer  (Viewer)
```

Airflow UI: **http://localhost:8080**

## Users

| Username      | Password     | Role   | Permissions                  |
|---------------|--------------|--------|------------------------------|
| `admin`       | `admin`      | Admin  | Full access                  |
| `user_devops` | `user_devops`| Op     | Read, edit, trigger DAGs     |
| `user_user`   | `user_user`  | User   | Read, trigger DAGs           |
| `user_viewer` | `user_viewer`| Viewer | Read only                    |

Credentials can be changed in `.env` (based on `.env.example`).

## Services

| Service            | Port | Description                    |
|--------------------|------|--------------------------------|
| airflow-webserver  | 8080 | UI + REST API                  |
| airflow-scheduler  | —    | DAG parsing + task scheduling  |
| airflow-worker     | —    | Celery task execution          |
| airflow-triggerer  | —    | Deferrable operators           |
| postgres           | 5432 | Metadata database              |
| redis              | 6379 | Celery broker                  |
| flower (optional)  | 5555 | Celery monitoring              |

## Example DAGs

| DAG                  | Schedule     | Description                                              |
|----------------------|--------------|----------------------------------------------------------|
| `hello_world`        | `@daily`     | Two TaskFlow tasks passing a value between them          |
| `etl_pipeline`       | `@daily`     | Extract → Transform (validation) → Load                  |
| `scheduled_report`   | `0 8 * * 1`  | Weekly report every Monday at 08:00 UTC                  |
| `postgres_explorer`  | manual       | Lists all tables and sample data from PostgreSQL         |
| `system_info`        | manual       | Displays OS, CPU, memory, disk and network info via Bash |

## Useful commands

```bash
# Start / stop
docker compose up -d
docker compose down
docker compose down --volumes          # stop + wipe database

# Start with Celery Flower on :5555
docker compose --profile flower up -d

# Test a DAG without the scheduler
docker compose exec airflow-scheduler airflow dags test <dag_id> 2024-01-01

# View logs
docker compose logs -f airflow-scheduler
docker compose logs -f airflow-worker
```

## Project structure

```
dags/       # DAG definitions (Python)
logs/       # Task logs (git-ignored)
plugins/    # Custom plugins / operators
config/     # Airflow configuration overrides
tests/      # Unit tests for DAGs
```

## Unit tests

Tests run locally without Docker using a virtual environment.

### Setup (once)

```bash
sh run-install-tests-dependency.sh
```

Installs all dependencies (`apache-airflow`, `pytest`, `psycopg2-binary`) using the official Airflow constraint file to ensure compatible versions.

### Running tests

```bash
./run-tests.sh
````
# Single test file
```bash
.venv/bin/pytest tests/test_etl_pipeline.py -v
```

### What is tested

| File                       | What it covers                                      |
|----------------------------|-----------------------------------------------------|
| `test_dag_integrity.py`    | All DAGs load without errors, correct task count, `catchup=False`, tags |
| `test_etl_pipeline.py`     | `extract` and `transform` logic — name cleaning, invalid record filtering |
| `test_scheduled_report.py` | `generate_report` output format, revenue formatting, churn percentage |

### Dependencies

Dependencies are listed in `requirements.txt`. Always install with the Airflow constraint file (as `run-install-test-dependecy.sh` does) to avoid version conflicts.
