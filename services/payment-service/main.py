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
    level = "ERROR" if random.random() < 0.6 else "INFO"

    log = {
        "service": "payment-service",
        "level": level,
        "timestamp": str(datetime.utcnow()),
        "message": "Payment processed" if level == "INFO" else "Payment timeout error"
    }

    try:
        requests.post(INGESTION_URL, json=log)
    except:
        print("Failed to send log")

    time.sleep(1)