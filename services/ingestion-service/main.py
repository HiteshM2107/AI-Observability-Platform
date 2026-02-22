from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import redis
import json
import psycopg2
import time
from fastapi import Query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wait for Redis
def wait_for_redis():
    while True:
        try:
            r = redis.Redis(host="redis", port=6379, decode_responses=True)
            r.ping()
            print("Connected to Redis")
            return r
        except:
            print("Waiting for Redis...")
            time.sleep(2)

# Wait for Postgres
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
        except:
            print("Waiting for Postgres...")
            time.sleep(2)

r = wait_for_redis()
conn = wait_for_postgres()

@app.post("/log")
async def receive_log(log: dict):
    r.rpush("logs", json.dumps(log))
    return {"status": "received"}

@app.get("/incidents")
async def get_incidents(service: str = Query(default=None)):
    cur = conn.cursor()

    if service and service != "ALL":
        cur.execute(
            "SELECT id, service, summary, created_at FROM incidents WHERE service = %s ORDER BY created_at DESC;",
            (service,)
        )
    else:
        cur.execute(
            "SELECT id, service, summary, created_at FROM incidents ORDER BY created_at DESC;"
        )

    rows = cur.fetchall()

    incidents = []
    for row in rows:
        incidents.append({
            "id": row[0],
            "service": row[1],
            "summary": row[2],
            "created_at": str(row[3])
        })

    return {"incidents": incidents}

@app.get("/metrics")
async def get_metrics():
    cur = conn.cursor()
    cur.execute("SELECT timestamp, total_logs, total_errors, error_rate FROM metrics ORDER BY timestamp ASC;")
    rows = cur.fetchall()

    data = []
    for row in rows:
        data.append({
            "timestamp": str(row[0]),
            "total_logs": row[1],
            "total_errors": row[2],
            "error_rate": row[3]
        })

    return {"metrics": data}

@app.get("/services")
async def get_services():
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT service FROM incidents;")
    rows = cur.fetchall()

    services = [row[0] for row in rows]

    return {"services": services}