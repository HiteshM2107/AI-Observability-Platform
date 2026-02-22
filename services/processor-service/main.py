import redis
import json
import time
import requests
import psycopg2
from datetime import datetime

# ----------------------------
# CONFIG
# ----------------------------
WINDOW_SIZE = 20            # Number of recent logs to evaluate
ERROR_THRESHOLD = 0.4       # 40% error rate threshold
METRIC_INTERVAL = 10        # Store metrics every N logs

# ----------------------------
# CONNECTION HELPERS
# ----------------------------

def wait_for_postgres():
    while True:
        try:
            conn = psycopg2.connect(
                host="postgres",
                database="logs",
                user="admin",
                password="admin"
            )
            print("Connected to Postgres")
            return conn
        except psycopg2.OperationalError:
            print("Waiting for Postgres...")
            time.sleep(2)

def wait_for_redis():
    while True:
        try:
            r = redis.Redis(host="redis", port=6379, decode_responses=True)
            r.ping()
            print("Connected to Redis")
            return r
        except redis.exceptions.ConnectionError:
            print("Waiting for Redis...")
            time.sleep(2)

# ----------------------------
# INITIALIZE
# ----------------------------

r = wait_for_redis()
conn = wait_for_postgres()
cur = conn.cursor()

# Create tables if not exist
cur.execute("""
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    service TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    total_logs INT,
    total_errors INT,
    error_rate FLOAT
)
""")

conn.commit()

print("Processor service started...")

# ----------------------------
# STATE
# ----------------------------

window = []          # sliding window of recent log levels
total_logs = 0
total_errors = 0
incident_cooldown = False

# ----------------------------
# MAIN LOOP
# ----------------------------

while True:
    log = r.lpop("logs")

    if log:
        log = json.loads(log)
        level = log.get("level", "INFO")

        total_logs += 1

        if level == "ERROR":
            total_errors += 1

        # ---- Sliding Window Logic ----
        window.append(level)
        if len(window) > WINDOW_SIZE:
            window.pop(0)

        if len(window) == WINDOW_SIZE:
            error_rate_window = window.count("ERROR") / WINDOW_SIZE

            # Trigger anomaly if threshold exceeded and not cooling down
            if error_rate_window > ERROR_THRESHOLD and not incident_cooldown:
                severity = "LOW"
                if error_rate_window > 0.7:
                    severity = "HIGH"
                elif error_rate_window > 0.5:
                    severity = "MEDIUM"

                response = requests.post(
                    "http://ai-service:8000/analyze",
                    json={"service": log["service"]}
                )
                summary = response.json()["summary"]

                final_summary = (
                    f"[{severity}] "
                    f"Error rate {round(error_rate_window*100,2)}% "
                    f"in last {WINDOW_SIZE} logs. {summary}"
                )

                cur.execute(
                    "INSERT INTO incidents (service, summary) VALUES (%s, %s)",
                    (log["service"], final_summary)
                )
                conn.commit()

                print("Incident created:", final_summary)

                incident_cooldown = True

        # Reset cooldown if system stabilizes
        if len(window) == WINDOW_SIZE:
            error_rate_window = window.count("ERROR") / WINDOW_SIZE
            if error_rate_window < 0.2:
                incident_cooldown = False

        # ---- Store Metrics Periodically ----
        if total_logs % METRIC_INTERVAL == 0:
            overall_error_rate = (total_errors / total_logs) * 100

            cur.execute(
                "INSERT INTO metrics (timestamp, total_logs, total_errors, error_rate) VALUES (%s, %s, %s, %s)",
                (datetime.utcnow(), total_logs, total_errors, overall_error_rate)
            )
            conn.commit()

    time.sleep(0.5)