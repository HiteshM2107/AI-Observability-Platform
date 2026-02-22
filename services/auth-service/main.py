import requests
import time
import random
from datetime import datetime

INGESTION_URL = "http://ingestion-service:8000/log"

def wait_for_ingestion():
    while True:
        try:
            requests.get("http://ingestion-service:8000/docs")
            print("Connected to ingestion-service")
            return
        except:
            print("Waiting for ingestion-service...")
            time.sleep(2)

wait_for_ingestion()

while True:
    log = {
        "service": "auth-service",
        "level": "INFO",
        "timestamp": str(datetime.utcnow()),
        "message": "User login attempt",
        "success": random.choice([True, True, True, False])
    }

    try:
        requests.post(INGESTION_URL, json=log)
    except:
        print("Failed to send log")

    time.sleep(2)