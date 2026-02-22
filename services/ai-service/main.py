from fastapi import FastAPI

app = FastAPI()

@app.post("/analyze")
async def analyze(data: dict):
    return {
        "summary": f"Spike detected in {data['service']}. Likely increased error rate. Investigate recent changes."
    }