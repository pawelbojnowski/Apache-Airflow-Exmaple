#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================
# DROP — Apache Airflow infrastructure
# ============================================================
echo "==> [DROP] Stopping and removing containers, volumes and networks..."
docker compose down --volumes --remove-orphans 2>/dev/null || true

echo "==> [DROP] Removing temporary folders and .env file..."
rm -rf logs
rm -f .env

# ============================================================
# CREATE — Apache Airflow infrastructure
# ============================================================
echo "==> [CREATE] Creating Airflow directories..."
mkdir -p logs

echo "==> [CREATE] Copying .env.example -> .env..."
cp .env.example .env

echo "==> [CREATE] Checking for required Python package: cryptography..."
python3 -c "import cryptography" 2>/dev/null || pip3 install --quiet cryptography

echo "==> [CREATE] Generating AIRFLOW_FERNET_KEY..."
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "==> [CREATE] Generating AIRFLOW_SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

sed -i.bak "s|^AIRFLOW_FERNET_KEY=.*|AIRFLOW_FERNET_KEY=${FERNET_KEY}|" .env
sed -i.bak "s|^AIRFLOW_SECRET_KEY=.*|AIRFLOW_SECRET_KEY=${SECRET_KEY}|" .env
rm -f .env.bak

echo "==> [CREATE] Setting AIRFLOW_UID..."
# On macOS, Docker Desktop manages volume permissions internally.
# Using the host UID (e.g. 501) fails because it has no entry in the
# container's /etc/passwd, causing: KeyError: 'getpwuid(): uid not found'
# Solution: use Airflow's built-in UID (50000) on macOS; host UID on Linux.
if [[ "$(uname)" == "Darwin" ]]; then
    echo "AIRFLOW_UID=50000" >> .env
else
    echo "AIRFLOW_UID=$(id -u)" >> .env
fi

echo "==> [CREATE] Initializing Airflow (DB migration + admin user)..."
docker compose up airflow-init

echo "==> [CREATE] Starting all services..."
docker compose up -d

echo ""
echo "Done. Airflow is running at http://localhost:8080"
echo ""
echo "Users:"
echo "  admin       / admin        (Admin)"
echo "  user_devops / user_devops  (DevOps)"
echo "  user_user   / user_user    (User)"
echo "  user_viewer / user_viewer  (Viewer)"
