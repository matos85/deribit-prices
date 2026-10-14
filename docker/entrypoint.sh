#!/bin/sh
set -eu

cd /opt/app

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import time

from sqlalchemy import create_engine, text

dsn = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://deribit:deribit@db:5432/deribit_prices",
)
engine = create_engine(dsn, pool_pre_ping=True)

for attempt in range(60):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("PostgreSQL is ready")
        break
    except Exception as exc:
        print(f"Attempt {attempt + 1}/60: {exc}")
        time.sleep(1)
else:
    raise SystemExit("PostgreSQL did not become ready in time")
PY

python - <<'PY'
from app.core.config import get_settings
from app.infrastructure.database import Database

database = Database(get_settings())
database.create_tables()
print("Database schema is ready")
PY

# Start Redis before supervisord so Celery has a broker immediately.
redis-server --bind 127.0.0.1 --port 6379 --save "" --appendonly no --daemonize yes

attempt=1
while [ "$attempt" -le 30 ]; do
    if redis-cli ping >/dev/null 2>&1; then
        echo "Redis is ready"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if ! redis-cli ping >/dev/null 2>&1; then
    echo "Redis did not become ready in time" >&2
    exit 1
fi

exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
