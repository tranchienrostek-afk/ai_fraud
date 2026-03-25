#!/bin/bash
set -e

# --- 0. Ensure runtime dirs ---
mkdir -p /app/notifications /app/logs /app/data

# --- 1. Wait for PostgreSQL (Only if using Postgres) ---
DB_TYPE_LOWER=$(echo "$DB_TYPE" | tr '[:upper:]' '[:lower:]')

if [ "$DB_TYPE_LOWER" = "postgres" ]; then
    echo "[Entrypoint] Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
    
    # Function to check internal connection
    wait_for_db() {
      python -c "
import psycopg2, os, time, sys
host = os.getenv('POSTGRES_HOST', 'postgres')
port = int(os.getenv('POSTGRES_PORT', '5432'))
user = os.getenv('POSTGRES_USER', 'postgres')
password = os.getenv('POSTGRES_PASSWORD', 'password')
db = os.getenv('POSTGRES_DB', 'medical_db')

for i in range(30):
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db)
        conn.close()
        print('DB Connected!')
        sys.exit(0)
    except Exception as e:
        print(f'Waiting... ({e})')
        time.sleep(2)
sys.exit(1)
"
    }

    if wait_for_db; then
        echo "[Entrypoint] Database is ready."
    else
        echo "[Entrypoint] Error: Database did not start."
        exit 1
    fi
else
    echo "[Entrypoint] Skipping PostgreSQL wait (DB_TYPE=$DB_TYPE)."
fi

# --- 2. Wait for Qdrant ---
echo "[Entrypoint] Waiting for Qdrant at ${QDRANT_URL}..."
python -c "
import os, time, sys, json, urllib.request
url = os.getenv('QDRANT_URL', 'http://qdrant:6333').rstrip('/')
collection = os.getenv('QDRANT_COLLECTION', 'icd_full_kb')
min_points = int(os.getenv('QDRANT_MIN_POINTS', '0') or '0')

def get_json(req_url, data=None):
    req = urllib.request.Request(req_url, data=data, headers={'Content-Type':'application/json'} if data else {})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read().decode())

for i in range(30):
    try:
        get_json(url + '/collections')
        if min_points > 0:
            payload = b'{"exact":true}'
            res = get_json(url + f'/collections/{collection}/points/count', data=payload)
            count = res.get('result', {}).get('count', 0)
            if count < min_points:
                raise Exception(f'count {count} < min {min_points}')
        print('Qdrant OK')
        sys.exit(0)
    except Exception as e:
        print(f'Waiting... ({e})')
        time.sleep(2)
sys.exit(1)
"

# --- 3. Auto-Migrate / Init Schema ---
echo "[Entrypoint] Running Schema Initialization / Migration..."

# Check if we need to run specific migration script or just rely on App startup
# app/database/core.py automatically initializes schema on first connection.
# But trigger creation requires superuser or specific run.
# Let's run a check script or the app itself triggers it.

# For robustness, we can try running the create_db script logic if needed,
# but typically the app handles "CREATE TABLE IF NOT EXISTS".

# Force init by instantiating DatabaseCore once
python -c "from app.database.core import DatabaseCore; DatabaseCore().get_connection().close(); print('Schema Initialized')"

# --- 4. Start Application ---
echo "[Entrypoint] Starting FastAPI..."
workers="${UVICORN_WORKERS:-1}"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "$workers"
